package com.cefriel;

import com.cefriel.template.io.Reader;
import com.cefriel.template.io.csv.CSVReader;
import com.cefriel.template.io.json.JSONReader;
import com.cefriel.template.io.rdf.RDFReader;
import com.cefriel.template.io.sql.SQLReader;
import com.cefriel.template.io.xml.XMLReader;
import com.cefriel.template.utils.Util;
import org.apache.camel.AggregationStrategy;
import org.apache.camel.Exchange;
import org.eclipse.rdf4j.rio.RDFFormat;
import org.eclipse.rdf4j.rio.Rio;

import java.security.InvalidParameterException;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class ReadersAggregation implements AggregationStrategy {

    @Override
    public Exchange aggregate(Exchange oldExchange, Exchange newExchange) {
        if (oldExchange == null) {
            newExchange.getMessage().setBody(getReaders(newExchange));
            return newExchange;
        }

        Map<String, Reader> oldReaders = (Map<String, Reader>) oldExchange.getMessage().getBody();
        Map<String, Reader> newReaders = getReaders(newExchange);

        HashMap<String, Reader> readers = new HashMap<>();
        readers.putAll(oldReaders);
        readers.putAll(newReaders);

        oldExchange.getMessage().setBody(readers);
        return oldExchange;
    }

    public Map<String, Reader> getReaders(Exchange exchange) {
        String readerContent = exchange.getMessage().getBody(String.class);
        // the exchange variable names are defined in the router.vm file from typhon-rml
        String readerFormat = exchange.getVariable("readerFormat", String.class);
        String readerName = exchange.getVariable("readerName", String.class);

        Reader reader = switch (readerFormat) {
            case "json" -> new JSONReader(readerContent);
            case "sql" -> {
                String jdbcDSN = exchange.getVariable("jdbcDSN", String.class);
                String username = exchange.getVariable("username", String.class);
                String password = exchange.getVariable("password", String.class);
                yield new SQLReader(jdbcDSN, username, password);
            }
            case "xml" -> {
                try {
                    yield new XMLReader(readerContent);
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            }
            case "csv" -> new CSVReader(readerContent);
            case "rdf" -> {
                RDFReader rdfReader = new RDFReader();
                String rmlPath = exchange.getVariable("readerInputFile", String.class);
                Optional<RDFFormat> rdfFormat = Rio.getParserFormatForFileName(rmlPath);
                try {
                    if (rdfFormat.isPresent())
                        rdfReader.addString(readerContent, rdfFormat.get());
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
                yield rdfReader;
            }
            default -> throw new InvalidParameterException("Cannot create Reader for format: " + readerFormat);
        };

        return Map.of(readerName, reader, "test", reader);
    }
}
