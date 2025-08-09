#!/bin/bash

# Render Database Restore Script
# Run this after creating a new free PostgreSQL database

# Set your new database URL (get from new Render database)
NEW_DATABASE_URL="your_new_database_url_here"

# Set backup file to restore
BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ Please provide backup file as argument"
    echo "Usage: ./restore-database.sh vira_backup_20241201_120000.sql"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "🔄 Restoring database from: $BACKUP_FILE"
echo "📍 Target database: $NEW_DATABASE_URL"
echo ""

# Restore the backup
psql "$NEW_DATABASE_URL" < "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Database restored successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Update DATABASE_URL in Render environment variables"
    echo "2. Test your application: curl https://your-app.onrender.com/actuator/health"
    echo "3. Verify admin login works"
    echo "4. Delete old database in Render dashboard"
else
    echo "❌ Restore failed!"
    exit 1
fi 