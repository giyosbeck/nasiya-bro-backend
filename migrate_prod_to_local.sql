-- Migration script to update production database schema to match local backend
-- Run this script on production database BEFORE deploying local backend code

-- WARNING: Always backup production database before running migrations
-- pg_dump -h your_host -U your_user -d nasiya_bro > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql

BEGIN;

-- 1. Fix auto_products table - add missing magazine_id column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'auto_products' AND column_name = 'magazine_id'
    ) THEN
        ALTER TABLE auto_products ADD COLUMN magazine_id INTEGER REFERENCES magazines(id);
        COMMENT ON COLUMN auto_products.magazine_id IS 'Added for consistency - nullable for AUTO users';
    END IF;
END $$;

-- 2. Fix auto_sales table - make magazine_id nullable for AUTO users
DO $$
BEGIN
    -- Check if magazine_id column exists and has NOT NULL constraint
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'auto_sales'
        AND column_name = 'magazine_id'
        AND is_nullable = 'NO'
    ) THEN
        -- Make magazine_id nullable
        ALTER TABLE auto_sales ALTER COLUMN magazine_id DROP NOT NULL;
        COMMENT ON COLUMN auto_sales.magazine_id IS 'Made nullable for AUTO users';
    END IF;
END $$;

-- 3. Fix auto_loans table - make magazine_id nullable for AUTO users
DO $$
BEGIN
    -- Check if magazine_id column exists and has NOT NULL constraint
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'auto_loans'
        AND column_name = 'magazine_id'
        AND is_nullable = 'NO'
    ) THEN
        -- Make magazine_id nullable
        ALTER TABLE auto_loans ALTER COLUMN magazine_id DROP NOT NULL;
        COMMENT ON COLUMN auto_loans.magazine_id IS 'Made nullable for AUTO users';
    END IF;
END $$;

-- 4. Fix users table - ensure user_type enum has correct values
-- First check if UserType enum needs updating
DO $$
BEGIN
    -- Add missing enum values if they don't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'GADGETS' AND enumtypid = 'public.usertype'::regtype) THEN
        ALTER TYPE public.usertype ADD VALUE 'GADGETS';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'AUTO' AND enumtypid = 'public.usertype'::regtype) THEN
        ALTER TYPE public.usertype ADD VALUE 'AUTO';
    END IF;

    -- Update existing 'gadgets' values to 'GADGETS' (case consistency)
    UPDATE users SET user_type = 'GADGETS' WHERE user_type = 'gadgets';
END $$;

-- 5. Add any missing notification types to enum
DO $$
BEGIN
    -- Check and add notification enum values
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'new_user_registration' AND enumtypid = 'public.notificationtype'::regtype) THEN
        ALTER TYPE public.notificationtype ADD VALUE 'new_user_registration';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'payment_overdue' AND enumtypid = 'public.notificationtype'::regtype) THEN
        ALTER TYPE public.notificationtype ADD VALUE 'payment_overdue';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'loan_approved' AND enumtypid = 'public.notificationtype'::regtype) THEN
        ALTER TYPE public.notificationtype ADD VALUE 'loan_approved';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'loan_rejected' AND enumtypid = 'public.notificationtype'::regtype) THEN
        ALTER TYPE public.notificationtype ADD VALUE 'loan_rejected';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'payment_reminder' AND enumtypid = 'public.notificationtype'::regtype) THEN
        ALTER TYPE public.notificationtype ADD VALUE 'payment_reminder';
    END IF;
END $$;

-- 6. Add any missing notification status values
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'pending' AND enumtypid = 'public.notificationstatus'::regtype) THEN
        ALTER TYPE public.notificationstatus ADD VALUE 'pending';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'sent' AND enumtypid = 'public.notificationstatus'::regtype) THEN
        ALTER TYPE public.notificationstatus ADD VALUE 'sent';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'failed' AND enumtypid = 'public.notificationstatus'::regtype) THEN
        ALTER TYPE public.notificationstatus ADD VALUE 'failed';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'delivered' AND enumtypid = 'public.notificationstatus'::regtype) THEN
        ALTER TYPE public.notificationstatus ADD VALUE 'delivered';
    END IF;
END $$;

-- 7. Ensure default values are consistent
DO $$
BEGIN
    -- Set default values for push_tokens
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'push_tokens'
        AND column_name = 'device_type'
        AND column_default LIKE '%mobile%'
    ) THEN
        ALTER TABLE push_tokens ALTER COLUMN device_type SET DEFAULT 'mobile';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'push_tokens'
        AND column_name = 'is_active'
        AND column_default = 'true'
    ) THEN
        ALTER TABLE push_tokens ALTER COLUMN is_active SET DEFAULT true;
    END IF;

    -- Set default values for notification_preferences
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'notification_preferences'
        AND column_name = 'is_enabled'
        AND column_default = 'true'
    ) THEN
        ALTER TABLE notification_preferences ALTER COLUMN is_enabled SET DEFAULT true;
    END IF;

    -- Set default values for notifications
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'notifications'
        AND column_name = 'status'
        AND column_default LIKE '%pending%'
    ) THEN
        ALTER TABLE notifications ALTER COLUMN status SET DEFAULT 'pending';
    END IF;
END $$;

-- 8. Create unique constraint for push_tokens if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_user_token'
    ) THEN
        ALTER TABLE push_tokens
        ADD CONSTRAINT uq_user_token UNIQUE (user_id, token);
        COMMENT ON CONSTRAINT uq_user_token ON push_tokens IS 'Ensures one token per user';
    END IF;
END $$;

-- 9. Update any data inconsistencies
UPDATE products SET count = 0 WHERE count IS NULL;
UPDATE auto_products SET count = 1 WHERE count IS NULL OR count = 0;

-- 10. Create missing indexes for performance
DO $$
BEGIN
    -- Index for auto_products.car_name
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'ix_auto_products_car_name') THEN
        CREATE INDEX ix_auto_products_car_name ON auto_products(car_name);
    END IF;

    -- Index for push_tokens.token
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'ix_push_tokens_token') THEN
        CREATE INDEX ix_push_tokens_token ON push_tokens(token);
    END IF;
END $$;

-- Commit all changes
COMMIT;

-- Verification queries (run these after migration to verify success)
/*
-- Check auto_products has magazine_id column
SELECT column_name, is_nullable FROM information_schema.columns
WHERE table_name = 'auto_products' AND column_name = 'magazine_id';

-- Check auto_sales magazine_id is nullable
SELECT column_name, is_nullable FROM information_schema.columns
WHERE table_name = 'auto_sales' AND column_name = 'magazine_id';

-- Check auto_loans magazine_id is nullable
SELECT column_name, is_nullable FROM information_schema.columns
WHERE table_name = 'auto_loans' AND column_name = 'magazine_id';

-- Check user_type enum values
SELECT enumlabel FROM pg_enum WHERE enumtypid = 'public.usertype'::regtype ORDER BY enumlabel;

-- Check notification enum values
SELECT enumlabel FROM pg_enum WHERE enumtypid = 'public.notificationtype'::regtype ORDER BY enumlabel;

-- Verify unique constraint exists
SELECT conname FROM pg_constraint WHERE conname = 'uq_user_token';
*/