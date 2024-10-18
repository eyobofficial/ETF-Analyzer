import yfinance as yf
from tabulate import tabulate

class StockAnalyzer:
    def __init__(self, stock_symbol):
        self.stock_symbol = stock_symbol
        self.stock_data = None
        self.stock_info = None

    def fetch_stock_data(self, range_days=10):
        """Fetch stock data for a longer period and then slice for the last X days."""
        stock = yf.Ticker(self.stock_symbol)
        # Fetch data for 1 month, then slice the last `range_days` days.
        self.stock_data = stock.history(period='1mo').tail(range_days)
        self.stock_info = stock.info

        if self.stock_data.empty:
            raise ValueError(f"No data available for {self.stock_symbol} over the last {range_days} days.")

    def calculate_daily_returns(self):
        """Calculate daily returns in points, percentages, and volume for the given stock."""
        daily_returns = []
        for i in range(1, len(self.stock_data)):
            previous_close = self.stock_data['Close'].iloc[i-1]
            current_close = self.stock_data['Close'].iloc[i]
            point_return = round(current_close - previous_close, 2)
            percentage_return = round((point_return / previous_close) * 100, 2) if previous_close != 0 else 0
            volume = self.stock_data['Volume'].iloc[i]

            # Store date, point return, percentage return, and volume
            daily_returns.append({
                'date': self.stock_data.index[i].strftime('%Y-%m-%d'),
                'point_return': point_return,
                'percentage_return': percentage_return,
                'volume': volume
            })

        # Sort by date in descending order (latest first)
        return sorted(daily_returns, key=lambda x: x['date'], reverse=True)

    def calculate_total_return(self):
        """Calculate the total return in points and percentage over the given period."""
        start_price = self.stock_data['Close'].iloc[0]
        end_price = self.stock_data['Close'].iloc[-1]
        point_return = round(end_price - start_price, 2)
        percentage_return = round((point_return / start_price) * 100, 2) if start_price != 0 else 0
        return {
            'total_point_return': point_return,
            'total_percentage_return': percentage_return
        }

    def print_daily_returns(self, daily_returns):
        """Print daily returns in a table format with color coding and volume."""
        table_data = []
        for day_return in daily_returns:
            point_return = day_return['point_return']
            percentage_return = day_return['percentage_return']
            volume = day_return['volume']
            # Color the return values: Green for gains, Red for losses
            color = "\033[92m" if point_return > 0 else "\033[91m"  # Green for gain, Red for loss
            reset_color = "\033[0m"
            
            table_data.append([
                day_return['date'],
                f"{color}{point_return}{reset_color}",  # Colored point return
                f"{color}{percentage_return}%{reset_color}",  # Colored percentage return
                f"{volume:,}"  # Add volume with thousands separator
            ])

        headers = ["Date", "Point", "Percentage", "Volume"]
        print(tabulate(table_data, headers=headers, tablefmt="plain"))

    def print_summary(self):
        """Print the stock's summary information and compare P/E ratio against industry if available."""
        stock_name = self.stock_info.get('longName', 'N/A')
        # Use 'regularMarketPrice' or fallback to 'previousClose' to get the correct stock price
        stock_price = round(self.stock_info.get('regularMarketPrice', self.stock_info.get('previousClose', 0)), 2)
        pe_ratio = round(self.stock_info.get('trailingPE', 0), 2) if self.stock_info.get('trailingPE') else 'N/A'
        sector = self.stock_info.get('sector', 'N/A')
        industry = self.stock_info.get('industry', 'N/A')
        industry_pe = self.stock_info.get('industryPE', 'N/A')  # Some tickers might have this data

        # Compare P/E ratio against industry P/E if possible
        if pe_ratio != 'N/A' and industry_pe != 'N/A':
            pe_comparison = f"{pe_ratio} (Stock P/E) vs {industry_pe} (Industry P/E)"
        else:
            pe_comparison = "Industry P/E data not available for comparison"

        summary = [
            ["Stock Name", stock_name],
            ["Stock Price", f"${stock_price}"],
            ["P/E Ratio", pe_ratio],
            ["Sector", sector],
            ["Industry", industry],
            ["P/E Comparison", pe_comparison]
        ]
        print(tabulate(summary, tablefmt="plain"))

    def analyze(self, range_days=10):
        """Run the analysis for the given stock over the specified period."""
        self.fetch_stock_data(range_days)
        daily_returns = self.calculate_daily_returns()
        total_return = self.calculate_total_return()

        # Print stock summary
        print("\nStock Summary:")
        self.print_summary()

        # Print daily returns
        print("\nDaily Returns:")
        self.print_daily_returns(daily_returns)

        # Print total return
        print("\nTotal Return over the period:")
        color = "\033[92m" if total_return['total_point_return'] > 0 else "\033[91m"
        reset_color = "\033[0m"
        print(f"{color}Point Return: {total_return['total_point_return']}{reset_color}")
        print(f"{color}Percentage Return: {total_return['total_percentage_return']}%{reset_color}")

# Example usage:
if __name__ == "__main__":
    stock_analyzer = StockAnalyzer('AAPL')  # Replace with any stock symbol you want to analyze
    stock_analyzer.analyze(10)  # Analyze the last 10 days of stock data
