package com.vira.auth.repository;

import com.vira.auth.model.RefreshToken;
import com.vira.auth.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Optional;

/**
 * Repository interface for RefreshToken entity operations.
 */
@Repository
public interface RefreshTokenRepository extends JpaRepository<RefreshToken, Long> {

    /**
     * Find refresh token by token string.
     */
    Optional<RefreshToken> findByToken(String token);

    /**
     * Find all refresh tokens for a user.
     */
    @Query("SELECT rt FROM RefreshToken rt WHERE rt.user = :user")
    Optional<RefreshToken> findByUser(@Param("user") User user);

    /**
     * Delete refresh token by token string.
     */
    @Modifying
    @Query("DELETE FROM RefreshToken rt WHERE rt.token = :token")
    void deleteByToken(@Param("token") String token);

    /**
     * Delete all refresh tokens for a user.
     */
    @Modifying
    @Query("DELETE FROM RefreshToken rt WHERE rt.user = :user")
    void deleteByUser(@Param("user") User user);

    /**
     * Delete expired refresh tokens.
     */
    @Modifying
    @Query("DELETE FROM RefreshToken rt WHERE rt.expiresAt < :now")
    void deleteExpiredTokens(@Param("now") LocalDateTime now);

    /**
     * Check if refresh token exists by token string.
     */
    Boolean existsByToken(String token);
} 