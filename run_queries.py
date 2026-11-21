
import sqlite3
from pathlib import Path

DB_PATH = "database/bluestock_mf.db"
QUERY_PATH = Path("sql/queries.sql")

with open(QUERY_PATH, "r", encoding="utf-8") as file:
    sql_content = file.read()

# Split the file into individual SQL queries
queries = [
    query.strip()
    for query in sql_content.split(";")
    if query.strip()
]

connection = sqlite3.connect(DB_PATH)

print("=" * 65)
print("BLUESTOCK - ANALYTICAL SQL QUERY RESULTS")
print("=" * 65)

for number, query in enumerate(queries, start=1):
    print(f"\nQUERY {number}")
    print("-" * 65)

    try:
        cursor = connection.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        print("Columns:", " | ".join(columns))

        for row in rows:
            print(row)

        print("Total records:", len(rows))

    except sqlite3.Error as error:
        print("SQL ERROR:", error)

connection.close()
