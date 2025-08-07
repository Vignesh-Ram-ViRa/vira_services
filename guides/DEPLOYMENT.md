# Railway Deployment Guide - Step by Step

## 🚀 **Complete Railway Deployment Tutorial**

This guide will walk you through deploying your Vira Services Spring Boot backend to Railway's free hosting platform. Written for absolute beginners - every step explained!

## 📋 **Prerequisites Checklist**

Before starting deployment:
- ✅ Spring Boot application running locally
- ✅ GitHub account (free)
- ✅ Railway account (free - we'll create this)
- ✅ Your project code pushed to GitHub

## 🎯 **Step 1: Prepare Your Project for Deployment**

### 1.1 Create Production Configuration
Ensure you have `application-prod.yml`:

```yaml
# src/main/resources/application-prod.yml
server:
  port: ${PORT:8080}

spring:
  datasource:
    url: ${DATABASE_URL}
    username: ${DATABASE_USERNAME}
    password: ${DATABASE_PASSWORD}
    driver-class-name: org.postgresql.Driver
  
  jpa:
    hibernate:
      ddl-auto: validate
    database-platform: org.hibernate.dialect.PostgreSQLDialect
    show-sql: false

  flyway:
    enabled: true
    baseline-on-migrate: true

logging:
  level:
    root: INFO
    com.vira: INFO

# JWT Configuration
app:
  jwt:
    secret: ${JWT_SECRET}
    expiration: 86400000  # 24 hours
    refresh-expiration: 604800000  # 7 days
```

### 1.2 Update Main Configuration
In `application.yml`, set default profile:

```yaml
spring:
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}
```

### 1.3 Create Procfile (Optional but Recommended)
Create `Procfile` in project root:

```
web: java -Dspring.profiles.active=prod -Dserver.port=$PORT -jar target/vira-services-*.jar
```

## 🐙 **Step 2: Push to GitHub**

### 2.1 Initialize Git Repository (if not done)
```bash
# In your project directory
git init
git add .
git commit -m "Initial commit: Vira Services backend"
```

### 2.2 Create GitHub Repository
1. Go to https://github.com
2. Click **"+"** → **"New repository"**
3. **Repository name**: `vira-services`
4. **Description**: `Multi-service Spring Boot backend for personal projects`
5. **Visibility**: Public (for free deployment)
6. **DO NOT** initialize with README, .gitignore, or license
7. Click **"Create repository"**

### 2.3 Connect Local to GitHub
```bash
# Add remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/vira-services.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🚂 **Step 3: Create Railway Account & Deploy**

### 3.1 Sign Up for Railway
1. Go to https://railway.app
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway to access your GitHub account
4. Complete account setup

### 3.2 Create New Project
1. **Railway Dashboard** → Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. **Choose Repository**: Find and select `vira-services`
4. Click **"Deploy Now"**

### 3.3 Add PostgreSQL Database
1. In your Railway project dashboard
2. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
3. Wait for PostgreSQL to provision (1-2 minutes)
4. Your database is ready!

## ⚙️ **Step 4: Configure Environment Variables**

### 4.1 Access Your Application Settings
1. In Railway project dashboard
2. Click on your **application service** (not the database)
3. Go to **"Variables"** tab

### 4.2 Add Required Environment Variables
Click **"+ New Variable"** for each:

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `SPRING_PROFILES_ACTIVE` | `prod` | Activates production profile |
| `PORT` | `8080` | Railway sets this automatically |
| `JWT_SECRET` | `your-super-secret-jwt-key-here-make-it-long-and-random` | Create a random 64+ character string |

### 4.3 Database Variables (Auto-configured)
Railway automatically provides these from your PostgreSQL service:
- `DATABASE_URL` ✅ (Auto-configured)
- `DATABASE_USERNAME` ✅ (Auto-configured)  
- `DATABASE_PASSWORD` ✅ (Auto-configured)

### 4.4 Connect Database to Application
1. Go to your PostgreSQL service
2. Click **"Connect"** tab
3. Click **"Connect to [your-app-name]"**
4. This automatically shares database credentials

## 🔄 **Step 5: Deploy and Monitor**

### 5.1 Trigger Deployment
1. **Method 1 (Automatic)**: Push changes to GitHub
   ```bash
   git add .
   git commit -m "Add production configuration"
   git push origin main
   ```

2. **Method 2 (Manual)**: In Railway dashboard
   - Go to **"Deployments"** tab
   - Click **"Deploy Latest"**

### 5.2 Monitor Deployment
1. **Watch Build Logs**:
   - Railway dashboard → **"Deployments"** tab
   - Click on latest deployment
   - Watch build progress in real-time

2. **Check for Success**:
   ```
   ✅ BUILD SUCCESSFUL
   ✅ Spring Boot application started
   ✅ Database connection established
   ✅ Application available at: https://your-app-name.railway.app
   ```

### 5.3 Common Build Issues & Solutions

**Issue: Maven Build Timeout**
```yaml
# Add to your pom.xml
<properties>
    <maven.build.timeout>600</maven.build.timeout>
</properties>
```

**Issue: Out of Memory During Build**
```yaml
# Add Railway build configuration
# Create nixpacks.toml in project root:
[build]
cmd = "./mvnw clean package -DskipTests -Dspring-boot.build-image.env.BP_JVM_VERSION=17"
```

**Issue: Database Connection Failed**
- Verify database service is running
- Check if DATABASE_URL variable is set
- Ensure application and database are connected

## ✅ **Step 6: Test Your Deployed Application**

### 6.1 Get Your Application URL
1. Railway dashboard → Your application service
2. Click **"Settings"** tab → **"Domains"**
3. Your URL: `https://your-app-name.railway.app`

### 6.2 Test Health Endpoint
```bash
# Replace with your actual URL
curl https://your-app-name.railway.app/actuator/health

# Expected response:
{"status":"UP"}
```

### 6.3 Test API Documentation
Visit: `https://your-app-name.railway.app/swagger-ui/index.html`

### 6.4 Test Authentication Flow
```bash
# 1. Register user
curl -X POST https://your-app-name.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# 2. Login
curl -X POST https://your-app-name.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# 3. Use JWT token for authenticated requests
```

## 📊 **Step 7: Monitor and Maintain**

### 7.1 Check Application Metrics
Railway Dashboard → Your app → **"Metrics"** tab:
- CPU usage
- Memory usage
- Request count
- Response times

### 7.2 View Application Logs
Railway Dashboard → Your app → **"Deploy Logs"** tab:
- Real-time application logs
- Error tracking
- Performance monitoring

### 7.3 Database Management
Railway Dashboard → PostgreSQL service → **"Data"** tab:
- View tables and data
- Execute SQL queries
- Monitor database performance

## 🔄 **Step 8: Continuous Deployment Setup**

### 8.1 Automatic Deployments
Railway automatically deploys when you push to your main branch:

```bash
# Make changes to your code
git add .
git commit -m "Add new feature"
git push origin main

# Railway automatically:
# 1. Detects the push
# 2. Starts new build
# 3. Runs tests
# 4. Deploys if successful
# 5. Updates your live application
```

### 8.2 Environment-Specific Branches
```bash
# Create staging branch for testing
git checkout -b staging
git push origin staging

# In Railway, create new service for staging environment
# Use different database and environment variables
```

## 💰 **Step 9: Understanding Railway Free Tier**

### Free Tier Limits:
- ✅ **500 hours/month** execution time
- ✅ **1GB PostgreSQL** storage
- ✅ **8GB RAM** per service
- ✅ **Custom domains** with hobby plan
- ✅ **Unlimited** deployments

### Tips to Stay Within Limits:
- **Sleep inactive applications** (Railway does this automatically)
- **Optimize queries** to reduce database load
- **Monitor usage** in Railway dashboard
- **Use caching** to reduce computational needs

## 🚨 **Troubleshooting Common Issues**

### Application Won't Start
**Check logs for:**
```
# Database connection issues
ERROR: Connection to database failed

# Solution: Verify DATABASE_URL in variables

# Port binding issues  
ERROR: Port already in use

# Solution: Remove hardcoded ports, use ${PORT:8080}

# Missing environment variables
ERROR: JWT secret not found

# Solution: Add JWT_SECRET variable
```

### Deployment Fails
```bash
# Build timeout
BUILD FAILED: timeout after 10m

# Solution: Optimize dependencies, use Maven daemon

# Out of memory
Error: Java heap space

# Solution: Add JVM options to Procfile
```

### Database Issues
```bash
# Migration fails
Flyway migration failed

# Solution: Check migration scripts, reset if needed

# Connection pool exhausted
HikariPool connection timeout

# Solution: Optimize connection pool settings
```

## 🎯 **Step 10: Production Readiness Checklist**

Before going live:
- ✅ **Environment variables** properly set
- ✅ **Database migrations** run successfully
- ✅ **Authentication** working correctly
- ✅ **CORS** configured for your frontend domains
- ✅ **Error handling** comprehensive
- ✅ **Logging** properly configured
- ✅ **Health checks** responding
- ✅ **API documentation** accessible
- ✅ **SSL/HTTPS** working (Railway provides this)

## 🔗 **Step 11: Connect to Frontend**

### Update Frontend Configuration
```javascript
// In your React app
const API_BASE_URL = 'https://your-app-name.railway.app';

// Example API call
const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'testuser',
    password: 'password123'
  })
});
```

### CORS Configuration
Your Spring Boot app should already be configured for CORS:

```java
@CrossOrigin(origins = {
    "http://localhost:3000",           // Local development
    "https://your-frontend-domain.com" // Production frontend
})
```

---

## 🎉 **Congratulations!**

Your Spring Boot backend is now:
- ✅ **Deployed** on Railway's free tier
- ✅ **Connected** to PostgreSQL database
- ✅ **Accessible** via HTTPS
- ✅ **Ready** for frontend integration
- ✅ **Automatically deploying** on code changes

**Your API is live at:** `https://your-app-name.railway.app`

**Next Steps:**
1. Connect your React frontend
2. Add more services to your backend
3. Monitor performance and usage
4. Scale as your projects grow

**Need help?** Check Railway's documentation or ask in their Discord community!

---

**🎯 Quick Reference URLs:**
- **Railway Dashboard**: https://railway.app/dashboard
- **API Documentation**: https://your-app-name.railway.app/swagger-ui/index.html
- **Health Check**: https://your-app-name.railway.app/actuator/health 