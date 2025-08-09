# Production Security Guide

> **Comprehensive security best practices for Vira Services in production**

## 🔐 **Security Overview**

This guide covers essential security measures for production deployment:
- **Admin User Security** and management
- **API Protection** and access control
- **Network Security** and encryption
- **Data Protection** and privacy
- **Monitoring** and incident response

## 🚨 **Critical Security Tasks**

### 1. Admin User Security

**⚠️ IMMEDIATE ACTION REQUIRED:**

The application auto-creates a default admin user:
- **Username**: `admin`
- **Default Password**: `admin123`

**🔒 Secure Your Admin Account (Choose One):**

**Option A: Environment Variable (Recommended)**
```bash
# Set secure password via Railway environment variables
ADMIN_PASSWORD=YourVerySecurePassword123!@#$%

# Requirements:
# - At least 12 characters
# - Mix of letters, numbers, symbols
# - Not dictionary words
# - Unique to this application
```

**Option B: Change After First Login**
1. Login with default credentials
2. Create new admin user via API
3. Delete default admin user
4. Document new credentials securely

**Option C: Disable Default Admin**
```java
// Add to application-prod.yml
app:
  create-default-admin: false

// Manually create admin via database or special endpoint
```

### 2. JWT Security

**Configure Strong JWT Settings:**

```yaml
# application-prod.yml
jwt:
  secret: ${JWT_SECRET}  # Must be 64+ characters
  expiration: 3600000    # 1 hour (short for security)
  refresh-expiration: 604800000  # 7 days
```

**Generate Secure JWT Secret:**
```bash
# Generate cryptographically secure secret
openssl rand -base64 64

# Example output (use your own):
# mYsUperSecUr3JWTsecr3tK3yTh4tIsAtLe4st64Ch4r4ct3rsL0ngF0rPr0ducti0nUs3
```

**JWT Best Practices:**
- ✅ Use environment variables for secrets
- ✅ Short expiration times (1 hour)
- ✅ Implement refresh token rotation
- ✅ Validate tokens on every request
- ✅ Log failed authentication attempts

### 3. Database Security

**PostgreSQL Security:**
```yaml
# Use strong credentials
DATABASE_USERNAME=vira_prod_user
DATABASE_PASSWORD=VeryStr0ngD4t4b4seP4ssw0rd!

# Connection encryption
spring:
  datasource:
    url: ${DATABASE_URL}?ssl=true&sslmode=require
```

**Database Best Practices:**
- ✅ Use dedicated database user
- ✅ Enable SSL/TLS encryption
- ✅ Regular automated backups
- ✅ Restrict database access by IP
- ✅ Monitor database connections

## 🌐 **API Security Layers**

### 1. CORS Configuration

**Production CORS Settings:**
```yaml
# application-prod.yml
cors:
  allowed-origins:
    - "https://yourdomain.com"
    - "https://app.yourdomain.com"
  allowed-methods: GET,POST,PUT,DELETE,OPTIONS,PATCH
  allowed-headers: Authorization,Content-Type,X-Requested-With
  allow-credentials: true
  max-age: 3600
```

**❌ Never Allow in Production:**
```yaml
# NEVER DO THIS IN PRODUCTION
cors:
  allowed-origins: "*"  # Too permissive
```

### 2. Rate Limiting (Recommended Enhancement)

**Add Rate Limiting:**
```java
@Component
public class RateLimitingFilter implements Filter {
    private final Map<String, AtomicInteger> requests = new ConcurrentHashMap<>();
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {
        String clientIP = getClientIP((HttpServletRequest) request);
        
        // Allow 100 requests per hour per IP
        AtomicInteger requestCount = requests.computeIfAbsent(clientIP, k -> new AtomicInteger(0));
        
        if (requestCount.incrementAndGet() > 100) {
            throw new SecurityException("Rate limit exceeded");
        }
        
        chain.doFilter(request, response);
    }
}
```

### 3. API Key Authentication (Optional)

**For Additional API Security:**
```java
@Component
public class ApiKeyFilter implements Filter {
    private static final String API_KEY_HEADER = "X-API-Key";
    
    @Value("${app.api.keys}")
    private Set<String> validApiKeys;
    
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {
        String apiKey = ((HttpServletRequest) request).getHeader(API_KEY_HEADER);
        
        if (!validApiKeys.contains(apiKey)) {
            throw new SecurityException("Invalid API key");
        }
        
        chain.doFilter(request, response);
    }
}
```

## 🔒 **Network Security**

### 1. HTTPS Configuration

**Railway automatically provides HTTPS, but ensure:**
```yaml
# Force HTTPS redirects
server:
  ssl:
    enabled: true
  port: ${PORT:8080}

# Security headers
security:
  headers:
    frame-options: DENY
    content-type-options: nosniff
    xss-protection: "1; mode=block"
```

### 2. Security Headers

**Add Security Headers Filter:**
```java
@Component
public class SecurityHeadersFilter implements Filter {
    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) {
        HttpServletResponse httpResponse = (HttpServletResponse) response;
        
        // Security headers
        httpResponse.setHeader("X-Content-Type-Options", "nosniff");
        httpResponse.setHeader("X-Frame-Options", "DENY");
        httpResponse.setHeader("X-XSS-Protection", "1; mode=block");
        httpResponse.setHeader("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
        httpResponse.setHeader("Content-Security-Policy", "default-src 'self'");
        
        chain.doFilter(request, response);
    }
}
```

### 3. Input Validation

**Strict Input Validation:**
```java
// Use validation annotations
@Valid
@Size(min = 3, max = 50, message = "Username must be 3-50 characters")
@Pattern(regexp = "^[a-zA-Z0-9_]+$", message = "Username can only contain letters, numbers, and underscores")
private String username;

// Sanitize inputs
@PrePersist
@PreUpdate
public void sanitizeInputs() {
    this.username = StringEscapeUtils.escapeHtml4(this.username);
    this.email = StringEscapeUtils.escapeHtml4(this.email);
}
```

## 📊 **Monitoring & Logging**

### 1. Security Logging

**Enhanced Security Logging:**
```java
@Component
public class SecurityAuditLogger {
    private static final Logger logger = LoggerFactory.getLogger("SECURITY_AUDIT");
    
    @EventListener
    public void auditAuthenticationSuccess(AuthenticationSuccessEvent event) {
        logger.info("LOGIN_SUCCESS: user={}, ip={}, timestamp={}", 
            event.getAuthentication().getName(),
            getClientIP(),
            LocalDateTime.now());
    }
    
    @EventListener
    public void auditAuthenticationFailure(AbstractAuthenticationFailureEvent event) {
        logger.warn("LOGIN_FAILURE: user={}, ip={}, reason={}, timestamp={}", 
            event.getAuthentication().getName(),
            getClientIP(),
            event.getException().getMessage(),
            LocalDateTime.now());
    }
}
```

### 2. Failed Login Monitoring

**Track Failed Login Attempts:**
```java
@Service
public class LoginAttemptService {
    private final Map<String, AtomicInteger> attempts = new ConcurrentHashMap<>();
    
    public void loginFailed(String key) {
        int attemptCount = attempts.computeIfAbsent(key, k -> new AtomicInteger(0)).incrementAndGet();
        
        if (attemptCount >= 5) {
            logger.warn("SECURITY_ALERT: Too many failed login attempts from IP: {}", key);
            // Consider temporary IP blocking
        }
    }
    
    public void loginSucceeded(String key) {
        attempts.remove(key);
    }
}
```

### 3. Health Monitoring

**Security Health Checks:**
```java
@Component
public class SecurityHealthIndicator implements HealthIndicator {
    @Override
    public Health health() {
        // Check database connectivity
        // Verify JWT service
        // Check authentication service
        // Validate security configurations
        
        return Health.up()
            .withDetail("auth", "OK")
            .withDetail("database", "OK")
            .withDetail("jwt", "OK")
            .build();
    }
}
```

## 🚨 **Incident Response**

### 1. Security Alerts

**Set Up Monitoring for:**
- Multiple failed login attempts
- Unusual API usage patterns
- Database connection issues
- JWT token validation failures
- Admin account usage

### 2. Response Actions

**If Security Breach Suspected:**
1. **Immediate**: Change all passwords and JWT secrets
2. **Audit**: Check logs for unauthorized access
3. **Notify**: Inform users if data compromised
4. **Update**: Apply security patches
5. **Review**: Update security policies

### 3. Regular Security Tasks

**Weekly:**
- [ ] Review authentication logs
- [ ] Check for failed login patterns
- [ ] Monitor API usage statistics
- [ ] Verify backup integrity

**Monthly:**
- [ ] Update dependencies for security patches
- [ ] Review and rotate secrets
- [ ] Audit user accounts and permissions
- [ ] Test incident response procedures

## 🔐 **Data Protection**

### 1. Sensitive Data Handling

**Password Security:**
```java
// Strong password hashing
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12); // High cost factor
}

// Password validation
@Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$",
         message = "Password must contain uppercase, lowercase, number, and special character")
private String password;
```

**Personal Data Protection:**
```java
// Encrypt sensitive fields
@Convert(converter = AttributeEncryptor.class)
private String sensitiveData;

// Audit data access
@EntityListeners(DataAccessAuditListener.class)
public class User {
    // User entity
}
```

### 2. Database Encryption

**Enable Encryption at Rest:**
```yaml
# PostgreSQL configuration
spring:
  datasource:
    url: ${DATABASE_URL}?ssl=true&sslmode=require
    hikari:
      connection-init-sql: "SET application_name = 'vira-services'"
```

## ✅ **Security Checklist**

### Immediate Actions (Before Going Live)
- [ ] Change default admin password
- [ ] Generate and set secure JWT secret (64+ chars)
- [ ] Configure production CORS settings
- [ ] Enable HTTPS (Railway provides this)
- [ ] Set up strong database credentials
- [ ] Review all environment variables

### Authentication & Authorization
- [ ] JWT tokens expire in reasonable time (1 hour)
- [ ] Refresh token rotation implemented
- [ ] Role-based access control working
- [ ] Failed login attempts logged
- [ ] Strong password requirements enforced

### API Security
- [ ] Input validation on all endpoints
- [ ] SQL injection protection enabled
- [ ] XSS protection headers set
- [ ] Rate limiting considered/implemented
- [ ] CORS configured for production domains only

### Infrastructure Security
- [ ] Database access restricted
- [ ] Environment variables secured
- [ ] Logs configured and monitored
- [ ] Backup strategy implemented
- [ ] SSL/TLS encryption enabled

### Monitoring & Response
- [ ] Security logging implemented
- [ ] Health checks configured
- [ ] Incident response plan documented
- [ ] Regular security review scheduled

## 🔗 **Security Resources**

### Tools and References
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Spring Security Reference**: https://spring.io/projects/spring-security
- **JWT Best Practices**: https://tools.ietf.org/html/rfc8725
- **Railway Security**: https://docs.railway.app/deploy/security

### Related Guides
- **Deployment**: `guides/DEPLOYMENT.md`
- **Role Management**: `guides/ROLE_MANAGEMENT.md`
- **Local Setup**: `guides/LOCAL_SETUP.md`

---

**🛡️ Security is an ongoing process, not a one-time setup. Stay vigilant and keep your systems updated!** 🚀 