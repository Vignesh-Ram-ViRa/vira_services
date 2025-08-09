package com.vira.portfolio.dto;

import jakarta.validation.constraints.*;
import java.util.Set;

public class ProjectRequest {
    
    @NotBlank(message = "Title is required")
    @Size(max = 200, message = "Title must not exceed 200 characters")
    private String title;
    
    @NotBlank(message = "Description is required")
    @Size(max = 2000, message = "Description must not exceed 2000 characters")
    private String description;
    
    @Size(max = 500, message = "Live URL must not exceed 500 characters")
    private String liveUrl;
    
    @Size(max = 500, message = "GitHub URL must not exceed 500 characters")
    private String githubUrl;
    
    @Size(max = 500, message = "Demo URL must not exceed 500 characters")
    private String demoUrl;
    
    @Size(max = 500, message = "Image URL must not exceed 500 characters")
    private String imageUrl;
    
    @NotEmpty(message = "At least one technology is required")
    @Size(max = 20, message = "Maximum 20 technologies allowed")
    private Set<@NotBlank @Size(max = 50) String> technologies;
    
    @Size(max = 50, message = "Status must not exceed 50 characters")
    private String status = "Completed";
    
    @Size(max = 100, message = "Category must not exceed 100 characters")
    private String category;
    
    @Min(value = 1990, message = "Year must be at least 1990")
    @Max(value = 2100, message = "Year must not exceed 2100")
    private Integer year;
    
    private Boolean featured = false;

    private Boolean isPrivate = false;

    // Constructors
    public ProjectRequest() {}

    public ProjectRequest(String title, String description, Set<String> technologies) {
        this.title = title;
        this.description = description;
        this.technologies = technologies;
    }

    // Getters and Setters
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

    public Boolean getPrivate() {
        return isPrivate;
    }

    public void setPrivate(Boolean aPrivate) {
        isPrivate = aPrivate;
    }
} 