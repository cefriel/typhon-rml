package com.cefriel;

import com.cefriel.template.io.Reader;
import com.cefriel.template.io.csv.CSVReader;
import com.cefriel.template.io.json.JSONReader;
import com.cefriel.template.io.xml.XMLReader;
import org.apache.camel.AggregationStrategy;
import org.apache.camel.Exchange;

import java.security.InvalidParameterException;
import java.util.HashMap;
import java.util.Map;

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
        String readerFormat = exchange.getVariable("readerFormat", String.class);
        String readerName = exchange.getVariable("readerName", String.class);

        Reader reader = switch (readerFormat) {
            case "json" -> new JSONReader(readerContent);
            case "xml" -> {
                try {
                    yield new XMLReader(readerContent);
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            }
            case "csv" -> new CSVReader(readerContent);
            default -> throw new InvalidParameterException("Cannot create Reader for format: " + readerFormat);
        };

        return Map.of(readerName, reader, "test", reader);
    }
}
