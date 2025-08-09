# Role Management Guide

> **Complete guide to managing user roles and permissions in Vira Services**

## 🎯 **Role Hierarchy Overview**

```
ADMIN > SUPER_USER > NORMAL_USER > GUEST
```

### Role Definitions

| Role | Description | Access Level | Approval Required |
|------|-------------|--------------|-------------------|
| **GUEST** | Anonymous users | Public content only | No |
| **NORMAL_USER** | Standard registered users | Own data + standard features | No |
| **SUPER_USER** | Approved power users | Read-only access to all data | Yes (Admin) |
| **ADMIN** | System administrators | Full system access | No |

## 🔄 **Role Assignment Methods**

### 1. Automatic Assignment (Registration)

**Normal User Registration** (`/api/auth/register`):
- ✅ **Default Role**: `NORMAL_USER`
- ✅ **Status**: `APPROVED` (immediate access)
- ✅ **Permissions**: Manage own portfolio/projects

**Google OAuth Registration** (`/oauth2/authorization/google`):
- ✅ **Default Role**: `NORMAL_USER`
- ✅ **Status**: `APPROVED` (immediate access)
- ✅ **Account Linking**: Links to existing account by email if found
- ✅ **Auto-Creation**: Creates new account if email not found
- ✅ **Permissions**: Same as normal user registration

**Super User Registration** (`/api/auth/register-super-user`):
- ✅ **Initial Role**: `GUEST` (temporary)
- ✅ **Status**: `PENDING_APPROVAL`
- ✅ **Final Role**: `SUPER_USER` (after admin approval)

### 2. Admin Role Management

**Available Admin Operations:**
- View pending approvals
- Approve/reject super user requests
- Directly assign any role to any user
- Create super users without approval process

### 3. Default Admin User

**Auto-Created on Startup:**
- **Username**: `admin`
- **Password**: `admin123` (change in production!)
- **Role**: `ADMIN`
- **Status**: `APPROVED`

## 🛠️ **Managing Roles via API**

### Admin Endpoints

**Get Pending Approvals:**
```bash
GET /api/admin/pending-approvals
Authorization: Bearer {admin_jwt_token}
```

**Approve Super User:**
```bash
POST /api/admin/approve-super-user
Content-Type: application/json
Authorization: Bearer {admin_jwt_token}

{
  "userId": 1,
  "approved": true,
  "notes": "Approved for business analytics access"
}
```

**Update User Role Directly:**
```bash
PUT /api/admin/users/{userId}/role?role=SUPER_USER
Authorization: Bearer {admin_jwt_token}
```

**Create Super User (Admin Bypass):**
```bash
POST /api/admin/register-super-user
Content-Type: application/json
Authorization: Bearer {admin_jwt_token}

{
  "username": "superuser1",
  "email": "superuser1@example.com",
  "password": "securepass123",
  "justification": "Business analytics access",
  "organization": "Example Corp",
  "position": "Business Analyst"
}
```

## 📋 **Role Management Workflows**

### Super User Approval Process

**Step 1: User Requests Super User Access**
```bash
POST /api/auth/register-super-user
{
  "username": "analyst1",
  "email": "analyst1@company.com",
  "password": "password123",
  "justification": "Need read access for quarterly reports",
  "organization": "ABC Corp",
  "position": "Business Analyst"
}
```

**Step 2: Admin Reviews Request**
- View pending approvals
- Review justification and user details
- Make approval decision

**Step 3: Admin Approves/Rejects**
```bash
POST /api/admin/approve-super-user
{
  "userId": 5,
  "approved": true,
  "notes": "Approved for Q1 reporting access"
}
```

**Step 4: User Gains Access**
- User status changes to `APPROVED`
- Role changes from `GUEST` to `SUPER_USER`
- User can now login and access super user features

### Emergency Role Changes

**Quick Role Assignment (Admin):**
```bash
# Promote user to admin in emergency
PUT /api/admin/users/5/role?role=ADMIN

# Demote problematic user
PUT /api/admin/users/3/role?role=GUEST

# Grant temporary super user access
PUT /api/admin/users/7/role?role=SUPER_USER
```

## 🎛️ **Role-Based Permissions**

### API Endpoint Permissions

| Endpoint | GUEST | NORMAL_USER | SUPER_USER | ADMIN |
|----------|-------|-------------|------------|-------|
| `GET /api/auth/register` | ✅ | ✅ | ✅ | ✅ |
| `POST /api/auth/login` | ✅ | ✅ | ✅ | ✅ |
| `GET /api/auth/me` | ❌ | ✅ | ✅ | ✅ |
| `GET /api/portfolio/projects` | ❌ | ✅ (own) | ✅ (all) | ✅ (all) |
| `POST /api/portfolio/projects` | ❌ | ✅ | ❌ | ✅ |
| `PUT /api/portfolio/projects/{id}` | ❌ | ✅ (own) | ❌ | ✅ (all) |
| `DELETE /api/portfolio/projects/{id}` | ❌ | ✅ (own) | ❌ | ✅ (all) |
| `GET /api/admin/pending-approvals` | ❌ | ❌ | ❌ | ✅ |
| `POST /api/admin/approve-super-user` | ❌ | ❌ | ❌ | ✅ |
| `PUT /api/admin/users/{id}/role` | ❌ | ❌ | ❌ | ✅ |

### Feature Access Matrix

| Feature | GUEST | NORMAL_USER | SUPER_USER | ADMIN |
|---------|-------|-------------|------------|-------|
| View public content | ✅ | ✅ | ✅ | ✅ |
| Create account | ✅ | N/A | N/A | N/A |
| Manage own projects | ❌ | ✅ | ❌ | ✅ |
| View all projects | ❌ | ❌ | ✅ (read-only) | ✅ |
| Analytics dashboard | ❌ | ❌ | ✅ (read-only) | ✅ |
| User management | ❌ | ❌ | ❌ | ✅ |
| System configuration | ❌ | ❌ | ❌ | ✅ |

## 🔧 **Implementation in Code**

### Backend Role Checks

**Controller Level:**
```java
@PreAuthorize("hasRole('ADMIN')")
@GetMapping("/admin/users")
public ResponseEntity<List<User>> getAllUsers() {
    // Admin only endpoint
}

@PreAuthorize("hasRole('NORMAL_USER') or hasRole('SUPER_USER') or hasRole('ADMIN')")
@GetMapping("/portfolio/projects")
public ResponseEntity<List<Project>> getProjects() {
    // Authenticated users only
}
```

**Service Level:**
```java
@PreAuthorize("hasRole('ADMIN') or (hasRole('NORMAL_USER') and #userId == authentication.principal.id)")
public Project updateProject(Long projectId, Long userId, ProjectRequest request) {
    // Admin can update any project, users can update only their own
}
```

**Method Level Role Filtering:**
```java
public List<Project> getProjectsForUser(Authentication auth) {
    if (hasRole(auth, "ADMIN") || hasRole(auth, "SUPER_USER")) {
        return projectRepository.findAll(); // All projects
    } else {
        return projectRepository.findByUserId(getUserId(auth)); // Own projects only
    }
}
```

### Frontend Role Checks

**React Component Guards:**
```javascript
import { useAuth } from '../contexts/AuthContext';

const ProjectList = () => {
  const { hasRole, hasAnyRole } = useAuth();

  return (
    <div>
      {/* Content for all authenticated users */}
      {hasAnyRole(['NORMAL_USER', 'SUPER_USER', 'ADMIN']) && (
        <ProjectDashboard />
      )}

      {/* Admin only content */}
      {hasRole('ADMIN') && (
        <AdminControls />
      )}

      {/* Super user analytics */}
      {hasAnyRole(['SUPER_USER', 'ADMIN']) && (
        <AnalyticsView />
      )}
    </div>
  );
};
```

## 📊 **Monitoring & Auditing**

### User Role Tracking

**Database Schema for Auditing:**
```sql
-- Track role changes
CREATE TABLE auth_role_changes (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES auth_users(id),
    old_role VARCHAR(50),
    new_role VARCHAR(50),
    changed_by BIGINT REFERENCES auth_users(id),
    change_reason TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track super user requests
CREATE TABLE auth_super_user_requests (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES auth_users(id),
    justification TEXT,
    organization VARCHAR(100),
    position VARCHAR(100),
    status VARCHAR(20) DEFAULT 'PENDING',
    reviewed_by BIGINT REFERENCES auth_users(id),
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Logging Role Changes

**Audit Log Service:**
```java
@Service
public class RoleAuditService {
    
    public void logRoleChange(Long userId, RoleName oldRole, RoleName newRole, Long changedBy, String reason) {
        RoleChangeLog log = new RoleChangeLog();
        log.setUserId(userId);
        log.setOldRole(oldRole);
        log.setNewRole(newRole);
        log.setChangedBy(changedBy);
        log.setChangeReason(reason);
        log.setChangedAt(LocalDateTime.now());
        
        roleChangeRepository.save(log);
        
        // Log to application logs
        logger.info("ROLE_CHANGE: user={}, oldRole={}, newRole={}, changedBy={}, reason={}", 
            userId, oldRole, newRole, changedBy, reason);
    }
}
```

## 🚨 **Security Considerations**

### Role Security Best Practices

**1. Principle of Least Privilege:**
- Users get minimum required permissions
- Regular review of user roles
- Temporary role elevations when needed

**2. Role Validation:**
- Always validate roles on backend
- Frontend role checks are for UX only
- Double-check permissions on sensitive operations

**3. Admin Account Security:**
- Change default admin password immediately
- Use strong, unique passwords
- Enable MFA for admin accounts (future enhancement)
- Regular admin account audits

**4. Super User Management:**
- Require business justification
- Regular review of super user access
- Time-limited access where appropriate
- Audit super user activities

### Security Monitoring

**Monitor for:**
- Unusual role change patterns
- Failed admin login attempts
- Super user request spikes
- Privilege escalation attempts
- Unauthorized admin operations

## 🛠️ **Common Role Management Tasks**

### Regular Maintenance

**Weekly Tasks:**
- Review new super user requests
- Check for inactive super users
- Audit admin account usage

**Monthly Tasks:**
- Review all user roles
- Check for orphaned accounts
- Update role documentation
- Review access patterns

**Quarterly Tasks:**
- Audit all admin accounts
- Review role hierarchy
- Update security policies
- Test role-based access controls

### Bulk Operations

**Bulk Role Updates (Admin):**
```java
@PostMapping("/admin/bulk-role-update")
public ResponseEntity<?> bulkUpdateRoles(@RequestBody BulkRoleUpdateRequest request) {
    for (Long userId : request.getUserIds()) {
        userService.updateUserRole(userId, request.getNewRole(), getCurrentAdmin());
    }
    return ResponseEntity.ok("Bulk role update completed");
}
```

**Bulk User Deactivation:**
```java
@PostMapping("/admin/bulk-deactivate")
public ResponseEntity<?> bulkDeactivateUsers(@RequestBody List<Long> userIds) {
    for (Long userId : userIds) {
        userService.deactivateUser(userId, getCurrentAdmin());
    }
    return ResponseEntity.ok("Users deactivated");
}
```

## 📈 **Role Analytics**

### User Role Statistics

**Track Role Distribution:**
- Total users per role
- Role change frequency
- Super user approval rates
- Admin activity levels

**Example Queries:**
```sql
-- Users by role
SELECT r.name, COUNT(ur.user_id) as user_count
FROM auth_roles r
LEFT JOIN auth_user_roles ur ON r.id = ur.role_id
GROUP BY r.name;

-- Recent role changes
SELECT u.username, rc.old_role, rc.new_role, rc.changed_at
FROM auth_role_changes rc
JOIN auth_users u ON rc.user_id = u.id
WHERE rc.changed_at > NOW() - INTERVAL '30 days'
ORDER BY rc.changed_at DESC;

-- Pending super user requests
SELECT COUNT(*) as pending_requests
FROM auth_users
WHERE status = 'PENDING_APPROVAL' AND requested_role = 'SUPER_USER';
```

## 🔗 **Related Resources**

### API Documentation
- **Swagger UI**: `/swagger-ui/index.html`
- **Admin Endpoints**: Tag "Admin" in Swagger
- **Auth Endpoints**: Tag "Authentication" in Swagger

### Related Guides
- **Security**: `guides/SECURITY.md`
- **React Integration**: `guides/REACT_INTEGRATION.md`
- **Deployment**: `guides/DEPLOYMENT.md`
- **Local Setup**: `guides/LOCAL_SETUP.md`

---

**🎯 Effective role management ensures secure, scalable user access control. Regular auditing and monitoring are key to maintaining security!** 🚀 