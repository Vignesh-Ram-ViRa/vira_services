# Dockerfile for Render deployment of Spring Boot app
FROM eclipse-temurin:17-jdk
WORKDIR /app
COPY . .
RUN ./mvnw clean package -DskipTests
EXPOSE 8080
CMD ["java", "-Dspring.profiles.active=prod", "-jar", "target/vira-services-0.0.1-SNAPSHOT.jar"]
