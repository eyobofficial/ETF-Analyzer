import yfinance as yf
import requests
from tabulate import tabulate
from mail import send_email


class ETFAnalyzer:
    def __init__(self, etf_symbol, constituents_url):
        self.constituents_url = constituents_url
        self.etf_symbol = etf_symbol
        self.etf_data = None
        self.stock_data = {}

    def fetch_etf_data(self):
        """Fetch ETF data for the given trading day."""
        etf = yf.Ticker(self.etf_symbol)
        history = etf.history(period='5d')

        if len(history) < 2:
            raise ValueError("Not enough historical data for the ETF.")

        # Format the date as 'dd-mm-yyyy'
        self.etf_data = {
            'previous_close': round(history['Close'].iloc[-2], 2),
            'current_close': round(history['Close'].iloc[-1], 2),
            'volume': history['Volume'].iloc[-1],
            'date': history.index[-1].strftime('%d-%m-%Y')
        }

    def fetch_stock_data(self):
        """Fetch stock data for the underlying assets of the ETF."""
        response = requests.get(self.constituents_url)
        if response.status_code == 200:
            csv_data = response.text.splitlines()
            symbols = [row.split(",")[0] for row in csv_data[1:]]  # Extract stock symbols

            # Fetch stock data for each symbol
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                history = ticker.history(period='5d')
                info = ticker.info
                if len(history) >= 2:
                    self.stock_data[symbol] = {
                        'previous_close': round(history['Close'].iloc[-2], 2),
                        'current_close': round(history['Close'].iloc[-1], 2),
                        'company_name': info.get('longName', 'N/A'),
                        'stock_price': round(info.get('regularMarketPrice', info.get('previousClose', 0)), 2)
                    }

    @property
    def trading_date(self):
        return self.etf_data['date']

    def calculate_stock_gains(self):
        """Calculate percentage and point gains/loss for each stock."""
        stock_gains = {}
        for symbol, data in self.stock_data.items():
            previous_close = data['previous_close']
            current_close = data['current_close']
            point_gain = round(current_close - previous_close, 2)
            percentage_gain = round((point_gain / previous_close) * 100, 2) if previous_close else 0

            stock_gains[symbol] = {
                'point_gain': point_gain,
                'percentage_gain': percentage_gain
            }

        # Sort by percentage gain, from highest to lowest
        stock_gains = dict(sorted(stock_gains.items(), key=lambda x: x[1]['percentage_gain'], reverse=True))
        return stock_gains

    def calculate_etf_contribution(self):
        """Calculate each stock's contribution to the overall ETF change."""
        total_change = round(self.etf_data['current_close'] - self.etf_data['previous_close'], 2)
        total_percentage_change = round((total_change / self.etf_data['previous_close']) * 100, 2)
        stock_contributions = {}

        for symbol, data in self.stock_data.items():
            previous_close = data['previous_close']
            point_gain = round(data['current_close'] - previous_close, 2)
            contribution_point = round((point_gain / total_change), 2) if total_change != 0 else 0
            contribution_percentage = round((point_gain / self.etf_data['previous_close']) * 100, 2) if previous_close else 0

            stock_contributions[symbol] = {
                'point_contribution': contribution_point,
                'percentage_contribution': contribution_percentage
            }

        return stock_contributions, total_change, total_percentage_change

    def get_summary(self, colored=False, html=False):
        """Return the ETF summary."""
        point_change = round(self.etf_data['current_close'] - self.etf_data['previous_close'], 2)
        if point_change > 0:
            point_change_display = f"<span style='color:green'>+{point_change:.2f}</span>" if html else f"\033[92m+{point_change:.2f}\033[0m"
            percentage_change_display = f"<span style='color:green'>+{(point_change / self.etf_data['previous_close']) * 100:.2f}%</span>" if html else f"\033[92m+{(point_change / self.etf_data['previous_close']) * 100:.2f}%\033[0m"
        else:
            point_change_display = f"<span style='color:red'>{point_change:.2f}</span>" if html else f"\033[91m{point_change:.2f}\033[0m"
            percentage_change_display = f"<span style='color:red'>{(point_change / self.etf_data['previous_close']) * 100:.2f}%</span>" if html else f"\033[91m{(point_change / self.etf_data['previous_close']) * 100:.2f}%\033[0m"

        summary = [
            ["<b>Trading Date: </b>" if html else "Trading Date: ", self.etf_data['date']],
            ["<b>ETF Name: </b>" if html else "ETF Name: ", self.etf_symbol],
            ["<b>Price: </b>" if html else "Price: ", f"${self.etf_data['current_close']:.2f}"],
            ["<b>Volume: </b>" if html else "Volume: ", f"{self.etf_data['volume']:,}"],
            ["<b>Point Change: </b>" if html else "Point Change: ", point_change_display if colored else f"{point_change:.2f}"],
            ["<b>Percentage Change: </b>" if html else "Percentage Change: ", percentage_change_display if colored else f"{(point_change / self.etf_data['previous_close']) * 100:.2f}%"]
        ]

        if html:
            return f"<table border='1'>{''.join([f'<tr><td>{row[0]}</td><td>{row[1]}</td></tr>' for row in summary])}</table>"
        return tabulate(summary, tablefmt="plain")

    def get_stock_list(self, colored=False, html=False):
        """Return the stock gains and ETF contributions."""
        stock_contributions, _, _ = self.calculate_etf_contribution()

        table_data = []
        headers = ["#", "Stock", "Company", "Gain (Pt)", "Gain (%)", "Price ($)", "Contribution (%)"]
        for i, (symbol, gains) in enumerate(self.calculate_stock_gains().items(), start=1):
            point_gain = gains['point_gain']
            percentage_gain = gains['percentage_gain']
            contribution_percentage = stock_contributions[symbol]['percentage_contribution']
            color = "\033[92m" if point_gain > 0 else "\033[91m"  # Green for gain, Red for loss
            reset_color = "\033[0m"

            # Colored or HTML output
            if html:
                color = "green" if point_gain > 0 else "red"
                row = f"<tr><td>{i}</td><td>{symbol}</td><td>{self.stock_data[symbol]['company_name']}</td><td style='color:{color}'>{point_gain:.2f}</td><td style='color:{color}'>{percentage_gain:.2f}%</td><td>{self.stock_data[symbol]['stock_price']:.2f}</td><td>{contribution_percentage:.2f}%</td></tr>"
                table_data.append(row)
            else:
                row = [
                    f"{i:^3}",
                    symbol,
                    self.stock_data[symbol]['company_name'],
                    f"{color}{point_gain:>6.2f}{reset_color}" if colored else f"{point_gain:>6.2f}",
                    f"{color}{percentage_gain:>6.2f}%{reset_color}" if colored else f"{percentage_gain:>6.2f}%",
                    f"{self.stock_data[symbol]['stock_price']:>10.2f}",
                    f"{contribution_percentage:>10.2f}%"
                ]
                table_data.append(row)

        if html:
            header_row = f"<tr>{''.join([f'<th>{header}</th>' for header in headers])}</tr>"
            return f"<table border='1'>{header_row}{''.join(table_data)}</table>"
        return tabulate(table_data, headers=headers, tablefmt="grid")

    def get_report(self, colored=False, html=False):
        """Combine the summary and stock list into a full report."""
        summary = self.get_summary(colored=colored, html=html)
        stock_list = self.get_stock_list(colored=colored, html=html)
        if html:
            return f"<html><body>{summary}<br><br>{stock_list}</body></html>"
        return f'{summary}\n\n{stock_list}'


if __name__ == "__main__":
    etf = 'VOO'  # Example using VOO ETF (S&P 500 ETF)
    constituents_url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"

    # Generate the report and send it via email
    analyzer = ETFAnalyzer(etf, constituents_url)
    analyzer.fetch_etf_data()
    analyzer.fetch_stock_data()
    report = analyzer.get_report(colored=True, html=True)
    send_email('hello@eyob.tech', 'VOO Report', body_html=report)