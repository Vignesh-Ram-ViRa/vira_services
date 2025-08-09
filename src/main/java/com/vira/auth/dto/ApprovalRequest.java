package com.vira.auth.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

/**
 * DTO for admin approval/rejection of super user requests.
 */
public class ApprovalRequest {
    
    @NotNull(message = "User ID is required")
    private Long userId;
    
    @NotNull(message = "Approval decision is required")
    private Boolean approved;
    
    @Size(max = 500, message = "Notes must not exceed 500 characters")
    private String notes;

    // Constructors
    public ApprovalRequest() {}

    public ApprovalRequest(Long userId, Boolean approved, String notes) {
        this.userId = userId;
        this.approved = approved;
        this.notes = notes;
    }

    // Getters and Setters
    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Boolean getApproved() {
        return approved;
    }

    public void setApproved(Boolean approved) {
        this.approved = approved;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    @Override
    public String toString() {
        return "ApprovalRequest{" +
                "userId=" + userId +
                ", approved=" + approved +
                ", notes='" + notes + '\'' +
                '}';
    }
} 