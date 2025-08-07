# Local Development Guide

## 🚀 Running Vira Services Locally

This guide will walk you through setting up and running the Spring Boot backend on your local machine for development and testing.

## 📋 Prerequisites

### Required Software
```bash
# Check if you have these installed:
java -version          # Should be Java 17 or higher
mvn -version          # Maven 3.6+ (or use ./mvnw wrapper)
git --version         # Git for version control
```

### Recommended Tools
- **IDE**: IntelliJ IDEA Community (free) or VSCode with Java extensions
- **API Testing**: Postman (free) or use built-in Swagger UI
- **Database**: PostgreSQL (production-like) or H2 (simpler setup)

## 🗄️ Database Setup Options

### Option 1: H2 Database (Easiest - Recommended for Development)
H2 is an in-memory database that requires zero setup:

```yaml
# application-dev.yml configuration
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
    username: sa
    password: password
  h2:
    console:
      enabled: true
      path: /h2-console
  jpa:
    database-platform: org.hibernate.dialect.H2Dialect
    hibernate:
      ddl-auto: create-drop
```

**Access H2 Console**: http://localhost:8080/h2-console
- **JDBC URL**: `jdbc:h2:mem:testdb`
- **Username**: `sa`
- **Password**: `password`

### Option 2: PostgreSQL (Production-like)
If you want to use PostgreSQL locally:

#### Install PostgreSQL
```bash
# Windows (using Chocolatey)
choco install postgresql

# Or download from: https://www.postgresql.org/download/windows/
```

#### Create Database
```sql
-- Connect to PostgreSQL and run:
CREATE DATABASE vira_services;
CREATE USER vira_user WITH PASSWORD 'vira_password';
GRANT ALL PRIVILEGES ON DATABASE vira_services TO vira_user;
```

#### Configuration
```yaml
# application-dev.yml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/vira_services
    username: vira_user
    password: vira_password
    driver-class-name: org.postgresql.Driver
  jpa:
    database-platform: org.hibernate.dialect.PostgreSQLDialect
    hibernate:
      ddl-auto: validate
```

## 🏃‍♂️ Running the Application

### Method 1: Using Maven Wrapper (Recommended for Corporate)
```bash
# Navigate to project directory
cd vira_services

# Windows: Use Maven Wrapper (no Maven installation needed)
./mvnw spring-boot:run -Dspring-boot.run.profiles=dev

# Alternative if above doesn't work:
mvnw.cmd spring-boot:run -Dspring-boot.run.profiles=dev

# If you have Maven installed:
mvn spring-boot:run -Dspring-boot.run.profiles=dev
```

**Maven Wrapper Benefits:**
- ✅ No Maven installation required
- ✅ Consistent Maven version across environments  
- ✅ Downloads Maven automatically on first run
- ✅ Works on corporate devices (if network allows)

### Method 2: Using IDE (IntelliJ IDEA)
1. **Import Project**: File → Open → Select `pom.xml`
2. **Set Active Profile**: 
   - Go to Run/Debug Configurations
   - Add VM Options: `-Dspring.profiles.active=dev`
3. **Run**: Click the green play button next to `ViraServicesApplication`

### Method 3: Using JAR
```bash
# Build the project (use wrapper)
./mvnw clean package -DskipTests

# Run the JAR
java -jar target/vira-services-0.0.1-SNAPSHOT.jar --spring.profiles.active=dev
```

## 🧪 **Running Tests**

### Unit Tests
```bash
# Run all tests
./mvnw test

# Run tests for specific service
./mvnw test -Dtest=com.vira.auth.*

# Run tests with coverage report
./mvnw test jacoco:report

# View coverage report
# Open: target/site/jacoco/index.html
```

### Integration Tests
```bash
# Run integration tests only
./mvnw test -Dtest=*IntegrationTest

# Run with test profile
./mvnw test -Dspring.profiles.active=test

# Run specific integration test
./mvnw test -Dtest=AuthControllerIntegrationTest
```

### Test Categories
```bash
# Unit tests (fast, no external dependencies)
./mvnw test -Dgroups=unit

# Integration tests (slower, with database)
./mvnw test -Dgroups=integration

# All tests with detailed output
./mvnw test -Dtest.verbose=true
```

## ✅ Checking If Services Are Running

### 1. Application Startup Logs
Look for these key messages in the console:

```
Started ViraServicesApplication in X.XXX seconds
Tomcat started on port(s): 8080 (http)
Database initialized successfully
JWT secret loaded
```

### 2. Health Check Endpoint
```bash
# Basic health check
curl http://localhost:8080/actuator/health

# Expected response:
{"status":"UP"}
```

### 3. API Documentation (Swagger UI)
Once running, visit: **http://localhost:8080/swagger-ui/index.html**

You'll see all available endpoints with interactive documentation.

## 🧪 Testing the APIs

### Using Swagger UI (Easiest)
1. Go to http://localhost:8080/swagger-ui/index.html
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in parameters and click "Execute"

### Using Postman
Import this collection or create requests manually:

#### 1. Register User
```http
POST http://localhost:8080/api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

#### 2. Login User
```http
POST http://localhost:8080/api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

**Save the JWT token from response!**

#### 3. Create Portfolio Project
```http
POST http://localhost:8080/api/portfolio/projects
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN_HERE

{
  "title": "My Awesome Project",
  "description": "A great project description",
  "technologies": ["React", "Spring Boot"],
  "status": "completed",
  "category": "Full-Stack Application",
  "year": 2024,
  "featured": true
}
```

#### 4. Get All Projects
```http
GET http://localhost:8080/api/portfolio/projects
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

### Using cURL
```bash
# Register
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Use the token from login response
TOKEN="your_jwt_token_here"

# Get projects
curl -X GET http://localhost:8080/api/portfolio/projects \
  -H "Authorization: Bearer $TOKEN"
```

## 🔍 Monitoring and Debugging

### Application Logs
The console will show:
- **INFO**: Normal application flow
- **DEBUG**: Detailed execution info (if debug logging enabled)
- **ERROR**: Problems that need attention

### Common Log Patterns
```
# Successful API call
2024-01-15 10:30:00 INFO  AuthController - User login successful: testuser

# Database query
2024-01-15 10:30:01 DEBUG JpaRepository - Executing query: SELECT * FROM auth_users WHERE username = ?

# Security
2024-01-15 10:30:02 DEBUG JwtAuthenticationFilter - JWT token validated successfully
```

### Database Inspection

#### H2 Console
1. Visit http://localhost:8080/h2-console
2. Use connection details mentioned above
3. Browse tables: `AUTH_USERS`, `PORTFOLIO_PROJECTS`, etc.

#### PostgreSQL
```bash
# Connect to database
psql -h localhost -U vira_user -d vira_services

# List tables
\dt

# Query users
SELECT * FROM auth_users;

# Query projects
SELECT * FROM portfolio_projects;
```

## 🔧 Development Tips

### Hot Reload with Spring Boot DevTools
Add this dependency for automatic restarts:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-devtools</artifactId>
    <scope>runtime</scope>
    <optional>true</optional>
</dependency>
```

**Benefits:**
- Automatic restart when you change Java files
- LiveReload browser extension support
- Property defaults for development

### Profile-Specific Configuration
```yaml
# application.yml (default)
server:
  port: 8080

# application-dev.yml (development)
logging:
  level:
    com.vira: DEBUG
    org.springframework.security: DEBUG

# application-prod.yml (production)
logging:
  level:
    root: WARN
```

### Environment Variables (Alternative to application.yml)
```bash
# Set these before running
export SPRING_PROFILES_ACTIVE=dev
export DATABASE_URL=jdbc:h2:mem:testdb
export JWT_SECRET=mySecretKey

# Then run
mvn spring-boot:run
```

## 🏢 Corporate Environment Considerations

### Maven Wrapper in Corporate Networks
If you're on a corporate device, Maven Wrapper might face restrictions:

#### Test Network Access First
```bash
# Test Maven Central connectivity
curl https://repo1.maven.org/maven2/ 

# Test basic ping
ping repo1.maven.org
```

#### Common Corporate Issues & Solutions

**Issue: Proxy Authentication Required**
```bash
# Set proxy in Maven settings (create ~/.m2/settings.xml)
<settings>
  <proxies>
    <proxy>
      <id>corporate-proxy</id>
      <active>true</active>
      <protocol>http</protocol>
      <host>your-proxy-host</host>
      <port>your-proxy-port</port>
      <username>your-username</username>
      <password>your-password</password>
    </proxy>
  </proxies>
</settings>
```

**Issue: Firewall Blocks Maven Downloads**
- Request IT to whitelist `repo1.maven.org` and `central.maven.org`
- Use IDE with embedded Maven (IntelliJ IDEA)
- Wait for official Maven installation

**Alternative: Manual Project Setup**
If Maven Wrapper fails completely:
1. Use Spring Initializr web interface: https://start.spring.io/
2. Download ZIP and extract to your project folder
3. Import into IDE and use IDE's build tools

## 🚨 Troubleshooting Common Issues

### Port Already in Use
```
Error: Port 8080 was already in use.
```
**Solution:**
```bash
# Find process using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID)
taskkill /PID YOUR_PID /F

# Or use different port
./mvnw spring-boot:run -Dserver.port=8081
```

### Database Connection Failed
```
Error: Connection to database failed
```
**Solutions:**
- Check if PostgreSQL is running: `pg_ctl status`
- Verify connection details in application-dev.yml
- Switch to H2 for simpler setup

### JWT Token Issues
```
Error: JWT token expired or invalid
```
**Solutions:**
- Check token format in Authorization header: `Bearer YOUR_TOKEN`
- Ensure token hasn't expired (default: 24 hours)
- Get new token via login endpoint

### Maven Build Fails
```
Error: Could not resolve dependencies
```
**Solutions:**
```bash
# Clear Maven cache (use wrapper)
./mvnw dependency:purge-local-repository

# Re-download dependencies
./mvnw clean install

# Skip tests if they're failing
./mvnw clean install -DskipTests

# Corporate network issues - try offline mode first
./mvnw clean install -o
```

### Test Failures
```
Error: Tests are failing
```
**Solutions:**
```bash
# Run tests with detailed output
./mvnw test -X

# Run only failing test
./mvnw test -Dtest=FailingTestClass

# Update test database if needed
./mvnw flyway:clean flyway:migrate -Dspring.profiles.active=test

# Check test logs for specific errors
./mvnw test -Dlogging.level.org.springframework.test=DEBUG
```

## 📊 Monitoring Endpoints

With Spring Boot Actuator, you get these monitoring endpoints:

```bash
# Application health
GET http://localhost:8080/actuator/health

# Application info
GET http://localhost:8080/actuator/info

# Metrics
GET http://localhost:8080/actuator/metrics

# All actuator endpoints
GET http://localhost:8080/actuator
```

## 🎯 Quick Validation Checklist

Before considering your local setup complete:

- ✅ Application starts without errors
- ✅ Swagger UI loads at http://localhost:8080/swagger-ui/index.html
- ✅ Can register a new user
- ✅ Can login and receive JWT token
- ✅ Can create a portfolio project with authentication
- ✅ Can retrieve projects list
- ✅ Database console/connection works
- ✅ Application logs show proper INFO/DEBUG messages
- ✅ All unit tests pass (`./mvnw test`)
- ✅ Test coverage is above 80% (check jacoco report)
- ✅ Integration tests pass with test database

## 💡 Next Steps

Once your local development is working:
1. **Test all API endpoints** thoroughly
2. **Create sample data** for frontend integration
3. **Document any issues** or improvements needed
4. **Prepare for deployment** to Railway

---

**🎉 You're all set for local development!**

Need help with any specific step? Just ask! 