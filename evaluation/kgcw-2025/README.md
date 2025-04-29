# KGCW2025 Typhon-RML Benchmark Results

The benchmark was run using the version v0.2 of [Typhon-RML](https://github.com/cefriel/typhon-rml/releases/tag/v0.2).

The output produced by **typhon-rml** is compared to the expected output using [`rdflib`](https://rdflib.readthedocs.io/en/stable/):

``` python
[...]
to_isomorphic(graph_expected) == to_isomorphic(graph_produced)
[...]
```

## Rml-Core Results

48 out of 59 tests for the `rml-core` challenge pass successfully.
The `route.xml` and `template.vm` files generated from the `mapping.ttl` files are available in [../kgcw-2025/rml-core/](../kgcw-2025/rml-core/).
