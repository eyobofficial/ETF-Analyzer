# ETF Market Analyzer

ETF Analyzer is a Python-based project designed to analyze the performance of ETFs (Exchange-Traded Funds) and their constituent stocks for the previous market trading day. This tool fetches data from financial APIs (such as Yahoo Finance) to calculate daily gains or losses for both the ETF and individual stocks within the fund. It provides a detailed breakdown of each stock's point and percentage gains and their contribution to the overall performance of the ETF.

## Requirements
* Python 3.10+


# Local Setup
1. Clone the repository to your local machine.
```sh
git clone git@github.com:eyobofficial/ETF-Analyzer.git
```
2. Navigate to the root directory of the repository and create a Python virtual environment. (optional but recommended)
```sh
cd etf-analyzer
python3 -m venv venv
source venv/bin/activate
```
3. Install the Python dependencies from the `requirements.txt` file.
```sh
python -m pip install -r requirements.txt
```
4. Copy `.env.example` to a new file and rename the new file to .env. This is where we are going to put all the environmental variables. Update the environmental variables accordingly.
```sh

# The source Google email you want to send the report from
FROM_EMAIL=

# The name that should be displayed in the email sent
FROM_NAME=

# Your Gmail handle
GOOGLE_APP_LOGIN=

# Your Google App password (Warning: Do not use your main password. Create a Google App instead)
GOOGLE_APP_PASSWORD=
```
5. Run your script using the Click command line utility. For example, to retrieve the [VOO] ETF market data for the previous trading day.
```sh
cd ./src

python main.py --etf-symbol VOO --data-url https://datahub.io/core/s-and-p-500-companies/r/constituents.csv --to-email targetemail@example.com
```