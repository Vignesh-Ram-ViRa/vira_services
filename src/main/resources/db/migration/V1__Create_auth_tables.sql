-- Create authentication tables for Vira Services
-- Migration: V1__Create_auth_tables.sql

-- Users table
CREATE TABLE auth_users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Roles table
CREATE TABLE auth_roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(20) UNIQUE NOT NULL,
    description VARCHAR(255)
);

-- User roles junction table
CREATE TABLE auth_user_roles (
    user_id BIGINT NOT NULL REFERENCES auth_users(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES auth_roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Refresh tokens table
CREATE TABLE auth_refresh_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES auth_users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default roles
INSERT INTO auth_roles (name, description) VALUES 
    ('USER', 'Standard user role with basic permissions'),
    ('ADMIN', 'Administrator role with full permissions');

-- Create indexes for better performance
CREATE INDEX idx_auth_users_username ON auth_users(username);
CREATE INDEX idx_auth_users_email ON auth_users(email);
CREATE INDEX idx_auth_users_enabled ON auth_users(enabled);
CREATE INDEX idx_auth_refresh_tokens_user_id ON auth_refresh_tokens(user_id);
CREATE INDEX idx_auth_refresh_tokens_token ON auth_refresh_tokens(token);
CREATE INDEX idx_auth_refresh_tokens_expires_at ON auth_refresh_tokens(expires_at);

-- Update trigger for updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_auth_users_updated_at BEFORE UPDATE ON auth_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default roles
INSERT INTO auth_roles (name, description, created_at) VALUES 
    ('USER', 'Default user role', CURRENT_TIMESTAMP),
    ('ADMIN', 'Administrator role', CURRENT_TIMESTAMP); 