-- PostgreSQL migration script to add IMEI fields
-- Run this directly on your PostgreSQL database

-- Add IMEI field to sales table
ALTER TABLE sales 
ADD COLUMN IF NOT EXISTS imei VARCHAR(20);

-- Add IMEI field to loans table  
ALTER TABLE loans 
ADD COLUMN IF NOT EXISTS imei VARCHAR(20);

-- Create indexes for IMEI searches (improves performance)
CREATE INDEX IF NOT EXISTS idx_sales_imei ON sales(imei);
CREATE INDEX IF NOT EXISTS idx_loans_imei ON loans(imei);

-- Verify the changes
\d sales;
\d loans;