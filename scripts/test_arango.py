import os
from dotenv import load_dotenv
from arango import ArangoClient

load_dotenv()

url = os.getenv("ARANGO_URL")
username = os.getenv("ARANGO_USERNAME")
password = os.getenv("ARANGO_PASSWORD")
database = os.getenv("ARANGO_DATABASE", "_system")

print("=== ARANGODB CONNECTION TEST ===")
print(f"URL: {url}")
print(f"Username: {username}")

if not url or not username or not password:
    print("ARANGO_URL, ARANGO_USERNAME or ARANGO_PASSWORD is missing")
    raise SystemExit(1)

client = ArangoClient(hosts=url)

try:
    db = client.db(
        database,
        username=username,
        password=password
    )

    version = db.version()

    print("Connection: SUCCESS")
    print("ArangoDB version:", version)
    print("ArangoDB connection is working.")

except Exception as e:
    print("Connection: FAILED")
    print("Error:", e)