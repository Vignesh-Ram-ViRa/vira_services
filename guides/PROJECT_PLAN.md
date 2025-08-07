# Vira Services - Multi-Project Backend Repository

## 📋 Project Requirements Brief

### Vision
Create a centralized Spring Boot backend repository that can serve multiple mini projects with a single PostgreSQL database and shared authentication system. The goal is to host all APIs in one repository and add new service endpoints (organized by folders) as new projects are developed.

### Key Requirements
- **Single Repository Architecture**: One repo for all APIs to simplify hosting and management
- **Shared Database**: Single PostgreSQL instance for all services
- **Local to Cloud Migration**: Currently using local APIs/DBs, moving to hosted solutions
- **Small Scale**: Designed for personal use, maximum 5 users
- **CRUD Focus**: Most endpoints will be simple CRUD operations
- **Free Hosting**: Must use free tier hosting solutions
- **React Integration**: Backend will serve React frontend applications

### Target Use Cases
- Hobby dashboards
- Finance tracker applications
- AI tools library
- Personal creations/portfolio library
- Future mini projects as needed

### Technical Constraints
- Java Spring Boot (developer has 5+ years old experience, needs guidance)
- PostgreSQL database
- JWT-based authentication
- Free hosting platform
- React frontend integration
- Step-by-step deployment documentation required

## 🎯 Action Plan

### 🏗️ Repository Structure
```
vira-services/
├── src/main/java/com/vira/
│   ├── ViraServicesApplication.java
│   ├── config/                   # Shared configurations
│   │   ├── SecurityConfig.java
│   │   ├── JwtConfig.java
│   │   └── CorsConfig.java
│   ├── common/                   # Shared utilities
│   │   ├── dto/ApiResponse.java
│   │   ├── exception/GlobalExceptionHandler.java
│   │   └── utils/JwtUtils.java
│   ├── auth/                     # Authentication Service
│   │   ├── controller/AuthController.java
│   │   ├── service/AuthService.java
│   │   ├── repository/UserRepository.java
│   │   ├── model/User.java
│   │   └── dto/{LoginRequest, RegisterRequest, AuthResponse}.java
│   └── portfolio/                # Portfolio/Projects Service
│       ├── controller/PortfolioController.java
│       ├── service/PortfolioService.java
│       ├── repository/ProjectRepository.java
│       ├── model/Project.java
│       └── dto/{ProjectRequest, ProjectResponse}.java
├── src/main/resources/
│   ├── application.yml           # Main configuration
│   ├── application-dev.yml       # Local development
│   ├── application-prod.yml      # Production configuration
│   └── db/migration/             # Flyway database migrations
│       ├── V1__Create_auth_tables.sql
│       └── V2__Create_portfolio_tables.sql
├── docker/                       # Docker configurations
├── guides/                       # Project documentation
├── docs/                         # API documentation
├── pom.xml                       # Maven dependencies
├── README.md                     # Project overview
└── Procfile                      # Deployment configuration
```

### 🗄️ Database Schema Design

#### Authentication Tables
```sql
-- Users table
auth_users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Roles table
auth_roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);

-- User roles junction table
auth_user_roles (
    user_id BIGINT REFERENCES auth_users(id),
    role_id BIGINT REFERENCES auth_roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- Refresh tokens table
auth_refresh_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES auth_users(id),
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Portfolio Service Tables
```sql
-- Projects table for portfolio service
portfolio_projects (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    link VARCHAR(500),              -- Hosted URL
    github VARCHAR(500),            -- GitHub repository URL
    image VARCHAR(500),             -- Image URL or file path
    technologies JSONB,             -- Array of technologies as JSON
    status VARCHAR(50),             -- completed, in-progress, planned
    category VARCHAR(100),          -- Full-Stack Application, etc.
    year INTEGER,
    featured BOOLEAN DEFAULT FALSE,
    user_id BIGINT REFERENCES auth_users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 🚀 API Endpoints Design

#### Authentication Service (`/api/auth`)
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT + refresh token)
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - Logout (invalidate tokens)
- `GET /api/auth/me` - Get current user info

#### Portfolio Service (`/api/portfolio`)
- `GET /api/portfolio/projects` - Get all projects (with pagination)
- `GET /api/portfolio/projects/{id}` - Get specific project
- `POST /api/portfolio/projects` - Create new project
- `PUT /api/portfolio/projects/{id}` - Update project
- `DELETE /api/portfolio/projects/{id}` - Delete project
- `GET /api/portfolio/projects/featured` - Get featured projects
- `GET /api/portfolio/projects/by-category/{category}` - Filter by category

### 📚 Technology Stack

#### Backend Dependencies
- **Spring Boot Starter Web** - REST API framework
- **Spring Boot Starter Security** - Authentication & authorization
- **Spring Boot Starter Data JPA** - Database ORM
- **Spring Boot Starter Validation** - Request validation
- **PostgreSQL Driver** - Database connectivity
- **JJWT** - JWT token handling
- **Flyway** - Database migrations
- **SpringDoc OpenAPI** - API documentation

#### Hosting Platform: Railway
**Selected for:**
- Most user-friendly free tier
- Automatic PostgreSQL provisioning
- Git-based deployments
- Built-in environment management
- 500 hours/month + 1GB PostgreSQL free
- Zero-configuration Spring Boot deployment

### 🎨 Sample Data Model (Portfolio Project)
```json
{
    "id": 1,
    "title": "Enterprise Task Management System",
    "description": "Built a comprehensive task management platform for enterprise teams with real-time collaboration, advanced analytics, and automated workflow management. Features include drag-and-drop task boards, time tracking, and team performance insights.",
    "technologies": ["React", "Node.js", "PostgreSQL", "Socket.io", "Redux"],
    "status": "completed",
    "category": "Full-Stack Application",
    "link": "https://task-manager-enterprise.netlify.app/",
    "github": "https://github.com/vigneshram/enterprise-task-manager",
    "image": "/assets/images/project-task-manager.jpg",
    "featured": true,
    "year": 2023,
    "userId": 1,
    "createdAt": "2023-10-15T10:30:00Z",
    "updatedAt": "2023-10-15T10:30:00Z"
}
```

### 🔄 Development Phases

#### Phase 1: Core Setup
- [ ] Create Spring Boot project structure
- [ ] Configure database connections and migrations
- [ ] Set up security and JWT configuration
- [ ] Implement authentication service
- [ ] Write unit tests for authentication service
- [ ] Write integration tests for auth endpoints

#### Phase 2: Portfolio Service
- [ ] Create portfolio project model and repository
- [ ] Implement CRUD operations
- [ ] Add validation and error handling
- [ ] Write comprehensive unit tests for all service layers
- [ ] Create integration tests for API endpoints
- [ ] Create comprehensive API documentation

#### Phase 3: Documentation & Deployment
- [ ] Create detailed deployment guide for Railway
- [ ] Create React integration guide with examples
- [ ] Set up CI/CD pipeline
- [ ] Deploy to Railway and test

#### Phase 4: Future Expansion
- [ ] Template for adding new services
- [ ] Monitoring and logging setup
- [ ] Performance optimization
- [ ] Additional services as needed

### 📖 Documentation Deliverables

1. **guides/DEPLOYMENT.md** - Step-by-step Railway deployment guide
2. **guides/FRONTEND_INTEGRATION.md** - React integration with code examples
3. **guides/LOCAL_DEVELOPMENT.md** - Local setup and testing guide
4. **guides/TESTING_GUIDE.md** - Comprehensive testing standards
5. **README.md** - Project overview and quick start

### 🎯 Success Criteria

- ✅ Working authentication system with JWT
- ✅ Complete portfolio CRUD service
- ✅ Comprehensive unit test coverage (minimum 80%)
- ✅ Integration tests for all API endpoints
- ✅ Successful deployment on Railway
- ✅ React frontend successfully consuming APIs
- ✅ Comprehensive documentation for future development
- ✅ Scalable architecture for adding new services
- ✅ Production-ready error handling and validation

### 🔗 Future Service Examples

The architecture supports easy addition of:
- **Finance Tracker Service** (`/api/finance`)
- **AI Tools Service** (`/api/ai-tools`)
- **Dashboard Service** (`/api/dashboards`)
- **File Management Service** (`/api/files`)
- **Notification Service** (`/api/notifications`)

Each new service follows the same pattern:
- Separate package under `com.vira.{service}`
- Own controllers, services, repositories, models, DTOs
- Comprehensive unit tests for all service layers
- Integration tests for all API endpoints
- Shared authentication and common utilities
- Database tables with consistent naming: `{service}_{table}`

---

**Ready to start development when explicitly requested!** 🚀 