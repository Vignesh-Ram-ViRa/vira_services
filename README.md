# Vira Services - Multi-Project Backend Repository

> **A centralized Spring Boot backend for all your personal projects with shared authentication and PostgreSQL database.**

## 🎯 **Project Overview**

Vira Services is a scalable Spring Boot backend designed to serve multiple mini projects from a single repository. Perfect for hobby dashboards, finance trackers, AI tools libraries, portfolio management, and any future projects you want to build.

### **Key Features**
- ✅ **JWT Authentication** with refresh tokens and role-based access
- ✅ **Google OAuth Integration** for seamless user authentication
- ✅ **Guest Access** for public content viewing (no authentication required)
- ✅ **4-Tier Role System** (GUEST, NORMAL_USER, SUPER_USER, ADMIN)
- ✅ **Portfolio/Projects Management** with public/private project support
- ✅ **Multi-Service Architecture** (easy to add new services)
- ✅ **PostgreSQL Database** with Flyway migrations
- ✅ **Railway Deployment** ready
- ✅ **React Integration** friendly with role-based UI
- ✅ **Corporate Environment** compatible
- ✅ **Maven Wrapper** included (no Maven installation needed)

## 📁 **Repository Structure**

```
vira-services/
├── src/main/java/com/vira/
│   ├── ViraServicesApplication.java
│   ├── config/                   # Security, JWT, CORS configs
│   ├── common/                   # Shared utilities & DTOs
│   ├── auth/                     # Authentication service with role management
│   └── portfolio/                # Portfolio/Projects service
├── src/main/resources/
│   ├── application*.yml          # Environment configurations
│   └── db/migration/             # Flyway database migrations
├── guides/                       # Project documentation
├── mvnw, mvnw.cmd               # Maven wrapper scripts
└── pom.xml                      # Maven dependencies and plugins
```

## 🚀 **Quick Start (5 minutes)**

### **1. Clone and Setup**
```bash
git clone https://github.com/Vignesh-Ram-ViRa/vira_services.git
cd vira_services

# Windows
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
.\mvnw.cmd spring-boot:run

# Linux/Mac
export JAVA_HOME=/path/to/java-17
./mvnw spring-boot:run
```

### **2. Verify Installation**
- **Health Check**: http://localhost:8080/actuator/health
- **API Documentation**: http://localhost:8080/swagger-ui/index.html
- **H2 Database Console**: http://localhost:8080/h2-console

### **3. Test Authentication**
```bash
# Login as default admin
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Register new user
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

## 📖 **Documentation**

| Document | Description |
|----------|-------------|
| **[LOCAL_SETUP.md](guides/LOCAL_SETUP.md)** | 🚀 Complete local development setup (5-minute quick start) |
| **[DEPLOYMENT.md](guides/DEPLOYMENT.md)** | 🌐 Production deployment with security best practices |
| **[GOOGLE_OAUTH.md](guides/GOOGLE_OAUTH.md)** | 🔑 Google OAuth setup and React integration guide |
| **[REACT_INTEGRATION.md](guides/REACT_INTEGRATION.md)** | ⚛️ React integration with role-based UI components |
| **[ROLE_MANAGEMENT.md](guides/ROLE_MANAGEMENT.md)** | 👥 User roles, permissions, and approval workflows |
| **[SECURITY.md](guides/SECURITY.md)** | 🔐 Production security guide and best practices |
| **[NEW_SERVICE_GUIDE.md](guides/NEW_SERVICE_GUIDE.md)** | 🛠️ Adding new services to the backend |
| **[TESTING_GUIDE.md](guides/TESTING_GUIDE.md)** | 🧪 Comprehensive testing standards and examples |

## 🔐 **Role-Based Access Control**

### **Role Hierarchy**
```
ADMIN > SUPER_USER > NORMAL_USER > GUEST
```

### **Default Users**
- **Admin**: `admin/admin123` (change password in production!)
- **Auto-Role Assignment**: New registrations get `NORMAL_USER` role
- **Super User Process**: Requires admin approval

### **Role Permissions**
| Feature | GUEST | NORMAL_USER | SUPER_USER | ADMIN |
|---------|-------|-------------|------------|-------|
| Public content | ✅ | ✅ | ✅ | ✅ |
| Own projects | ❌ | ✅ | ❌ | ✅ |
| All projects (read) | ❌ | ❌ | ✅ | ✅ |
| User management | ❌ | ❌ | ❌ | ✅ |

## 🔧 **Services Available**

### **1. Authentication Service** (`/api/auth`)
- User registration and login
- Google OAuth integration for seamless authentication
- JWT token management with refresh tokens
- Role-based access control (4 roles)
- Admin approval workflow for super users

### **2. Portfolio Service** (`/api/portfolio`)
- CRUD operations for personal projects
- Public/private project visibility control
- Technology stack tracking
- Project categorization and status management
- User-specific project filtering

### **3. Public Service** (`/api/public`) - No Auth Required
- Guest access to public portfolio projects
- Public project statistics and analytics
- Featured projects showcase
- Technology-based project filtering

### **4. Admin Service** (`/api/admin`)
- User role management
- Super user approval workflow
- System administration endpoints

## 🏗️ **Database Schema Overview**

### **Authentication Tables**
- `auth_users` - User accounts with role relationships
- `auth_roles` - Role definitions (GUEST, NORMAL_USER, SUPER_USER, ADMIN)
- `auth_user_roles` - User-role relationships
- `auth_refresh_tokens` - JWT refresh token management

### **Portfolio Tables**
- `portfolio_projects` - User projects and portfolios
- `portfolio_project_technologies` - Technology associations

## 🌐 **API Overview**

### **Authentication Endpoints**
```bash
POST /api/auth/register          # Register new user (NORMAL_USER role)
POST /api/auth/register-super-user  # Request super user access (requires approval)
POST /api/auth/login             # User authentication
POST /api/auth/refresh           # Refresh JWT tokens
POST /api/auth/logout            # Invalidate tokens
GET  /api/auth/me               # Get current user info
```

### **Portfolio Endpoints**
```bash
GET    /api/portfolio/projects        # Get user projects (paginated)
POST   /api/portfolio/projects        # Create new project
GET    /api/portfolio/projects/{id}   # Get specific project
PUT    /api/portfolio/projects/{id}   # Update project
DELETE /api/portfolio/projects/{id}   # Delete project
GET    /api/portfolio/projects/stats  # Get project statistics
```

### **Admin Endpoints**
```bash
GET  /api/admin/pending-approvals     # Get pending super user requests
POST /api/admin/approve-super-user    # Approve/reject super user
PUT  /api/admin/users/{id}/role       # Update user role directly
POST /api/admin/register-super-user   # Create super user (admin bypass)
```

## 🏢 **Corporate Environment Support**

### **Network-Friendly Features**
- ✅ **Maven Wrapper** - No admin installation required
- ✅ **Proxy Support** - Configurable for corporate networks
- ✅ **H2 Database** - No external database setup needed for development
- ✅ **Spring Initializr Fallback** - Alternative if network restrictions exist

**Network Issues?** See [LOCAL_SETUP.md](guides/LOCAL_SETUP.md) for troubleshooting.

## ⚛️ **React Integration Example**

### **Authentication Context**
```javascript
const { login, user, hasRole, logout } = useAuth();

// Role-based rendering
{hasRole('ADMIN') && <AdminPanel />}
{hasRole('SUPER_USER') && <AnalyticsView />}
{hasRole('NORMAL_USER') && <Portfolio />}
```

### **API Integration**
```javascript
// Authenticated API calls
const response = await portfolioAPI.getProjects({
  page: 0, size: 10, sortBy: 'createdAt'
});

// Role-based API access
if (hasRole('ADMIN')) {
  await adminAPI.getPendingApprovals();
}
```

**Complete Guide:** [REACT_INTEGRATION.md](guides/REACT_INTEGRATION.md)

## 🔧 **Adding New Services**

### **1. Create Package Structure**
```
src/main/java/com/vira/newservice/
├── controller/
├── service/
├── repository/
├── model/
└── dto/
```

### **2. Create Database Migration**
```sql
-- src/main/resources/db/migration/V3__Create_newservice_tables.sql
CREATE TABLE newservice_data (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id BIGINT REFERENCES auth_users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **3. Implement Endpoints**
```java
@RestController
@RequestMapping("/api/newservice")
@CrossOrigin(origins = {"http://localhost:3000"})
@PreAuthorize("hasRole('NORMAL_USER') or hasRole('SUPER_USER') or hasRole('ADMIN')")
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

# Generate test coverage report
./mvnw test jacoco:report

# Clean build
./mvnw clean package
```

### **Database Management**
```bash
# Access H2 console (development)
# URL: http://localhost:8080/h2-console
# JDBC URL: jdbc:h2:mem:viradb
# Username: sa, Password: (empty)

# Run database migrations
./mvnw flyway:migrate

# Generate migration from JPA entities
./mvnw flyway:baseline
```

### **API Testing**
```bash
# Health check
curl http://localhost:8080/actuator/health

# API documentation
open http://localhost:8080/swagger-ui/index.html

# Test authentication
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 🎯 **Production Ready Features**

### **Security**
- ✅ **JWT Authentication** with configurable expiration
- ✅ **Role-Based Authorization** with 4-tier hierarchy
- ✅ **BCrypt Password Hashing** with high cost factor
- ✅ **CORS Configuration** for production domains
- ✅ **Security Headers** and XSS protection
- ✅ **Admin User Management** with secure defaults

### **Database**
- ✅ **Flyway Migrations** for version control
- ✅ **Connection Pooling** (HikariCP)
- ✅ **Automatic Timestamps** for audit trails
- ✅ **Relationship Integrity** with foreign keys
- ✅ **Indexing Strategy** for performance

### **Monitoring**
- ✅ **Spring Boot Actuator** for health checks
- ✅ **Comprehensive Logging** with security events
- ✅ **Error Handling** with consistent API responses
- ✅ **Request/Response Validation** 

### **Testing**
- ✅ **80% Code Coverage** requirement
- ✅ **Unit Tests** for all service classes
- ✅ **Integration Tests** for API endpoints
- ✅ **Security Tests** for authentication
- ✅ **Repository Tests** for database operations

## 🚀 **Quick Links**

- **Start Development**: [LOCAL_SETUP.md](guides/LOCAL_SETUP.md)
- **Deploy to Production**: [DEPLOYMENT.md](guides/DEPLOYMENT.md)
- **Integrate with React**: [REACT_INTEGRATION.md](guides/REACT_INTEGRATION.md)
- **Manage User Roles**: [ROLE_MANAGEMENT.md](guides/ROLE_MANAGEMENT.md)
- **Security Best Practices**: [SECURITY.md](guides/SECURITY.md)
- **Add New Service**: [NEW_SERVICE_GUIDE.md](guides/NEW_SERVICE_GUIDE.md)

**🚀 Ready to start development?** Follow the [LOCAL_SETUP.md](guides/LOCAL_SETUP.md) guide to get started!

**🌐 Ready to deploy?** Follow the [DEPLOYMENT.md](guides/DEPLOYMENT.md) guide for Railway deployment!

**⚛️ Building a React frontend?** Check out [REACT_INTEGRATION.md](guides/REACT_INTEGRATION.md)!

---

**🎯 Built for scalability, security, and developer productivity. Start building amazing projects today!** 🚀 