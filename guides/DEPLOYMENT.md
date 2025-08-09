# Production Deployment Guide

> **Complete guide to deploy Vira Services to production with security best practices**

## 🎯 **Deployment Platforms**

### Recommended Options
- **Railway** (Primary - Free tier available)
- **Heroku** (Alternative)
- **AWS/Azure/GCP** (Enterprise)
- **Docker** (Self-hosted)

## 🚀 **Railway Deployment (Recommended)**

### Prerequisites
- [Railway account](https://railway.app) (free tier)
- GitHub repository
- Basic understanding of environment variables

### Step 1: Prepare Application

**1.1 Verify Production Config (`application-prod.yml`):**
```yaml
server:
  port: ${PORT:8080}

spring:
  profiles:
    active: prod
  
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
    baseline-on-migrate: true

# JWT Configuration
jwt:
  secret: ${JWT_SECRET}
  expiration: 3600000
  refresh-expiration: 604800000

# CORS Configuration  
cors:
  allowed-origins: ${FRONTEND_URL:https://your-frontend.com}
  allowed-methods: GET,POST,PUT,DELETE,OPTIONS,PATCH
  allowed-headers: "*"
  allow-credentials: true

# Security
app:
  admin:
    username: ${ADMIN_USERNAME:admin}
    password: ${ADMIN_PASSWORD}
```

**1.2 Create `Procfile`:**
```
web: java -Dserver.port=$PORT -Dspring.profiles.active=prod -jar target/vira-services-1.0.0.jar
```

### Step 2: Deploy to Railway

**2.1 Create Project:**
1. Go to [Railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Connect your vira-services repository
4. Add PostgreSQL service

**2.2 Environment Variables:**
```bash
# Database (auto-configured)
DATABASE_URL=postgresql://...
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=********

# Security (REQUIRED)
JWT_SECRET=your-super-secret-jwt-key-at-least-64-characters-long
ADMIN_PASSWORD=your-secure-admin-password-change-this

# Frontend Integration
FRONTEND_URL=https://your-frontend-domain.com

# Profile
SPRING_PROFILES_ACTIVE=prod
```

**2.3 Generate Secure JWT Secret:**
```bash
# Generate 64-character secret
openssl rand -base64 64
```

### Step 3: Verify Deployment

**3.1 Health Check:**
```bash
curl https://your-app.railway.app/actuator/health
```

**3.2 Test Admin Login:**
```bash
curl -X POST https://your-app.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YOUR_ADMIN_PASSWORD"}'
```

**3.3 Access Swagger UI:**
- https://your-app.railway.app/swagger-ui/index.html

## 🔐 **Production Security**

### Admin User Management

**⚠️ CRITICAL: Default Admin Security**

The application automatically creates an admin user on startup:
- **Username**: `admin` (or `${ADMIN_USERNAME}`)
- **Password**: `admin123` (or `${ADMIN_PASSWORD}`)

**🔒 Secure Your Admin Account:**

**Option 1: Environment Variable (Recommended)**
```bash
# Set secure password via environment
ADMIN_PASSWORD=your-very-secure-password-123!@#
```

**Option 2: Change After Deployment**
1. Login as admin
2. Use `/api/admin/users/{userId}/role` to create new admin
3. Delete default admin user

**Option 3: Disable Default Admin**
```java
// In DataInitializer.java
@Value("${app.create-default-admin:true}")
private boolean createDefaultAdmin;
```

### API Security Layers

**1. CORS Restrictions:**
```yaml
cors:
  allowed-origins: 
    - "https://yourdomain.com"
    - "https://app.yourdomain.com"
  # Remove localhost in production
```

**2. Rate Limiting (Optional Enhancement):**
```java
@RateLimiter(key = "#request.remoteAddr", rate = "100/hour")
```

**3. API Key Authentication (Optional):**
```java
// Custom filter for API client authentication
@Component
public class ApiKeyFilter implements Filter {
    private static final String API_KEY_HEADER = "X-API-Key";
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {
        String apiKey = ((HttpServletRequest) request).getHeader(API_KEY_HEADER);
        if (!isValidApiKey(apiKey)) {
            throw new SecurityException("Invalid API key");
        }
        chain.doFilter(request, response);
    }
}
```

### Network Security

**1. HTTPS Only:**
- Railway provides automatic SSL
- Enforce HTTPS in production

**2. Database Security:**
- Use strong database passwords
- Enable connection encryption
- Restrict database access

**3. Environment Variables:**
- Never commit secrets to code
- Use Railway's secure environment variables
- Rotate secrets regularly

## 🔄 **CI/CD Pipeline**

### Auto-Deployment Setup
```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Use Node.js
        uses: actions/setup-node@v3
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      - name: Deploy
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## 📊 **Monitoring & Maintenance**

### Health Monitoring
- **Railway Dashboard**: Built-in metrics
- **Application Health**: `/actuator/health`
- **Custom Health Checks**: `/actuator/info`

### Database Management
- **Automatic Backups**: Railway provides PostgreSQL backups
- **Migration Status**: Check Flyway migration logs
- **Data Initialization**: Roles created automatically via `DataInitializer`

### Log Monitoring
```bash
# View Railway logs
railway logs

# Key metrics to monitor
- Authentication attempts
- Failed logins
- API response times
- Database connection pool
```

## 🚨 **Troubleshooting**

### Common Production Issues

**Database Connection:**
```bash
# Check database status
railway connect postgresql

# Verify environment variables
railway env
```

**Memory Issues:**
```yaml
# Optimize JVM in Procfile
web: java -Xmx512m -Dspring.profiles.active=prod -jar target/vira-services-1.0.0.jar
```

**CORS Issues:**
```yaml
# Update allowed origins
cors:
  allowed-origins: ${FRONTEND_URL}
```

## ✅ **Production Checklist**

### Security
- [ ] Admin password changed from default
- [ ] JWT secret is 64+ characters
- [ ] CORS configured for production domains only
- [ ] HTTPS enabled
- [ ] Database password is strong
- [ ] Environment variables are secure

### Functionality
- [ ] Health check endpoint responds
- [ ] Admin login works
- [ ] User registration/login works
- [ ] Portfolio endpoints accessible
- [ ] Database migrations applied
- [ ] Default roles created

### Monitoring
- [ ] Application logs are readable
- [ ] Health monitoring setup
- [ ] Error tracking enabled
- [ ] Database backups configured

### Performance
- [ ] JVM memory optimized
- [ ] Connection pooling configured
- [ ] Static resources cached

## 🎯 **Post-Deployment Steps**

1. **Test all endpoints** via Swagger UI
2. **Create your first admin operations**
3. **Deploy React frontend** (see `REACT_INTEGRATION.md`)
4. **Set up monitoring** and alerts
5. **Document your production URLs**

## 🔗 **Related Guides**

- **Local Setup**: `guides/LOCAL_SETUP.md`
- **React Integration**: `guides/REACT_INTEGRATION.md`
- **Role Management**: `guides/ROLE_MANAGEMENT.md`
- **Security Best Practices**: `guides/SECURITY.md`

---

**🎉 Your Vira Services backend is production-ready!** Deploy with confidence! 🚀 