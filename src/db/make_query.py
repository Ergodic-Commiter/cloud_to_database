import sys
from src.db import engine


if __name__ == '__main__': 
    column = sys.argv[1] if len(sys.argv) > 1 else 'Nombre en PBI'
    file = sys.argv[2] if len(sys.argv) > 2 else 'refs/sql/excel_query.sql'

    engine.make_query(column, file)
