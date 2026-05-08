# Test Runner for Typhon-RML

This script runs RML conformance test cases using Typhon-RML and Apache Camel.

## Prerequisites

- Java 11 or higher
- JBang 
- Camel JBang
- Python 3.10+
- Required Python packages: `rdflib`

## Setup

1. Place `typhon-rml.jar` in the same directory as `run_tests.py`
2. Ensure `ShutDownProcessor.java` is in the same directory
3. Clone the RML test cases repository or point to your test cases directory

## Usage

### Run tests from a directory
```bash
python run_tests.py --path /path/to/test-cases
```

### Run a single test
```bash
python run_tests.py --path /path/to/test-cases/RMLTC0000-CSV
```

### Clean test artifacts
```bash
python run_tests.py --path /path/to/test-cases --clean
```

## Output

- Results are printed to console
- CSV report is generated: `YYYYMMDD_HHMMSS_<test-suite>_results.csv`
- Passed tests are marked with `.done` file to skip on re-runs
