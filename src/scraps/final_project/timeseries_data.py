import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import yfinance as yf


class TimeseriesData:
    def __init__(self):
        # Database name
        self.db_name = 'sqlite:///sp_500.db'

    def scrape_sp500_constituents(self):
        """
        Scrape the constituents of the S&P 500 index

        Returns
        -------
        S&P 500 symbols: list[str]
            List of S&P 500 constituent symbols
        """
        # Address to scrape S&P500 constituents from
        url = r"https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

        # Scrape symbols
        self.symbols = pd.read_html(url)[0].Symbol.to_list()

        return self.symbols

    def get_constituents_sector(self):
        """
        Get sector and industry for tickers

        Returns
        -------
        sector_df: pd.DataFrame
            DataFrame with Sector and Industry data for tickers
        """

        sector_dict = {}
        for symbol in self.symbols:
            ticker = yf.Ticker(symbol)
            # Get sector
            try:
                sector = ticker.info.get("sector", "Missing")
            except KeyError:
                print(f"Encountered error for sector extraction for ticker "
                      f"{symbol}")
                sector = "Missing"
            # Get industry
            try:
                industry = ticker.info.get("industry", "Missing")
            except KeyError:
                print(f"Encountered error for industry extraction for ticker "
                      f"{symbol}")
                industry = "Missing"

            # Assign results to dictionary
            sector_dict[symbol] = [sector, industry]

        sector_df = pd.DataFrame(sector_dict).T
        sector_df.columns = ["Sector", "Industry"]

        return sector_df

    def run_locally(self):
        """
        Assign self.symbols attribute locally to avoid online scraping.
        """
        self.symbols = symbols_local

    def create_sp500_database(self, start: str, end: str):
        """
        Fetch S&P 500 data from yfinance and store in database.

        start: str
            Start date for price extraction
        end: str
            End date for price extraction
        """
        # Create engine to interact with database
        engine = create_engine(self.db_name)

        # Fetch data from yahoo using list comprehension
        data = [yf.download(symbol, start=start, end=end, progress=False)
                .reset_index() for symbol in self.symbols]

        # Save it to database
        for frame, symbol in zip(data, self.symbols):
            frame.to_sql(symbol, engine, if_exists='replace', index=False)

    def query_db(self, query):
        """
        Query database

        Parameters
        ----------
        query: str
            SQL query for database.

        Returns
        -------
        result: pd.DataFrame
            Result of query.
        """
        # Engine to interact with database
        engine = create_engine(self.db_name)

        # Connect to database and execute query
        with engine.connect() as connection:
            result = pd.read_sql_query(
                text(query), connection, index_col="Date")

        return result

    def aggregate_adj_close(self):
        """
        Aggregate Adj Close prices across all tickers into one dataframe.

        Returns
        -------
        self.df_close: pd.DataFrame
            DataFrame aggregating close price timeseries across all tickers
        """
        dfs_list = []

        # For each symbol, query database for Adj Close timeseries
        for symbol in self.symbols:
            query = f'SELECT "Date", "Adj Close" FROM "{symbol}"'

            df_symbol = self.query_db(query)

            df_symbol.columns = [symbol]

            dfs_list.append(df_symbol)

        # Merge all dataframes together
        df_agg = dfs_list[0].join(dfs_list[1:], how="outer")

        # Data cleaning via forward fill
        self.df_close = df_agg.ffill()

        return self.df_close

    def get_correlated_pairs(self, threshold: float = 0.95):
        """
        Get correlated pairs above threshold.

        Parameters
        ----------
        theshold: float, default=0.95
            Threshold for pairs correlation.

        Returns
        -------
        self.high_corr_pairs: list
            List of S&P500 pairs with correlation above the input threshold.
            Each element in list is a tuple (a, b, correlation)
        """

        corr_matrix = self.df_close.corr()

        # Define upper triangular matrix (without diag) to avoid pair duplicates.
        upper_triangle = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)

        # Get pairs above threshold
        self.high_corr_pairs = [
            (corr_matrix.index[i], corr_matrix.columns[j], corr_matrix.iat[i, j])
            for i in range(corr_matrix.shape[0])
            for j in range(corr_matrix.shape[1])
            if upper_triangle[i, j] and corr_matrix.iat[i, j] > threshold
        ]

        # Display results
        for pair in self.high_corr_pairs:
            print(f"Pair: {pair[0]}-{pair[1]}, Correlation: {pair[2]}")

        n_corr_pairs = len(self.high_corr_pairs)

        print(f"Number of pairs above correlation threshold: {n_corr_pairs}")

        return self.high_corr_pairs


# Local store of symbols
symbols_local = [
 'MMM',
 'AOS',
 'ABT',
 'ABBV',
 'ACN',
 'ADBE',
 'AMD',
 'AES',
 'AFL',
 'A',
 'APD',
 'ABNB',
 'AKAM',
 'ALB',
 'ARE',
 'ALGN',
 'ALLE',
 'LNT',
 'ALL',
 'GOOGL',
 'GOOG',
 'MO',
 'AMZN',
 'AMCR',
 'AEE',
 'AEP',
 'AXP',
 'AIG',
 'AMT',
 'AWK',
 'AMP',
 'AME',
 'AMGN',
 'APH',
 'ADI',
 'ANSS',
 'AON',
 'APA',
 'APO',
 'AAPL',
 'AMAT',
 'APTV',
 'ACGL',
 'ADM',
 'ANET',
 'AJG',
 'AIZ',
 'T',
 'ATO',
 'ADSK',
 'ADP',
 'AZO',
 'AVB',
 'AVY',
 'AXON',
 'BKR',
 'BALL',
 'BAC',
 'BAX',
 'BDX',
 'BRK.B',
 'BBY',
 'TECH',
 'BIIB',
 'BLK',
 'BX',
 'BK',
 'BA',
 'BKNG',
 'BWA',
 'BSX',
 'BMY',
 'AVGO',
 'BR',
 'BRO',
 'BF.B',
 'BLDR',
 'BG',
 'BXP',
 'CHRW',
 'CDNS',
 'CZR',
 'CPT',
 'CPB',
 'COF',
 'CAH',
 'KMX',
 'CCL',
 'CARR',
 'CAT',
 'CBOE',
 'CBRE',
 'CDW',
 'CE',
 'COR',
 'CNC',
 'CNP',
 'CF',
 'CRL',
 'SCHW',
 'CHTR',
 'CVX',
 'CMG',
 'CB',
 'CHD',
 'CI',
 'CINF',
 'CTAS',
 'CSCO',
 'C',
 'CFG',
 'CLX',
 'CME',
 'CMS',
 'KO',
 'CTSH',
 'CL',
 'CMCSA',
 'CAG',
 'COP',
 'ED',
 'STZ',
 'CEG',
 'COO',
 'CPRT',
 'GLW',
 'CPAY',
 'CTVA',
 'CSGP',
 'COST',
 'CTRA',
 'CRWD',
 'CCI',
 'CSX',
 'CMI',
 'CVS',
 'DHR',
 'DRI',
 'DVA',
 'DAY',
 'DECK',
 'DE',
 'DELL',
 'DAL',
 'DVN',
 'DXCM',
 'FANG',
 'DLR',
 'DFS',
 'DG',
 'DLTR',
 'D',
 'DPZ',
 'DOV',
 'DOW',
 'DHI',
 'DTE',
 'DUK',
 'DD',
 'EMN',
 'ETN',
 'EBAY',
 'ECL',
 'EIX',
 'EW',
 'EA',
 'ELV',
 'EMR',
 'ENPH',
 'ETR',
 'EOG',
 'EPAM',
 'EQT',
 'EFX',
 'EQIX',
 'EQR',
 'ERIE',
 'ESS',
 'EL',
 'EG',
 'EVRG',
 'ES',
 'EXC',
 'EXPE',
 'EXPD',
 'EXR',
 'XOM',
 'FFIV',
 'FDS',
 'FICO',
 'FAST',
 'FRT',
 'FDX',
 'FIS',
 'FITB',
 'FSLR',
 'FE',
 'FI',
 'FMC',
 'F',
 'FTNT',
 'FTV',
 'FOXA',
 'FOX',
 'BEN',
 'FCX',
 'GRMN',
 'IT',
 'GE',
 'GEHC',
 'GEV',
 'GEN',
 'GNRC',
 'GD',
 'GIS',
 'GM',
 'GPC',
 'GILD',
 'GPN',
 'GL',
 'GDDY',
 'GS',
 'HAL',
 'HIG',
 'HAS',
 'HCA',
 'DOC',
 'HSIC',
 'HSY',
 'HES',
 'HPE',
 'HLT',
 'HOLX',
 'HD',
 'HON',
 'HRL',
 'HST',
 'HWM',
 'HPQ',
 'HUBB',
 'HUM',
 'HBAN',
 'HII',
 'IBM',
 'IEX',
 'IDXX',
 'ITW',
 'INCY',
 'IR',
 'PODD',
 'INTC',
 'ICE',
 'IFF',
 'IP',
 'IPG',
 'INTU',
 'ISRG',
 'IVZ',
 'INVH',
 'IQV',
 'IRM',
 'JBHT',
 'JBL',
 'JKHY',
 'J',
 'JNJ',
 'JCI',
 'JPM',
 'JNPR',
 'K',
 'KVUE',
 'KDP',
 'KEY',
 'KEYS',
 'KMB',
 'KIM',
 'KMI',
 'KKR',
 'KLAC',
 'KHC',
 'KR',
 'LHX',
 'LH',
 'LRCX',
 'LW',
 'LVS',
 'LDOS',
 'LEN',
 'LII',
 'LLY',
 'LIN',
 'LYV',
 'LKQ',
 'LMT',
 'L',
 'LOW',
 'LULU',
 'LYB',
 'MTB',
 'MPC',
 'MKTX',
 'MAR',
 'MMC',
 'MLM',
 'MAS',
 'MA',
 'MTCH',
 'MKC',
 'MCD',
 'MCK',
 'MDT',
 'MRK',
 'META',
 'MET',
 'MTD',
 'MGM',
 'MCHP',
 'MU',
 'MSFT',
 'MAA',
 'MRNA',
 'MHK',
 'MOH',
 'TAP',
 'MDLZ',
 'MPWR',
 'MNST',
 'MCO',
 'MS',
 'MOS',
 'MSI',
 'MSCI',
 'NDAQ',
 'NTAP',
 'NFLX',
 'NEM',
 'NWSA',
 'NWS',
 'NEE',
 'NKE',
 'NI',
 'NDSN',
 'NSC',
 'NTRS',
 'NOC',
 'NCLH',
 'NRG',
 'NUE',
 'NVDA',
 'NVR',
 'NXPI',
 'ORLY',
 'OXY',
 'ODFL',
 'OMC',
 'ON',
 'OKE',
 'ORCL',
 'OTIS',
 'PCAR',
 'PKG',
 'PLTR',
 'PANW',
 'PARA',
 'PH',
 'PAYX',
 'PAYC',
 'PYPL',
 'PNR',
 'PEP',
 'PFE',
 'PCG',
 'PM',
 'PSX',
 'PNW',
 'PNC',
 'POOL',
 'PPG',
 'PPL',
 'PFG',
 'PG',
 'PGR',
 'PLD',
 'PRU',
 'PEG',
 'PTC',
 'PSA',
 'PHM',
 'PWR',
 'QCOM',
 'DGX',
 'RL',
 'RJF',
 'RTX',
 'O',
 'REG',
 'REGN',
 'RF',
 'RSG',
 'RMD',
 'RVTY',
 'ROK',
 'ROL',
 'ROP',
 'ROST',
 'RCL',
 'SPGI',
 'CRM',
 'SBAC',
 'SLB',
 'STX',
 'SRE',
 'NOW',
 'SHW',
 'SPG',
 'SWKS',
 'SJM',
 'SW',
 'SNA',
 'SOLV',
 'SO',
 'LUV',
 'SWK',
 'SBUX',
 'STT',
 'STLD',
 'STE',
 'SYK',
 'SMCI',
 'SYF',
 'SNPS',
 'SYY',
 'TMUS',
 'TROW',
 'TTWO',
 'TPR',
 'TRGP',
 'TGT',
 'TEL',
 'TDY',
 'TFX',
 'TER',
 'TSLA',
 'TXN',
 'TPL',
 'TXT',
 'TMO',
 'TJX',
 'TSCO',
 'TT',
 'TDG',
 'TRV',
 'TRMB',
 'TFC',
 'TYL',
 'TSN',
 'USB',
 'UBER',
 'UDR',
 'ULTA',
 'UNP',
 'UAL',
 'UPS',
 'URI',
 'UNH',
 'UHS',
 'VLO',
 'VTR',
 'VLTO',
 'VRSN',
 'VRSK',
 'VZ',
 'VRTX',
 'VTRS',
 'VICI',
 'V',
 'VST',
 'VMC',
 'WRB',
 'GWW',
 'WAB',
 'WBA',
 'WMT',
 'DIS',
 'WBD',
 'WM',
 'WAT',
 'WEC',
 'WFC',
 'WELL',
 'WST',
 'WDC',
 'WY',
 'WMB',
 'WTW',
 'WDAY',
 'WYNN',
 'XEL',
 'XYL',
 'YUM',
 'ZBRA',
 'ZBH',
 'ZTS']
