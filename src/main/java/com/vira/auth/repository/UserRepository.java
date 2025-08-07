package com.vira.auth.repository;

import com.vira.auth.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Repository interface for User entity operations.
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * Find user by username.
     */
    Optional<User> findByUsername(String username);

    /**
     * Find user by email.
     */
    Optional<User> findByEmail(String email);

    /**
     * Find user by username or email.
     */
    @Query("SELECT u FROM User u WHERE u.username = :usernameOrEmail OR u.email = :usernameOrEmail")
    Optional<User> findByUsernameOrEmail(@Param("usernameOrEmail") String usernameOrEmail);

    /**
     * Check if username exists.
     */
    Boolean existsByUsername(String username);

    /**
     * Check if email exists.
     */
    Boolean existsByEmail(String email);

    /**
     * Find enabled user by username.
     */
    @Query("SELECT u FROM User u WHERE u.username = :username AND u.enabled = true")
    Optional<User> findByUsernameAndEnabled(@Param("username") String username);

    /**
     * Count total users.
     */
    @Query("SELECT COUNT(u) FROM User u")
    Long countAllUsers();

    /**
     * Count enabled users.
     */
    @Query("SELECT COUNT(u) FROM User u WHERE u.enabled = true")
    Long countEnabledUsers();
} 