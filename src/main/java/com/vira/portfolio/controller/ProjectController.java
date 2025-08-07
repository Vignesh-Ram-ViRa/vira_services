package com.vira.portfolio.controller;

import com.vira.common.dto.ApiResponse;
import com.vira.portfolio.dto.ProjectRequest;
import com.vira.portfolio.dto.ProjectResponse;
import com.vira.portfolio.service.ProjectService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/portfolio")
@Tag(name = "Portfolio", description = "Project portfolio management endpoints")
@SecurityRequirement(name = "Bearer Authentication")
@PreAuthorize("hasRole('USER')")
public class ProjectController {
    
    private final ProjectService projectService;

    @Autowired
    public ProjectController(ProjectService projectService) {
        this.projectService = projectService;
    }

    @PostMapping("/projects")
    @Operation(summary = "Create a new project", description = "Creates a new project for the authenticated user")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "201", description = "Project created successfully",
                content = @Content(schema = @Schema(implementation = ProjectResponse.class))),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "400", description = "Invalid input"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "409", description = "Project with same title already exists")
    })
    public ResponseEntity<ApiResponse<ProjectResponse>> createProject(
            @Valid @RequestBody ProjectRequest request,
            Authentication authentication) {
        
        ProjectResponse projectResponse = projectService.createProject(request, authentication.getName());
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success(projectResponse, "Project created successfully"));
    }

    @PutMapping("/projects/{id}")
    @Operation(summary = "Update a project", description = "Updates an existing project for the authenticated user")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Project updated successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "Project not found"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "409", description = "Project with same title already exists")
    })
    public ResponseEntity<ApiResponse<ProjectResponse>> updateProject(
            @PathVariable Long id,
            @Valid @RequestBody ProjectRequest request,
            Authentication authentication) {
        
        ProjectResponse projectResponse = projectService.updateProject(id, request, authentication.getName());
        return ResponseEntity.ok(ApiResponse.success(projectResponse, "Project updated successfully"));
    }

    @GetMapping("/projects")
    @Operation(summary = "Get user projects", description = "Retrieves paginated list of projects for the authenticated user")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Projects retrieved successfully")
    })
    public ResponseEntity<ApiResponse<Page<ProjectResponse>>> getUserProjects(
            @Parameter(description = "Page number (0-based)", example = "0")
            @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Page size", example = "10")
            @RequestParam(defaultValue = "10") int size,
            @Parameter(description = "Sort field", example = "createdAt")
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @Parameter(description = "Sort direction", example = "desc")
            @RequestParam(defaultValue = "desc") String sortDir,
            Authentication authentication) {
        
        Page<ProjectResponse> projects = projectService.getUserProjects(
                authentication.getName(), page, size, sortBy, sortDir);
        return ResponseEntity.ok(ApiResponse.success(projects, "Projects retrieved successfully"));
    }

    @GetMapping("/projects/featured")
    @Operation(summary = "Get featured projects", description = "Retrieves featured projects for the authenticated user")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Featured projects retrieved successfully")
    })
    public ResponseEntity<ApiResponse<List<ProjectResponse>>> getFeaturedProjects(Authentication authentication) {
        List<ProjectResponse> featuredProjects = projectService.getFeaturedProjects(authentication.getName());
        return ResponseEntity.ok(ApiResponse.success(featuredProjects, "Featured projects retrieved successfully"));
    }

    @GetMapping("/projects/{id}")
    @Operation(summary = "Get project by ID", description = "Retrieves a specific project by ID for the authenticated user")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Project retrieved successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "Project not found")
    })
    public ResponseEntity<ApiResponse<ProjectResponse>> getProjectById(
            @PathVariable Long id,
            Authentication authentication) {
        
        ProjectResponse project = projectService.getProjectById(id, authentication.getName());
        return ResponseEntity.ok(ApiResponse.success(project, "Project retrieved successfully"));
    }

    @GetMapping("/projects/search")
    @Operation(summary = "Search projects", description = "Search projects by title or description")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Search results retrieved successfully")
    })
    public ResponseEntity<ApiResponse<Page<ProjectResponse>>> searchProjects(
            @Parameter(description = "Search query", example = "react")
            @RequestParam String q,
            @Parameter(description = "Page number (0-based)", example = "0")
            @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Page size", example = "10")
            @RequestParam(defaultValue = "10") int size,
            Authentication authentication) {
        
        Page<ProjectResponse> searchResults = projectService.searchProjects(
                authentication.getName(), q, page, size);
        return ResponseEntity.ok(ApiResponse.success(searchResults, "Search results retrieved successfully"));
    }

    @GetMapping("/projects/category/{category}")
    @Operation(summary = "Get projects by category", description = "Retrieves projects filtered by category")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Projects retrieved successfully")
    })
    public ResponseEntity<ApiResponse<Page<ProjectResponse>>> getProjectsByCategory(
            @PathVariable String category,
            @Parameter(description = "Page number (0-based)", example = "0")
            @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Page size", example = "10")
            @RequestParam(defaultValue = "10") int size,
            Authentication authentication) {
        
        Page<ProjectResponse> projects = projectService.getProjectsByCategory(
                authentication.getName(), category, page, size);
        return ResponseEntity.ok(ApiResponse.success(projects, "Projects retrieved successfully"));
    }

    @GetMapping("/projects/technology/{technology}")
    @Operation(summary = "Get projects by technology", description = "Retrieves projects filtered by technology")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Projects retrieved successfully")
    })
    public ResponseEntity<ApiResponse<Page<ProjectResponse>>> getProjectsByTechnology(
            @PathVariable String technology,
            @Parameter(description = "Page number (0-based)", example = "0")
            @RequestParam(defaultValue = "0") int page,
            @Parameter(description = "Page size", example = "10")
            @RequestParam(defaultValue = "10") int size,
            Authentication authentication) {
        
        Page<ProjectResponse> projects = projectService.getProjectsByTechnology(
                authentication.getName(), technology, page, size);
        return ResponseEntity.ok(ApiResponse.success(projects, "Projects retrieved successfully"));
    }

    @DeleteMapping("/projects/{id}")
    @Operation(summary = "Delete a project", description = "Deletes a project for the authenticated user")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Project deleted successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "Project not found")
    })
    public ResponseEntity<ApiResponse<String>> deleteProject(
            @PathVariable Long id,
            Authentication authentication) {
        
        projectService.deleteProject(id, authentication.getName());
        return ResponseEntity.ok(ApiResponse.success(null, "Project deleted successfully"));
    }

    @GetMapping("/stats")
    @Operation(summary = "Get project statistics", description = "Retrieves project statistics for the authenticated user")
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Statistics retrieved successfully")
    })
    public ResponseEntity<ApiResponse<ProjectService.ProjectStatsResponse>> getProjectStats(Authentication authentication) {
        ProjectService.ProjectStatsResponse stats = projectService.getProjectStats(authentication.getName());
        return ResponseEntity.ok(ApiResponse.success(stats, "Statistics retrieved successfully"));
    }
} 