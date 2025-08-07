# Vira Services - Multi-Project Backend Repository

> **A centralized Spring Boot backend for all your personal projects with shared authentication and PostgreSQL database.**

## 🎯 **Project Overview**

Vira Services is a scalable Spring Boot backend designed to serve multiple mini projects from a single repository. Perfect for hobby dashboards, finance trackers, AI tools libraries, portfolio management, and any future projects you want to build.

### **Key Features**
- ✅ **JWT Authentication** with refresh tokens
- ✅ **Portfolio/Projects Management** CRUD service
- ✅ **Multi-Service Architecture** (easy to add new services)
- ✅ **PostgreSQL Database** with Flyway migrations
- ✅ **Railway Deployment** ready
- ✅ **React Integration** friendly
- ✅ **Corporate Environment** compatible
- ✅ **Maven Wrapper** included (no Maven installation needed)

## 📁 **Repository Structure**

```
vira-services/
├── src/main/java/com/vira/
│   ├── ViraServicesApplication.java
│   ├── config/                   # Security, JWT, CORS configs
│   ├── common/                   # Shared utilities & DTOs
│   ├── auth/                     # Authentication service
│   └── portfolio/                # Portfolio/Projects service
├── src/main/resources/
│   ├── application*.yml          # Environment configurations
│   └── db/migration/             # Database migrations
├── guides/                       # Project documentation
│   ├── PROJECT_PLAN.md           # Complete project plan
│   ├── LOCAL_DEVELOPMENT.md      # Local setup guide
│   ├── DEPLOYMENT.md             # Railway deployment guide
│   ├── TESTING_GUIDE.md          # Testing standards
│   └── FRONTEND_INTEGRATION.md   # React integration guide
└── README.md                     # This file
```

## 🚀 **Quick Start**

### **Prerequisites**
- Java 17+ (OpenJDK recommended)
- Git
- Corporate network access (for Maven dependencies)

### **1. Clone & Run Locally**
```bash
# Clone the repository
git clone <your-repo-url>
cd vira-services

# Run with Maven Wrapper (no Maven installation needed)
./mvnw spring-boot:run -Dspring-boot.run.profiles=dev

$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"; $env:SPRING_PROFILES_ACTIVE = "dev"; $env:SERVER_PORT = "8081"; .\mvnw.cmd spring-boot:run

# Application will start at: http://localhost:8080
```

### **2. Access API Documentation**
- **Swagger UI**: http://localhost:8080/swagger-ui/index.html
- **H2 Console**: http://localhost:8080/h2-console (dev profile)
- **Health Check**: http://localhost:8080/actuator/health

### **3. Test Authentication**
```bash
# Register user
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login user
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

## 📖 **Documentation**

| Document | Description |
|----------|-------------|
| **[PROJECT_PLAN.md](guides/PROJECT_PLAN.md)** | Complete project requirements and architecture plan |
| **[LOCAL_DEVELOPMENT.md](guides/LOCAL_DEVELOPMENT.md)** | Detailed local development setup and testing guide |
| **[DEPLOYMENT.md](guides/DEPLOYMENT.md)** | Step-by-step Railway deployment tutorial |
| **[FRONTEND_INTEGRATION.md](guides/FRONTEND_INTEGRATION.md)** | React integration guide with code examples |
| **[TESTING_GUIDE.md](guides/TESTING_GUIDE.md)** | Comprehensive testing standards and examples |

## 🔐 **Services Available**

### **Authentication Service** (`/api/auth`)
- User registration and login
- JWT token generation and refresh
- Role-based access control
- Secure password hashing

**Endpoints:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user info

### **Portfolio Service** (`/api/portfolio`)
- Project/portfolio management
- CRUD operations for projects
- Featured projects and categorization
- Technology stack tracking

**Endpoints:**
- `GET /api/portfolio/projects` - Get all projects
- `POST /api/portfolio/projects` - Create new project
- `GET /api/portfolio/projects/{id}` - Get specific project
- `PUT /api/portfolio/projects/{id}` - Update project
- `DELETE /api/portfolio/projects/{id}` - Delete project
- `GET /api/portfolio/projects/featured` - Get featured projects

## 🗄️ **Database Schema**

### **Authentication Tables**
- `auth_users` - User accounts
- `auth_roles` - User roles
- `auth_user_roles` - User-role relationships
- `auth_refresh_tokens` - JWT refresh tokens

### **Portfolio Tables**
- `portfolio_projects` - Project/portfolio items

**Sample Project Record:**
```json
{
  "title": "Enterprise Task Management System",
  "description": "Comprehensive task management platform...",
  "technologies": ["React", "Spring Boot", "PostgreSQL"],
  "status": "completed",
  "category": "Full-Stack Application",
  "link": "https://demo.com",
  "github": "https://github.com/user/repo",
  "featured": true,
  "year": 2024
}
```

## 🏢 **Corporate Environment Support**

This project is designed to work in corporate environments:

- ✅ **Maven Wrapper** - No admin installation required
- ✅ **Proxy Support** - Configurable for corporate networks
- ✅ **H2 Database** - No external database setup needed for development
- ✅ **Spring Initializr Fallback** - Alternative if network restrictions exist

**Network Issues?** See [LOCAL_DEVELOPMENT.md](guides/LOCAL_DEVELOPMENT.md#corporate-environment-considerations) for troubleshooting.

## ☁️ **Deployment**

### **Railway (Recommended)**
- **Free Tier**: 500 hours/month + 1GB PostgreSQL
- **Auto-deploy**: Connects to GitHub for automatic deployments
- **Zero Config**: Automatic PostgreSQL provisioning

**Deploy Steps:**
1. Push code to GitHub
2. Connect Railway to your repository
3. Add PostgreSQL service
4. Configure environment variables
5. Your API is live!

**Detailed Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

## ⚛️ **Frontend Integration**

### **React Integration**
Complete React setup with:
- Authentication context and hooks
- API service layer
- Portfolio management components
- Error handling and loading states

**Key Features:**
```javascript
// Authentication
const { login, register, logout, user, isAuthenticated } = useAuth();

// Portfolio Management  
const { projects, createProject, updateProject, deleteProject } = usePortfolio();

// API Calls
const response = await apiCall('/api/portfolio/projects', {
  method: 'POST',
  body: JSON.stringify(projectData)
});
```

**Complete Guide:** [FRONTEND_INTEGRATION.md](guides/FRONTEND_INTEGRATION.md)

## 🔄 **Adding New Services**

The architecture supports easy addition of new services:

### **1. Create Service Package**
```
src/main/java/com/vira/newservice/
├── controller/NewServiceController.java
├── service/NewServiceService.java  
├── repository/NewServiceRepository.java
├── model/NewServiceEntity.java
└── dto/NewServiceDto.java
```

### **2. Add Database Migration**
```sql
-- src/main/resources/db/migration/V3__Create_newservice_tables.sql
CREATE TABLE newservice_items (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id BIGINT REFERENCES auth_users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **3. Implement Endpoints**
```java
@RestController
@RequestMapping("/api/newservice")
@CrossOrigin(origins = {"http://localhost:3000"})
public class NewServiceController {
    // CRUD endpoints
}
```

## 🎯 **Future Service Ideas**

The architecture supports easy addition of:
- **Finance Tracker** (`/api/finance`) - Expense tracking, budgets
- **AI Tools Library** (`/api/ai-tools`) - AI tool collection and reviews
- **Dashboard Service** (`/api/dashboards`) - Custom dashboard management
- **File Management** (`/api/files`) - File upload and organization
- **Notifications** (`/api/notifications`) - User notification system

## 🛠️ **Development Tools**

### **Local Development**
```bash
# Run with hot reload
./mvnw spring-boot:run -Dspring-boot.run.profiles=dev

# Run all tests
./mvnw test

# Run tests with coverage
./mvnw test jacoco:report

# Build for production
./mvnw clean package

# Build without running tests (not recommended)
./mvnw clean package -DskipTests
```

### **API Testing**
- **Swagger UI**: Interactive API documentation
- **Postman**: Import collection from Swagger
- **cURL**: Command-line testing
- **H2 Console**: Database inspection

### **Monitoring**
- **Actuator Endpoints**: Health, metrics, info
- **Application Logs**: Structured logging with profiles
- **Railway Metrics**: CPU, memory, request tracking

## 📊 **Production Readiness**

### **Security Features**
- ✅ JWT authentication with refresh tokens
- ✅ Password hashing with BCrypt
- ✅ CORS configuration for frontend domains
- ✅ Input validation and sanitization
- ✅ Secure headers and HTTPS support

### **Performance Features**
- ✅ Database connection pooling
- ✅ Flyway migrations for schema versioning
- ✅ Environment-specific configurations
- ✅ Caching for frequently accessed data
- ✅ Pagination for large datasets

### **Observability**
- ✅ Structured logging with different levels
- ✅ Health check endpoints
- ✅ Application metrics via Actuator
- ✅ Error tracking and monitoring

### **Quality Assurance**
- ✅ Comprehensive unit test coverage (minimum 80%)
- ✅ Integration tests for all API endpoints
- ✅ Automated test execution in CI/CD
- ✅ Code quality checks and static analysis
- ✅ Test categorization (unit vs integration vs e2e)

## 🤝 **Contributing**

### **Adding New Features**
1. Create feature branch
2. Add service in new package
3. Add database migrations
4. Update documentation
5. Test locally and in production
6. Submit pull request

### **Code Standards**
- Follow Spring Boot best practices
- Use consistent naming conventions
- Add comprehensive documentation
- Include error handling
- **Write comprehensive unit tests** (minimum 80% coverage)
- **Write integration tests** for all API endpoints
- Use proper test categorization (unit vs integration)
- Mock external dependencies in unit tests

## 📞 **Support**

- **Documentation**: Check the guides in this repository
- **Issues**: Create GitHub issues for bugs or feature requests
- **Railway Support**: Use Railway's Discord community

## 🔗 **Quick Links**

- **Local Development**: [LOCAL_DEVELOPMENT.md](guides/LOCAL_DEVELOPMENT.md)
- **Deployment Guide**: [DEPLOYMENT.md](guides/DEPLOYMENT.md)
- **React Integration**: [FRONTEND_INTEGRATION.md](guides/FRONTEND_INTEGRATION.md)
- **Testing Guide**: [TESTING_GUIDE.md](guides/TESTING_GUIDE.md)
- **Project Plan**: [PROJECT_PLAN.md](guides/PROJECT_PLAN.md)

---

**🚀 Ready to start development?** Follow the [LOCAL_DEVELOPMENT.md](guides/LOCAL_DEVELOPMENT.md) guide to get started!

**🌐 Ready to deploy?** Follow the [DEPLOYMENT.md](guides/DEPLOYMENT.md) guide for Railway deployment!

**⚛️ Building a React frontend?** Check out [FRONTEND_INTEGRATION.md](guides/FRONTEND_INTEGRATION.md)! 