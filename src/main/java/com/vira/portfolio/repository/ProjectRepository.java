package com.vira.portfolio.repository;

import com.vira.portfolio.model.Project;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProjectRepository extends JpaRepository<Project, Long> {
    
    // Find projects by user ID
    Page<Project> findByUserId(Long userId, Pageable pageable);
    List<Project> findByUserId(Long userId);
    
    // Find featured projects by user
    List<Project> findByUserIdAndFeaturedTrueOrderByCreatedAtDesc(Long userId);
    
    // Find projects by category
    Page<Project> findByUserIdAndCategoryContainingIgnoreCase(Long userId, String category, Pageable pageable);
    
    // Find projects by status
    Page<Project> findByUserIdAndStatus(Long userId, String status, Pageable pageable);
    
    // Find projects by year
    Page<Project> findByUserIdAndYear(Long userId, Integer year, Pageable pageable);
    
    // Search projects by title or description
    @Query("SELECT p FROM Project p WHERE p.user.id = :userId AND " +
           "(LOWER(p.title) LIKE LOWER(CONCAT('%', :search, '%')) OR " +
           "LOWER(p.description) LIKE LOWER(CONCAT('%', :search, '%')))")
    Page<Project> searchProjects(@Param("userId") Long userId, 
                                 @Param("search") String search, 
                                 Pageable pageable);
    
    // Find projects by technology
    @Query("SELECT p FROM Project p JOIN p.technologies t WHERE p.user.id = :userId AND " +
           "LOWER(t) LIKE LOWER(CONCAT('%', :technology, '%'))")
    Page<Project> findByUserIdAndTechnologiesContaining(@Param("userId") Long userId, 
                                                        @Param("technology") String technology, 
                                                        Pageable pageable);
    
    // Count projects by user
    long countByUserId(Long userId);
    
    // Check if project exists by title and user
    boolean existsByUserIdAndTitleIgnoreCase(Long userId, String title);
    
    // Find project by ID and user ID (for security)
    Optional<Project> findByIdAndUserId(Long id, Long userId);

    // ========================
    // PUBLIC PROJECT METHODS (Guest Access)
    // ========================
    
    // Find all public projects (private = false)
    Page<Project> findByIsPrivateFalse(Pageable pageable);
    List<Project> findByIsPrivateFalse();
    
    // Find public projects by category
    Page<Project> findByIsPrivateFalseAndCategoryContainingIgnoreCase(String category, Pageable pageable);
    
    // Find public featured projects
    List<Project> findByIsPrivateFalseAndFeaturedTrueOrderByCreatedAtDesc();
    
    // Find public projects by technology
    @Query("SELECT p FROM Project p JOIN p.technologies t WHERE p.isPrivate = false AND LOWER(t) LIKE LOWER(CONCAT('%', :technology, '%'))")
    Page<Project> findPublicProjectsByTechnology(@Param("technology") String technology, Pageable pageable);
    
    // Find public project by ID
    @Query("SELECT p FROM Project p WHERE p.id = :id AND p.isPrivate = false")
    Optional<Project> findPublicProjectById(@Param("id") Long id);
    
    // Count public projects
    long countByIsPrivateFalse();
    
    // Count public featured projects
    long countByIsPrivateFalseAndFeaturedTrue();
    
    // Get all technologies from public projects
    @Query("SELECT DISTINCT t FROM Project p JOIN p.technologies t WHERE p.isPrivate = false ORDER BY t")
    List<String> findDistinctTechnologiesFromPublicProjects();
    
    // Complex public project filtering
    @Query("SELECT p FROM Project p JOIN p.technologies t WHERE " +
           "p.isPrivate = false " +
           "AND (:category IS NULL OR LOWER(p.category) LIKE LOWER(CONCAT('%', :category, '%'))) " +
           "AND (:technology IS NULL OR LOWER(t) LIKE LOWER(CONCAT('%', :technology, '%'))) " +
           "AND (:featured IS NULL OR p.featured = :featured)")
    Page<Project> findPublicProjectsWithFilters(
        @Param("category") String category,
        @Param("technology") String technology, 
        @Param("featured") Boolean featured,
        Pageable pageable
    );
} 