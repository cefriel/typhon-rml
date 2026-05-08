# KGCW2026 Typhon-RML Benchmark Results

The benchmark was run using the version v0.3 of [Typhon-RML](https://github.com/cefriel/typhon-rml/releases/tag/v0.3).

Using the [run_tests.py](./test-runner/run_tests.py) script the output produced by **typhon-rml** is compared to the expected output using [`rdflib`](https://rdflib.readthedocs.io/en/stable/):

``` python
[...]
to_isomorphic(graph_expected) == to_isomorphic(graph_produced)
[...]
```

## RML-Core Results

66 out of 76 tests for the `rml-core` challenge pass successfully.
The `route.xml` and `template.vm` files generated from the `mapping.ttl` files are available in [../kgcw-2026/rml-core/test-cases](../kgcw-2026/rml-core/test-cases).

## RML-IO Results

63 out of the 73 tests for the `rml-io` challenge pass successfully.
The `route.xml` and `template.vm` files generated from the `mapping.ttl` files are available in [../kgcw-2026/rml-io/test-cases](../kgcw-2026/rml-io/test-cases).
