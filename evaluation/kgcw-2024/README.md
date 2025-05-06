# KGCW2024 Typhon-RML Benchmark Results

The benchmark was run using the following Docker image for **Typhon-RML**:

```bash
docker pull cefriel/typhon-rml:v0.3
```

The challenge was executed using the official execution tool provided by the [KG-construct challenge](https://github.com/kg-construct/exectool):

## Rml-Core Results

234 out of 238 tests for the `rml-core` challenge pass successfully.
4 tests fail due to intended differences in how typhon-rml handles missing files and/or missing data attributes.
The `route.xml` and `template.vm` files generated from the `mapping.ttl` files are available in [../kgcw-2024/rml-core/](../kgcw-2024/rml-core/).

### Failing Tests

| No. | Test Case             | Reason                                                                                       |
|-----|-----------------------|----------------------------------------------------------------------------------------------|
| 1   | RMLTC0002e-CSV        | Tries to read a file that does not exist. Typhon-RML expects it to exist.                    |
| 2   | RMLTC0002e-JSON       | Same as above.                                                                               |
| 3   | RMLTC0002e-XML        | Same as above.                                                                               |
| 4   | RMLTC0002g-JSON       | Same as above.                                                                               |
