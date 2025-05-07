# KGCW2025 Typhon-RML Benchmark Results

The benchmark was run using the version v0.2 of [Typhon-RML](https://github.com/cefriel/typhon-rml/releases/tag/v0.2).

The output produced by **typhon-rml** is compared to the expected output using [`rdflib`](https://rdflib.readthedocs.io/en/stable/):

``` python
[...]
to_isomorphic(graph_expected) == to_isomorphic(graph_produced)
[...]
```

## RML-Core Results

54 out of 59 tests for the `rml-core` challenge pass successfully.
The `route.xml` and `template.vm` files generated from the `mapping.ttl` files are available in [../kgcw-2025/rml-core/](../kgcw-2025/rml-core/).

## RML-IO Results

16 out of the 73 tests for the `rml-io` challenge pass successfully.
The `route.xml` and `template.vm` files generated from the `mapping.ttl` files are available in [../kgcw-2025/rml-io/](../kgcw-2025/rml-io/).

## RML-LV Results

9 out of the 32 tests for the `rml-lv` challenge pass successfully. Experimental RML to MTL test case conversion using the [feat-lv](https://github.com/cefriel/mapping-template/tree/feat-lv) branch of the mapping-template, still not integrated in Typhon-RML. The `mapping.rml.vm` file generated from the `mapping.ttl` is available in [../kgcw-2025/rml-lv/](../kgcw-2025/rml-lv/).
