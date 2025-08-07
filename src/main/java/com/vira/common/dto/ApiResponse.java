package com.vira.common.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * Standardized API response wrapper for consistent JSON responses across all services.
 * 
 * @param <T> The type of data being returned
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Schema(description = "Standard API response wrapper")
public class ApiResponse<T> {

    @Schema(description = "Indicates if the request was successful", example = "true")
    private boolean success;

    @Schema(description = "Response data")
    private T data;

    @Schema(description = "Success message", example = "Operation completed successfully")
    private String message;

    @Schema(description = "Error message", example = "Validation failed")
    private String error;

    @Schema(description = "Response timestamp", example = "2024-01-15T10:30:00")
    private LocalDateTime timestamp;

    // Private constructor to enforce use of static factory methods
    private ApiResponse() {
        this.timestamp = LocalDateTime.now();
    }

    /**
     * Creates a successful response with data and message.
     *
     * @param data The response data
     * @param message Success message
     * @param <T> Type of data
     * @return ApiResponse instance
     */
    public static <T> ApiResponse<T> success(T data, String message) {
        ApiResponse<T> response = new ApiResponse<>();
        response.success = true;
        response.data = data;
        response.message = message;
        return response;
    }

    /**
     * Creates a successful response with data only.
     *
     * @param data The response data
     * @param <T> Type of data
     * @return ApiResponse instance
     */
    public static <T> ApiResponse<T> success(T data) {
        return success(data, "Success");
    }

    /**
     * Creates a successful response with message only.
     *
     * @param message Success message
     * @return ApiResponse instance
     */
    public static <Object> ApiResponse<Object> success(String message) {
        return success(null, message);
    }

    /**
     * Creates an error response with error message.
     *
     * @param error Error message
     * @return ApiResponse instance
     */
    public static <Object> ApiResponse<Object> error(String error) {
        ApiResponse<Object> response = new ApiResponse<>();
        response.success = false;
        response.error = error;
        return response;
    }

    /**
     * Creates an error response with error message and data.
     *
     * @param error Error message
     * @param data Additional error data
     * @param <T> Type of data
     * @return ApiResponse instance
     */
    public static <T> ApiResponse<T> error(String error, T data) {
        ApiResponse<T> response = new ApiResponse<>();
        response.success = false;
        response.error = error;
        response.data = data;
        return response;
    }

    // Getters
    public boolean isSuccess() {
        return success;
    }

    public T getData() {
        return data;
    }

    public String getMessage() {
        return message;
    }

    public String getError() {
        return error;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    // Setters for serialization
    public void setSuccess(boolean success) {
        this.success = success;
    }

    public void setData(T data) {
        this.data = data;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public void setError(String error) {
        this.error = error;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
} 