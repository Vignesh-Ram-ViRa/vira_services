package com.vira.config;

import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.enums.SecuritySchemeType;
import io.swagger.v3.oas.annotations.info.Contact;
import io.swagger.v3.oas.annotations.info.Info;
import io.swagger.v3.oas.annotations.info.License;
import io.swagger.v3.oas.annotations.security.SecurityScheme;
import io.swagger.v3.oas.annotations.servers.Server;
import org.springframework.context.annotation.Configuration;

/**
 * OpenAPI configuration for Swagger UI documentation.
 * Configures JWT Bearer token authentication for protected endpoints.
 */
@Configuration
@OpenAPIDefinition(
    info = @Info(
        title = "Vira Services API",
        description = "Multi-service backend with JWT authentication for personal projects",
        version = "1.0.0",
        contact = @Contact(
            name = "Vira Services",
            email = "contact@viraservices.com",
            url = "https://github.com/yourusername/vira-services"
        ),
        license = @License(
            name = "MIT License",
            url = "https://opensource.org/licenses/MIT"
        )
    ),
    servers = {
        @Server(url = "http://localhost:8080", description = "Development Server"),
        @Server(url = "https://your-app.railway.app", description = "Production Server")
    }
)
@SecurityScheme(
    name = "Bearer Authentication",
    type = SecuritySchemeType.HTTP,
    bearerFormat = "JWT",
    scheme = "bearer",
    description = "Enter JWT Bearer token obtained from /api/auth/login endpoint"
)
public class OpenApiConfig {
} 