import os
import random
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from falkordb import FalkorDB


load_dotenv()

HOST = os.getenv("FALKORDB_HOST")
PORT = int(os.getenv("FALKORDB_PORT"))
USERNAME = os.getenv("FALKORDB_USERNAME")
PASSWORD = os.getenv("FALKORDB_PASSWORD")

GRAPH_NAME = "wiki_vote"

ITERATIONS = 100
WARMUP_ITERATIONS = 10


db = FalkorDB(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD
)

graph = db.select_graph(GRAPH_NAME)


def load_node_ids():

    result = graph.query("""
        MATCH (u:User)
        RETURN u.id AS id
    """)

    return [
        record[0]
        for record in result.result_set
    ]


def percentile(values, p):

    values = sorted(values)

    if not values:
        return 0.0

    index = (len(values) - 1) * (p / 100)

    lower = int(index)

    upper = min(
        lower + 1,
        len(values) - 1
    )

    weight = index - lower

    return (
        values[lower] * (1 - weight)
        + values[upper] * weight
    )


def latency_stats(latencies):

    latencies_ms = [
        x * 1000
        for x in latencies
    ]

    return {
        "p50_ms": percentile(
            latencies_ms,
            50
        ),

        "p95_ms": percentile(
            latencies_ms,
            95
        ),

        "min_ms": min(latencies_ms),

        "max_ms": max(latencies_ms),

        "mean_ms": statistics.mean(
            latencies_ms
        )
    }


def run_query(query, parameters=None):

    result = graph.query(
        query,
        parameters or {}
    )

    return result


def benchmark_query(query, node_ids):

    for _ in range(WARMUP_ITERATIONS):

        node_id = random.choice(node_ids)

        run_query(
            query,
            {"id": node_id}
        )

    latencies = []

    for _ in range(ITERATIONS):

        node_id = random.choice(node_ids)

        start = time.perf_counter()

        run_query(
            query,
            {"id": node_id}
        )

        end = time.perf_counter()

        latencies.append(
            end - start
        )

    return latency_stats(latencies)


def count_nodes():

    result = graph.query("""
        MATCH (u:User)
        RETURN count(u) AS count
    """)

    return result.result_set[0][0]


def count_relationships():

    result = graph.query("""
        MATCH ()-[r:VOTED]->()
        RETURN count(r) AS count
    """)

    return result.result_set[0][0]


def benchmark_traversals(node_ids):

    queries = {

        "1-hop": """
            MATCH (u:User {id: $id})
                  -[:VOTED]->(v)
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

    print("\n=== FALKORDB TRAVERSAL BENCHMARK ===")

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

    print("\n=== FALKORDB POINT LOOKUP ===")

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

    print("\n=== FALKORDB FILTERED LOOKUP ===")

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

    for _ in range(WARMUP_ITERATIONS):

        run_query(query)

    latencies = []

    for _ in range(ITERATIONS):

        start = time.perf_counter()

        run_query(query)

        end = time.perf_counter()

        latencies.append(
            end - start
        )

    stats = latency_stats(latencies)

    print("\n=== FALKORDB AGGREGATION ===")

    print(
        f"Aggregation: "
        f"p50={stats['p50_ms']:.3f} ms, "
        f"p95={stats['p95_ms']:.3f} ms"
    )

    return stats


def mixed_worker(worker_id, operations=50):

    local_db = FalkorDB(
        host=HOST,
        port=PORT,
        username=USERNAME,
        password=PASSWORD
    )

    local_graph = local_db.select_graph(
        GRAPH_NAME
    )

    completed = 0

    try:

        for i in range(operations):

            node_id = random.randint(
                1,
                8283
            )

            read_query = """
                MATCH (u:User {id: $id})
                OPTIONAL MATCH
                    (u)-[:VOTED]->(v)
                RETURN count(v) AS count
            """

            local_graph.query(
                read_query,
                {"id": node_id}
            )

            temporary_id = (
                f"__benchmark_"
                f"{worker_id}_{i}"
            )

            write_query = """
                CREATE (u:User {id: $id})
                WITH u
                DETACH DELETE u
            """

            local_graph.query(
                write_query,
                {"id": temporary_id}
            )

            completed += 2

    finally:

        local_db.close()

    return completed


def benchmark_mixed_workload(
    concurrency=10
):

    print(
        "\n=== FALKORDB MIXED "
        "READ/WRITE WORKLOAD "
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

            for worker_id
            in range(concurrency)
        ]

        total_operations = sum(
            future.result()
            for future in futures
        )

    end = time.perf_counter()

    elapsed = end - start

    throughput = (
        total_operations
        / elapsed
    )

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
        f"Throughput: "
        f"{throughput:.2f} "
        "operations/second"
    )

    return {
        "clients": concurrency,
        "operations": total_operations,
        "seconds": elapsed,
        "throughput": throughput
    }


def main():

    print(
        "Starting FalkorDB benchmark..."
    )

    node_ids = load_node_ids()

    print(
        f"Database nodes: "
        f"{len(node_ids)}"
    )

    print(
        f"Database relationships: "
        f"{count_relationships()}"
    )

    benchmark_traversals(
        node_ids
    )

    benchmark_point_lookup(
        node_ids
    )

    benchmark_filtered_lookup(
        node_ids
    )

    benchmark_aggregation()

    benchmark_mixed_workload(
        concurrency=10
    )

    print(
        "\n=== FALKORDB BENCHMARK COMPLETE ==="
    )


if __name__ == "__main__":

    try:

        main()

    finally:

        db.close()