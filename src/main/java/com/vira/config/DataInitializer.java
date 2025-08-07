package com.vira.config;

import com.vira.auth.model.Role;
import com.vira.auth.model.RoleName;
import com.vira.auth.repository.RoleRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/**
 * Data initializer to ensure default roles exist in the database.
 */
@Component
public class DataInitializer implements CommandLineRunner {

    private static final Logger logger = LoggerFactory.getLogger(DataInitializer.class);

    private final RoleRepository roleRepository;

    @Autowired
    public DataInitializer(RoleRepository roleRepository) {
        this.roleRepository = roleRepository;
    }

    @Override
    public void run(String... args) throws Exception {
        logger.info("Initializing default data...");
        
        // Create default roles if they don't exist
        if (!roleRepository.existsByName(RoleName.USER)) {
            Role userRole = new Role();
            userRole.setName(RoleName.USER);
            userRole.setDescription("Default user role");
            roleRepository.save(userRole);
            logger.info("Created default USER role");
        }

        if (!roleRepository.existsByName(RoleName.ADMIN)) {
            Role adminRole = new Role();
            adminRole.setName(RoleName.ADMIN);
            adminRole.setDescription("Administrator role");
            roleRepository.save(adminRole);
            logger.info("Created default ADMIN role");
        }

        logger.info("Data initialization completed");
    }
} 