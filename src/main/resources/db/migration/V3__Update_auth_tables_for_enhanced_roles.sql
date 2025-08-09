-- Migration to enhance auth tables for new role system
-- Adds user approval workflow and Google OAuth support

-- Add new columns to auth_users table
ALTER TABLE auth_users 
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'APPROVED',
ADD COLUMN requested_role VARCHAR(20),
ADD COLUMN approval_notes VARCHAR(500),
ADD COLUMN approved_by BIGINT,
ADD COLUMN approved_at TIMESTAMP,
ADD COLUMN google_id VARCHAR(255) UNIQUE;

-- Add foreign key constraint for approved_by
ALTER TABLE auth_users 
ADD CONSTRAINT fk_auth_users_approved_by 
FOREIGN KEY (approved_by) REFERENCES auth_users(id);

-- Update existing USER role to NORMAL_USER (migration from old role system)
UPDATE auth_roles SET name = 'NORMAL_USER', description = 'Regular users with standard application access' WHERE name = 'USER';

-- Insert new roles
INSERT INTO auth_roles (name, description) VALUES 
('GUEST', 'Anonymous users with limited read-only access'),
('SUPER_USER', 'Approved users with read-only access to everything'),
('ADMIN', 'Full system access and user management')
ON CONFLICT (name) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_auth_users_status ON auth_users(status);
CREATE INDEX IF NOT EXISTS idx_auth_users_google_id ON auth_users(google_id);
CREATE INDEX IF NOT EXISTS idx_auth_users_requested_role ON auth_users(requested_role);
CREATE INDEX IF NOT EXISTS idx_auth_users_approved_by ON auth_users(approved_by);

-- Update the trigger function for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Ensure trigger exists for auth_users
DROP TRIGGER IF EXISTS update_auth_users_updated_at ON auth_users;
CREATE TRIGGER update_auth_users_updated_at 
    BEFORE UPDATE ON auth_users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 