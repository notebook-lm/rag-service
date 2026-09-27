import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:change-me@localhost:5432/notebook_lm"
)
