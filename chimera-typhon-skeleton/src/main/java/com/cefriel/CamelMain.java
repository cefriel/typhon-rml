package com.cefriel;

import org.apache.camel.CamelContext;
import org.apache.camel.ExtendedCamelContext;
import org.apache.camel.impl.DefaultCamelContext;
import org.apache.camel.impl.event.ExchangeFailedEvent;
import org.apache.camel.main.Main;
import org.apache.camel.model.ModelCamelContext;
import org.apache.camel.spi.CamelEvent;
import org.apache.camel.spi.Resource;
import org.apache.camel.spi.RoutesLoader;
import org.apache.camel.support.EventNotifierSupport;
import org.apache.camel.support.PluginHelper;
import org.apache.camel.support.ResourceHelper;


import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.logging.Level;
import java.util.logging.Logger;

public class CamelMain {

    private static final Logger LOGGER = Logger.getLogger(CamelMain.class.getName());

    public static void main(String[] args) {
        CamelContext camelContext = new DefaultCamelContext();

        camelContext.getManagementStrategy().addEventNotifier(new EventNotifierSupport() {
            @Override
            public void notify(CamelEvent event) {
                if (event instanceof ExchangeFailedEvent) {
                    LOGGER.log(Level.SEVERE, "Exchange failed: " + event);
                    System.exit(1);
                }
            }
        });

        File xmlRoute = new File("./data/route.xml");

        if (xmlRoute.exists()) {
            byte[] routeDefinitionBytes = null;
            try {
                routeDefinitionBytes = Files.readAllBytes(xmlRoute.toPath());
            } catch (IOException e) {
                LOGGER.log(Level.WARNING, e.getMessage());
                System.exit(1);
            }
            Resource resource = ResourceHelper.fromBytes(xmlRoute.getAbsolutePath(), routeDefinitionBytes);

            RoutesLoader x = PluginHelper.getRoutesLoader(camelContext);
            try {
                x.loadRoutes(resource);
            } catch (Exception e) {
                LOGGER.log(Level.SEVERE, e.getMessage());
                System.exit(1);
            }

            camelContext.start();
        }
        else {
            System.out.println(xmlRoute + " not found!");
        }
    }
}