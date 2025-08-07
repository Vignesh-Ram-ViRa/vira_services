package com.vira.auth.repository;

import com.vira.auth.model.Role;
import com.vira.auth.model.RoleName;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Repository interface for Role entity operations.
 */
@Repository
public interface RoleRepository extends JpaRepository<Role, Long> {

    /**
     * Find role by name.
     */
    Optional<Role> findByName(RoleName name);

    /**
     * Check if role exists by name.
     */
    Boolean existsByName(RoleName name);
} 