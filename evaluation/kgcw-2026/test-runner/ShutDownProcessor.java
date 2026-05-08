package com.cefriel;

import org.apache.camel.CamelContext;
import org.apache.camel.Exchange;
import org.apache.camel.Processor;

public class ShutDownProcessor implements Processor {
    @Override
    public void process(Exchange exchange) throws Exception {
        CamelContext camelContext = exchange.getContext();
        camelContext.stop();
        System.out.println("Forcing JVM shutdown...");
        System.exit(0);
    }
}
