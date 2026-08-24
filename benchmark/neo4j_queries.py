import os
import random
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")

DATASET_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "Wiki-Vote.txt"
)

ITERATIONS = 100
WARMUP_ITERATIONS = 10


driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def load_node_ids():
    """
    Read node IDs from Wiki-Vote.txt.
    """
    node_ids = set()

    with open(DATASET_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()

            if len(parts) >= 2:
                node_ids.add(int(parts[0]))
                node_ids.add(int(parts[1]))

    return list(node_ids)


def percentile(values, p):
    """
    Calculate percentile without requiring NumPy.
    """
    values = sorted(values)

    if not values:
        return 0.0

    index = (len(values) - 1) * (p / 100)

    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    weight = index - lower

    return values[lower] * (1 - weight) + values[upper] * weight


def latency_stats(latencies):
    """
    Return p50 and p95 latency in milliseconds.
    """
    latencies_ms = [x * 1000 for x in latencies]

    return {
        "p50_ms": percentile(latencies_ms, 50),
        "p95_ms": percentile(latencies_ms, 95),
        "min_ms": min(latencies_ms),
        "max_ms": max(latencies_ms),
        "mean_ms": statistics.mean(latencies_ms)
    }


def run_query(session, query, parameters=None):
    """
    Execute one query and consume the complete result.
    """
    result = session.run(
        query,
        parameters or {}
    )

    result.consume()


def benchmark_query(query, node_ids):
    """
    Warm up and then execute a query 100 times.
    """
    with driver.session(database=DATABASE) as session:

        # Warm-up
        for _ in range(WARMUP_ITERATIONS):
            node_id = random.choice(node_ids)

            run_query(
                session,
                query,
                {"id": node_id}
            )

        # Measured runs
        latencies = []

        for _ in range(ITERATIONS):

            node_id = random.choice(node_ids)

            start = time.perf_counter()

            run_query(
                session,
                query,
                {"id": node_id}
            )

            end = time.perf_counter()

            latencies.append(end - start)

    return latency_stats(latencies)


def create_index():
    """
    Create an index on User.id for indexed lookup.
    """
    query = """
    CREATE INDEX user_id_index IF NOT EXISTS
    FOR (u:User)
    ON (u.id)
    """

    with driver.session(database=DATABASE) as session:
        session.run(query).consume()


def count_nodes():
    """
    Count User nodes.
    """
    query = """
    MATCH (u:User)
    RETURN count(u) AS count
    """

    with driver.session(database=DATABASE) as session:
        record = session.run(query).single()

        return record["count"]


def count_relationships():
    """
    Count VOTED relationships.
    """
    query = """
    MATCH ()-[r:VOTED]->()
    RETURN count(r) AS count
    """

    with driver.session(database=DATABASE) as session:
        record = session.run(query).single()

        return record["count"]


def benchmark_traversals(node_ids):

    queries = {

        "1-hop": """
        MATCH (u:User {id: $id})-[:VOTED]->(v)
        RETURN count(v) AS count
        """,

        "2-hop": """
        MATCH (u:User {id: $id})
              -[:VOTED]->()
              -[:VOTED]->(v)
        RETURN count(v) AS count
        """,

        "3-hop": """
        MATCH (u:User {id: $id})
              -[:VOTED]->()
              -[:VOTED]->()
              -[:VOTED]->(v)
        RETURN count(v) AS count
        """
    }

    print("\n=== TRAVERSAL BENCHMARK ===")

    results = {}

    for name, query in queries.items():

        stats = benchmark_query(
            query,
            node_ids
        )

        results[name] = stats

        print(
            f"{name}: "
            f"p50={stats['p50_ms']:.3f} ms, "
            f"p95={stats['p95_ms']:.3f} ms"
        )

    return results


def benchmark_point_lookup(node_ids):

    query = """
    MATCH (u:User {id: $id})
    RETURN u.id AS id
    """

    print("\n=== POINT LOOKUP ===")

    stats = benchmark_query(
        query,
        node_ids
    )

    print(
        f"Point lookup: "
        f"p50={stats['p50_ms']:.3f} ms, "
        f"p95={stats['p95_ms']:.3f} ms"
    )

    return stats


def benchmark_filtered_lookup(node_ids):

    query = """
    MATCH (u:User)
    WHERE u.id = $id
    RETURN u.id AS id
    """

    print("\n=== FILTERED LOOKUP ===")

    stats = benchmark_query(
        query,
        node_ids
    )

    print(
        f"Filtered lookup: "
        f"p50={stats['p50_ms']:.3f} ms, "
        f"p95={stats['p95_ms']:.3f} ms"
    )

    return stats


def benchmark_aggregation():

    query = """
    MATCH ()-[r:VOTED]->()
    RETURN type(r) AS relationship_type,
           count(*) AS relationship_count
    """

    with driver.session(database=DATABASE) as session:

        # Warm-up
        for _ in range(WARMUP_ITERATIONS):
            run_query(session, query)

        latencies = []

        for _ in range(ITERATIONS):

            start = time.perf_counter()

            run_query(session, query)

            end = time.perf_counter()

            latencies.append(end - start)

    stats = latency_stats(latencies)

    print("\n=== AGGREGATION ===")

    print(
        f"Aggregation: "
        f"p50={stats['p50_ms']:.3f} ms, "
        f"p95={stats['p95_ms']:.3f} ms"
    )

    return stats


def mixed_worker(worker_id, operations=50):

    local_driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    completed = 0

    try:

        with local_driver.session(database=DATABASE) as session:

            for i in range(operations):

                # READ
                node_id = random.randint(1, 8283)

                read_query = """
                MATCH (u:User {id: $id})
                OPTIONAL MATCH (u)-[:VOTED]->(v)
                RETURN count(v) AS count
                """

                result = session.run(
                    read_query,
                    {"id": node_id}
                )

                result.consume()

                # WRITE
                temporary_id = (
                    f"__benchmark_{worker_id}_{i}"
                )

                write_query = """
                CREATE (u:User {id: $id})
                WITH u
                DETACH DELETE u
                """

                session.run(
                    write_query,
                    {"id": temporary_id}
                ).consume()

                completed += 2

    finally:
        local_driver.close()

    return completed


def benchmark_mixed_workload(concurrency=10):

    print(
        f"\n=== MIXED READ/WRITE WORKLOAD "
        f"({concurrency} CLIENTS) ==="
    )

    start = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=concurrency
    ) as executor:

        futures = [
            executor.submit(
                mixed_worker,
                worker_id
            )
            for worker_id in range(concurrency)
        ]

        total_operations = sum(
            future.result()
            for future in futures
        )

    end = time.perf_counter()

    elapsed = end - start

    throughput = total_operations / elapsed

    print(
        f"Clients: {concurrency}"
    )

    print(
        f"Operations: {total_operations}"
    )

    print(
        f"Time: {elapsed:.2f} seconds"
    )

    print(
        f"Throughput: {throughput:.2f} operations/second"
    )

    return {
        "clients": concurrency,
        "operations": total_operations,
        "seconds": elapsed,
        "throughput": throughput
    }


def main():

    print("Starting Neo4j benchmark...")

    node_ids = load_node_ids()

    print(
        f"Dataset nodes discovered: "
        f"{len(node_ids)}"
    )

    print(
        f"Database nodes: "
        f"{count_nodes()}"
    )

    print(
        f"Database relationships: "
        f"{count_relationships()}"
    )

    # Create index required for indexed lookup
    create_index()

    print("\nUser.id index created/verified.")

    # Required workloads
    benchmark_traversals(node_ids)

    benchmark_point_lookup(node_ids)

    benchmark_filtered_lookup(node_ids)

    benchmark_aggregation()

    # Mixed workload with 10 concurrent clients
    benchmark_mixed_workload(
        concurrency=10
    )

    print("\n=== BENCHMARK COMPLETE ===")


if __name__ == "__main__":

    try:
        main()

    finally:
        driver.close()