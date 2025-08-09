# Local Development Setup

> **Complete guide to set up Vira Services on your local machine**

## 📋 **Prerequisites**

### Required Software
- **Java 17** or higher ([Download](https://adoptium.net/))
- **Git** ([Download](https://git-scm.com/))
- **PostgreSQL** (optional - H2 used by default)

### Verify Installation
```bash
java -version    # Should show Java 17+
git --version    # Any recent version
```

## 🚀 **Quick Start (5 minutes)**

### Step 1: Clone Repository
```bash
git clone https://github.com/Vignesh-Ram-ViRa/vira_services.git
cd vira_services
```

### Step 2: Set Environment Variables (Windows)
```powershell
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
$env:SPRING_PROFILES_ACTIVE = "dev"
```

### Step 3: Start Application
```bash
# Windows
.\mvnw.cmd spring-boot:run

# Linux/Mac
./mvnw spring-boot:run
```

### Step 4: Verify Setup
- **Application**: http://localhost:8080/actuator/health
- **Swagger UI**: http://localhost:8080/swagger-ui/index.html
- **H2 Console**: http://localhost:8080/h2-console

## 🔧 **Development Configuration**

### H2 Database (Default - Dev Mode)
```yaml
# application-dev.yml (active by default)
spring:
  datasource:
    url: jdbc:h2:mem:viradb
    username: sa
    password: 
    driver-class-name: org.h2.Driver
```

**H2 Console Access:**
- URL: `jdbc:h2:mem:viradb`
- Username: `sa`
- Password: (empty)

### PostgreSQL Setup (Optional)
```bash
# Install PostgreSQL
# Create database
createdb vira_services

# Update application-dev.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/vira_services
    username: your_username
    password: your_password
```

## 🧪 **Testing the Application**

### Default Users (Auto-created)
```json
// Admin User (Auto-created on startup)
{
  "username": "admin",
  "password": "admin123",
  "role": "ADMIN"
}
```

### Role System
- **GUEST**: No authentication required for public endpoints
- **NORMAL_USER**: Standard users (register/login + Google OAuth)
- **SUPER_USER**: Approved users with read-only access to everything
- **ADMIN**: Full system access

### API Testing Steps

**1. Test Guest Access (No Auth Required):**
```bash
# Public portfolio projects
curl -X GET http://localhost:8080/api/public/projects

# Public project statistics
curl -X GET http://localhost:8080/api/public/projects/stats

# Featured projects
curl -X GET http://localhost:8080/api/public/projects/featured
```

**2. Register New User:**
```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

**3. Login:**
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

**4. Use JWT Token:**
```bash
curl -X GET http://localhost:8080/api/portfolio/projects \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**5. Test Google OAuth (Browser):**
```bash
# Initiate Google OAuth (opens Google login)
http://localhost:8080/oauth2/authorization/google
```

### Swagger UI Testing
1. Go to http://localhost:8080/swagger-ui/index.html
2. **Test Guest Endpoints**: Use "Public" section (no auth needed)
3. **Test Authenticated Endpoints**:
   - Click **🔒 Authorize** button
   - Login to get JWT token
   - Enter: `Bearer YOUR_TOKEN_HERE`
   - Test any protected endpoint

## 🛠️ **Development Tools**

### Hot Reload (Spring Boot DevTools)
- **Automatic restart** on code changes
- **LiveReload** for static resources
- Included in development profile

### Useful Commands
```bash
# Clean build
.\mvnw.cmd clean package

# Run tests with coverage
.\mvnw.cmd test jacoco:report

# Skip tests
.\mvnw.cmd spring-boot:run -Dspring-boot.run.profiles=dev -DskipTests

# Check dependencies
.\mvnw.cmd dependency:tree

# Database migration (if using PostgreSQL)
.\mvnw.cmd flyway:migrate
```

### IDE Setup (Recommended)
- **IntelliJ IDEA** or **VS Code**
- **Spring Boot plugin** for your IDE
- **Lombok plugin** (if using Lombok)

## 🐛 **Troubleshooting**

### Common Issues

**Port 8080 already in use:**
```bash
# Windows - Find and kill process
netstat -ano | findstr ":8080"
taskkill /PID <PID> /F

# Change port (optional)
server.port=8081
```

**Java version issues:**
```bash
# Check Java version
java -version

# Set JAVA_HOME if needed
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
```

**Compilation errors:**
```bash
# Clean and rebuild
.\mvnw.cmd clean compile

# Full clean install
.\mvnw.cmd clean install
```

**Database connection issues:**
- H2: Check if application is running
- PostgreSQL: Verify connection details and database exists

**Authentication issues:**
- Check JWT token format: `Bearer eyJhbGciOiJIUzI1NiJ9...`
- Verify token is not expired (15 min default)
- Use refresh token if access token expired

### Logs Location
- **Console**: Real-time logs in terminal
- **File**: `logs/spring.log` (if configured)

## 📁 **Project Structure**
```
vira_services/
├── src/main/java/com/vira/
│   ├── auth/                 # Authentication service + OAuth
│   ├── portfolio/            # Portfolio/Projects service
│   ├── config/               # Configuration classes
│   └── common/               # Shared utilities
├── src/main/resources/
│   ├── application*.yml      # Configuration files
│   └── db/migration/         # Database migrations
├── guides/                   # Documentation
└── mvnw.cmd                  # Maven wrapper
```

## 🔄 **Development Workflow**

1. **Make changes** to Java code
2. **Spring DevTools** auto-restarts application
3. **Test** via Swagger UI or curl
4. **Check logs** in console
5. **Test both authenticated and guest endpoints**
6. **Commit** when ready

## 🎯 **Next Steps**

- **Google OAuth Setup**: See `guides/GOOGLE_OAUTH.md`
- **Production Deployment**: See `guides/DEPLOYMENT.md`
- **React Integration**: See `guides/REACT_INTEGRATION.md`
- **Adding New Services**: See `guides/NEW_SERVICE_GUIDE.md`
- **Role Management**: See `guides/ROLE_MANAGEMENT.md`
- **Security Configuration**: See `guides/SECURITY.md`

---

**✅ Your local development environment is ready!** Start building amazing features! 🚀 