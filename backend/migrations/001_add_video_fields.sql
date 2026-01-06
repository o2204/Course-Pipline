-- Migration: Add url_1, url_2 fields and rename script_clean to motion_prompt in videos table
-- Date: 2026-01-06
-- Description: Updates videos table schema to support frontend API contract

-- Step 1: Add new columns for storing image URLs
ALTER TABLE videos ADD COLUMN IF NOT EXISTS url_1 TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS url_2 TEXT;

-- Step 2: Add new motion_prompt column
ALTER TABLE videos ADD COLUMN IF NOT EXISTS motion_prompt TEXT;

-- Step 3: Migrate data from script_clean to motion_prompt (if script_clean exists)
UPDATE videos SET motion_prompt = script_clean WHERE script_clean IS NOT NULL AND motion_prompt IS NULL;

-- Step 4: Drop old script_clean column (optional - comment out if you want to keep it for rollback)
-- ALTER TABLE videos DROP COLUMN IF EXISTS script_clean;

-- Verify changes
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'videos' 
-- ORDER BY ordinal_position;
