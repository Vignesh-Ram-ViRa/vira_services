# 🔐 Single Sign-On (SSO) Guide for Vira Services

**Implementing seamless authentication across multiple frontend applications using Vira Services backend**

## 📋 Overview

This guide explains how to implement Single Sign-On (SSO) across multiple frontend applications (e.g., Portfolio App and Ledger App) that share the same Vira Services authentication backend.

## 🎯 Use Case Example

- **Portfolio App**: Lists all your projects and services
- **Ledger App**: Financial management and tracking
- **Shared Backend**: Vira Services with JWT authentication
- **Goal**: User logs into Portfolio → clicks Ledger link → automatically logged into Ledger

## ✅ SSO Compatibility with Vira Services

Your Vira Services backend is **already SSO-ready** because:
- ✅ JWT tokens are stateless and portable
- ✅ Shared user database across all apps
- ✅ CORS configured for multiple origins
- ✅ Token validation works across applications
- ✅ Refresh token rotation implemented

## 🏗️ Architecture Options

### Option 1: Shared Domain Setup (Recommended)

```
Authentication:  auth.yourdomain.com
API Backend:     api.yourdomain.com
Portfolio App:   portfolio.yourdomain.com
Ledger App:      ledger.yourdomain.com
```

**Advantages:**
- Shared cookies work automatically
- Most secure implementation
- Seamless user experience
- Simple to implement

### Option 2: Cross-Domain Setup

```
Portfolio App:   portfolio-app.netlify.app
Ledger App:      ledger-app.vercel.app
API Backend:     vira-api.railway.app
```

**Advantages:**
- Flexible hosting options
- Independent deployments
- Works with different providers

**Challenges:**
- Requires token passing mechanisms
- More complex security considerations

## 🔧 Implementation Strategies

### Strategy 1: Shared Domain Cookies (Easiest)

#### Backend Configuration

```yaml
# application.yml
server:
  servlet:
    session:
      cookie:
        domain: .yourdomain.com
        secure: true
        http-only: true
        same-site: lax
```

#### Frontend Implementation

```javascript
// Both apps automatically share authentication cookies
// No additional code needed for token sharing
```

#### CORS Configuration

```java
@Configuration
public class CorsConfig {
    @Bean
    public WebMvcConfigurer corsConfigurer() {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**")
                    .allowedOrigins(
                        "https://portfolio.yourdomain.com",
                        "https://ledger.yourdomain.com",
                        "https://auth.yourdomain.com"
                    )
                    .allowCredentials(true);
            }
        };
    }
}
```

### Strategy 2: URL Token Passing

#### Portfolio App (Source)

```javascript
// When user clicks link to Ledger App
function redirectToLedgerApp() {
    const token = localStorage.getItem('jwt_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (token && isTokenValid(token)) {
        // Pass token securely
        const url = `https://ledger-app.com/auth/sso?token=${encodeURIComponent(token)}`;
        window.location.href = url;
    } else {
        // Redirect to login
        window.location.href = 'https://auth.yourdomain.com/login';
    }
}

function isTokenValid(token) {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp * 1000 > Date.now();
    } catch {
        return false;
    }
}
```

#### Ledger App (Target)

```javascript
// Handle SSO token on app load
function handleSSOToken() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
        // Validate token with backend
        validateAndStoreToken(token);
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } else {
        // Check for existing local token
        checkExistingAuth();
    }
}

async function validateAndStoreToken(token) {
    try {
        // Verify token with backend
        const response = await fetch('/api/auth/validate', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const userData = await response.json();
            
            // Store token locally
            localStorage.setItem('jwt_token', token);
            localStorage.setItem('user_data', JSON.stringify(userData));
            
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            // Token invalid, redirect to login
            redirectToLogin();
        }
    } catch (error) {
        console.error('Token validation failed:', error);
        redirectToLogin();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', handleSSOToken);
```

### Strategy 3: postMessage API (Advanced)

#### Portfolio App

```javascript
function openLedgerInPopup() {
    const popup = window.open('https://ledger-app.com/sso', 'ledger', 'width=800,height=600');
    
    // Listen for ready message from popup
    window.addEventListener('message', (event) => {
        if (event.origin !== 'https://ledger-app.com') return;
        
        if (event.data.type === 'SSO_READY') {
            // Send token to popup
            const token = localStorage.getItem('jwt_token');
            popup.postMessage({
                type: 'SSO_TOKEN',
                token: token
            }, 'https://ledger-app.com');
        }
    });
}
```

#### Ledger App

```javascript
// In popup window
window.addEventListener('message', (event) => {
    if (event.origin !== 'https://portfolio.yourdomain.com') return;
    
    if (event.data.type === 'SSO_TOKEN') {
        const token = event.data.token;
        
        // Validate and store token
        validateAndStoreToken(token).then(() => {
            // Close popup and redirect parent
            window.opener.location.href = 'https://ledger-app.com/dashboard';
            window.close();
        });
    }
});

// Signal ready for token
window.parent.postMessage({ type: 'SSO_READY' }, 'https://portfolio.yourdomain.com');
```

## 🔒 Security Considerations

### Token Security

1. **Never pass tokens in URLs for production**
   ```javascript
   // ❌ Bad - visible in logs
   window.location.href = `https://app.com?token=${token}`;
   
   // ✅ Good - use POST or cookies
   // Use form submission or secure cookies instead
   ```

2. **Always validate tokens**
   ```javascript
   // Validate token before trusting
   async function validateToken(token) {
       const response = await fetch('/api/auth/validate', {
           headers: { 'Authorization': `Bearer ${token}` }
       });
       return response.ok;
   }
   ```

3. **Handle token expiration**
   ```javascript
   // Check expiration before redirect
   function isTokenExpired(token) {
       try {
           const payload = JSON.parse(atob(token.split('.')[1]));
           return payload.exp * 1000 <= Date.now();
       } catch {
           return true;
       }
   }
   ```

### HTTPS Requirements

```nginx
# Ensure all apps use HTTPS
server {
    listen 443 ssl;
    server_name portfolio.yourdomain.com;
    
    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
}
```

## 🔄 User Flow Examples

### Successful SSO Flow

```
1. User visits portfolio.yourdomain.com
2. User logs in (JWT token stored)
3. User clicks "Open Ledger" button
4. Portfolio app redirects with token
5. Ledger app validates token with backend
6. User automatically logged into Ledger
7. Dashboard loads without login prompt
```

### Token Expired Flow

```
1. User visits portfolio.yourdomain.com
2. Token exists but expired
3. User clicks "Open Ledger" button
4. Portfolio app detects expired token
5. Redirects to auth.yourdomain.com/login
6. User logs in fresh
7. Redirected back to intended app
```

### Logout Synchronization

```javascript
// Global logout function
async function globalLogout() {
    try {
        // Invalidate token on backend
        await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
            }
        });
        
        // Clear local storage
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        
        // Notify other apps via postMessage or storage events
        window.dispatchEvent(new CustomEvent('global-logout'));
        
        // Redirect to login
        window.location.href = 'https://auth.yourdomain.com/login';
        
    } catch (error) {
        console.error('Logout failed:', error);
    }
}

// Listen for logout events from other apps
window.addEventListener('storage', (event) => {
    if (event.key === 'jwt_token' && event.newValue === null) {
        // Another app logged out, redirect to login
        window.location.href = 'https://auth.yourdomain.com/login';
    }
});
```

## ⚙️ Backend Modifications

### Enhanced Token Validation Endpoint

```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {
    
    @PostMapping("/validate")
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<ApiResponse<UserResponse>> validateToken(
            HttpServletRequest request) {
        
        try {
            // Token already validated by security filter
            String username = SecurityContextHolder.getContext()
                .getAuthentication().getName();
            
            User user = userService.findByUsername(username);
            UserResponse userResponse = UserResponse.fromUser(user);
            
            return ResponseEntity.ok(
                ApiResponse.success(userResponse, "Token is valid")
            );
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(ApiResponse.error("Invalid token"));
        }
    }
    
    @PostMapping("/sso/redirect")
    public ResponseEntity<ApiResponse<String>> createSSORedirect(
            @RequestBody SSORedirectRequest request,
            HttpServletRequest httpRequest) {
        
        try {
            // Validate current user token
            String currentToken = jwtUtils.getJwtFromRequest(httpRequest);
            if (!jwtUtils.validateJwtToken(currentToken)) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.error("Invalid source token"));
            }
            
            // Generate temporary SSO token (short-lived)
            String ssoToken = jwtUtils.generateSSOToken(currentToken, 300); // 5 minutes
            
            // Build redirect URL
            String redirectUrl = request.getTargetApp() + "/auth/sso?token=" + ssoToken;
            
            return ResponseEntity.ok(
                ApiResponse.success(redirectUrl, "SSO redirect URL created")
            );
            
        } catch (Exception e) {
            return ResponseEntity.badRequest()
                .body(ApiResponse.error("Failed to create SSO redirect"));
        }
    }
}
```

### CORS Configuration for Multiple Apps

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        
        // Allow multiple frontend domains
        configuration.setAllowedOriginPatterns(Arrays.asList(
            "https://portfolio.yourdomain.com",
            "https://ledger.yourdomain.com",
            "https://auth.yourdomain.com",
            "https://*.yourdomain.com", // Wildcard for subdomains
            "http://localhost:3000",    // Development
            "http://localhost:3001"     // Development
        ));
        
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", configuration);
        
        return source;
    }
}
```

## 🧪 Testing SSO Implementation

### Manual Testing Checklist

- [ ] User can log into App A
- [ ] User can navigate to App B without re-login
- [ ] Token expiration handled gracefully
- [ ] Logout from one app logs out from all
- [ ] Invalid tokens redirect to login
- [ ] CORS works across all domains
- [ ] Security headers present
- [ ] No tokens visible in browser history

### Automated Testing

```javascript
// Cypress test example
describe('SSO Flow', () => {
    it('should enable seamless app switching', () => {
        // Login to Portfolio app
        cy.visit('https://portfolio.yourdomain.com');
        cy.login('user@example.com', 'password');
        
        // Verify login successful
        cy.url().should('include', '/dashboard');
        
        // Click link to Ledger app
        cy.get('[data-cy=ledger-link]').click();
        
        // Should be automatically logged into Ledger
        cy.origin('https://ledger.yourdomain.com', () => {
            cy.url().should('include', '/dashboard');
            cy.get('[data-cy=user-menu]').should('be.visible');
        });
    });
});
```

## 📝 Implementation Checklist

### Phase 1: Basic SSO
- [ ] Configure CORS for multiple domains
- [ ] Implement token validation endpoint
- [ ] Add SSO redirect functionality
- [ ] Test with two apps

### Phase 2: Enhanced Security
- [ ] Implement short-lived SSO tokens
- [ ] Add token encryption
- [ ] Implement logout synchronization
- [ ] Add security headers

### Phase 3: User Experience
- [ ] Handle token expiration gracefully
- [ ] Add loading states during SSO
- [ ] Implement error handling
- [ ] Add fallback mechanisms

## 🚀 Deployment Considerations

### Domain Setup

```bash
# DNS Configuration
portfolio.yourdomain.com    A    123.456.789.10
ledger.yourdomain.com       A    123.456.789.11
api.yourdomain.com          A    123.456.789.12
auth.yourdomain.com         A    123.456.789.13
```

### SSL Certificates

```bash
# Wildcard certificate for all subdomains
*.yourdomain.com

# Or individual certificates
portfolio.yourdomain.com
ledger.yourdomain.com
api.yourdomain.com
auth.yourdomain.com
```

### Environment Variables

```bash
# Shared across all apps
AUTH_API_URL=https://api.yourdomain.com
SSO_DOMAIN=.yourdomain.com
JWT_SECRET=your-shared-secret

# App-specific
PORTFOLIO_URL=https://portfolio.yourdomain.com
LEDGER_URL=https://ledger.yourdomain.com
```

## 🎯 Next Steps

1. **Choose your architecture** (shared domain vs cross-domain)
2. **Implement basic token sharing** between two apps
3. **Test the complete flow** end-to-end
4. **Add security enhancements** as needed
5. **Scale to additional apps** using the same pattern

## 📚 Additional Resources

- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [CORS Configuration Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Spring Security Reference](https://docs.spring.io/spring-security/reference/)
- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)

---

**📝 Note:** This guide will be updated as you implement and refine your SSO solution. Feel free to add your own findings and improvements! 