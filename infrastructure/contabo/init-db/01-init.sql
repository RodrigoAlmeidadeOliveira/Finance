-- ===========================================
-- Flow Forecaster - Database Initialization
-- This script runs on first PostgreSQL startup
-- ===========================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant privileges (if needed)
-- GRANT ALL PRIVILEGES ON DATABASE flow_forecaster TO forecaster;

-- Note: Actual table creation is handled by Flask-Migrate/Alembic
-- This file is for any initial setup that needs to happen before migrations
