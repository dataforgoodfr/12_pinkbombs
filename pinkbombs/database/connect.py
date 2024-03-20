from sqlalchemy import create_engine

from pinkbombs.database.config import (
    DATABASEID,
    PGDATABASE,
    PGHOST,
    PGPASSWORD,
    PGPORT,
    PGUSER,
)

engine = create_engine(
    (
        f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}?"
        f"sslmode=require&options=databaseid{DATABASEID}"
    ),
    connect_args={"connect_timeout": 30},
)
