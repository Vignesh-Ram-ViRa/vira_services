# Render Monthly Database Maintenance Guide

> **Simple guide to handle the 30-day PostgreSQL database renewal on Render free tier**

## 📅 **Timeline Overview**

```
Day 1:   🟢 Database created
Day 25:  📧 Render sends warning email
Day 27:  ⚠️  Start backup process (recommended)
Day 30:  🔴 Database expires
Day 44:  💀 Database permanently deleted (if not upgraded)
```

## 🔄 **Monthly Renewal Process (30 minutes)**

### **Step 1: Backup Current Database (Day 25-29)**

1. **Get Database URL from Render**
   - Go to Render dashboard
   - Click on **"vira-postgres"** service
   - Copy the **"External Database URL"**

2. **Run Backup Script**
   ```bash
   # Edit the script with your database URL
   nano scripts/backup-database.sh
   
   # Update this line with your actual URL:
   DATABASE_URL="postgresql://username:password@host:port/database"
   
   # Run backup
   chmod +x scripts/backup-database.sh
   ./scripts/backup-database.sh
   ```

3. **Verify Backup**
   ```bash
   # Check backup file was created
   ls -la vira_backup_*.sql
   
   # Should show file size (typically 10-50KB for small project)
   ```

### **Step 2: Create New Database**

1. **In Render Dashboard**
   - Click **"New"** → **"PostgreSQL"**
   - Choose **"Free"** plan
   - Name: `vira-postgres-new` (or similar)
   - Wait for database to be created (~2 minutes)

2. **Get New Database URL**
   - Click on the new database service
   - Copy the **"External Database URL"**

### **Step 3: Restore Data to New Database**

1. **Run Restore Script**
   ```bash
   # Edit restore script with new database URL
   nano scripts/restore-database.sh
   
   # Update this line:
   NEW_DATABASE_URL="postgresql://new_username:new_password@new_host:port/database"
   
   # Run restore
   chmod +x scripts/restore-database.sh
   ./scripts/restore-database.sh vira_backup_20241201_120000.sql
   ```

### **Step 4: Update Application Configuration**

1. **Update Environment Variables in Render**
   - Go to **"vira-services"** web service
   - Click **"Environment"** tab
   - Update database connection variables:
     ```
     DATABASE_URL=postgresql://new_connection_string
     DATABASE_USERNAME=new_username  
     DATABASE_PASSWORD=new_password
     ```

2. **Save and Redeploy**
   - Click **"Save Changes"**
   - Wait for automatic redeploy (~3-5 minutes)

### **Step 5: Verify Everything Works**

1. **Test Health Check**
   ```bash
   curl https://your-app.onrender.com/actuator/health
   # Should return: {"status":"UP"}
   ```

2. **Test Admin Login**
   ```bash
   curl -X POST https://your-app.onrender.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"SecureAdmin123!"}'
   ```

3. **Check Data Integrity**
   - Visit Swagger UI: `https://your-app.onrender.com/swagger-ui/index.html`
   - Test portfolio endpoints
   - Verify user accounts still exist

### **Step 6: Cleanup**

1. **Delete Old Database**
   - Go to old **"vira-postgres"** service
   - Click **"Settings"** → **"Delete Service"**

2. **Rename New Database (Optional)**
   - Rename `vira-postgres-new` to `vira-postgres`

---

## 📧 **Reminder System**

### **Set Calendar Reminders**
- **Day 20**: "Render DB expires in 10 days - prepare backup"
- **Day 25**: "Render DB expires in 5 days - START BACKUP NOW"
- **Day 28**: "Render DB expires in 2 days - URGENT: Complete migration"

### **Email Notifications**
- Render automatically sends warnings
- Add reminder to your email calendar

---

## 🚨 **Emergency Recovery**

**If you forgot and database expired:**

1. **Don't Panic** - You have 14 days grace period
2. **Contact Render Support** - They might restore access temporarily
3. **Upgrade to Paid** - $15/month for permanent storage
4. **Start Fresh** - If all else fails, reinitialize with default data

---

## 💡 **Pro Tips**

### **Minimize Downtime**
- Do the migration during low-traffic hours
- Have backup ready 3-4 days early
- Test the restore process in advance

### **Automate with GitHub Actions**
```yaml
# .github/workflows/monthly-backup.yml
name: Monthly Database Backup
on:
  schedule:
    - cron: "0 0 25 * *"  # Run on 25th of each month
jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Backup Database
        run: |
          pg_dump ${{ secrets.DATABASE_URL }} > monthly_backup.sql
      - name: Upload Backup
        uses: actions/upload-artifact@v3
        with:
          name: database-backup
          path: monthly_backup.sql
```

### **Data Optimization**
- Regularly clean up old data
- Keep within 1GB limit
- Monitor database size:
  ```sql
  SELECT pg_size_pretty(pg_database_size('vira_db'));
  ```

---

## ⚖️ **When to Upgrade to Paid**

**Consider upgrading Database ($15/month) when:**
- ✅ Monthly migration becomes annoying
- ✅ You have important user data
- ✅ Database size approaches 1GB
- ✅ You want automatic backups

**Consider upgrading Web Service ($7/month) when:**
- ✅ Users complain about cold start delays
- ✅ You need 24/7 availability
- ✅ You're using it professionally

---

## 📋 **Monthly Checklist**

```
□ Day 25: Receive Render warning email
□ Day 27: Run backup script
□ Day 27: Verify backup file created
□ Day 28: Create new PostgreSQL database
□ Day 28: Run restore script
□ Day 28: Update environment variables
□ Day 29: Test application functionality
□ Day 29: Delete old database
□ Day 30: Confirm everything works
```

**Total time investment: ~30 minutes per month**

---

## 🎯 **Bottom Line**

**For personal projects with <5 users, the monthly renewal is totally manageable!**

- ✅ **30 minutes of work per month**
- ✅ **$0 cost**
- ✅ **Full PostgreSQL features**
- ✅ **Professional deployment**

**When you grow or get tired of monthly maintenance, upgrade to paid tier.** 