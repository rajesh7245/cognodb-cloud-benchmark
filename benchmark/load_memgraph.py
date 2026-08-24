import os
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("MEMGRAPH_URL")
USERNAME = os.getenv("MEMGRAPH_USERNAME")
PASSWORD = os.getenv("MEMGRAPH_PASSWORD")

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "Wiki-Vote.txt"
)


def load_data():
    edges = []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()

            if len(parts) >= 2:
                source = int(parts[0])
                target = int(parts[1])
                edges.append((source, target))

    print(f"Dataset relationships discovered: {len(edges)}")

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    start_time = time.perf_counter()

    try:
        with driver.session() as session:

            print("Clearing existing Memgraph data...")

            session.run(
                "MATCH (n) DETACH DELETE n"
            ).consume()

            print("Loading Wiki-Vote dataset...")

            batch_size = 500

            for i in range(0, len(edges), batch_size):
                batch = edges[i:i + batch_size]

                rows = [
                    {
                        "source": source,
                        "target": target
                    }
                    for source, target in batch
                ]

                session.run(
                    """
                    UNWIND $rows AS row
                    MERGE (a:User {id: row.source})
                    MERGE (b:User {id: row.target})
                    MERGE (a)-[:VOTED]->(b)
                    """,
                    rows=rows
                ).consume()

                if (i + batch_size) % 10000 == 0:
                    print(
                        f"Loaded approximately "
                        f"{min(i + batch_size, len(edges))} relationships..."
                    )

            end_time = time.perf_counter()
            elapsed = end_time - start_time

            result = session.run(
                """
                MATCH (n:User)
                RETURN count(n) AS nodes
                """
            ).single()

            nodes = result["nodes"]

            result = session.run(
                """
                MATCH ()-[r:VOTED]->()
                RETURN count(r) AS relationships
                """
            ).single()

            relationships = result["relationships"]

            print()
            print("=== MEMGRAPH LOAD COMPLETE ===")
            print(f"Nodes: {nodes}")
            print(f"Relationships: {relationships}")
            print(f"Load time: {elapsed:.2f} seconds")

            if elapsed > 0:
                print(
                    f"Relationships/second: "
                    f"{relationships / elapsed:.2f}"
                )

    finally:
        driver.close()


if __name__ == "__main__":
    load_data()