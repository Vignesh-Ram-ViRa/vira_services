package com.vira.config;

import com.vira.auth.model.Role;
import com.vira.auth.model.RoleName;
import com.vira.auth.model.User;
import com.vira.auth.repository.RoleRepository;
import com.vira.auth.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.util.HashSet;
import java.util.Set;

/**
 * Initialize default data on application startup.
 * Creates default roles and admin user if they don't exist.
 */
@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private RoleRepository roleRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) throws Exception {
        createDefaultRoles();
        createDefaultAdminUser();
    }

    private void createDefaultRoles() {
        // Create GUEST role
        if (!roleRepository.existsByName(RoleName.GUEST)) {
            Role guestRole = new Role();
            guestRole.setName(RoleName.GUEST);
            guestRole.setDescription("Guest users with limited read-only access");
            roleRepository.save(guestRole);
            System.out.println("Created GUEST role");
        }

        // Create NORMAL_USER role
        if (!roleRepository.existsByName(RoleName.NORMAL_USER)) {
            Role userRole = new Role();
            userRole.setName(RoleName.NORMAL_USER);
            userRole.setDescription("Regular users with standard application access");
            roleRepository.save(userRole);
            System.out.println("Created NORMAL_USER role");
        }

        // Create SUPER_USER role
        if (!roleRepository.existsByName(RoleName.SUPER_USER)) {
            Role superUserRole = new Role();
            superUserRole.setName(RoleName.SUPER_USER);
            superUserRole.setDescription("Approved users with read-only access to everything");
            roleRepository.save(superUserRole);
            System.out.println("Created SUPER_USER role");
        }

        // Create ADMIN role
        if (!roleRepository.existsByName(RoleName.ADMIN)) {
            Role adminRole = new Role();
            adminRole.setName(RoleName.ADMIN);
            adminRole.setDescription("Administrators with full system access");
            roleRepository.save(adminRole);
            System.out.println("Created ADMIN role");
        }
    }

    private void createDefaultAdminUser() {
        // Create default admin user if not exists
        if (!userRepository.existsByUsername("admin")) {
            User admin = new User();
            admin.setUsername("admin");
            admin.setEmail("admin@vira.com");
            admin.setPassword(passwordEncoder.encode("admin123"));
            admin.setEnabled(true);
            admin.setStatus(User.UserStatus.APPROVED);

            // Assign ADMIN role
            Set<Role> roles = new HashSet<>();
            Role adminRole = roleRepository.findByName(RoleName.ADMIN)
                    .orElseThrow(() -> new RuntimeException("Admin role not found"));
            roles.add(adminRole);
            admin.setRoles(roles);

            userRepository.save(admin);
            System.out.println("✅ Created default ADMIN user: username='admin', password='admin123'");
        }
    }
} 