package com.vira.auth.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vira.common.dto.ApiResponse;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;

import java.io.IOException;

/**
 * JWT authentication entry point to handle unauthorized access attempts.
 * Returns a standardized JSON error response for authentication failures.
 */
@Component
public class JwtAuthenticationEntryPoint implements AuthenticationEntryPoint {

    private static final Logger logger = LoggerFactory.getLogger(JwtAuthenticationEntryPoint.class);

    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response,
                         AuthenticationException authException) throws IOException, ServletException {
        
        logger.error("Unauthorized error: {}", authException.getMessage());

        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);

        ApiResponse<String> errorResponse = ApiResponse.error("Unauthorized: " + authException.getMessage());

        final ObjectMapper mapper = new ObjectMapper();
        mapper.findAndRegisterModules(); // Register JavaTimeModule for LocalDateTime
        mapper.writeValue(response.getOutputStream(), errorResponse);
    }
} 