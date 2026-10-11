from sqlalchemy import text

from database.postgres_sql import get_engine, create_database


def create_tables() -> None:
    engine = get_engine()

    if engine.dialect.name == "sqlite":
        query = """
        CREATE TABLE IF NOT EXISTS financial_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company VARCHAR(100),
            year VARCHAR(10),
            revenue TEXT,
            net_income TEXT,
            operating_income TEXT,
            cash_flow TEXT,
            total_assets TEXT,
            total_liabilities TEXT,
            risk_factors TEXT,
            growth_drivers TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    else:
        query = """
        CREATE TABLE IF NOT EXISTS financial_metrics (
            id SERIAL PRIMARY KEY,
            company VARCHAR(100),
            year VARCHAR(10),
            revenue TEXT,
            net_income TEXT,
            operating_income TEXT,
            cash_flow TEXT,
            total_assets TEXT,
            total_liabilities TEXT,
            risk_factors TEXT,
            growth_drivers TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

    with engine.begin() as connection:
        connection.execute(text(query))

    print("financial_metrics table created.")
    
    # Auto-seed initial data if empty
    try:
        with engine.begin() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM financial_metrics"))
            count = result.scalar()
            if count == 0:
                from database.seed_data import seed_metrics
                seed_metrics(connection)
    except Exception as e:
        print(f"Notice on seed check: {e}")


if __name__ == "__main__":
    create_database()
    create_tables()