FROM maven:3.9-eclipse-temurin-21-alpine AS builder

WORKDIR /app

COPY pom.xml ./
RUN mvn dependency:go-offline

COPY . .
RUN mvn clean package -DskipTests

FROM eclipse-temurin:21-jre-alpine AS runtime

WORKDIR /app

RUN mkdir -p /app/data

# Volume for external data mapping
VOLUME ["/app/data"]

COPY --from=builder /app/target/typhon-rml.jar /app/typhon-rml.jar

COPY ./chimera-typhon-skeleton.jar /app/chimera-typhon-skeleton.jar

# Keep container running
CMD ["tail", "-f", "/dev/null"]
