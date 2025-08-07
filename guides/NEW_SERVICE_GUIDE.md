# 🔧 Adding New Services Guide - Vira Services Backend

This guide walks you through adding a new service to your Vira Services backend. We'll use a practical example: creating a "Blog" service for managing blog posts.

## 🎯 What You'll Learn

- How to structure a new service
- Database design and migration
- API endpoint creation
- Security integration
- Testing your new service

---

## 📋 Step 1: Plan Your New Service

### Example: Blog Service
**Purpose:** Allow users to create, read, update, and delete blog posts
**Features:**
- Create blog posts with title, content, and tags
- List all blog posts (with pagination)
- Search blog posts
- Mark posts as published/draft
- Associate posts with authenticated users

### Define Your Data Model
```
Blog Post:
- id (unique identifier)
- title (string, required)
- content (text, required)
- summary (string, optional)
- tags (list of strings)
- status (DRAFT/PUBLISHED)
- featured (boolean)
- publishedAt (date)
- user (who created it)
- createdAt, updatedAt (automatic timestamps)
```

---

## 📁 Step 2: Create the Package Structure

Create these directories in `src/main/java/com/vira/`:

```
blog/
├── controller/
├── dto/
├── model/
├── repository/
└── service/
```

**Commands:**
```bash
# Navigate to your project
cd src/main/java/com/vira

# Create the directory structure
mkdir -p blog/controller blog/dto blog/model blog/repository blog/service
```

---

## 🗃️ Step 3: Create the Database Model

### 3.1 Create the Entity

Create `src/main/java/com/vira/blog/model/BlogPost.java`:

```java
package com.vira.blog.model;

import com.vira.auth.model.User;
import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "blog_posts")
@EntityListeners(AuditingEntityListener.class)
public class BlogPost {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "Title is required")
    @Size(max = 255, message = "Title must not exceed 255 characters")
    @Column(name = "title", nullable = false)
    private String title;

    @Column(name = "content", columnDefinition = "TEXT")
    private String content;

    @Size(max = 500, message = "Summary must not exceed 500 characters")
    @Column(name = "summary", length = 500)
    private String summary;

    @ElementCollection
    @CollectionTable(name = "blog_post_tags", joinColumns = @JoinColumn(name = "post_id"))
    @Column(name = "tag")
    private List<String> tags;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    private PostStatus status = PostStatus.DRAFT;

    @Column(name = "featured", nullable = false)
    private Boolean featured = false;

    @Column(name = "published_at")
    private LocalDateTime publishedAt;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @CreatedDate
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    // Constructors
    public BlogPost() {}

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }

    public List<String> getTags() { return tags; }
    public void setTags(List<String> tags) { this.tags = tags; }

    public PostStatus getStatus() { return status; }
    public void setStatus(PostStatus status) { this.status = status; }

    public Boolean getFeatured() { return featured; }
    public void setFeatured(Boolean featured) { this.featured = featured; }

    public LocalDateTime getPublishedAt() { return publishedAt; }
    public void setPublishedAt(LocalDateTime publishedAt) { this.publishedAt = publishedAt; }

    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}
```

### 3.2 Create the Status Enum

Create `src/main/java/com/vira/blog/model/PostStatus.java`:

```java
package com.vira.blog.model;

public enum PostStatus {
    DRAFT,
    PUBLISHED,
    ARCHIVED
}
```

---

## 🗄️ Step 4: Create Database Migration

Create `src/main/resources/db/migration/V3__Create_blog_tables.sql`:

```sql
-- Create blog_posts table
CREATE TABLE blog_posts (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    summary VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    featured BOOLEAN NOT NULL DEFAULT FALSE,
    published_at TIMESTAMP,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_blog_posts_user 
        FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE
);

-- Create blog_post_tags table for tags
CREATE TABLE blog_post_tags (
    post_id BIGINT NOT NULL,
    tag VARCHAR(100) NOT NULL,
    
    CONSTRAINT fk_blog_post_tags_post 
        FOREIGN KEY (post_id) REFERENCES blog_posts(id) ON DELETE CASCADE
);

-- Add indexes for better performance
CREATE INDEX idx_blog_posts_user_id ON blog_posts(user_id);
CREATE INDEX idx_blog_posts_status ON blog_posts(status);
CREATE INDEX idx_blog_posts_featured ON blog_posts(featured);
CREATE INDEX idx_blog_posts_published_at ON blog_posts(published_at);
CREATE INDEX idx_blog_post_tags_post_id ON blog_post_tags(post_id);
CREATE INDEX idx_blog_post_tags_tag ON blog_post_tags(tag);

-- Add trigger for updated_at
CREATE OR REPLACE FUNCTION update_blog_posts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_blog_posts_updated_at
    BEFORE UPDATE ON blog_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_blog_posts_updated_at();
```

---

## 📋 Step 5: Create DTOs (Data Transfer Objects)

### 5.1 Request DTO

Create `src/main/java/com/vira/blog/dto/BlogPostRequest.java`:

```java
package com.vira.blog.dto;

import com.vira.blog.model.PostStatus;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.util.List;

public class BlogPostRequest {

    @NotBlank(message = "Title is required")
    @Size(max = 255, message = "Title must not exceed 255 characters")
    private String title;

    @NotBlank(message = "Content is required")
    private String content;

    @Size(max = 500, message = "Summary must not exceed 500 characters")
    private String summary;

    private List<String> tags;

    private PostStatus status = PostStatus.DRAFT;

    private Boolean featured = false;

    // Constructors
    public BlogPostRequest() {}

    // Getters and Setters
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }

    public List<String> getTags() { return tags; }
    public void setTags(List<String> tags) { this.tags = tags; }

    public PostStatus getStatus() { return status; }
    public void setStatus(PostStatus status) { this.status = status; }

    public Boolean getFeatured() { return featured; }
    public void setFeatured(Boolean featured) { this.featured = featured; }
}
```

### 5.2 Response DTO

Create `src/main/java/com/vira/blog/dto/BlogPostResponse.java`:

```java
package com.vira.blog.dto;

import com.vira.blog.model.BlogPost;
import com.vira.blog.model.PostStatus;

import java.time.LocalDateTime;
import java.util.List;

public class BlogPostResponse {

    private Long id;
    private String title;
    private String content;
    private String summary;
    private List<String> tags;
    private PostStatus status;
    private Boolean featured;
    private LocalDateTime publishedAt;
    private String authorUsername;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    // Constructors
    public BlogPostResponse() {}

    public BlogPostResponse(BlogPost blogPost) {
        this.id = blogPost.getId();
        this.title = blogPost.getTitle();
        this.content = blogPost.getContent();
        this.summary = blogPost.getSummary();
        this.tags = blogPost.getTags();
        this.status = blogPost.getStatus();
        this.featured = blogPost.getFeatured();
        this.publishedAt = blogPost.getPublishedAt();
        this.authorUsername = blogPost.getUser().getUsername();
        this.createdAt = blogPost.getCreatedAt();
        this.updatedAt = blogPost.getUpdatedAt();
    }

    // Static factory method
    public static BlogPostResponse from(BlogPost blogPost) {
        return new BlogPostResponse(blogPost);
    }

    // Getters and Setters (add all of them)
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    // ... add all other getters and setters
}
```

---

## 🔍 Step 6: Create Repository

Create `src/main/java/com/vira/blog/repository/BlogPostRepository.java`:

```java
package com.vira.blog.repository;

import com.vira.blog.model.BlogPost;
import com.vira.blog.model.PostStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface BlogPostRepository extends JpaRepository<BlogPost, Long> {

    // Find posts by user
    Page<BlogPost> findByUserId(Long userId, Pageable pageable);

    // Find posts by status
    Page<BlogPost> findByStatus(PostStatus status, Pageable pageable);

    // Find featured posts
    List<BlogPost> findByFeaturedTrueAndStatusOrderByPublishedAtDesc(PostStatus status);

    // Find posts by user and status
    Page<BlogPost> findByUserIdAndStatus(Long userId, PostStatus status, Pageable pageable);

    // Search posts by title or content
    @Query("SELECT b FROM BlogPost b WHERE b.userId = :userId AND " +
           "(LOWER(b.title) LIKE LOWER(CONCAT('%', :search, '%')) OR " +
           "LOWER(b.content) LIKE LOWER(CONCAT('%', :search, '%')))")
    Page<BlogPost> searchPosts(@Param("userId") Long userId, 
                              @Param("search") String search, 
                              Pageable pageable);

    // Find posts by tag
    @Query("SELECT b FROM BlogPost b JOIN b.tags t WHERE b.userId = :userId AND " +
           "LOWER(t) LIKE LOWER(CONCAT('%', :tag, '%'))")
    Page<BlogPost> findByUserIdAndTagsContaining(@Param("userId") Long userId, 
                                                 @Param("tag") String tag, 
                                                 Pageable pageable);

    // Check if post exists by title and user
    boolean existsByUserIdAndTitleIgnoreCase(Long userId, String title);

    // Find post by ID and user (for security)
    Optional<BlogPost> findByIdAndUserId(Long id, Long userId);

    // Count posts by user
    long countByUserId(Long userId);
}
```

---

## 🏗️ Step 7: Create Service Layer

Create `src/main/java/com/vira/blog/service/BlogPostService.java`:

```java
package com.vira.blog.service;

import com.vira.auth.model.User;
import com.vira.auth.repository.UserRepository;
import com.vira.blog.dto.BlogPostRequest;
import com.vira.blog.dto.BlogPostResponse;
import com.vira.blog.model.BlogPost;
import com.vira.blog.model.PostStatus;
import com.vira.blog.repository.BlogPostRepository;
import com.vira.common.exception.BusinessException;
import jakarta.persistence.EntityNotFoundException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@Transactional
public class BlogPostService {

    private static final Logger logger = LoggerFactory.getLogger(BlogPostService.class);

    private final BlogPostRepository blogPostRepository;
    private final UserRepository userRepository;

    @Autowired
    public BlogPostService(BlogPostRepository blogPostRepository, UserRepository userRepository) {
        this.blogPostRepository = blogPostRepository;
        this.userRepository = userRepository;
    }

    /**
     * Create a new blog post
     */
    public BlogPostResponse createPost(BlogPostRequest request, String username) {
        logger.info("Creating new blog post '{}' for user '{}'", request.getTitle(), username);

        User user = getUserByUsername(username);

        // Check if post with same title already exists
        if (blogPostRepository.existsByUserIdAndTitleIgnoreCase(user.getId(), request.getTitle())) {
            throw new BusinessException("Blog post with title '" + request.getTitle() + "' already exists", 
                                      HttpStatus.CONFLICT);
        }

        BlogPost blogPost = new BlogPost();
        mapRequestToPost(request, blogPost);
        blogPost.setUser(user);

        // Set published date if status is PUBLISHED
        if (blogPost.getStatus() == PostStatus.PUBLISHED && blogPost.getPublishedAt() == null) {
            blogPost.setPublishedAt(LocalDateTime.now());
        }

        BlogPost savedPost = blogPostRepository.save(blogPost);
        logger.info("Blog post '{}' created successfully with ID: {}", savedPost.getTitle(), savedPost.getId());

        return BlogPostResponse.from(savedPost);
    }

    /**
     * Update an existing blog post
     */
    public BlogPostResponse updatePost(Long postId, BlogPostRequest request, String username) {
        logger.info("Updating blog post ID: {} for user '{}'", postId, username);

        User user = getUserByUsername(username);
        BlogPost existingPost = getPostByIdAndUser(postId, user.getId());

        // Check title uniqueness if title is being changed
        if (!existingPost.getTitle().equalsIgnoreCase(request.getTitle()) &&
            blogPostRepository.existsByUserIdAndTitleIgnoreCase(user.getId(), request.getTitle())) {
            throw new BusinessException("Blog post with title '" + request.getTitle() + "' already exists", 
                                      HttpStatus.CONFLICT);
        }

        PostStatus oldStatus = existingPost.getStatus();
        mapRequestToPost(request, existingPost);

        // Set published date if status changed from DRAFT to PUBLISHED
        if (oldStatus != PostStatus.PUBLISHED && existingPost.getStatus() == PostStatus.PUBLISHED) {
            existingPost.setPublishedAt(LocalDateTime.now());
        }

        BlogPost savedPost = blogPostRepository.save(existingPost);
        logger.info("Blog post '{}' updated successfully", savedPost.getTitle());

        return BlogPostResponse.from(savedPost);
    }

    /**
     * Get all posts for a user with pagination
     */
    @Transactional(readOnly = true)
    public Page<BlogPostResponse> getUserPosts(String username, int page, int size, String sortBy, String sortDir) {
        logger.info("Fetching blog posts for user '{}' - page: {}, size: {}", username, page, size);

        User user = getUserByUsername(username);

        Sort sort = Sort.by(sortDir.equalsIgnoreCase("desc") ? Sort.Direction.DESC : Sort.Direction.ASC, sortBy);
        Pageable pageable = PageRequest.of(page, size, sort);

        Page<BlogPost> posts = blogPostRepository.findByUserId(user.getId(), pageable);

        return posts.map(BlogPostResponse::from);
    }

    /**
     * Get post by ID
     */
    @Transactional(readOnly = true)
    public BlogPostResponse getPostById(Long postId, String username) {
        logger.info("Fetching blog post ID: {} for user '{}'", postId, username);

        User user = getUserByUsername(username);
        BlogPost post = getPostByIdAndUser(postId, user.getId());

        return BlogPostResponse.from(post);
    }

    /**
     * Delete a blog post
     */
    public void deletePost(Long postId, String username) {
        logger.info("Deleting blog post ID: {} for user '{}'", postId, username);

        User user = getUserByUsername(username);
        BlogPost post = getPostByIdAndUser(postId, user.getId());

        blogPostRepository.delete(post);
        logger.info("Blog post '{}' deleted successfully", post.getTitle());
    }

    /**
     * Publish a blog post
     */
    public BlogPostResponse publishPost(Long postId, String username) {
        logger.info("Publishing blog post ID: {} for user '{}'", postId, username);

        User user = getUserByUsername(username);
        BlogPost post = getPostByIdAndUser(postId, user.getId());

        post.setStatus(PostStatus.PUBLISHED);
        post.setPublishedAt(LocalDateTime.now());

        BlogPost savedPost = blogPostRepository.save(post);
        return BlogPostResponse.from(savedPost);
    }

    // Helper methods
    private User getUserByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new EntityNotFoundException("User not found: " + username));
    }

    private BlogPost getPostByIdAndUser(Long postId, Long userId) {
        return blogPostRepository.findByIdAndUserId(postId, userId)
                .orElseThrow(() -> new EntityNotFoundException("Blog post not found with ID: " + postId));
    }

    private void mapRequestToPost(BlogPostRequest request, BlogPost post) {
        post.setTitle(request.getTitle());
        post.setContent(request.getContent());
        post.setSummary(request.getSummary());
        post.setTags(request.getTags());
        post.setStatus(request.getStatus());
        post.setFeatured(request.getFeatured() != null ? request.getFeatured() : false);
    }
}
```

---

## 🎮 Step 8: Create Controller

Create `src/main/java/com/vira/blog/controller/BlogPostController.java`:

```java
package com.vira.blog.controller;

import com.vira.blog.dto.BlogPostRequest;
import com.vira.blog.dto.BlogPostResponse;
import com.vira.blog.service.BlogPostService;
import com.vira.common.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/blog")
@Tag(name = "Blog", description = "Blog post management endpoints")
@PreAuthorize("hasRole('USER')")
public class BlogPostController {

    private final BlogPostService blogPostService;

    @Autowired
    public BlogPostController(BlogPostService blogPostService) {
        this.blogPostService = blogPostService;
    }

    @PostMapping("/posts")
    @Operation(summary = "Create a new blog post")
    public ResponseEntity<ApiResponse<BlogPostResponse>> createPost(
            @Valid @RequestBody BlogPostRequest request,
            Authentication authentication) {

        BlogPostResponse response = blogPostService.createPost(request, authentication.getName());
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success(response, "Blog post created successfully"));
    }

    @GetMapping("/posts")
    @Operation(summary = "Get user's blog posts")
    public ResponseEntity<ApiResponse<Page<BlogPostResponse>>> getUserPosts(
            @Parameter(description = "Page number") @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Page size") @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "Sort field") @RequestParam(defaultValue = "createdAt") String sortBy,
            @Parameter(description = "Sort direction") @RequestParam(defaultValue = "desc") String sortDir,
            Authentication authentication) {

        Page<BlogPostResponse> posts = blogPostService.getUserPosts(
                authentication.getName(), page, size, sortBy, sortDir);
        return ResponseEntity.ok(ApiResponse.success(posts, "Blog posts retrieved successfully"));
    }

    @GetMapping("/posts/{id}")
    @Operation(summary = "Get blog post by ID")
    public ResponseEntity<ApiResponse<BlogPostResponse>> getPostById(
            @PathVariable Long id,
            Authentication authentication) {

        BlogPostResponse post = blogPostService.getPostById(id, authentication.getName());
        return ResponseEntity.ok(ApiResponse.success(post, "Blog post retrieved successfully"));
    }

    @PutMapping("/posts/{id}")
    @Operation(summary = "Update blog post")
    public ResponseEntity<ApiResponse<BlogPostResponse>> updatePost(
            @PathVariable Long id,
            @Valid @RequestBody BlogPostRequest request,
            Authentication authentication) {

        BlogPostResponse response = blogPostService.updatePost(id, request, authentication.getName());
        return ResponseEntity.ok(ApiResponse.success(response, "Blog post updated successfully"));
    }

    @DeleteMapping("/posts/{id}")
    @Operation(summary = "Delete blog post")
    public ResponseEntity<ApiResponse<String>> deletePost(
            @PathVariable Long id,
            Authentication authentication) {

        blogPostService.deletePost(id, authentication.getName());
        return ResponseEntity.ok(ApiResponse.success(null, "Blog post deleted successfully"));
    }

    @PostMapping("/posts/{id}/publish")
    @Operation(summary = "Publish blog post")
    public ResponseEntity<ApiResponse<BlogPostResponse>> publishPost(
            @PathVariable Long id,
            Authentication authentication) {

        BlogPostResponse response = blogPostService.publishPost(id, authentication.getName());
        return ResponseEntity.ok(ApiResponse.success(response, "Blog post published successfully"));
    }
}
```

---

## 🧪 Step 9: Build and Test Your New Service

### 9.1 Compile the Application
```bash
# Make sure you're in the project root
.\mvnw.cmd clean compile
```

### 9.2 Run Database Migration
```bash
# Start the application - it will run the migration automatically
.\mvnw.cmd spring-boot:run
```

### 9.3 Test the New Endpoints

#### Register and Login first:
```bash
# Register a user
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"blogger","email":"blogger@example.com","password":"password123"}'

# Login to get token
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"blogger","password":"password123"}'
```

#### Test Blog Endpoints:
```bash
# Create a blog post (replace YOUR_TOKEN with actual token from login)
curl -X POST http://localhost:8080/api/blog/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "My First Blog Post",
    "content": "This is the content of my first blog post...",
    "summary": "A summary of my first post",
    "tags": ["technology", "programming"],
    "status": "PUBLISHED",
    "featured": true
  }'

# Get all blog posts
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8080/api/blog/posts

# Get specific blog post
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8080/api/blog/posts/1
```

---

## 📚 Step 10: Add to Documentation

### Update Swagger Documentation
Your new endpoints will automatically appear in Swagger UI at:
```
http://localhost:8080/swagger-ui/index.html
```

### Update README.md
Add your new service to the project README:

```markdown
## 📂 Services Available

### Authentication Service
- User registration and login
- JWT token management
- Role-based security

### Portfolio Service  
- Project CRUD operations
- Search and filtering
- Project statistics

### Blog Service (NEW!)
- Blog post management
- Draft/Published status
- Tag-based organization
- Featured posts
```

---

## ✅ Step 11: Testing Checklist

### Manual Testing:
- [ ] Create blog post
- [ ] List blog posts
- [ ] Update blog post
- [ ] Delete blog post
- [ ] Publish blog post
- [ ] Test with invalid data
- [ ] Test without authentication
- [ ] Test with wrong user access

### Database Testing:
- [ ] Check tables were created
- [ ] Verify foreign key constraints
- [ ] Test cascading deletes

### API Testing:
- [ ] All endpoints return correct status codes
- [ ] Error handling works
- [ ] Pagination works
- [ ] Authentication is enforced

---

## 🚀 Step 12: Deploy Your New Service

Since you followed the same patterns as existing services, your new blog service will automatically be included when you deploy:

```bash
# Commit your changes
git add .
git commit -m "Add blog service for managing blog posts"

# Push to trigger deployment (if using Railway/Heroku with auto-deploy)
git push origin main
```

---

## 🔄 Step 13: Extending Further

### Add More Features:
1. **Comments System:** Add a `BlogComment` entity
2. **Categories:** Add a `BlogCategory` entity
3. **File Uploads:** Add image upload for blog posts
4. **Analytics:** Track view counts and reading time

### Performance Optimizations:
1. **Caching:** Add Redis for frequently accessed posts
2. **Search:** Integrate Elasticsearch for better search
3. **CDN:** Use CDN for images and static content

---

## 📝 Summary

You've successfully added a new Blog service to your application! Here's what you accomplished:

✅ **Database Layer:** Created entities and migrations
✅ **Business Layer:** Implemented service logic
✅ **API Layer:** Created REST endpoints  
✅ **Security:** Integrated with JWT authentication
✅ **Documentation:** Added Swagger annotations
✅ **Testing:** Verified all functionality

### Key Points to Remember:

1. **Follow the same package structure** for consistency
2. **Use database migrations** for schema changes
3. **Implement proper security** for all endpoints
4. **Add comprehensive validation** for all inputs
5. **Write tests** for all new functionality
6. **Update documentation** when adding features

**🎉 Congratulations!** You can now add any new service to your application following this same pattern! 