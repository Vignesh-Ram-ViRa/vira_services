# 🚀 Local Setup Guide - Vira Services Backend

This guide will help you set up and run the Vira Services backend on a new machine from scratch, even if you're not familiar with backend development.

## 📋 Prerequisites (What You Need to Install)

### 1. Install Java 17
**Why:** Spring Boot requires Java to run
**Steps:**
1. Go to [Oracle JDK Downloads](https://www.oracle.com/java/technologies/javase/jdk17-archive-downloads.html)
2. Download Java 17 for your operating system
3. Install it following the installer instructions
4. **Verify installation:**
   ```bash
   java -version
   ```
   Should show: `java version "17.x.x"`

### 2. Install Git
**Why:** To clone the project from repository
**Steps:**
1. Go to [Git Downloads](https://git-scm.com/downloads)
2. Download and install Git for your OS
3. **Verify installation:**
   ```bash
   git --version
   ```

### 3. Install a Code Editor (Optional but Recommended)
**Options:**
- **VS Code** (Recommended): [Download here](https://code.visualstudio.com/)
- **IntelliJ IDEA Community**: [Download here](https://www.jetbrains.com/idea/download/)

## 📂 Step 1: Get the Project

### Clone the Repository
```bash
# Navigate to where you want the project
cd Desktop

# Clone the project (replace with actual repository URL)
git clone https://github.com/yourusername/vira-services.git

# Enter the project folder
cd vira-services
```

## ⚙️ Step 2: Set Up Environment Variables

### Windows (PowerShell):
```powershell
# Set Java Home (adjust path if Java is installed elsewhere)
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"

# Add to PATH (so 'java' command works)
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
```

### Mac/Linux (Terminal):
```bash
# Add to your ~/.bashrc or ~/.zshrc file
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export PATH=$JAVA_HOME/bin:$PATH

# Reload the file
source ~/.bashrc  # or source ~/.zshrc
```

## 🔧 Step 3: Build and Run the Application

### Make Maven Wrapper Executable (Mac/Linux only)
```bash
chmod +x mvnw
```

### Start the Application

**Option 1: Quick Start (Development Mode)**
```bash
# Windows
.\mvnw.cmd spring-boot:run

# Mac/Linux
./mvnw spring-boot:run
```

**Option 2: Build First, Then Run**
```bash
# Windows
.\mvnw.cmd clean package
java -jar target/vira-services-0.0.1-SNAPSHOT.jar

# Mac/Linux
./mvnw clean package
java -jar target/vira-services-0.0.1-SNAPSHOT.jar
```

## ✅ Step 4: Verify Everything is Working

### 1. Check if Server Started
Look for this message in the terminal:
```
Started ViraServicesApplication in X.XXX seconds
```

### 2. Test Health Endpoint
Open a new terminal and run:
```bash
curl http://localhost:8080/actuator/health
```
**Expected Response:**
```json
{"status":"UP"}
```

### 3. Access Swagger UI (API Documentation)
Open your browser and go to:
```
http://localhost:8080/swagger-ui/index.html
```
You should see the API documentation interface.

### 4. Test User Registration
```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "password123"
  }'
```

## 🛠️ Troubleshooting Common Issues

### Issue 1: "Port 8080 already in use"
**Solution:** Kill the process using the port
```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID_NUMBER> /F

# Mac/Linux
lsof -i :8080
kill -9 <PID_NUMBER>
```

### Issue 2: "JAVA_HOME not found"
**Solution:** Set the JAVA_HOME environment variable (see Step 2)

### Issue 3: "mvnw command not found"
**Solution:** 
- Make sure you're in the project root directory
- On Windows, use `.\mvnw.cmd` instead of `./mvnw`

### Issue 4: Database Connection Error
**Solution:** The app uses H2 (in-memory database) for development, so no setup needed. If you see database errors, restart the application.

## 📱 Different Profiles

### Development Mode (Default)
- Uses H2 in-memory database
- All data is lost when app stops
- Perfect for testing
```bash
.\mvnw.cmd spring-boot:run -Dspring-boot.run.profiles=dev
```

### Production Mode
- Requires PostgreSQL database
- For deployment only
```bash
.\mvnw.cmd spring-boot:run -Dspring-boot.run.profiles=prod
```

## 🔍 Understanding the Application Structure

```
vira-services/
├── src/main/java/com/vira/
│   ├── auth/              # User authentication & security
│   ├── portfolio/         # Project management
│   ├── config/           # Application configuration
│   └── common/           # Shared utilities
├── src/main/resources/
│   ├── application*.yml  # Configuration files
│   └── db/migration/     # Database setup scripts
└── target/               # Built application files
```

## 📚 Important Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/actuator/health` | GET | Check if app is running |
| `/swagger-ui/index.html` | GET | API documentation |
| `/api/auth/register` | POST | Create new user |
| `/api/auth/login` | POST | User login |
| `/api/portfolio/projects` | GET | List projects |
| `/h2-console` | GET | Database viewer (dev mode) |

## 🎯 Next Steps

1. **Test the APIs** using Swagger UI or curl commands
2. **Create a user** via `/api/auth/register`
3. **Login** via `/api/auth/login` to get JWT token
4. **Use the token** to access protected endpoints
5. **Create projects** via `/api/portfolio/projects`

## ❓ Need Help?

- Check the **console logs** for error messages
- Use **Swagger UI** to test endpoints interactively
- Verify **Java version** and **environment variables**
- Ensure **port 8080** is available

---

**🎉 Congratulations!** Your Vira Services backend is now running locally! 