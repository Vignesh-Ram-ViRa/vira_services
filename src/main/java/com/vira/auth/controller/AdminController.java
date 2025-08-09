package com.vira.auth.controller;

import com.vira.auth.dto.ApprovalRequest;
import com.vira.auth.dto.SuperUserRequest;
import com.vira.auth.dto.UserResponse;
import com.vira.auth.model.RoleName;
import com.vira.auth.service.AuthService;
import com.vira.common.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.Set;

@RestController
@RequestMapping("/api/admin")
@CrossOrigin(origins = {"http://localhost:8080", "http://localhost:3000", "http://localhost:3001"}, allowCredentials = "true")
@Tag(name = "Admin", description = "Admin-only endpoints for user and role management. Requires ADMIN role. Use the 🔒 Authorize button with your JWT token.")
@SecurityRequirement(name = "Bearer Authentication")
@PreAuthorize("hasRole('ADMIN')")
public class AdminController {

    @Autowired
    private AuthService authService;

    @GetMapping("/pending-approvals")
    @Operation(
        summary = "Get pending super user approvals",
        description = "Retrieve all users pending approval for SUPER_USER role. Only accessible by ADMIN users."
    )
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Successfully retrieved pending approvals"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "403", description = "Access denied - ADMIN role required")
    })
    public ResponseEntity<ApiResponse<Set<UserResponse>>> getPendingApprovals() {
        Set<UserResponse> pendingUsers = authService.getPendingApprovals();
        return ResponseEntity.ok(ApiResponse.success(pendingUsers, "Pending approvals retrieved successfully"));
    }

    @PostMapping("/approve-super-user")
    @Operation(
        summary = "Approve or reject super user request",
        description = "Approve or reject a pending SUPER_USER registration. Only accessible by ADMIN users."
    )
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "User approval processed successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Invalid request"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "User not found"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "403", description = "Access denied - ADMIN role required")
    })
    public ResponseEntity<ApiResponse<UserResponse>> approveSuperUser(
            @Valid @RequestBody ApprovalRequest request,
            Authentication authentication) {
        UserResponse user = authService.approveSuperUser(request, authentication);
        String message = request.getApproved() ? "User approved successfully" : "User rejected successfully";
        return ResponseEntity.ok(ApiResponse.success(user, message));
    }

    @PutMapping("/users/{userId}/role")
    @Operation(
        summary = "Update user role",
        description = "Update a user's role directly. This bypasses the approval process. Only accessible by ADMIN users."
    )
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "User role updated successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Invalid role"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "User not found"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "403", description = "Access denied - ADMIN role required")
    })
    public ResponseEntity<ApiResponse<UserResponse>> updateUserRole(
            @Parameter(description = "User ID", example = "1") 
            @PathVariable Long userId,
            @Parameter(description = "New role for the user", example = "SUPER_USER") 
            @RequestParam RoleName role,
            Authentication authentication) {
        UserResponse user = authService.updateUserRole(userId, role, authentication);
        return ResponseEntity.ok(ApiResponse.success(user, "User role updated successfully"));
    }

    @PostMapping("/register-super-user")
    @Operation(
        summary = "Register super user (admin bypass)",
        description = "Register a SUPER_USER directly without approval process. Only accessible by ADMIN users."
    )
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "201", description = "Super user registered successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Username or email already exists"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "403", description = "Access denied - ADMIN role required")
    })
    public ResponseEntity<ApiResponse<UserResponse>> registerSuperUserDirect(
            @Valid @RequestBody SuperUserRequest request,
            Authentication authentication) {
        // For admin, we'll create the super user directly without approval process
        var authResponse = authService.registerSuperUser(request);
        
        // If created by admin, auto-approve
        if (authResponse.getUser() != null) {
            ApprovalRequest approvalRequest = new ApprovalRequest();
            approvalRequest.setUserId(authResponse.getUser().getId());
            approvalRequest.setApproved(true);
            approvalRequest.setNotes("Auto-approved by admin during registration");
            
            UserResponse user = authService.approveSuperUser(approvalRequest, authentication);
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(ApiResponse.success(user, "Super user registered and approved successfully"));
        }
        
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success(authResponse.getUser(), "Super user registered successfully"));
    }
} 