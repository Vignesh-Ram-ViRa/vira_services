# Testing Guide - Vira Services

## 🎯 **Testing Philosophy**

All services in Vira Services **MUST** have comprehensive test coverage to ensure reliability, maintainability, and confidence in deployments. This guide covers testing standards, practices, and examples for all service layers.

## 📋 **Testing Requirements**

### **Mandatory Requirements**
- ✅ **Minimum 80% code coverage** for all services
- ✅ **Unit tests** for all service classes
- ✅ **Integration tests** for all API endpoints
- ✅ **Repository tests** for all database operations
- ✅ **Security tests** for authentication and authorization
- ✅ **Validation tests** for all DTOs and request objects

### **Test Categories**
- **Unit Tests**: Fast, isolated tests with mocked dependencies
- **Integration Tests**: Tests with real database and Spring context
- **Security Tests**: Authentication and authorization scenarios
- **Validation Tests**: Input validation and error handling

## 🏗️ **Test Structure**

### **Directory Structure**
```
src/test/java/com/vira/
├── config/                       # Test configurations
│   ├── TestConfig.java
│   └── TestDataConfig.java
├── auth/                         # Authentication service tests
│   ├── controller/
│   │   ├── AuthControllerTest.java           # Unit tests
│   │   └── AuthControllerIntegrationTest.java # Integration tests
│   ├── service/
│   │   └── AuthServiceTest.java
│   ├── repository/
│   │   └── UserRepositoryTest.java
│   └── security/
│       └── JwtAuthenticationTest.java
├── portfolio/                    # Portfolio service tests
│   ├── controller/
│   │   ├── PortfolioControllerTest.java
│   │   └── PortfolioControllerIntegrationTest.java
│   ├── service/
│   │   └── PortfolioServiceTest.java
│   └── repository/
│       └── ProjectRepositoryTest.java
└── common/                       # Shared test utilities
    ├── TestDataFactory.java
    ├── TestUtils.java
    └── BaseIntegrationTest.java
```

## 🧪 **Unit Testing**

### **Unit Test Standards**
- **Fast execution** (< 1 second per test)
- **Isolated** (no external dependencies)
- **Mocked dependencies** using @Mock or @MockBean
- **High coverage** of business logic paths
- **Clear test names** describing the scenario

### **Example: Service Unit Test**
```java
// src/test/java/com/vira/portfolio/service/PortfolioServiceTest.java
@ExtendWith(MockitoExtension.class)
class PortfolioServiceTest {

    @Mock
    private ProjectRepository projectRepository;

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private PortfolioService portfolioService;

    @Test
    void shouldCreateProjectSuccessfully() {
        // Given
        Long userId = 1L;
        ProjectRequest request = ProjectRequest.builder()
            .title("Test Project")
            .description("Test Description")
            .technologies(Arrays.asList("Java", "Spring Boot"))
            .build();
        
        User user = new User();
        user.setId(userId);
        
        Project savedProject = new Project();
        savedProject.setId(1L);
        savedProject.setTitle(request.getTitle());
        savedProject.setUser(user);

        when(userRepository.findById(userId)).thenReturn(Optional.of(user));
        when(projectRepository.save(any(Project.class))).thenReturn(savedProject);

        // When
        ProjectResponse response = portfolioService.createProject(userId, request);

        // Then
        assertThat(response).isNotNull();
        assertThat(response.getTitle()).isEqualTo("Test Project");
        verify(projectRepository).save(any(Project.class));
    }

    @Test
    void shouldThrowExceptionWhenUserNotFound() {
        // Given
        Long userId = 1L;
        ProjectRequest request = new ProjectRequest();
        
        when(userRepository.findById(userId)).thenReturn(Optional.empty());

        // When & Then
        assertThrows(UserNotFoundException.class, 
            () -> portfolioService.createProject(userId, request));
        
        verify(projectRepository, never()).save(any());
    }

    @Test
    void shouldUpdateProjectSuccessfully() {
        // Given
        Long projectId = 1L;
        Long userId = 1L;
        ProjectRequest updateRequest = ProjectRequest.builder()
            .title("Updated Title")
            .description("Updated Description")
            .build();

        User user = new User();
        user.setId(userId);

        Project existingProject = new Project();
        existingProject.setId(projectId);
        existingProject.setUser(user);
        existingProject.setTitle("Original Title");

        when(projectRepository.findById(projectId)).thenReturn(Optional.of(existingProject));
        when(projectRepository.save(any(Project.class))).thenAnswer(i -> i.getArgument(0));

        // When
        ProjectResponse response = portfolioService.updateProject(projectId, userId, updateRequest);

        // Then
        assertThat(response.getTitle()).isEqualTo("Updated Title");
        verify(projectRepository).save(existingProject);
    }
}
```

### **Example: Controller Unit Test**
```java
// src/test/java/com/vira/portfolio/controller/PortfolioControllerTest.java
@WebMvcTest(PortfolioController.class)
@Import(SecurityConfig.class)
class PortfolioControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private PortfolioService portfolioService;

    @MockBean
    private JwtAuthenticationEntryPoint jwtAuthenticationEntryPoint;

    @MockBean
    private JwtRequestFilter jwtRequestFilter;

    @Test
    @WithMockUser(username = "testuser")
    void shouldCreateProjectSuccessfully() throws Exception {
        // Given
        ProjectRequest request = ProjectRequest.builder()
            .title("Test Project")
            .description("Test Description")
            .build();

        ProjectResponse response = ProjectResponse.builder()
            .id(1L)
            .title("Test Project")
            .description("Test Description")
            .build();

        when(portfolioService.createProject(anyLong(), any(ProjectRequest.class)))
            .thenReturn(response);

        // When & Then
        mockMvc.perform(post("/api/portfolio/projects")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.title").value("Test Project"))
                .andExpect(jsonPath("$.description").value("Test Description"));
    }

    @Test
    void shouldRequireAuthentication() throws Exception {
        // Given
        ProjectRequest request = new ProjectRequest();

        // When & Then
        mockMvc.perform(post("/api/portfolio/projects")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isUnauthorized());
    }
}
```

## 🔗 **Integration Testing**

### **Integration Test Standards**
- **Real Spring context** with @SpringBootTest
- **Test database** (H2 or PostgreSQL test container)
- **Full request/response cycle** testing
- **Database state verification**
- **Authentication flow testing**

### **Base Integration Test Class**
```java
// src/test/java/com/vira/common/BaseIntegrationTest.java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@ActiveProfiles("test")
@Transactional
@TestMethodOrder(OrderAnnotation.class)
public abstract class BaseIntegrationTest {

    @Autowired
    protected TestRestTemplate restTemplate;

    @Autowired
    protected TestEntityManager testEntityManager;

    @Value("${local.server.port}")
    protected int port;

    protected String getBaseUrl() {
        return "http://localhost:" + port;
    }

    protected HttpHeaders createAuthHeaders(String token) {
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + token);
        headers.setContentType(MediaType.APPLICATION_JSON);
        return headers;
    }

    protected String authenticateUser(String username, String password) {
        LoginRequest loginRequest = new LoginRequest(username, password);
        HttpEntity<LoginRequest> request = new HttpEntity<>(loginRequest);
        
        ResponseEntity<AuthResponse> response = restTemplate.postForEntity(
            getBaseUrl() + "/api/auth/login", 
            request, 
            AuthResponse.class
        );
        
        return response.getBody().getToken();
    }
}
```

### **Example: Integration Test**
```java
// src/test/java/com/vira/portfolio/controller/PortfolioControllerIntegrationTest.java
@Sql(scripts = "/test-data.sql", executionPhase = Sql.ExecutionPhase.BEFORE_TEST_METHOD)
@Sql(scripts = "/cleanup.sql", executionPhase = Sql.ExecutionPhase.AFTER_TEST_METHOD)
class PortfolioControllerIntegrationTest extends BaseIntegrationTest {

    @Test
    @Order(1)
    void shouldCreateProjectWithAuthentication() {
        // Given
        String token = authenticateUser("testuser", "password");
        
        ProjectRequest request = ProjectRequest.builder()
            .title("Integration Test Project")
            .description("Created via integration test")
            .technologies(Arrays.asList("Java", "Spring Boot", "PostgreSQL"))
            .status("completed")
            .category("Backend API")
            .year(2024)
            .featured(true)
            .build();

        HttpEntity<ProjectRequest> entity = new HttpEntity<>(request, createAuthHeaders(token));

        // When
        ResponseEntity<ProjectResponse> response = restTemplate.postForEntity(
            getBaseUrl() + "/api/portfolio/projects",
            entity,
            ProjectResponse.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getTitle()).isEqualTo("Integration Test Project");
        assertThat(response.getBody().getId()).isNotNull();
    }

    @Test
    @Order(2)
    void shouldGetAllProjectsWithPagination() {
        // Given
        String token = authenticateUser("testuser", "password");
        HttpEntity<String> entity = new HttpEntity<>(createAuthHeaders(token));

        // When
        ResponseEntity<PagedProjectResponse> response = restTemplate.exchange(
            getBaseUrl() + "/api/portfolio/projects?page=0&size=10",
            HttpMethod.GET,
            entity,
            PagedProjectResponse.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().getContent()).isNotEmpty();
    }

    @Test
    void shouldReturnUnauthorizedWithoutToken() {
        // Given
        ProjectRequest request = new ProjectRequest();
        HttpEntity<ProjectRequest> entity = new HttpEntity<>(request);

        // When
        ResponseEntity<String> response = restTemplate.postForEntity(
            getBaseUrl() + "/api/portfolio/projects",
            entity,
            String.class
        );

        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }
}
```

## 🛡️ **Security Testing**

### **Authentication Tests**
```java
// src/test/java/com/vira/auth/security/JwtAuthenticationTest.java
@SpringBootTest
@ActiveProfiles("test")
class JwtAuthenticationTest {

    @Autowired
    private JwtUtils jwtUtils;

    @Test
    void shouldGenerateValidJwtToken() {
        // Given
        String username = "testuser";
        
        // When
        String token = jwtUtils.generateToken(username);
        
        // Then
        assertThat(token).isNotNull();
        assertThat(jwtUtils.validateToken(token)).isTrue();
        assertThat(jwtUtils.getUsernameFromToken(token)).isEqualTo(username);
    }

    @Test
    void shouldRejectExpiredToken() {
        // Given
        String expiredToken = generateExpiredToken();
        
        // When & Then
        assertThat(jwtUtils.validateToken(expiredToken)).isFalse();
    }

    @Test
    void shouldRejectInvalidSignature() {
        // Given
        String tokenWithInvalidSignature = "invalid.jwt.token";
        
        // When & Then
        assertThat(jwtUtils.validateToken(tokenWithInvalidSignature)).isFalse();
    }
}
```

## 🗄️ **Repository Testing**

### **Example: Repository Test**
```java
// src/test/java/com/vira/portfolio/repository/ProjectRepositoryTest.java
@DataJpaTest
@ActiveProfiles("test")
class ProjectRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private ProjectRepository projectRepository;

    @Test
    void shouldFindProjectsByUserId() {
        // Given
        User user = new User();
        user.setUsername("testuser");
        user.setEmail("test@example.com");
        user = entityManager.persistAndFlush(user);

        Project project1 = new Project();
        project1.setTitle("Project 1");
        project1.setUser(user);
        entityManager.persistAndFlush(project1);

        Project project2 = new Project();
        project2.setTitle("Project 2");
        project2.setUser(user);
        entityManager.persistAndFlush(project2);

        // When
        List<Project> projects = projectRepository.findByUserId(user.getId());

        // Then
        assertThat(projects).hasSize(2);
        assertThat(projects).extracting(Project::getTitle)
            .containsExactlyInAnyOrder("Project 1", "Project 2");
    }

    @Test
    void shouldFindFeaturedProjects() {
        // Given
        User user = createAndPersistUser();
        
        Project featuredProject = new Project();
        featuredProject.setTitle("Featured Project");
        featuredProject.setFeatured(true);
        featuredProject.setUser(user);
        entityManager.persistAndFlush(featuredProject);

        Project nonFeaturedProject = new Project();
        nonFeaturedProject.setTitle("Regular Project");
        nonFeaturedProject.setFeatured(false);
        nonFeaturedProject.setUser(user);
        entityManager.persistAndFlush(nonFeaturedProject);

        // When
        List<Project> featuredProjects = projectRepository.findByFeaturedTrue();

        // Then
        assertThat(featuredProjects).hasSize(1);
        assertThat(featuredProjects.get(0).getTitle()).isEqualTo("Featured Project");
    }
}
```

## ✅ **Validation Testing**

### **DTO Validation Tests**
```java
// src/test/java/com/vira/portfolio/dto/ProjectRequestValidationTest.java
class ProjectRequestValidationTest {

    private Validator validator;

    @BeforeEach
    void setUp() {
        ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @Test
    void shouldPassValidationWithValidData() {
        // Given
        ProjectRequest request = ProjectRequest.builder()
            .title("Valid Title")
            .description("Valid description")
            .technologies(Arrays.asList("Java", "Spring"))
            .status("completed")
            .category("Backend")
            .year(2024)
            .build();

        // When
        Set<ConstraintViolation<ProjectRequest>> violations = validator.validate(request);

        // Then
        assertThat(violations).isEmpty();
    }

    @Test
    void shouldFailValidationWithEmptyTitle() {
        // Given
        ProjectRequest request = ProjectRequest.builder()
            .title("")
            .description("Valid description")
            .build();

        // When
        Set<ConstraintViolation<ProjectRequest>> violations = validator.validate(request);

        // Then
        assertThat(violations).hasSize(1);
        assertThat(violations.iterator().next().getMessage())
            .contains("Title cannot be blank");
    }

    @Test
    void shouldFailValidationWithInvalidYear() {
        // Given
        ProjectRequest request = ProjectRequest.builder()
            .title("Valid Title")
            .year(1999) // Invalid year
            .build();

        // When
        Set<ConstraintViolation<ProjectRequest>> violations = validator.validate(request);

        // Then
        assertThat(violations).hasSize(1);
        assertThat(violations.iterator().next().getMessage())
            .contains("Year must be between 2000 and 2030");
    }
}
```

## 🔧 **Test Configuration**

### **Test Application Properties**
```yaml
# src/test/resources/application-test.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
    driver-class-name: org.h2.Driver
    username: sa
    password: password
  
  jpa:
    hibernate:
      ddl-auto: create-drop
    database-platform: org.hibernate.dialect.H2Dialect
    show-sql: true
  
  flyway:
    enabled: false  # Disable for tests, use ddl-auto instead

logging:
  level:
    org.springframework.security: DEBUG
    com.vira: DEBUG
    org.springframework.test: DEBUG

app:
  jwt:
    secret: test-secret-key-for-testing-purposes-only
    expiration: 3600000  # 1 hour for tests
```

### **Test Data Setup**
```sql
-- src/test/resources/test-data.sql
INSERT INTO auth_users (id, username, email, password_hash, created_at) 
VALUES (1, 'testuser', 'test@example.com', '$2a$10$encrypted.password.hash', NOW());

INSERT INTO auth_roles (id, name, description) 
VALUES (1, 'USER', 'Standard user role');

INSERT INTO auth_user_roles (user_id, role_id) 
VALUES (1, 1);
```

```sql
-- src/test/resources/cleanup.sql
DELETE FROM auth_user_roles;
DELETE FROM auth_refresh_tokens;
DELETE FROM portfolio_projects;
DELETE FROM auth_users;
DELETE FROM auth_roles;
```

## 📊 **Test Coverage Requirements**

### **Coverage Targets**
- **Overall Coverage**: Minimum 80%
- **Service Layer**: Minimum 90%
- **Controller Layer**: Minimum 85%
- **Repository Layer**: Minimum 80%
- **Security Components**: Minimum 95%

### **Coverage Report Generation**
```bash
# Generate coverage report
./mvnw test jacoco:report

# View HTML report
open target/site/jacoco/index.html

# Check coverage thresholds
./mvnw jacoco:check
```

### **JaCoCo Configuration**
```xml
<!-- pom.xml -->
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.8</version>
    <executions>
        <execution>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
        <execution>
            <id>check</id>
            <goals>
                <goal>check</goal>
            </goals>
            <configuration>
                <rules>
                    <rule>
                        <element>CLASS</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

## 🚀 **Running Tests**

### **Local Testing Commands**
```bash
# Run all tests
./mvnw test

# Run unit tests only
./mvnw test -Dgroups=unit

# Run integration tests only
./mvnw test -Dgroups=integration

# Run specific test class
./mvnw test -Dtest=PortfolioServiceTest

# Run with coverage
./mvnw test jacoco:report

# Run tests in watch mode (with spring-boot-devtools)
./mvnw test -Dspring-boot.run.fork=false
```

### **CI/CD Integration**
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-java@v3
        with:
          java-version: '17'
      
      - name: Run tests
        run: ./mvnw test
      
      - name: Generate coverage report
        run: ./mvnw jacoco:report
      
      - name: Check coverage thresholds
        run: ./mvnw jacoco:check
```

## 📝 **Testing Best Practices**

### **Naming Conventions**
- Test classes: `ClassNameTest` (unit) or `ClassNameIntegrationTest`
- Test methods: `should[ExpectedBehavior]When[StateUnderTest]`
- Example: `shouldCreateProjectSuccessfullyWhenValidDataProvided`

### **Test Organization**
- **Given-When-Then** structure for all tests
- **Arrange-Act-Assert** pattern
- **One assertion per test** (when possible)
- **Descriptive test names** that explain the scenario

### **Mock Usage**
- **Mock external dependencies** in unit tests
- **Use real implementations** in integration tests
- **Verify interactions** with mocks when behavior matters
- **Avoid over-mocking** - test real behavior when possible

### **Test Data Management**
- **Use builders** for test data creation
- **Create factory methods** for common test objects
- **Clean up test data** after each test
- **Use meaningful test data** that represents real scenarios

---

## 🎯 **Testing Checklist for New Services**

When adding a new service, ensure:

- ✅ **Unit tests** for all service methods
- ✅ **Controller tests** for all endpoints
- ✅ **Repository tests** for custom queries
- ✅ **Integration tests** for complete request flows
- ✅ **Security tests** for authentication/authorization
- ✅ **Validation tests** for all DTOs
- ✅ **Error handling tests** for exception scenarios
- ✅ **Coverage report** shows minimum 80% coverage
- ✅ **All tests pass** in CI/CD pipeline
- ✅ **Test documentation** updated in this guide

**Remember: Good tests are your safety net for refactoring and adding new features!** 🛡️ 