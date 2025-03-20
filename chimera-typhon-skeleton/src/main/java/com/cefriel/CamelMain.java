package com.cefriel;

import org.apache.camel.CamelContext;
import org.apache.camel.ExtendedCamelContext;
import org.apache.camel.impl.DefaultCamelContext;
import org.apache.camel.main.Main;
import org.apache.camel.model.ModelCamelContext;
import org.apache.camel.spi.Resource;
import org.apache.camel.spi.RoutesLoader;
import org.apache.camel.support.PluginHelper;
import org.apache.camel.support.ResourceHelper;


import java.io.File;
import java.nio.file.Files;

public class CamelMain {
    public static void main(String[] args) throws Exception {
        CamelContext camelContext = new DefaultCamelContext();

        File xmlRoute = new File("./data/route.xml");

        if (xmlRoute.exists()) {
            byte[] routeDefinitionBytes = Files.readAllBytes(xmlRoute.toPath());
            Resource resource = ResourceHelper.fromBytes(xmlRoute.getAbsolutePath(), routeDefinitionBytes);

            RoutesLoader x = PluginHelper.getRoutesLoader(camelContext);
            x.loadRoutes(resource);
            camelContext.start();

            // Main main = new Main(CamelMain.class);
            // main.run(args);
        }
        else {
            System.out.println(xmlRoute + " not found!");
        }
    }
}