package com.cefriel;

import com.cefriel.template.TemplateExecutor;
import com.cefriel.template.TemplateMap;
import com.cefriel.template.io.Reader;
import com.cefriel.template.io.rdf.RDFReader;
import com.cefriel.template.io.xml.XMLFormatter;
import com.cefriel.template.utils.RMLCompilerUtils;
import org.eclipse.rdf4j.model.Model;
import org.eclipse.rdf4j.query.QueryResults;
import org.eclipse.rdf4j.repository.Repository;
import org.eclipse.rdf4j.repository.RepositoryConnection;
import org.eclipse.rdf4j.repository.sail.SailRepository;
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

    private static final String constructQuery = "prefix rml: <http://w3id.org/rml/>\n" +
            "CONSTRUCT {\n" +
            "  ?ls rml:reader ?readerId .\n" +
            "}\n" +
            "WHERE {      \n" +
            "?ls rml:source ?source .\n" +
            "BIND(STR(UUID()) as ?readerId)\n" +
            "}";

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

        // TODO run construct query

        Repository repository = new SailRepository(new MemoryStore());
        repository.init();

        // Execute the CONSTRUCT query and add the new triples back into the repository
        try (RepositoryConnection connection = repository.getConnection()) {

            FileInputStream inputStream = new FileInputStream(filePath);
            connection.add(inputStream, "", RDFFormat.TURTLE);

            Model constructResult = Repositories.graphQuery(repository, constructQuery, QueryResults::asModel);
            connection.add(constructResult);

            // Dump the entire in-memory graph as a Turtle-formatted string
            StringWriter writer = new StringWriter();

            Model entireGraph = QueryResults.asModel(connection.getStatements(null, null, null));
            Rio.write(entireGraph, writer, RDFFormat.TURTLE);
            String finalTurtle = writer.toString();
            Files.write(Path.of("./mapping-augmented.ttl"), finalTurtle.getBytes(), StandardOpenOption.CREATE, StandardOpenOption.WRITE);
            // System.out.println(finalTurtle);

            // TODO run mapping to extract route

            RDFReader augmentedRMLMappingReader = new RDFReader();
            augmentedRMLMappingReader.addString(finalTurtle, RDFFormat.TURTLE);

            Map<String, Reader> readers = Map.of("reader", augmentedRMLMappingReader);
            TemplateExecutor routeExecutor = new TemplateExecutor(true, false, true, new XMLFormatter());
            Path outputRoute = routeExecutor.executeMapping(readers, Path.of("router.vm"), Path.of("route.xml"));
            System.out.println("From " + filePath + " produced " + outputRoute + " Apache Camel route.");

            // TODO Convert augmented mapping to MLT mapping

            Path typhonRMLCompiler = Paths.get("typhon-rml-compiler.vm");

            Map<String,String> rmlMap = new HashMap<>();
            var rmlCompilerUtils = new RMLCompilerUtils();

            String baseIriRML = rmlCompilerUtils.getBaseIRI(Path.of(filePath));
            // baseIriRML = baseIriRML != null ? baseIriRML : "http://www.cefriel.com/data/";
            rmlMap.put("baseIRI", baseIriRML);

            TemplateExecutor templateExecutor = new TemplateExecutor(false, false,true, null);
            Path outputMapping = templateExecutor.executeMapping(readers, typhonRMLCompiler, Path.of("template.vm"), rmlCompilerUtils, new TemplateMap(rmlMap));
            System.out.println("From " + filePath + " produced " + outputMapping + " MTL mapping.");
        }
    }
}

