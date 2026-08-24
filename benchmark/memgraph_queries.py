import os
import time
import statistics
import concurrent.futures

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("MEMGRAPH_URL")
USERNAME = os.getenv("MEMGRAPH_USERNAME")
PASSWORD = os.getenv("MEMGRAPH_PASSWORD")


def percentile(values, percentile_value):
    values = sorted(values)

    if not values:
        return 0

    index = int(
        (percentile_value / 100) * (len(values) - 1)
    )

    return values[index]


def benchmark_query(driver, query, params=None, runs=20):
    times = []

    for _ in range(runs):
        start = time.perf_counter()

        with driver.session() as session:
            session.run(query, params or {}).consume()

        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)

    return (
        percentile(times, 50),
        percentile(times, 95)
    )


def mixed_operation(driver, operation_number):
    with driver.session() as session:

        user_id = (operation_number % 7115) + 1
        target_id = ((operation_number + 1) % 7115) + 1

        if operation_number % 2 == 0:
            session.run(
                """
                MATCH (n:User {id: $id})
                RETURN n.id
                """,
                id=user_id
            ).consume()

        else:
            session.run(
                """
                MERGE (a:User {id: $source})
                MERGE (b:User {id: $target})
                MERGE (a)-[:BENCHMARK_WRITE]->(b)
                """,
                source=user_id,
                target=target_id
            ).consume()


def run_mixed_client(driver, operations):
    start = time.perf_counter()

    for i in range(operations):
        mixed_operation(
            driver,
            i
        )

    return time.perf_counter() - start


def main():

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    try:

        with driver.session() as session:
            node_count = session.run(
                "MATCH (n:User) RETURN count(n) AS count"
            ).single()["count"]

            relationship_count = session.run(
                "MATCH ()-[r:VOTED]->() RETURN count(r) AS count"
            ).single()["count"]

        print()
        print("=== MEMGRAPH TRAVERSAL BENCHMARK ===")

        traversal_queries = [
            (
                "1-hop",
                """
                MATCH (a:User {id:1})-[:VOTED]->(b)
                RETURN b.id
                """
            ),
            (
                "2-hop",
                """
                MATCH (a:User {id:1})
                      -[:VOTED*2]->(b)
                RETURN b.id
                """
            ),
            (
                "3-hop",
                """
                MATCH (a:User {id:1})
                      -[:VOTED*3]->(b)
                RETURN b.id
                """
            )
        ]

        for name, query in traversal_queries:

            p50, p95 = benchmark_query(
                driver,
                query
            )

            print(
                f"{name}: "
                f"p50={p50:.3f} ms, "
                f"p95={p95:.3f} ms"
            )

        print()
        print("=== MEMGRAPH POINT LOOKUP ===")

        p50, p95 = benchmark_query(
            driver,
            """
            MATCH (n:User {id:1})
            RETURN n
            """
        )

        print(
            f"Point lookup: "
            f"p50={p50:.3f} ms, "
            f"p95={p95:.3f} ms"
        )

        print()
        print("=== MEMGRAPH FILTERED LOOKUP ===")

        p50, p95 = benchmark_query(
            driver,
            """
            MATCH (n:User)
            WHERE n.id >= 1 AND n.id <= 100
            RETURN n.id
            """
        )

        print(
            f"Filtered lookup: "
            f"p50={p50:.3f} ms, "
            f"p95={p95:.3f} ms"
        )

        print()
        print("=== MEMGRAPH AGGREGATION ===")

        p50, p95 = benchmark_query(
            driver,
            """
            MATCH (n:User)
            RETURN count(n)
            """
        )

        print(
            f"Aggregation: "
            f"p50={p50:.3f} ms, "
            f"p95={p95:.3f} ms"
        )

        print()
        print("=== MEMGRAPH MIXED READ/WRITE WORKLOAD (10 CLIENTS) ===")

        clients = 10
        operations_per_client = 100

        start = time.perf_counter()

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=clients
        ) as executor:

            futures = [
                executor.submit(
                    run_mixed_client,
                    driver,
                    operations_per_client
                )
                for _ in range(clients)
            ]

            for future in futures:
                future.result()

        elapsed = time.perf_counter() - start

        total_operations = clients * operations_per_client
        throughput = total_operations / elapsed

        print(f"Clients: {clients}")
        print(f"Operations: {total_operations}")
        print(f"Time: {elapsed:.2f} seconds")
        print(
            f"Throughput: "
            f"{throughput:.2f} operations/second"
        )

        print()
        print("Dataset nodes:", node_count)
        print("Dataset relationships:", relationship_count)

        print()
        print("=== MEMGRAPH BENCHMARK COMPLETE ===")

    finally:
        driver.close()


if __name__ == "__main__":
    main()