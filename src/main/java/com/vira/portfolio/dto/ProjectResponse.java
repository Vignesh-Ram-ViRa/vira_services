package com.vira.portfolio.dto;

import com.vira.portfolio.model.Project;
import java.time.LocalDateTime;
import java.util.Set;

public class ProjectResponse {
    
    private Long id;
    private String title;
    private String description;
    private String liveUrl;
    private String githubUrl;
    private String demoUrl;
    private String imageUrl;
    private Set<String> technologies;
    private String status;
    private String category;
    private Integer year;
    private Boolean featured;
    private String username; // User who created the project
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    // Constructors
    public ProjectResponse() {}

    public ProjectResponse(Project project) {
        this.id = project.getId();
        this.title = project.getTitle();
        this.description = project.getDescription();
        this.liveUrl = project.getLink();
        this.githubUrl = project.getGithub();
        this.demoUrl = null; // Not in Project entity
        this.imageUrl = project.getImage();
        this.technologies = project.getTechnologies() != null ? 
            new java.util.HashSet<>(project.getTechnologies()) : new java.util.HashSet<>();
        this.status = project.getStatus();
        this.category = project.getCategory();
        this.year = project.getYear();
        this.featured = project.getFeatured();
        this.username = project.getUser().getUsername();
        this.createdAt = project.getCreatedAt();
        this.updatedAt = project.getUpdatedAt();
    }

    // Static factory method
    public static ProjectResponse from(Project project) {
        return new ProjectResponse(project);
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getLiveUrl() {
        return liveUrl;
    }

    public void setLiveUrl(String liveUrl) {
        this.liveUrl = liveUrl;
    }

    public String getGithubUrl() {
        return githubUrl;
    }

    public void setGithubUrl(String githubUrl) {
        this.githubUrl = githubUrl;
    }

    public String getDemoUrl() {
        return demoUrl;
    }

    public void setDemoUrl(String demoUrl) {
        this.demoUrl = demoUrl;
    }

    public String getImageUrl() {
        return imageUrl;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public Set<String> getTechnologies() {
        return technologies;
    }

    public void setTechnologies(Set<String> technologies) {
        this.technologies = technologies;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public Integer getYear() {
        return year;
    }

    public void setYear(Integer year) {
        this.year = year;
    }

    public Boolean getFeatured() {
        return featured;
    }

    public void setFeatured(Boolean featured) {
        this.featured = featured;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
} 