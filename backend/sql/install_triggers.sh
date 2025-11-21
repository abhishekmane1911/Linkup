#!/bin/bash

# ============================================
# Install Database Triggers Script
# ============================================

echo "=================================="
echo "Linkup Database Triggers Installer"
echo "=================================="
echo ""

# Load environment variables if .env exists
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

# Database configuration
DB_NAME=${DB_NAME:-linkup_db}
DB_USER=${DB_USER:-root}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-3306}

echo "Database Configuration:"
echo "  Host: $DB_HOST:$DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Prompt for password
read -sp "Enter MySQL password for $DB_USER: " DB_PASSWORD
echo ""
echo ""

# Check if MySQL is accessible
echo "Testing database connection..."
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" -e "USE $DB_NAME;" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Error: Cannot connect to database"
    echo "Please check your credentials and try again"
    exit 1
fi

echo "✅ Database connection successful"
echo ""

# Show current triggers
echo "Current triggers in database:"
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TRIGGERS;" 2>/dev/null
echo ""

# Confirm installation
read -p "Do you want to install/update triggers? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 0
fi

echo ""
echo "Installing triggers..."
echo ""

# Execute the triggers SQL file
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < triggers.sql 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Triggers installed successfully!"
    echo ""
    echo "Installed triggers:"
    mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TRIGGERS;" 2>/dev/null
    echo ""
    echo "📝 Audit tables created:"
    echo "  - audit_log"
    echo "  - report_status_history"
    echo ""
    echo "Next steps:"
    echo "  1. Test the triggers (see TRIGGER_IMPLEMENTATION_GUIDE.md)"
    echo "  2. Monitor the audit_log table"
    echo "  3. Set up periodic cleanup of old audit data"
else
    echo ""
    echo "❌ Error installing triggers"
    echo "Check the error messages above"
    exit 1
fi
