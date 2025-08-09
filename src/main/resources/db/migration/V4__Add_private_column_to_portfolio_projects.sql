-- Add private column to portfolio_projects table
-- This allows users to mark projects as private (not visible to others)

ALTER TABLE portfolio_projects 
ADD COLUMN private BOOLEAN NOT NULL DEFAULT false;

-- Add index for performance when filtering by private status
CREATE INDEX idx_portfolio_projects_private ON portfolio_projects(private);

-- Add composite index for user-specific private filtering
CREATE INDEX idx_portfolio_projects_user_private ON portfolio_projects(user_id, private);

-- Update existing projects to be public by default (explicit update for clarity)
UPDATE portfolio_projects SET private = false WHERE private IS NULL; 