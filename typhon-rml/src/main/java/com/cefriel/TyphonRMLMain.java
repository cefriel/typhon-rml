package com.cefriel;

import com.cefriel.template.TemplateExecutor;
import com.cefriel.template.TemplateMap;
import com.cefriel.template.io.Reader;
import com.cefriel.template.io.rdf.RDFReader;
import com.cefriel.template.io.xml.XMLFormatter;
import com.cefriel.template.utils.RMLCompilerUtils;
import com.cefriel.template.utils.TemplateFunctions;
import org.eclipse.rdf4j.model.Model;
import org.eclipse.rdf4j.model.ValueFactory;
import org.eclipse.rdf4j.model.impl.SimpleValueFactory;
import org.eclipse.rdf4j.query.BindingSet;
import org.eclipse.rdf4j.query.QueryResults;
import org.eclipse.rdf4j.query.TupleQuery;
import org.eclipse.rdf4j.query.TupleQueryResult;
import org.eclipse.rdf4j.repository.Repository;
import org.eclipse.rdf4j.repository.RepositoryConnection;
import org.eclipse.rdf4j.repository.sail.SailRepository;
import org.eclipse.rdf4j.repository.util.Connections;
import org.eclipse.rdf4j.repository.util.Repositories;
import org.eclipse.rdf4j.rio.RDFFormat;
import org.eclipse.rdf4j.rio.Rio;
import org.eclipse.rdf4j.sail.memory.MemoryStore;

import java.io.File;
import java.io.FileInputStream;
import java.io.StringWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.HashMap;
import java.util.Map;

public class TyphonRMLMain {

    public static void addReaderIds(RepositoryConnection connection) {
        String propertiesForSource = "PREFIX rml: <http://w3id.org/rml/>\n" +
                "\n" +
                "SELECT ?logicalSource (GROUP_CONCAT(CONCAT(\"rml:referenceFormulation=\", STR(?ref), \", \", STR(?predicate), \"=\", STR(?object)); separator=\", \") AS ?details)\n" +
                "WHERE {\n" +
                "  ?triplesMap a rml:TriplesMap ;\n" +
                "              rml:logicalSource ?logicalSource .\n" +
                "  \n" +
                "  ?logicalSource rml:source ?source ;\n" +
                "                 rml:referenceFormulation ?ref .\n" +
                "  \n" +
                "  ?source ?predicate ?object .\n" +
                "}\n" +
                "GROUP BY ?logicalSource\n";

        ValueFactory vf = SimpleValueFactory.getInstance();
        TupleQuery query = connection.prepareTupleQuery(propertiesForSource);
        try (TupleQueryResult result = query.evaluate()) {
            while (result.hasNext()) {
                BindingSet bindingSet = result.next();
                String logicalSource = bindingSet.getValue("logicalSource").stringValue();
                String details = bindingSet.getValue("details").stringValue();

                connection.add(vf.createBNode(logicalSource), vf.createIRI("http://w3id.org/rml/reader"), vf.createLiteral(TemplateFunctions.literalHash(details)));
            }
        }
    }

    public static void main(String[] args) throws Exception {

        if (args.length < 2 || !args[0].equals("--rml-mapping")) {
            System.out.println("Usage: java Main --rml-mapping <file_path>");
            return;
        }

        String filePath = args[1];
        File file = new File(filePath);

        if (!file.exists() || file.isDirectory()) {
            System.out.println("Error: The specified file does not exist or is a directory.");
            return;
        }

        System.out.println("RML Mapping file provided: " + filePath);
        Repository repository = new SailRepository(new MemoryStore());
        repository.init();

        // Execute the CONSTRUCT query and add the new triples back into the repository
        try (RepositoryConnection connection = repository.getConnection()) {

            FileInputStream inputStream = new FileInputStream(filePath);
            connection.add(inputStream, "", RDFFormat.TURTLE);
            addReaderIds(connection);

            // Dump the entire in-memory graph as a Turtle-formatted string
            StringWriter writer = new StringWriter();

            Model entireGraph = QueryResults.asModel(connection.getStatements(null, null, null));
            Rio.write(entireGraph, writer, RDFFormat.TURTLE);
            String finalTurtle = writer.toString();
            Files.write(Path.of("./mapping-augmented.ttl"), finalTurtle.getBytes(), StandardOpenOption.CREATE, StandardOpenOption.WRITE);

            RDFReader augmentedRMLMappingReader = new RDFReader();
            augmentedRMLMappingReader.addString(finalTurtle, RDFFormat.TURTLE);

            Map<String, Reader> readers = Map.of("reader", augmentedRMLMappingReader);
            TemplateExecutor routeExecutor = new TemplateExecutor(true, false, true, new XMLFormatter());
            Path outputRoute = routeExecutor.executeMapping(readers, Path.of("router.vm"), Path.of("route.xml"));
            System.out.println("From " + filePath + " produced " + outputRoute + " Apache Camel route.");

            Path typhonRMLCompiler = Paths.get("typhon-rml-compiler.vm");

            Map<String,String> rmlMap = new HashMap<>();
            var rmlCompilerUtils = new RMLCompilerUtils();

            String baseIriRML = rmlCompilerUtils.getBaseIRI(Path.of(filePath));
            rmlMap.put("baseIRI", baseIriRML);

            TemplateExecutor templateExecutor = new TemplateExecutor(false, false,true, null);
            Path outputMapping = templateExecutor.executeMapping(readers, typhonRMLCompiler, Path.of("template.vm"), rmlCompilerUtils, new TemplateMap(rmlMap));
            System.out.println("From " + filePath + " produced " + outputMapping + " MTL mapping.");
        }
    }
}

