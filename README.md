# CognoDB Cloud Benchmark

Reproducible benchmarking of CognoDB Cloud against Neo4j, Memgraph, ArangoDB, and FalkorDB using the Wiki-Vote graph dataset.

## Dataset

Dataset: Wiki-Vote

Source: SNAP Wiki-Vote graph dataset

Nodes: 7,115

Relationships: 103,689 directed relationships

The same source dataset was loaded into all five databases.

## Benchmark Workloads

The benchmark measures:

- 1-hop graph traversal
- 2-hop graph traversal
- 3-hop graph traversal
- Point lookup
- Filtered lookup
- Aggregation
- Mixed read/write workload

Latency is reported using p50 and p95 values.

The mixed read/write workload uses:

- Clients: 10
- Operations: 1000

Each read workload uses:

- 10 warm-up iterations
- 100 measured iterations

---

## Methodology

The benchmark uses the same dataset and the same logical workload categories across all five database platforms.

### Dataset

The Wiki-Vote dataset contains:

- 7,115 unique nodes
- 103,689 directed relationships

### Query Execution

For read workloads:

- 10 warm-up iterations were performed.
- 100 measured iterations were performed.
- Start nodes were selected randomly from the dataset.
- Latency was measured using Python's `time.perf_counter()`.
- p50 and p95 latency were calculated from the measured runs.

### Traversal Workloads

Three traversal depths were measured:

- 1-hop
- 2-hop
- 3-hop

### Lookup Workloads

Two lookup workloads were measured:

- Point lookup using the `User.id` property.
- Filtered lookup using a `WHERE` predicate on `User.id`.

The benchmark scripts use the `User.id` property for lookup operations. Index configuration was not recorded consistently across every platform and is therefore treated as a methodology limitation.

### Aggregation

An aggregation query counted relationships grouped by relationship type.

### Mixed Read/Write Workload

The mixed workload used:

- 10 concurrent clients
- 1,000 total operations
- Read operations
- Temporary write/delete operations

Throughput is reported as operations per second.

### Client and Region

The benchmarks were executed from the same client machine during the recorded test sessions.

The cloud regions were not identical across all platforms because the available free/free-trial instances were provisioned in different regions.

---

## Environment and Resource Specifications

The benchmark was executed using the available free or free-trial managed database tiers.

The following information was observable from the respective cloud consoles.

| Database | Tier / Plan | vCPU | RAM | Storage | Region | Cloud |
|---|---|---:|---:|---:|---|---|
| CognoDB | Free · c0 | 0.5 | 256 MB | 1 GB | us-east4 | Not specified |
| Neo4j | AuraDB Free | Not observable | Not observable | Not observable | Not observable | Not observable |
| Memgraph | Free Trial | 2 CPU | 2 GB | Not observable | Europe (Frankfurt) | Not specified |
| ArangoDB | Not observable | Not observable | Not observable | Not observable | Iowa, USA | Google Cloud Platform |
| FalkorDB | Free | Not observable | Not observable | Not observable | ap-south-1 | AWS |

### Resource Fairness Caveat

The available free/free-trial configurations were not hardware-equivalent across all platforms.

For example, the observable CognoDB configuration provided 0.5 vCPU and 256 MB RAM, while the Memgraph project exposed 2 CPU and 2 GB RAM.

Some platforms did not expose complete vCPU, RAM, or storage information in their cloud consoles.

Therefore, the results should not be interpreted as a strict hardware-equivalent comparison.

The benchmark reports the configurations that were actually used and does not invent resource values that were not observable.

---

# Benchmark Results

## Neo4j

| Workload | p50 | p95 |
|---|---:|---:|
| 1-hop traversal | 102.469 ms | 122.273 ms |
| 2-hop traversal | 102.464 ms | 138.746 ms |
| 3-hop traversal | 102.405 ms | 144.347 ms |
| Point lookup | 102.357 ms | 104.512 ms |
| Filtered lookup | 102.576 ms | 205.677 ms |
| Aggregation | 102.619 ms | 205.006 ms |

### Mixed Read/Write Workload

- Clients: 10
- Operations: 1000
- Time: 8.16 seconds
- Throughput: 122.51 operations/second

### Loading

- Load time: 273.92 seconds
- Relationships/second: 378.53
- Nodes/second: Not measured

---

## Memgraph

| Workload | p50 | p95 |
|---|---:|---:|
| 1-hop traversal | 148.636 ms | 198.708 ms |
| 2-hop traversal | 147.271 ms | 161.373 ms |
| 3-hop traversal | 147.275 ms | 155.367 ms |
| Point lookup | 146.769 ms | 151.711 ms |
| Filtered lookup | 149.490 ms | 153.638 ms |
| Aggregation | 146.076 ms | 147.369 ms |

### Mixed Read/Write Workload

- Clients: 10
- Operations: 1000
- Time: 15.70 seconds
- Throughput: 63.68 operations/second

### Loading

- Load time: Not measured
- Relationships/second: Not measured
- Nodes/second: Not measured

---

## CognoDB

| Workload | p50 | p95 |
|---|---:|---:|
| 1-hop traversal | 307.896 ms | 409.606 ms |
| 2-hop traversal | 307.464 ms | 491.078 ms |
| 3-hop traversal | 308.227 ms | 620.458 ms |
| Point lookup | 307.650 ms | 410.608 ms |
| Filtered lookup | 307.442 ms | 411.327 ms |
| Aggregation | 376.017 ms | 452.646 ms |

### Mixed Read/Write Workload

- Clients: 10
- Operations: 1000
- Time: 35.89 seconds
- Throughput: 27.86 operations/second

### Loading

- Load time: Not measured in the recorded benchmark results
- Relationships/second: Not measured
- Nodes/second: Not measured

---

## ArangoDB

| Workload | p50 | p95 |
|---|---:|---:|
| 1-hop traversal | 306.736 ms | 310.177 ms |
| 2-hop traversal | 308.217 ms | 510.578 ms |
| 3-hop traversal | 7685.703 ms | 8297.400 ms |
| Point lookup | 307.112 ms | 393.173 ms |
| Filtered lookup | 305.879 ms | 448.861 ms |
| Aggregation | 423.526 ms | 714.337 ms |

### Mixed Read/Write Workload

- Clients: 10
- Operations: 1000
- Time: 99.97 seconds
- Throughput: 10.00 operations/second

### Loading

- Load time: Not measured
- Relationships/second: Not measured
- Nodes/second: Not measured

---

## FalkorDB

| Workload | p50 | p95 |
|---|---:|---:|
| 1-hop traversal | 17.012 ms | 50.925 ms |
| 2-hop traversal | 17.388 ms | 19.185 ms |
| 3-hop traversal | 17.049 ms | 17.664 ms |
| Point lookup | 16.828 ms | 85.482 ms |
| Filtered lookup | 17.148 ms | 86.224 ms |
| Aggregation | 102.817 ms | 204.899 ms |

### Mixed Read/Write Workload

- Clients: 10
- Operations: 1000
- Time: 4.08 seconds
- Throughput: 245.33 operations/second

### Loading

- Load time: 350.40 seconds
- Relationships/second: 295.91
- Nodes/second: Not measured

---

# Overall Comparison

| Database | 1-hop p50 | 2-hop p50 | 3-hop p50 | Point lookup p50 | Filtered lookup p50 | Aggregation p50 | Mixed workload |
|---|---:|---:|---:|---:|---:|---:|---:|
| Neo4j | 102.469 ms | 102.464 ms | 102.405 ms | 102.357 ms | 102.576 ms | 102.619 ms | 122.51 ops/s |
| Memgraph | 148.636 ms | 147.271 ms | 147.275 ms | 146.769 ms | 149.490 ms | 146.076 ms | 63.68 ops/s |
| CognoDB | 307.896 ms | 307.464 ms | 308.227 ms | 307.650 ms | 307.442 ms | 376.017 ms | 27.86 ops/s |
| ArangoDB | 306.736 ms | 308.217 ms | 7685.703 ms | 307.112 ms | 305.879 ms | 423.526 ms | 10.00 ops/s |
| FalkorDB | 17.012 ms | 17.388 ms | 17.049 ms | 16.828 ms | 17.148 ms | 102.817 ms | 245.33 ops/s |

---

# Load Performance

| Database | Load time | Relationships/second | Nodes/second |
|---|---:|---:|---:|
| Neo4j | 273.92 s | 378.53 | Not measured |
| Memgraph | Not measured | Not measured | Not measured |
| CognoDB | Not measured | Not measured | Not measured |
| ArangoDB | Not measured | Not measured | Not measured |
| FalkorDB | 350.40 s | 295.91 | Not measured |

Only measurements that were actually recorded are reported.

Missing measurements are explicitly marked as **Not measured**.

---

# Footprint and Observable Resource Usage

| Database | Stored data size | Memory usage | Instance resources |
|---|---|---|---|
| CognoDB | Not observable | Not observable | 0.5 vCPU, 256 MB RAM, 1 GB storage |
| Neo4j | Not observable | Not observable | Not observable |
| Memgraph | Not observable | Not observable | 2 CPU, 2 GB RAM |
| ArangoDB | Not observable | Not observable | Not observable |
| FalkorDB | Not observable | Not observable | Not observable |

The managed platforms did not expose directly comparable stored-data-size or live-memory measurements in the information recorded during the benchmark.

These values are therefore reported as **Not observable** rather than estimated.

---

# Observations

Based on the measured benchmark results:

- FalkorDB produced the lowest measured p50 latency across the tested traversal workloads.
- FalkorDB produced the lowest measured p50 latency for point lookup.
- FalkorDB achieved the highest mixed read/write throughput at 245.33 operations/second in this benchmark.
- Neo4j produced lower latency than Memgraph, CognoDB, and ArangoDB in the measured workloads.
- Memgraph was the second fastest database in the measured traversal and lookup workloads after FalkorDB.
- CognoDB showed similar latency to ArangoDB for 1-hop, 2-hop, and lookup workloads.
- ArangoDB showed a significantly higher 3-hop traversal latency in this benchmark.
- Neo4j achieved 122.51 operations/second in the mixed read/write workload.
- Memgraph achieved 63.68 operations/second.
- CognoDB achieved 27.86 operations/second.
- ArangoDB achieved 10.00 operations/second.
- FalkorDB achieved 245.33 operations/second.

These observations are specific to this benchmark configuration, dataset, workload implementation, resource configuration, network conditions, and test environment.

The results should not be interpreted as a universal ranking of the database platforms because the available free/free-trial resource configurations were not equivalent.

---

# Caveats

The following limitations should be considered when interpreting the results:

- The available free/free-trial tiers were not hardware-equivalent across all platforms.
- Some platforms did not expose complete vCPU, RAM, or storage specifications.
- Cloud network latency can affect database query latency.
- Free-tier throttling or resource limits may affect performance.
- Driver and query-language differences can affect results.
- The benchmark uses equivalent logical workloads, but query syntax is platform-specific.
- Load metrics were not recorded for every platform.
- Nodes/second was not measured in the recorded loading runs.
- ArangoDB load time was not measured.
- Results represent the recorded benchmark runs and were not averaged across multiple independent benchmark sessions.
- The benchmark is intended as an empirical comparison of the recorded configurations rather than a universal ranking of the database products.

---

# Reproducibility

## Requirements

- Python 3.x
- A free/free-trial account for each database platform
- Network access to the managed database instances

## Install Dependencies

Create a virtual environment:

```bash
python -m venv myenv

Windows

Activate the virtual environment:

myenv\Scripts\activate

Install the benchmark dependencies used by the project:

pip install neo4j python-dotenv arango falkordb
Configure Environment Variables

Create a local .env file in the project root.

Do not commit .env to GitHub.

Configure only the credentials required by the database you are running.

The .env file is intentionally excluded through .gitignore.

Dataset

Place the Wiki-Vote dataset at:

data/Wiki-Vote.txt

The benchmark scripts read the dataset from this location.

Running the Benchmarks
FalkorDB

Test the connection:

python scripts/test_connection.py

Verify the loaded dataset:

python scripts/test_falkordb_data.py

Load the dataset:

python benchmark/load_falkordb.py

Run the benchmark:

python benchmark/falkordb_queries.py
CognoDB

Load the dataset:

python benchmark/load_cognodb.py

Run the benchmark:

python benchmark/cognodb_queries.py
Memgraph

Load the dataset:

python benchmark/load_memgraph.py

Run the benchmark:

python benchmark/memgraph_queries.py
ArangoDB

Load the dataset:

python benchmark/load_arango.py

Run the benchmark:

python benchmark/arango_queries.py
Neo4j

Load the dataset:

python benchmark/load_data.py

Run the benchmark:

python benchmark/neo4j_queries.py
Results Files

Individual benchmark result files are stored in the results/ directory:

results/
|
|-- neo4j_results.txt
|-- cognodb_results.txt
|-- memgraph_results.txt
|-- arango_results.txt
|-- falkordb_results.txt
Repository Structure
cognodb-benchmark/
|
|-- benchmark/
|   |-- load_data.py
|   |-- load_cognodb.py
|   |-- load_memgraph.py
|   |-- load_arango.py
|   |-- load_falkordb.py
|   |-- neo4j_queries.py
|   |-- cognodb_queries.py
|   |-- memgraph_queries.py
|   |-- arango_queries.py
|   |-- falkordb_queries.py
|
|-- data/
|   |-- Wiki-Vote.txt
|
|-- scripts/
|   |-- test_neo4j.py
|   |-- test_cognodb.py
|   |-- test_memgraph.py
|   |-- test_arango.py
|   |-- test_connection.py
|   |-- test_falkordb_data.py
|
|-- results/
|   |-- neo4j_results.txt
|   |-- cognodb_results.txt
|   |-- memgraph_results.txt
|   |-- arango_results.txt
|   |-- falkordb_results.txt
|
|-- .env
|-- .gitignore
|-- README.md

.env is a local configuration file and must not be committed to the repository.

Conclusion

This benchmark provides a comparative evaluation of CognoDB Cloud, Neo4j, Memgraph, ArangoDB, and FalkorDB using the Wiki-Vote graph dataset.

In the recorded benchmark:

FalkorDB achieved the lowest measured p50 latency for the tested traversal workloads.
FalkorDB achieved the lowest measured p50 latency for point lookup.
FalkorDB achieved the highest mixed read/write throughput.
Neo4j also demonstrated strong performance across the measured workloads.
Memgraph showed moderate latency and mixed-workload throughput.
CognoDB and ArangoDB showed higher latency in several measured workloads.
ArangoDB showed particularly high latency for the 3-hop traversal.

These results are specific to the recorded benchmark configuration, dataset, workload implementation, resource configuration, network conditions, and test environment.

Because the available free/free-trial resource configurations were not fully equivalent, the results should be treated as an empirical benchmark rather than a universal ranking of the database platforms.