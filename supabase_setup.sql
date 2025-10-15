-- Vish AI - Supabase Database Setup
-- Run this in your Supabase SQL Editor
-- https://supabase.com/dashboard/project/lyebtceryednzafhyunq/sql

-- ============================================
-- 1. Create Logs Table
-- ============================================
CREATE TABLE IF NOT EXISTS vish_ai_logs (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT,
    prompt TEXT,
    response TEXT,
    model_type TEXT CHECK (model_type IN ('chat', 'summarization', 'sentiment')),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 2. Create Indexes for Performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_vish_ai_logs_user 
    ON vish_ai_logs(user_email);

CREATE INDEX IF NOT EXISTS idx_vish_ai_logs_timestamp 
    ON vish_ai_logs(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_vish_ai_logs_model_type 
    ON vish_ai_logs(model_type);

-- ============================================
-- 3. Enable Row Level Security (RLS)
-- ============================================
ALTER TABLE vish_ai_logs ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 4. Create RLS Policies
-- ============================================

-- Policy: Users can view their own logs
DROP POLICY IF EXISTS "Users can view own logs" ON vish_ai_logs;
CREATE POLICY "Users can view own logs"
    ON vish_ai_logs 
    FOR SELECT
    USING (auth.jwt() ->> 'email' = user_email);

-- Policy: Service role can insert logs (for anonymous + authenticated)
DROP POLICY IF EXISTS "Service role can insert logs" ON vish_ai_logs;
CREATE POLICY "Service role can insert logs"
    ON vish_ai_logs 
    FOR INSERT
    WITH CHECK (true);

-- Policy: Users can view anonymous logs (optional - remove if you want privacy)
DROP POLICY IF EXISTS "Anyone can view anonymous logs" ON vish_ai_logs;
CREATE POLICY "Anyone can view anonymous logs"
    ON vish_ai_logs 
    FOR SELECT
    USING (user_email = 'anonymous');

-- ============================================
-- 5. Create Analytics View (Optional)
-- ============================================
CREATE OR REPLACE VIEW vish_ai_analytics AS
SELECT 
    DATE_TRUNC('day', timestamp) as date,
    model_type,
    COUNT(*) as interaction_count,
    COUNT(DISTINCT user_email) as unique_users,
    AVG(LENGTH(prompt)) as avg_prompt_length,
    AVG(LENGTH(response)) as avg_response_length
FROM vish_ai_logs
GROUP BY DATE_TRUNC('day', timestamp), model_type
ORDER BY date DESC, model_type;

-- ============================================
-- 6. Grant Permissions
-- ============================================
-- Allow authenticated users to read analytics
GRANT SELECT ON vish_ai_analytics TO authenticated;

-- Allow service role full access
GRANT ALL ON vish_ai_logs TO service_role;

-- ============================================
-- 7. Create Function for User Statistics
-- ============================================
CREATE OR REPLACE FUNCTION get_user_stats(user_email_param TEXT)
RETURNS TABLE (
    total_interactions BIGINT,
    chat_count BIGINT,
    summarization_count BIGINT,
    sentiment_count BIGINT,
    first_interaction TIMESTAMPTZ,
    last_interaction TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_interactions,
        COUNT(*) FILTER (WHERE model_type = 'chat') as chat_count,
        COUNT(*) FILTER (WHERE model_type = 'summarization') as summarization_count,
        COUNT(*) FILTER (WHERE model_type = 'sentiment') as sentiment_count,
        MIN(timestamp) as first_interaction,
        MAX(timestamp) as last_interaction
    FROM vish_ai_logs
    WHERE user_email = user_email_param;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================
-- 8. Create Trigger for Updated At (Optional)
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add updated_at column if you want to track modifications
-- ALTER TABLE vish_ai_logs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- CREATE TRIGGER update_vish_ai_logs_updated_at 
--     BEFORE UPDATE ON vish_ai_logs 
--     FOR EACH ROW 
--     EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 9. Sample Queries for Testing
-- ============================================

-- View all logs (as service role or authenticated user viewing their own)
-- SELECT * FROM vish_ai_logs ORDER BY timestamp DESC LIMIT 10;

-- Get analytics for last 7 days
-- SELECT * FROM vish_ai_analytics 
-- WHERE date > NOW() - INTERVAL '7 days'
-- ORDER BY date DESC;

-- Get user statistics
-- SELECT * FROM get_user_stats('user@example.com');

-- Count interactions by model type
-- SELECT model_type, COUNT(*) as count
-- FROM vish_ai_logs
-- GROUP BY model_type;

-- ============================================
-- 10. Cleanup Old Logs (Optional - for data retention)
-- ============================================

-- Create function to delete logs older than 90 days
CREATE OR REPLACE FUNCTION cleanup_old_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM vish_ai_logs
    WHERE timestamp < NOW() - INTERVAL '90 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- To run cleanup manually:
-- SELECT cleanup_old_logs();

-- To schedule automatic cleanup, you can use pg_cron extension:
-- SELECT cron.schedule('cleanup-vish-ai-logs', '0 0 * * 0', 'SELECT cleanup_old_logs()');

-- ============================================
-- Setup Complete! ✅
-- ============================================

-- Verify the setup:
SELECT 
    'Tables' as type, 
    COUNT(*) as count 
FROM information_schema.tables 
WHERE table_name = 'vish_ai_logs'
UNION ALL
SELECT 
    'Policies' as type, 
    COUNT(*) as count 
FROM pg_policies 
WHERE tablename = 'vish_ai_logs';
