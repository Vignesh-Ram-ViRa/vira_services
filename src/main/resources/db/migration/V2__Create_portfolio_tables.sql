-- Create portfolio tables for Vira Services
-- Migration: V2__Create_portfolio_tables.sql

-- Projects table
CREATE TABLE portfolio_projects (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    link VARCHAR(500),
    github VARCHAR(500),
    image VARCHAR(500),
    status VARCHAR(50),
    category VARCHAR(100),
    year INTEGER,
    featured BOOLEAN NOT NULL DEFAULT FALSE,
    user_id BIGINT NOT NULL REFERENCES auth_users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project technologies table (for many-to-many relationship)
CREATE TABLE portfolio_project_technologies (
    project_id BIGINT NOT NULL REFERENCES portfolio_projects(id) ON DELETE CASCADE,
    technology VARCHAR(100) NOT NULL,
    PRIMARY KEY (project_id, technology)
);

-- Create indexes for better performance
CREATE INDEX idx_portfolio_projects_user_id ON portfolio_projects(user_id);
CREATE INDEX idx_portfolio_projects_status ON portfolio_projects(status);
CREATE INDEX idx_portfolio_projects_category ON portfolio_projects(category);
CREATE INDEX idx_portfolio_projects_year ON portfolio_projects(year);
CREATE INDEX idx_portfolio_projects_featured ON portfolio_projects(featured);
CREATE INDEX idx_portfolio_projects_created_at ON portfolio_projects(created_at);

-- Update trigger for updated_at column
CREATE TRIGGER update_portfolio_projects_updated_at BEFORE UPDATE ON portfolio_projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 