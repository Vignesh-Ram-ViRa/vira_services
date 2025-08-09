package com.vira.auth.controller;

import com.vira.auth.dto.*;
import com.vira.auth.service.AuthService;
import com.vira.common.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import io.swagger.v3.oas.annotations.Parameter;

/**
 * REST Controller for authentication operations.
 */
@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = {"http://localhost:8080", "http://localhost:3000", "http://localhost:3001"}, allowCredentials = "true")
@Tag(name = "Authentication", description = "User authentication and authorization endpoints")
public class AuthController {

    @Autowired
    private AuthService authService;

    @Operation(summary = "Register new user", 
               description = "Create a new user account with NORMAL_USER role. " +
                           "✅ Test with: username='testuser', email='test@example.com', password='password123'")
    @ApiResponses(value = {
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "201", description = "User registered successfully"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Invalid input or user already exists")
    })
    @PostMapping("/register")
    public ResponseEntity<ApiResponse<AuthResponse>> register(@Valid @RequestBody RegisterRequest request) {
        AuthResponse response = authService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success(response, "User registered successfully"));
    }

    @Operation(summary = "User login", 
               description = "Authenticate user and return JWT tokens. " +
                           "✅ Test with: username='testuser', password='password123' " +
                           "(after registering above). Returns role information and JWT token.")
    @ApiResponses(value = {
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Login successful"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "401", description = "Invalid credentials")
    })
    @PostMapping("/login")
    public ResponseEntity<ApiResponse<AuthResponse>> login(@Valid @RequestBody LoginRequest request) {
        AuthResponse response = authService.login(request);
        return ResponseEntity.ok(ApiResponse.success(response, "Login successful"));
    }

    @Operation(summary = "Refresh JWT token", description = "Get new access token using refresh token")
    @ApiResponses(value = {
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Token refreshed successfully"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "401", description = "Invalid or expired refresh token")
    })
    @PostMapping("/refresh")
    public ResponseEntity<ApiResponse<AuthResponse>> refreshToken(@Valid @RequestBody RefreshTokenRequest request) {
        AuthResponse response = authService.refreshToken(request);
        return ResponseEntity.ok(ApiResponse.success(response, "Token refreshed successfully"));
    }

    @Operation(summary = "User logout", description = "Invalidate refresh token and logout user")
    @ApiResponses(value = {
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Logout successful")
    })
    @PostMapping("/logout")
    public ResponseEntity<ApiResponse<String>> logout(@RequestBody(required = false) RefreshTokenRequest request) {
        String refreshToken = request != null ? request.getRefreshToken() : null;
        authService.logout(refreshToken);
        return ResponseEntity.ok(ApiResponse.success("Logout successful"));
    }

    @Operation(summary = "Get current user", description = "Get current authenticated user information")
    @ApiResponses(value = {
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "User information retrieved"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "401", description = "User not authenticated")
    })
    @GetMapping("/me")
    public ResponseEntity<ApiResponse<UserResponse>> getCurrentUser() {
        UserResponse response = authService.getCurrentUser();
        return ResponseEntity.ok(ApiResponse.success(response, "User information retrieved"));
    }

    @PostMapping("/register-super-user")
    @Operation(
        summary = "Register for super user access",
        description = "Submit a request for SUPER_USER role that requires admin approval. " +
                     "Provide justification, organization, and position details. " +
                     "Example: {\"username\":\"superuser1\",\"email\":\"superuser1@example.com\"," +
                     "\"password\":\"securepass123\",\"justification\":\"Need analytics access\"," +
                     "\"organization\":\"Example Corp\",\"position\":\"Business Analyst\"}"
    )
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "201", description = "Super user request submitted for approval"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Username or email already exists")
    })
    public ResponseEntity<ApiResponse<UserResponse>> registerSuperUser(@Valid @RequestBody SuperUserRequest request) {
        AuthResponse response = authService.registerSuperUser(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success(response.getUser(), response.getMessage()));
    }

    @GetMapping("/oauth2/authorization/google")
    @Operation(
        summary = "Initiate Google OAuth2 login",
        description = "Redirects to Google OAuth2 authorization server for authentication. " +
                     "This is the starting point for Google login flow."
    )
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "302", description = "Redirect to Google OAuth2"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "OAuth2 configuration error")
    })
    public ResponseEntity<ApiResponse<String>> googleOAuth2Login() {
        // This endpoint is handled by Spring Security OAuth2
        // Users will be redirected to Google's authorization server
        return ResponseEntity.ok(ApiResponse.success(
            "/oauth2/authorization/google", 
            "Redirect to Google OAuth2 authorization"
        ));
    }

    @GetMapping("/oauth2/callback/google")
    @Operation(
        summary = "Google OAuth2 callback",
        description = "Handles the callback from Google OAuth2 after user authorization. " +
                     "This is automatically called by Google after user grants permission."
    )
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "OAuth2 login successful"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "OAuth2 authentication failed"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<ApiResponse<AuthResponse>> googleOAuth2Callback(
            @Parameter(hidden = true) org.springframework.security.oauth2.core.user.OAuth2User oauth2User
    ) {
        // This will be handled by OAuth2SuccessHandler
        return ResponseEntity.ok(ApiResponse.success(null, "OAuth2 callback processed"));
    }
} 