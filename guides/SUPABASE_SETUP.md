# Supabase Database Setup Guide

> **Complete guide to set up permanent, maintenance-free PostgreSQL database with Supabase**

## 🎯 **Why Supabase for Database?**

✅ **Permanent Storage** - Never expires (unlike Render's 30-day limit)  
✅ **Zero Maintenance** - No monthly renewals required  
✅ **500MB Free Storage** - Perfect for personal projects  
✅ **Auto-Resume** - Wakes up automatically when accessed  
✅ **SSL Security** - Built-in secure connections  
✅ **50,000 MAU** - More than enough for your use case  

---

## 🚀 **Step-by-Step Supabase Setup**

### **Step 1: Create Supabase Account & Project**

1. **Go to Supabase**
   - Visit [supabase.com](https://supabase.com)
   - Click **"Start your project"**
   - Sign up with GitHub (recommended) or email

2. **Create New Project**
   - Click **"New Project"**
   - Choose your organization (default is fine)
   - Set project details:
     ```
     Name: vira-services
     Database Password: [Generate secure password - SAVE THIS!]
     Region: Choose closest to you (e.g., US East, Europe West)
     Pricing Plan: Free
     ```
   - Click **"Create new project"**

3. **Wait for Setup**
   - Project creation takes ~2 minutes
   - You'll see a progress indicator
   - Don't close the tab during setup

---

### **Step 2: Get Database Connection Details**

1. **Navigate to Database Settings**
   - In your Supabase dashboard, click **"Settings"** (gear icon)
   - Click **"Database"** from the left menu

2. **Copy Connection Information**
   - Find **"Connection parameters"** section
   - Copy these values:
     ```
     Host: db.your-project-ref.supabase.co
     Database name: postgres
     Port: 5432
     User: postgres
     Password: [your-database-password]
     ```

3. **Get Connection Pool URL (Recommended)**
   - Scroll down to **"Connection pooling"** section
   - Copy the **"Connection string"** that looks like:
     ```
     postgresql://postgres.your-project-ref:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
     ```
   - **Use this URL for better performance!**

---

### **Step 3: Configure Database Access**

1. **Enable Connection Pooling (Important)**
   - In Supabase dashboard, go to **"Settings"** → **"Database"**
   - Scroll to **"Connection pooling"**
   - Ensure it's **enabled** (should be by default)
   - Mode should be **"Transaction"** (recommended for Spring Boot)

2. **Verify SSL Settings**
   - In same Database settings page
   - Ensure **"SSL enforcement"** is **enabled**
   - This is required for production connections

---

### **Step 4: Initialize Database Schema**

Your Spring Boot app will automatically create the database schema when it first connects, thanks to Flyway migrations.

**Database Tables That Will Be Created:**
- `auth_users` - User accounts and authentication
- `auth_roles` - User roles (USER, ADMIN)
- `auth_refresh_tokens` - JWT refresh tokens
- `portfolio_projects` - Portfolio project data

---

## 🔗 **Integration with Your Spring Boot App**

### **Environment Variables Needed:**

After getting your Supabase connection details, you'll set these in Render:

```bash
# Use the connection pool URL for better performance
SUPABASE_DATABASE_URL=postgresql://postgres.your-project-ref:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

# Or use individual parameters (alternative method)
SUPABASE_DATABASE_USERNAME=postgres.your-project-ref
SUPABASE_DATABASE_PASSWORD=your-database-password
```

### **SSL Connection (Required)**

Supabase requires SSL connections. Your Spring Boot app is already configured with:
```yaml
spring:
  datasource:
    hikari:
      ssl-mode: require
```

---

## 🗄️ **Database Management**

### **Access Your Database**

1. **Supabase Dashboard (Easiest)**
   - Go to **"Table Editor"** in Supabase dashboard
   - View and edit data directly in the browser
   - Perfect for quick checks and admin tasks

2. **SQL Editor**
   - Go to **"SQL Editor"** in Supabase dashboard
   - Run custom SQL queries
   - Great for data analysis and reports

3. **External Tools (Optional)**
   - Use pgAdmin, DBeaver, or any PostgreSQL client
   - Connect using the connection parameters from Step 2

### **Monitoring Usage**

1. **Database Size**
   - Go to **"Settings"** → **"Usage"**
   - Monitor your **Database size** (500MB limit)
   - Current usage shows in real-time

2. **Bandwidth Usage**
   - Same usage page shows **Bandwidth** (5GB/month limit)
   - Your API calls count toward this limit

---

## ⚡ **Performance & Limits**

### **Free Tier Specifications:**
- **Database Size**: 500MB
- **Bandwidth**: 5GB/month  
- **Monthly Active Users**: 50,000
- **Connection Pooling**: Included
- **SSL**: Required and included
- **Backup**: Manual export only

### **For Your Use Case (5 users max):**
- **Estimated Usage**: ~50MB database size
- **Bandwidth**: ~500MB/month
- **Well within limits**: 10x headroom for growth

---

## 🔄 **Project Lifecycle**

### **Inactivity Pausing:**
- **After 1 week** of no connections, project pauses
- **Auto-resumes** on first connection (30-60 seconds)
- **No data loss** - just a brief wake-up delay
- **No manual intervention** required

### **Permanent Storage:**
- ✅ **Never expires** (unlike Render's 30-day limit)
- ✅ **No monthly renewals** needed
- ✅ **Data persists** through pausing
- ✅ **True "set it and forget it"** solution

---

## 🚨 **Backup Strategy**

### **Manual Backup (Recommended)**
```sql
-- Export data via SQL Editor in Supabase dashboard
-- Or use pg_dump with connection string:
pg_dump "postgresql://postgres.your-project-ref:[password]@aws-0-[region].pooler.supabase.com:6543/postgres" > backup.sql
```

### **When to Backup:**
- Before major app updates
- Monthly (good practice)
- Before approaching 500MB limit

---

## 🔐 **Security Best Practices**

### **Database Password:**
- ✅ **Generated by Supabase** (highly secure)
- ✅ **Never commit to code** (use environment variables)
- ✅ **Rotate periodically** (can change in Supabase settings)

### **Connection Security:**
- ✅ **SSL enforced** by default
- ✅ **Connection pooling** for efficiency
- ✅ **IP allowlisting** available if needed

### **Access Control:**
- ✅ **Database level** security via Supabase
- ✅ **Application level** security via Spring Security
- ✅ **API level** security via JWT tokens

---

## 🎯 **What You Get**

### **Immediate Benefits:**
- 🆓 **$0 cost** - completely free
- 🔄 **Zero maintenance** - no monthly tasks
- 🛡️ **Enterprise security** - SSL, backups, monitoring
- ⚡ **High performance** - connection pooling, global CDN
- 📊 **Admin dashboard** - easy data management

### **Long-term Benefits:**
- 🔒 **Permanent storage** - never expires
- 📈 **Room to grow** - upgrade path available
- 🚀 **Professional grade** - production-ready from day one
- 🛠️ **Developer friendly** - SQL editor, API access

---

## 📋 **Quick Reference**

### **Essential URLs:**
- **Dashboard**: https://supabase.com/dashboard
- **Project URL**: https://app.supabase.com/project/[your-project-ref]
- **Database Settings**: Settings → Database
- **Usage Monitoring**: Settings → Usage

### **Connection Template:**
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

### **Environment Variables:**
```bash
SUPABASE_DATABASE_URL=postgresql://postgres.abc123:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres
SUPABASE_DATABASE_USERNAME=postgres.abc123
SUPABASE_DATABASE_PASSWORD=your-secure-password
```

---

## 🎉 **Next Steps**

After completing Supabase setup:

1. ✅ **Copy your connection details**
2. ✅ **Update environment variables in Render**
3. ✅ **Deploy your Spring Boot app**
4. ✅ **Test database connectivity**
5. ✅ **Verify automatic schema creation**
6. ✅ **Enjoy maintenance-free operation!**

**Your database is now permanently configured and will never require monthly maintenance!** 🚀 