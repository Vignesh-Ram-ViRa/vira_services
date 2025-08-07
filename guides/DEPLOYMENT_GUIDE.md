# 🚀 Deployment Guide - Vira Services Backend

This guide covers deploying your Vira Services backend to various platforms, with detailed steps for Railway and alternatives.

## 🎯 Deployment Options Overview

| Platform | Difficulty | Cost | Database | Best For |
|----------|------------|------|----------|-----------|
| **Railway** | Easy | Free tier | Included | Quick deployment |
| **Heroku** | Easy | Free tier limited | Add-on required | Beginners |
| **Render** | Easy | Free tier | Included | Alternative to Heroku |
| **DigitalOcean** | Medium | $5/month | Separate setup | Production |
| **AWS/GCP** | Hard | Pay-per-use | Separate setup | Enterprise |

---

## 🚂 Railway Deployment (Recommended)

Railway is perfect for beginners - it's simple, has a generous free tier, and includes PostgreSQL database.

### Step 1: Prepare Your Project

#### 1.1 Create Production Configuration
The project already has `application-prod.yml`, but let's verify it:

```yaml
# src/main/resources/application-prod.yml
spring:
  datasource:
    url: ${DATABASE_URL}
    username: ${DATABASE_USERNAME}
    password: ${DATABASE_PASSWORD}
    driver-class-name: org.postgresql.Driver
  
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: false
    
  flyway:
    enabled: true
    locations: classpath:db/migration
```

#### 1.2 Create Procfile
Create a `Procfile` in your project root:
```
web: java -jar target/vira-services-0.0.1-SNAPSHOT.jar --spring.profiles.active=prod
```

**Note**: The application includes automatic data initialization (`DataInitializer`) that creates default roles on startup.

#### 1.3 Verify pom.xml has correct configuration
Make sure your `pom.xml` has the build plugin:
```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

### Step 2: Set Up Railway Account

1. Go to [Railway.app](https://railway.app)
2. Click "Sign up" and use GitHub account (recommended)
3. Verify your email if required

### Step 3: Deploy to Railway

#### Method 1: GitHub Integration (Recommended)

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Create new Railway project:**
   - Go to Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Click "Deploy Now"

#### Method 2: Railway CLI

1. **Install Railway CLI:**
   ```bash
   # Windows (using npm)
   npm install -g @railway/cli
   
   # Mac (using brew)
   brew install railway
   ```

2. **Login and deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

### Step 4: Add PostgreSQL Database

1. **In Railway dashboard:**
   - Click on your project
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway will create database and provide connection details

2. **Database will automatically provide these environment variables:**
   - `DATABASE_URL`
   - `DATABASE_USERNAME` 
   - `DATABASE_PASSWORD`

### Step 5: Configure Environment Variables

1. **In Railway project dashboard:**
   - Click on your service
   - Go to "Variables" tab
   - Add these variables:

   ```
   SPRING_PROFILES_ACTIVE=prod
   JWT_SECRET=your-super-secret-jwt-key-here-make-it-long-and-random
   JWT_EXPIRATION=900000
   JWT_REFRESH_EXPIRATION=604800000
   SERVER_PORT=8080
   ```

### Step 6: Deploy and Test

1. **Railway will automatically:**
   - Build your Java application
   - Start the server
   - Provide you with a public URL

2. **Test your deployment:**
   ```bash
   # Replace YOUR-APP-URL with the URL Railway provides
   curl https://your-app-name.railway.app/actuator/health
   ```

3. **Access Swagger UI:**
   ```
   https://your-app-name.railway.app/swagger-ui/index.html
   ```

### Step 7: Set Up Continuous Deployment

Railway automatically redeploys when you push to your connected GitHub branch:

```bash
# Make changes to your code
git add .
git commit -m "Update feature"
git push origin main
# Railway will automatically redeploy!
```

---

## 🟣 Heroku Deployment (Alternative)

### Step 1: Install Heroku CLI
1. Download from [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Login: `heroku login`

### Step 2: Create Heroku App
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
```

### Step 3: Configure Environment Variables
```bash
heroku config:set SPRING_PROFILES_ACTIVE=prod
heroku config:set JWT_SECRET=your-secret-key
```

### Step 4: Deploy
```bash
git push heroku main
```

---

## 🟢 Render Deployment (Alternative)

### Step 1: Create Render Account
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub

### Step 2: Create Web Service
1. Click "New" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Build Command:** `./mvnw clean package -DskipTests`
   - **Start Command:** `java -jar target/vira-services-0.0.1-SNAPSHOT.jar --spring.profiles.active=prod`

### Step 3: Add PostgreSQL Database
1. Click "New" → "PostgreSQL"
2. Copy connection details to environment variables

---

## 🛠️ Post-Deployment Configuration

### 1. Update CORS for Frontend

After deployment, update your backend to allow your frontend domain:

```yaml
# application-prod.yml
cors:
  allowed-origins:
    - https://your-frontend-domain.com
    - http://localhost:3000  # Keep for local development
```

### 2. Test All Endpoints

Create a simple test script:

```bash
#!/bin/bash
BASE_URL="https://your-app.railway.app"

echo "Testing health endpoint..."
curl "$BASE_URL/actuator/health"

echo "Testing user registration..."
curl -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

echo "Testing user login..."
curl -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

### 3. Monitor Your Application

#### Railway Monitoring:
- Check "Deployments" tab for build logs
- Check "Metrics" for performance
- Check "Logs" for runtime errors

#### Health Checks:
Set up monitoring for `https://your-app.railway.app/actuator/health`

---

## 🔒 Production Security Checklist

### Environment Variables
- [ ] `JWT_SECRET` is long and random (64+ characters)
- [ ] Database credentials are secure
- [ ] No sensitive data in code/logs

### CORS Configuration
- [ ] Only allow your frontend domains
- [ ] Remove localhost from production CORS

### HTTPS
- [ ] Railway/Heroku provide HTTPS automatically
- [ ] Verify all API calls use HTTPS

### Database
- [ ] Flyway migrations work correctly
- [ ] Database connection is encrypted
- [ ] Backup strategy in place

---

## 📊 Monitoring and Maintenance

### 1. Application Monitoring
```bash
# Check application health
curl https://your-app.railway.app/actuator/health

# Check application info
curl https://your-app.railway.app/actuator/info
```

### 2. Database Monitoring
- Monitor connection pool usage
- Watch for slow queries
- Set up automated backups

### 3. Log Monitoring
Monitor these log patterns:
- Authentication failures
- Database connection errors
- JWT token issues
- API response times

---

## 🚨 Troubleshooting Deployment Issues

### Issue 1: Build Failures
**Symptoms:** Deployment fails during build
**Solutions:**
- Check Java version (should be 17)
- Verify Maven wrapper exists
- Check for compilation errors locally

### Issue 2: Database Connection Failed
**Symptoms:** App starts but can't connect to database
**Solutions:**
- Verify DATABASE_URL environment variable
- Check database service is running
- Verify Flyway migrations

### Issue 3: Port Binding Issues
**Symptoms:** App builds but doesn't start
**Solutions:**
- Ensure app uses `$PORT` environment variable
- Check if `server.port=${PORT:8080}` in application.yml

### Issue 4: CORS Errors in Production
**Symptoms:** Frontend can't connect to backend
**Solutions:**
- Add frontend domain to CORS configuration
- Verify HTTPS is used for all requests

### Issue 5: JWT Issues
**Symptoms:** Authentication not working
**Solutions:**
- Verify JWT_SECRET is set
- Check token expiration times
- Verify clock synchronization

---

## 💰 Cost Optimization Tips

### Railway Free Tier Limits:
- $5 credit per month
- Projects sleep after 30 minutes of inactivity
- 500MB RAM limit

### Optimization Strategies:
1. **Use H2 for development:** Save database costs
2. **Optimize Docker builds:** Faster deployments
3. **Enable compression:** Reduce bandwidth
4. **Monitor usage:** Track resource consumption

---

## 📈 Scaling Considerations

### When to Scale:
- Response times > 2 seconds
- Memory usage > 80%
- Database connections exhausted

### Scaling Options:
1. **Vertical scaling:** Increase RAM/CPU
2. **Horizontal scaling:** Multiple instances
3. **Database scaling:** Read replicas
4. **CDN:** For static assets

---

**🎉 Congratulations!** Your Vira Services backend is now deployed and ready for production use! 