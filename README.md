# CognoDB Cloud Benchmark

Reproducible benchmarking of CognoDB Cloud against Neo4j using the Wiki-Vote graph dataset.

## Dataset

Dataset: Wiki-Vote
Nodes: 7,115
Relationships: 103,689

## Benchmark Results

### Neo4j

| Workload | p50 | p95 |
|---|---:|---:|
| 1-hop traversal | 102.469 ms | 122.273 ms |
| 2-hop traversal | 102.464 ms | 138.746 ms |
| 3-hop traversal | 102.405 ms | 144.347 ms |
| Point lookup | 102.357 ms | 104.512 ms |
| Filtered lookup | 102.576 ms | 205.677 ms |
| Aggregation | 102.619 ms | 205.006 ms |

Mixed read/write workload: 10 clients, 1000 operations, 8.16 seconds, 122.51 operations/second.

Neo4j load time: 273.92 seconds.
Neo4j relationships/second during loading: 378.53.

### CognoDB

| Workload | p50 | p95 |
|---|---:|---:|
| 1-hop traversal | 307.896 ms | 409.606 ms |
| 2-hop traversal | 307.464 ms | 491.078 ms |
| 3-hop traversal | 308.227 ms | 620.458 ms |
| Point lookup | 307.650 ms | 410.608 ms |
| Filtered lookup | 307.442 ms | 411.327 ms |
| Aggregation | 376.017 ms | 452.646 ms |

Mixed read/write workload: 10 clients, 1000 operations, 35.89 seconds, 27.86 operations/second.

## Repository Structure

benchmark/
- load_data.py
- load_cognodb.py
- neo4j_queries.py
- cognodb_queries.py

data/
- Wiki-Vote.txt

results/
- neo4j_results.txt
- cognodb_results.txt

scripts/
- test_neo4j.py
- test_cognodb.py

## Running the Benchmarks

Activate the Python virtual environment and install the required dependencies.

Load the Wiki-Vote dataset into Neo4j:
python benchmark\load_data.py

Run the Neo4j benchmark:
python benchmark\neo4j_queries.py

Load the Wiki-Vote dataset into CognoDB:
python benchmark\load_cognodb.py

Run the CognoDB benchmark:
python benchmark\cognodb_queries.py

## Notes

Benchmark credentials are stored in .env and should not be committed.
The benchmark uses the same Wiki-Vote dataset and workload structure for comparison.
