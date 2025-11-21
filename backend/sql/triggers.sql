-- ============================================
-- Database Triggers for Linkup Application
-- Database: MySQL
-- ============================================
-- 
-- IMPORTANT NOTE:
-- The current backend uses @property methods to calculate counts dynamically.
-- Counter triggers are NOT included here to avoid conflicts.
-- These triggers focus on validation, audit logging, and data integrity.
-- ============================================

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS audit_tweet_changes;
DROP TRIGGER IF EXISTS audit_user_changes;
DROP TRIGGER IF EXISTS prevent_self_follow;
DROP TRIGGER IF EXISTS prevent_self_like;
DROP TRIGGER IF EXISTS log_report_status_change;
DROP TRIGGER IF EXISTS update_tweet_timestamp;

-- ============================================
-- 1. AUDIT TRIGGER - Track Tweet Changes
-- Logs all changes to tweets for audit purposes
-- ============================================
DELIMITER $$

CREATE TRIGGER audit_tweet_changes
AFTER UPDATE ON tweets
FOR EACH ROW
BEGIN
    -- Only log if content or is_deleted changed
    IF OLD.content != NEW.content OR OLD.is_deleted != NEW.is_deleted THEN
        INSERT INTO audit_log (
            table_name,
            record_id,
            action_type,
            old_value,
            new_value,
            changed_by,
            changed_at
        ) VALUES (
            'tweets',
            NEW.id,
            'UPDATE',
            JSON_OBJECT('content', OLD.content, 'is_deleted', OLD.is_deleted),
            JSON_OBJECT('content', NEW.content, 'is_deleted', NEW.is_deleted),
            NEW.author_id,
            NOW()
        );
    END IF;
END$$

DELIMITER ;

-- ============================================
-- 2. AUDIT TRIGGER - Track User Profile Changes
-- Logs changes to user profiles
-- ============================================
DELIMITER $$

CREATE TRIGGER audit_user_changes
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    -- Log if important fields changed
    IF OLD.username != NEW.username 
       OR OLD.email != NEW.email 
       OR OLD.is_verified != NEW.is_verified THEN
        INSERT INTO audit_log (
            table_name,
            record_id,
            action_type,
            old_value,
            new_value,
            changed_by,
            changed_at
        ) VALUES (
            'users',
            NEW.id,
            'UPDATE',
            JSON_OBJECT('username', OLD.username, 'email', OLD.email, 'is_verified', OLD.is_verified),
            JSON_OBJECT('username', NEW.username, 'email', NEW.email, 'is_verified', NEW.is_verified),
            NEW.id,
            NOW()
        );
    END IF;
END$$

DELIMITER ;

-- ============================================
-- 3. VALIDATION TRIGGER - Prevent Self-Follow
-- Ensures users cannot follow themselves
-- ============================================
DELIMITER $$

CREATE TRIGGER prevent_self_follow
BEFORE INSERT ON follows
FOR EACH ROW
BEGIN
    IF NEW.follower_id = NEW.followed_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Users cannot follow themselves';
    END IF;
END$$

DELIMITER ;

-- ============================================
-- 4. VALIDATION TRIGGER - Prevent Self-Like
-- Ensures users cannot like their own tweets
-- ============================================
DELIMITER $$

CREATE TRIGGER prevent_self_like
BEFORE INSERT ON likes
FOR EACH ROW
BEGIN
    DECLARE tweet_author_id BIGINT;
    
    SELECT author_id INTO tweet_author_id
    FROM tweets
    WHERE id = NEW.tweet_id;
    
    IF NEW.user_id = tweet_author_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Users cannot like their own tweets';
    END IF;
END$$

DELIMITER ;

-- ============================================
-- 5. LOGGING TRIGGER - Log Report Status Changes
-- Tracks when report statuses change for audit trail
-- ============================================
DELIMITER $$

CREATE TRIGGER log_report_status_change
AFTER UPDATE ON reports
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO report_status_history (
            report_id,
            old_status,
            new_status,
            changed_at,
            changed_by
        ) VALUES (
            NEW.id,
            OLD.status,
            NEW.status,
            NOW(),
            NEW.resolved_by_id
        );
    END IF;
END$$

DELIMITER ;

-- ============================================
-- 6. TIMESTAMP TRIGGER - Auto-update Tweet Timestamp
-- Updates updated_at when tweet is modified
-- ============================================
DELIMITER $$

CREATE TRIGGER update_tweet_timestamp
BEFORE UPDATE ON tweets
FOR EACH ROW
BEGIN
    SET NEW.updated_at = NOW();
END$$

DELIMITER ;

-- ============================================
-- OPTIONAL: Create Audit Tables
-- Run these if you want to use the audit triggers
-- ============================================

-- Audit log table for tracking changes
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id BIGINT NOT NULL,
    action_type VARCHAR(20) NOT NULL,
    old_value JSON,
    new_value JSON,
    changed_by BIGINT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_table_record (table_name, record_id),
    INDEX idx_changed_at (changed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Report status history table
CREATE TABLE IF NOT EXISTS report_status_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    report_id BIGINT NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by BIGINT,
    INDEX idx_report (report_id),
    INDEX idx_changed_at (changed_at),
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- VERIFICATION QUERIES
-- Run these to verify triggers are created
-- ============================================

-- Show all triggers
-- SHOW TRIGGERS;

-- Show triggers for specific table
-- SHOW TRIGGERS WHERE `Table` = 'tweets';

-- Show trigger details
-- SHOW CREATE TRIGGER prevent_self_follow;

-- ============================================
-- TESTING QUERIES
-- ============================================

-- Test prevent_self_follow trigger (should fail)
-- INSERT INTO follows (follower_id, followed_id, created_at) VALUES (1, 1, NOW());

-- Test prevent_self_like trigger (should fail if user 1 owns tweet 1)
-- INSERT INTO likes (user_id, tweet_id, created_at) VALUES (1, 1, NOW());

-- View audit log
-- SELECT * FROM audit_log ORDER BY changed_at DESC LIMIT 10;

-- View report status history
-- SELECT * FROM report_status_history ORDER BY changed_at DESC LIMIT 10;
