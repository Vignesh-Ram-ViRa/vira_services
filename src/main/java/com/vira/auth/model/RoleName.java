package com.vira.auth.model;

/**
 * Enumeration of available user roles in the system.
 * Roles are hierarchical: ADMIN > SUPER_USER > NORMAL_USER > GUEST
 */
public enum RoleName {
    /**
     * Guest role - anonymous users with very limited read-only access
     * Can view public content without authentication
     */
    GUEST,
    
    /**
     * Normal user role - registered users with limited application-specific access
     * Can perform CRUD operations on their own data
     * Supports Google OAuth authentication
     */
    NORMAL_USER,
    
    /**
     * Super user role - approved users with read-only access to everything
     * Must be approved by admin after registration
     * Can view all data across applications but cannot edit
     */
    SUPER_USER,
    
    /**
     * Admin role - full system access
     * Can manage users, approve super users, access all features
     * System configuration and cross-application management
     */
    ADMIN
} 