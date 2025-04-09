# Typhon-RML

**Typhon-RML** is a modular Java-based tool for constructing data pipelines for Knowledge Graphs (KGs) from heterogeneous data sources starting from RML mappings but with the possibility of introducing customizations. It leverages the [Chimera](https://github.com/cefriel/chimera) framework to separate concerns in the KG construction process, making it easier to customize and optimize both data access and mapping execution.

---

## Key Concepts

The **Typhon-RML** approach decomposes RML-based knowledge graph construction into **compile-time** and **runtime** phases:

- **Compile-time**: 
  - The input RML mapping is transformed into:
    - A Chimera data pipeline (`route.xml`) built using Apache Camel DSL.
    - A set of template-based mapping rules (`template.vm`) defined using [MTL](https://github.com/cefriel/mapping-template).
  - These artifacts are modifiable before execution to support different data integration scenarios or optimizations.

- **Runtime**:
  - The generated pipeline and mappings are executed using the `typhon-chimera-skeleton` component, yielding an output equivalent to the RML's declarative intent.

---

## How It Works

1. **Input**: Provide an RML mapping file to `typhon-rml`.
2. **Transformation**: The tool parses the RML and generates:
   - `route.xml` using `router.vm` (MTL)
   - `template.vm` using `translator.vm` (MTL)
3. **Customization (Optional)**:
   - Modify `route.xml` to use custom data sources via different Apache Camel components.
   - Adjust `template.vm` for performance tuning (e.g., optimized joins).
4. **Execution**:
   - Use `typhon-chimera-skeleton` to run the KG construction pipeline and produce the final output.

---

### Run Typhon-RML

```bash
java -jar target/typhon-rml.jar --rml-mapping <your-rml-file.ttl>
```

This will generate the following files:
- `route.xml`
- `template.vm`

### Execute the Pipeline

Use the [typhon-chimera-skeleton](https://github.com/cefriel/typhon-chimera-skeleton) to execute the generated pipeline. The typhon-chimera-skeleton expects the `route.xml` and `template.vm` files to be placed in a `data` directory where the following command will be run:

```bash
java -jar target/chimera-typhon-skeleton.jar
```

---

## Customization

- **Custom Data Access**: Modify `route.xml` to use any available [Camel component](https://camel.apache.org/components/latest/index.html) (e.g., read from a message queue instead of a file).
- **Optimized Mappings**: Edit `template.vm` to include transformations or optimizations not expressible in RML.

---

## Related Projects

- [Chimera](https://github.com/cefriel/chimera): Declarative data integration and transformation framework.
- [Mapping Template](https://github.com/cefriel/mapping-template): MTL-based engine for executing declarative transformation rules.
- [Apache Camel](https://camel.apache.org/): Integration framework for building routing and mediation rules.

---
