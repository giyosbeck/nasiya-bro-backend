-- Fix push tokens table to allow multiple users per device
-- This allows families/couples to share one phone with different accounts

-- Step 1: Drop the existing unique constraint on token
DROP INDEX IF EXISTS ix_push_tokens_token;
ALTER TABLE push_tokens DROP CONSTRAINT IF EXISTS push_tokens_token_key;

-- Step 2: Add composite unique constraint (user_id, token)
-- This allows same token for different users (shared device)
-- but prevents duplicate tokens for same user
ALTER TABLE push_tokens 
ADD CONSTRAINT uq_user_token UNIQUE (user_id, token);

-- Step 3: Recreate regular index on token for performance
CREATE INDEX ix_push_tokens_token ON push_tokens (token);

-- Step 4: Clean up any existing duplicates (keep the most recent)
WITH ranked_tokens AS (
    SELECT id, 
           ROW_NUMBER() OVER (PARTITION BY user_id, token ORDER BY updated_at DESC, created_at DESC) as rn
    FROM push_tokens
)
DELETE FROM push_tokens 
WHERE id IN (
    SELECT id FROM ranked_tokens WHERE rn > 1
);