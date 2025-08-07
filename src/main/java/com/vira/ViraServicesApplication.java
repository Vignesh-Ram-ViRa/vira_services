package com.vira;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

/**
 * Main Spring Boot application class for Vira Services.
 * 
 * This application serves as a centralized backend for multiple personal projects
 * with shared JWT authentication and PostgreSQL database.
 * 
 * @author Vira Services Team
 * @version 1.0
 * @since 2024
 */
@SpringBootApplication
@EnableJpaAuditing
public class ViraServicesApplication {

    public static void main(String[] args) {
        SpringApplication.run(ViraServicesApplication.class, args);
    }
} 