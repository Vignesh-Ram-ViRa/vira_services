#!/bin/bash

# Render Database Backup Script
# Run this before your database expires (day 25-29)

# Set your database URL (get from Render dashboard)
DATABASE_URL="your_database_url_here"

# Create backup with timestamp
BACKUP_FILE="vira_backup_$(date +%Y%m%d_%H%M%S).sql"

echo "🗄️ Creating backup of Vira database..."
pg_dump "$DATABASE_URL" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully: $BACKUP_FILE"
    echo "📁 File size: $(ls -lh $BACKUP_FILE | awk '{print $5}')"
    echo ""
    echo "📋 Next steps:"
    echo "1. Create new free PostgreSQL database in Render"
    echo "2. Get new DATABASE_URL from Render dashboard"
    echo "3. Run: psql \$NEW_DATABASE_URL < $BACKUP_FILE"
    echo "4. Update environment variables in Render"
else
    echo "❌ Backup failed!"
    exit 1
fi 