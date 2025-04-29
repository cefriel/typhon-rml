# KGCW2024 Typhon-RML Benchmark Results

The benchmark was run using the following Docker image for **Typhon-RML**:

```bash
docker pull cefriel/typhon-rml:v0.2
```

The challenge was executed using the official execution tool provided by the [KG-construct challenge](https://github.com/kg-construct/exectool):

## Rml-Core Results

222 out of 238 tests for the `rml-core` challenge pass successfully.
16 tests fail due to intended differences in how typhon-rml handles missing files and/or missing data attributes.
The `route.xml` and `template.vm` files generated from the `mapping.ttl` files are available in [../kgcw-2024/rml-core/](../kgcw-2024/rml-core/).

### Failing Tests

| No. | Test Case             | Reason                                                                                       |
|-----|-----------------------|----------------------------------------------------------------------------------------------|
| 1   | RMLTC0002e-CSV        | Tries to read a file that does not exist. Typhon-RML expects it to exist.                    |
| 2   | RMLTC0002e-JSON       | Same as above.                                                                               |
| 3   | RMLTC0002e-XML        | Same as above.                                                                               |
| 4   | RMLTC0002g-JSON       | Same as above.                                                                               |
| 5   | RMLTC0007h-JSON       | No error thrown when a selected column or attribute is missing.                              |
| 6   | RMLTC0007h-XML        | Same as above.                                                                               |
| 7   | RMLTC0012c-XML        | Fails due to a missing input file.                                                           |
| 8   | RMLTC0012d-CSV        | Should fail but doesn't. Possibly related to blank nodes; output contains duplicate triples. |
| 9   | RMLTC0012d-JSON       | Same as above.                                                                               |
| 10  | RMLTC0012d-MySQL      | Same as above.                                                                               |
| 11  | RMLTC0012d-PostgreSQL | Same as above.                                                                               |
| 12  | RMLTC0012d-XML        | Same as above.                                                                               |
| 13  | RMLTC0015b-CSV        | Typhon does not check for invalid language codes                                             |
| 14  | RMLTC0015b-JSON       | Same as above.                                                                               |
| 15  | RMLTC0015b-MySQL      | Same as above.                                                                               |
| 16  | RMLTC0015b-XML        | Same as above.                                                                               |

