package com.vira.portfolio.controller;

import com.vira.common.dto.ApiResponse;
import com.vira.portfolio.dto.ProjectResponse;
import com.vira.portfolio.service.ProjectService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/public")
@CrossOrigin(origins = {"http://localhost:8080", "http://localhost:3000", "http://localhost:3001"}, allowCredentials = "false")
@Tag(name = "Public", description = "Public endpoints accessible to guest users without authentication. No login required.")
public class PublicController {

    @Autowired
    private ProjectService projectService;

    @GetMapping("/projects")
    @Operation(
        summary = "Get public projects",
        description = "Retrieve all public projects (private = false) that are visible to guest users. " +
                     "No authentication required. Perfect for showcasing portfolios publicly."
    )
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Public projects retrieved successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<ApiResponse<Page<ProjectResponse>>> getPublicProjects(
            @Parameter(description = "Page number (0-based)", example = "0")
            @RequestParam(defaultValue = "0") int page,
            
            @Parameter(description = "Page size", example = "10")
            @RequestParam(defaultValue = "10") int size,
            
            @Parameter(description = "Sort field", example = "createdAt")
            @RequestParam(defaultValue = "createdAt") String sortBy,
            
            @Parameter(description = "Sort direction", example = "desc")
            @RequestParam(defaultValue = "desc") String sortDir,
            
            @Parameter(description = "Filter by technology", example = "React")
            @RequestParam(required = false) String technology,
            
            @Parameter(description = "Filter by category", example = "WEB_APPLICATION")
            @RequestParam(required = false) String category,
            
            @Parameter(description = "Show only featured projects", example = "true")
            @RequestParam(required = false) Boolean featured
    ) {
        Page<ProjectResponse> projects = projectService.getPublicProjects(
            page, size, sortBy, sortDir, technology, category, featured
        );
        return ResponseEntity.ok(ApiResponse.success(projects, "Public projects retrieved successfully"));
    }

    @GetMapping("/projects/{id}")
    @Operation(
        summary = "Get public project by ID",
        description = "Retrieve a specific public project by ID. Only returns the project if it's public (private = false). " +
                     "No authentication required."
    )
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Public project retrieved successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "404", description = "Project not found or is private"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<ApiResponse<ProjectResponse>> getPublicProject(
            @Parameter(description = "Project ID", example = "1")
            @PathVariable Long id
    ) {
        ProjectResponse project = projectService.getPublicProject(id);
        return ResponseEntity.ok(ApiResponse.success(project, "Public project retrieved successfully"));
    }

    @GetMapping("/projects/featured")
    @Operation(
        summary = "Get featured public projects",
        description = "Retrieve all featured public projects. These are highlighted projects that are both featured=true and private=false. " +
                     "Perfect for homepage showcases. No authentication required."
    )
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Featured projects retrieved successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<ApiResponse<List<ProjectResponse>>> getFeaturedPublicProjects() {
        List<ProjectResponse> projects = projectService.getFeaturedPublicProjects();
        return ResponseEntity.ok(ApiResponse.success(projects, "Featured public projects retrieved successfully"));
    }

    @GetMapping("/projects/stats")
    @Operation(
        summary = "Get public project statistics",
        description = "Get general statistics about public projects (total count, technology breakdown, etc.). " +
                     "No authentication required. Useful for dashboard widgets."
    )
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Statistics retrieved successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<ApiResponse<ProjectService.PublicProjectStatsResponse>> getPublicProjectStats() {
        ProjectService.PublicProjectStatsResponse stats = projectService.getPublicProjectStats();
        return ResponseEntity.ok(ApiResponse.success(stats, "Public project statistics retrieved successfully"));
    }

    @GetMapping("/projects/technologies")
    @Operation(
        summary = "Get all technologies used in public projects",
        description = "Retrieve a list of all technologies used across public projects. " +
                     "Useful for filtering and technology cloud displays. No authentication required."
    )
    @ApiResponses(value = {
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Technologies retrieved successfully"),
        @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "500", description = "Internal server error")
    })
    public ResponseEntity<ApiResponse<List<String>>> getPublicProjectTechnologies() {
        List<String> technologies = projectService.getPublicProjectTechnologies();
        return ResponseEntity.ok(ApiResponse.success(technologies, "Public project technologies retrieved successfully"));
    }
} 