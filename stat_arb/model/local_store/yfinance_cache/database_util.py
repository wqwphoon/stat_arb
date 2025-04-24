if __name__ == "__main__":
    import sqlite3

    import yfinance as yf

    db = "yfinance_analytics.db"

    conn = sqlite3.connect(db)

    c = conn.cursor()

    # data = yf.download("AMZN", "2024-01-01", "2025-01-01", multi_level_index=False)

    # data.to_sql("AMZN", conn, if_exists="replace")

    conn.close()
    pass
