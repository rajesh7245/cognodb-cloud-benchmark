import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def test_connection():
    with driver.session() as session:
        result = session.run(
            "RETURN 'CognoDB connection successful!' AS message"
        )

        record = result.single()

        print(record["message"])


try:
    test_connection()
finally:
    driver.close()