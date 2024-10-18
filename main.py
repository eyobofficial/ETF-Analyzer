import click

from etf import ETFAnalyzer
from mail import send_email


@click.command()
@click.option('--etf-symbol', required=True, help='The ETF symbol to analyze.')
@click.option('--data-url', required=True, help='URL to fetch the ETF constituents.')
@click.option('--to-email', required=True, help='Email address to send the report.')
def main(etf_symbol, data_url, to_email):
    try:
        # Initialize the ETF analyzer
        etf_analyzer = ETFAnalyzer(etf_symbol, data_url)
        etf_analyzer.fetch_etf_data()
        etf_analyzer.fetch_stock_data()
        
        # Prepare and send the email report
        subject = f'{etf_symbol.upper()} Analysis Report | {etf_analyzer.trading_date}'
        report =  etf_analyzer.get_report(colored=True, html=True)
        send_email(to_email, subject, body_html=report)
    except Exception as e:
        print(f'Failed to generate ETF analysis report. Error: {str(e)}')


if __name__ == '__main__':
    main()