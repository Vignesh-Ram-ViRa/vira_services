package com.vira.auth.dto;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * Data Transfer Object for authentication responses.
 */
@Schema(description = "Authentication response with tokens and user info")
public class AuthResponse {

    @Schema(description = "JWT access token", example = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    private String token;

    @Schema(description = "JWT refresh token", example = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    private String refreshToken;

    @Schema(description = "Token type", example = "Bearer")
    private String type = "Bearer";

    @Schema(description = "User information")
    private UserResponse user;

    // Constructors
    public AuthResponse() {}

    public AuthResponse(String token, String refreshToken, UserResponse user) {
        this.token = token;
        this.refreshToken = refreshToken;
        this.user = user;
    }

    // Getters and Setters
    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public String getRefreshToken() {
        return refreshToken;
    }

    public void setRefreshToken(String refreshToken) {
        this.refreshToken = refreshToken;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public UserResponse getUser() {
        return user;
    }

    public void setUser(UserResponse user) {
        this.user = user;
    }

    @Override
    public String toString() {
        return "AuthResponse{" +
                "type='" + type + '\'' +
                ", user=" + user +
                '}';
    }
} 