package com.vira.auth.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * DTO for super user registration request.
 * Super users need approval from admin.
 */
public class SuperUserRequest {
    
    @NotBlank(message = "Username is required")
    @Size(min = 3, max = 20, message = "Username must be between 3 and 20 characters")
    private String username;
    
    @NotBlank(message = "Email is required")
    @Email(message = "Email should be valid")
    @Size(max = 50, message = "Email must not exceed 50 characters")
    private String email;
    
    @NotBlank(message = "Password is required")
    @Size(min = 6, max = 120, message = "Password must be between 6 and 120 characters")
    private String password;
    
    @NotBlank(message = "Justification is required")
    @Size(min = 10, max = 500, message = "Justification must be between 10 and 500 characters")
    private String justification;
    
    @Size(max = 100, message = "Organization must not exceed 100 characters")
    private String organization;
    
    @Size(max = 50, message = "Position must not exceed 50 characters")
    private String position;

    // Constructors
    public SuperUserRequest() {}

    public SuperUserRequest(String username, String email, String password, String justification) {
        this.username = username;
        this.email = email;
        this.password = password;
        this.justification = justification;
    }

    // Getters and Setters
    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getJustification() {
        return justification;
    }

    public void setJustification(String justification) {
        this.justification = justification;
    }

    public String getOrganization() {
        return organization;
    }

    public void setOrganization(String organization) {
        this.organization = organization;
    }

    public String getPosition() {
        return position;
    }

    public void setPosition(String position) {
        this.position = position;
    }

    @Override
    public String toString() {
        return "SuperUserRequest{" +
                "username='" + username + '\'' +
                ", email='" + email + '\'' +
                ", organization='" + organization + '\'' +
                ", position='" + position + '\'' +
                '}';
    }
} 