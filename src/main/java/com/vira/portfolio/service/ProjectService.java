package com.vira.portfolio.service;

import com.vira.auth.model.User;
import com.vira.auth.repository.UserRepository;
import com.vira.common.exception.BusinessException;
import com.vira.portfolio.dto.ProjectRequest;
import com.vira.portfolio.dto.ProjectResponse;
import com.vira.portfolio.model.Project;
import com.vira.portfolio.repository.ProjectRepository;
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
public class ProjectService {
    
    private static final Logger logger = LoggerFactory.getLogger(ProjectService.class);
    
    private final ProjectRepository projectRepository;
    private final UserRepository userRepository;

    @Autowired
    public ProjectService(ProjectRepository projectRepository, UserRepository userRepository) {
        this.projectRepository = projectRepository;
        this.userRepository = userRepository;
    }

    /**
     * Create a new project
     */
    public ProjectResponse createProject(ProjectRequest request, String username) {
        logger.info("Creating new project '{}' for user '{}'", request.getTitle(), username);
        
        User user = getUserByUsername(username);
        
        // Check if project with same title already exists for this user
        if (projectRepository.existsByUserIdAndTitleIgnoreCase(user.getId(), request.getTitle())) {
            throw new BusinessException("Project with title '" + request.getTitle() + "' already exists", 
                                       HttpStatus.CONFLICT);
        }
        
        Project project = new Project();
        mapRequestToProject(request, project);
        project.setUser(user);
        
        // Set current year if not provided
        if (project.getYear() == null) {
            project.setYear(LocalDateTime.now().getYear());
        }
        
        Project savedProject = projectRepository.save(project);
        logger.info("Project '{}' created successfully with ID: {}", savedProject.getTitle(), savedProject.getId());
        
        return ProjectResponse.from(savedProject);
    }

    /**
     * Update an existing project
     */
    public ProjectResponse updateProject(Long projectId, ProjectRequest request, String username) {
        logger.info("Updating project ID: {} for user '{}'", projectId, username);
        
        User user = getUserByUsername(username);
        Project existingProject = getProjectByIdAndUser(projectId, user.getId());
        
        // Check title uniqueness if title is being changed
        if (!existingProject.getTitle().equalsIgnoreCase(request.getTitle()) &&
            projectRepository.existsByUserIdAndTitleIgnoreCase(user.getId(), request.getTitle())) {
            throw new BusinessException("Project with title '" + request.getTitle() + "' already exists", 
                                       HttpStatus.CONFLICT);
        }
        
        mapRequestToProject(request, existingProject);
        
        Project savedProject = projectRepository.save(existingProject);
        logger.info("Project '{}' updated successfully", savedProject.getTitle());
        
        return ProjectResponse.from(savedProject);
    }

    /**
     * Get all projects for a user with pagination
     */
    @Transactional(readOnly = true)
    public Page<ProjectResponse> getUserProjects(String username, int page, int size, String sortBy, String sortDir) {
        logger.info("Fetching projects for user '{}' - page: {}, size: {}", username, page, size);
        
        User user = getUserByUsername(username);
        
        Sort sort = Sort.by(sortDir.equalsIgnoreCase("desc") ? Sort.Direction.DESC : Sort.Direction.ASC, sortBy);
        Pageable pageable = PageRequest.of(page, size, sort);
        
        Page<Project> projects = projectRepository.findByUserId(user.getId(), pageable);
        
        return projects.map(ProjectResponse::from);
    }

    /**
     * Get featured projects for a user
     */
    @Transactional(readOnly = true)
    public List<ProjectResponse> getFeaturedProjects(String username) {
        logger.info("Fetching featured projects for user '{}'", username);
        
        User user = getUserByUsername(username);
        List<Project> featuredProjects = projectRepository.findByUserIdAndFeaturedTrueOrderByCreatedAtDesc(user.getId());
        
        return featuredProjects.stream()
                .map(ProjectResponse::from)
                .collect(Collectors.toList());
    }

    /**
     * Get project by ID
     */
    @Transactional(readOnly = true)
    public ProjectResponse getProjectById(Long projectId, String username) {
        logger.info("Fetching project ID: {} for user '{}'", projectId, username);
        
        User user = getUserByUsername(username);
        Project project = getProjectByIdAndUser(projectId, user.getId());
        
        return ProjectResponse.from(project);
    }

    /**
     * Search projects
     */
    @Transactional(readOnly = true)
    public Page<ProjectResponse> searchProjects(String username, String search, int page, int size) {
        logger.info("Searching projects for user '{}' with query: '{}'", username, search);
        
        User user = getUserByUsername(username);
        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));
        
        Page<Project> projects = projectRepository.searchProjects(user.getId(), search, pageable);
        
        return projects.map(ProjectResponse::from);
    }

    /**
     * Filter projects by category
     */
    @Transactional(readOnly = true)
    public Page<ProjectResponse> getProjectsByCategory(String username, String category, int page, int size) {
        logger.info("Fetching projects by category '{}' for user '{}'", category, username);
        
        User user = getUserByUsername(username);
        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));
        
        Page<Project> projects = projectRepository.findByUserIdAndCategoryContainingIgnoreCase(
                user.getId(), category, pageable);
        
        return projects.map(ProjectResponse::from);
    }

    /**
     * Filter projects by technology
     */
    @Transactional(readOnly = true)
    public Page<ProjectResponse> getProjectsByTechnology(String username, String technology, int page, int size) {
        logger.info("Fetching projects by technology '{}' for user '{}'", technology, username);
        
        User user = getUserByUsername(username);
        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));
        
        Page<Project> projects = projectRepository.findByUserIdAndTechnologiesContaining(
                user.getId(), technology, pageable);
        
        return projects.map(ProjectResponse::from);
    }

    /**
     * Delete a project
     */
    public void deleteProject(Long projectId, String username) {
        logger.info("Deleting project ID: {} for user '{}'", projectId, username);
        
        User user = getUserByUsername(username);
        Project project = getProjectByIdAndUser(projectId, user.getId());
        
        projectRepository.delete(project);
        logger.info("Project '{}' deleted successfully", project.getTitle());
    }

    /**
     * Get project statistics for a user
     */
    @Transactional(readOnly = true)
    public ProjectStatsResponse getProjectStats(String username) {
        logger.info("Fetching project statistics for user '{}'", username);
        
        User user = getUserByUsername(username);
        
        long totalProjects = projectRepository.countByUserId(user.getId());
        long featuredProjects = projectRepository.findByUserIdAndFeaturedTrueOrderByCreatedAtDesc(user.getId()).size();
        
        return new ProjectStatsResponse(totalProjects, featuredProjects);
    }

    /**
     * Create pageable object with sorting
     */
    private Pageable createPageable(int page, int size, String sortBy, String sortDir) {
        Sort.Direction direction = "asc".equalsIgnoreCase(sortDir) ? Sort.Direction.ASC : Sort.Direction.DESC;
        Sort sort = Sort.by(direction, sortBy);
        return PageRequest.of(page, size, sort);
    }

    // ========================
    // PUBLIC PROJECT METHODS (Guest Access)
    // ========================

    /**
     * Get public projects with pagination and filtering
     */
    @Transactional(readOnly = true)
    public Page<ProjectResponse> getPublicProjects(int page, int size, String sortBy, String sortDir, 
                                                  String technology, String category, Boolean featured) {
        logger.info("Fetching public projects - page: {}, size: {}, technology: {}, category: {}, featured: {}", 
                   page, size, technology, category, featured);
        
        Pageable pageable = createPageable(page, size, sortBy, sortDir);
        Page<Project> projects;
        
        // Use complex filtering if any filters are provided
        if (technology != null || category != null || featured != null) {
            projects = projectRepository.findPublicProjectsWithFilters(category, technology, featured, pageable);
        } else {
            projects = projectRepository.findByIsPrivateFalse(pageable);
        }
        
        logger.info("Found {} public projects", projects.getTotalElements());
        return projects.map(ProjectResponse::new);
    }

    /**
     * Get a specific public project by ID
     */
    @Transactional(readOnly = true)
    public ProjectResponse getPublicProject(Long id) {
        logger.info("Fetching public project with ID: {}", id);
        
        Project project = projectRepository.findPublicProjectById(id)
            .orElseThrow(() -> new BusinessException("Public project not found with ID: " + id, HttpStatus.NOT_FOUND));
        
        logger.info("Found public project: {}", project.getTitle());
        return new ProjectResponse(project);
    }

    /**
     * Get featured public projects
     */
    @Transactional(readOnly = true)
    public List<ProjectResponse> getFeaturedPublicProjects() {
        logger.info("Fetching featured public projects");
        
        List<Project> projects = projectRepository.findByIsPrivateFalseAndFeaturedTrueOrderByCreatedAtDesc();
        
        logger.info("Found {} featured public projects", projects.size());
        return projects.stream()
            .map(ProjectResponse::new)
            .collect(Collectors.toList());
    }

    /**
     * Get public project statistics
     */
    @Transactional(readOnly = true)
    public PublicProjectStatsResponse getPublicProjectStats() {
        logger.info("Fetching public project statistics");
        
        long totalPublicProjects = projectRepository.countByIsPrivateFalse();
        long featuredPublicProjects = projectRepository.countByIsPrivateFalseAndFeaturedTrue();
        List<String> technologies = projectRepository.findDistinctTechnologiesFromPublicProjects();
        
        logger.info("Public project stats - total: {}, featured: {}, technologies: {}", 
                   totalPublicProjects, featuredPublicProjects, technologies.size());
        
        return new PublicProjectStatsResponse(totalPublicProjects, featuredPublicProjects, technologies);
    }

    /**
     * Get all technologies used in public projects
     */
    @Transactional(readOnly = true)
    public List<String> getPublicProjectTechnologies() {
        logger.info("Fetching public project technologies");
        
        List<String> technologies = projectRepository.findDistinctTechnologiesFromPublicProjects();
        
        logger.info("Found {} distinct technologies in public projects", technologies.size());
        return technologies;
    }

    // Helper methods
    private User getUserByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new EntityNotFoundException("User not found: " + username));
    }

    private Project getProjectByIdAndUser(Long projectId, Long userId) {
        return projectRepository.findByIdAndUserId(projectId, userId)
                .orElseThrow(() -> new EntityNotFoundException("Project not found with ID: " + projectId));
    }

    private void mapRequestToProject(ProjectRequest request, Project project) {
        project.setTitle(request.getTitle());
        project.setDescription(request.getDescription());
        project.setLink(request.getLiveUrl());
        project.setGithub(request.getGithubUrl());
        project.setImage(request.getImageUrl());
        if (request.getTechnologies() != null) {
            project.setTechnologies(new java.util.ArrayList<>(request.getTechnologies()));
        }
        project.setStatus(request.getStatus());
        project.setCategory(request.getCategory());
        project.setYear(request.getYear());
        project.setFeatured(request.getFeatured() != null ? request.getFeatured() : false);
        project.setIsPrivate(request.getPrivate() != null ? request.getPrivate() : false);
    }

    // Inner class for project statistics
    public static class ProjectStatsResponse {
        private long totalProjects;
        private long featuredProjects;

        public ProjectStatsResponse(long totalProjects, long featuredProjects) {
            this.totalProjects = totalProjects;
            this.featuredProjects = featuredProjects;
        }

        public long getTotalProjects() {
            return totalProjects;
        }

        public long getFeaturedProjects() {
            return featuredProjects;
        }
    }

    // Inner class for public project statistics
    public static class PublicProjectStatsResponse {
        private long totalPublicProjects;
        private long featuredPublicProjects;
        private List<String> technologies;

        public PublicProjectStatsResponse(long totalPublicProjects, long featuredPublicProjects, List<String> technologies) {
            this.totalPublicProjects = totalPublicProjects;
            this.featuredPublicProjects = featuredPublicProjects;
            this.technologies = technologies;
        }

        public long getTotalPublicProjects() {
            return totalPublicProjects;
        }

        public long getFeaturedPublicProjects() {
            return featuredPublicProjects;
        }

        public List<String> getTechnologies() {
            return technologies;
        }
    }
} 