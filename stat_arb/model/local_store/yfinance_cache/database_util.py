if __name__ == "__main__":
    import sqlite3

    import yfinance as yf

    from stat_arb.model.config import DB

    conn = sqlite3.connect(DB)

    c = conn.cursor()

    if False:
        data = yf.download("AMZN", "2024-01-01", "2025-01-01", multi_level_index=False)

        data.to_sql("AMZN", conn, if_exists="replace")

    conn.close()
    pass
