package com.vira.auth.service;

import com.vira.auth.dto.AuthResponse;
import com.vira.auth.dto.UserResponse;
import com.vira.auth.model.Role;
import com.vira.auth.model.RoleName;
import com.vira.auth.model.User;
import com.vira.auth.repository.RoleRepository;
import com.vira.auth.repository.UserRepository;
import com.vira.auth.security.JwtUtils;
import com.vira.auth.security.UserDetailsImpl;
import com.vira.common.exception.BusinessException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashSet;
import java.util.Map;
import java.util.Set;

@Service
@Transactional
public class OAuth2Service {

    private static final Logger logger = LoggerFactory.getLogger(OAuth2Service.class);

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private RoleRepository roleRepository;

    @Autowired
    private JwtUtils jwtUtils;

    @Autowired
    private AuthService authService;

    /**
     * Process Google OAuth2 login
     */
    public AuthResponse processGoogleOAuth2User(OAuth2User oauth2User) {
        logger.info("Processing Google OAuth2 login");

        Map<String, Object> attributes = oauth2User.getAttributes();
        String googleId = (String) attributes.get("sub");
        String email = (String) attributes.get("email");
        String name = (String) attributes.get("name");
        String picture = (String) attributes.get("picture");

        logger.info("Google OAuth2 user - email: {}, name: {}, googleId: {}", email, name, googleId);

        // Check if user exists by Google ID
        User user = userRepository.findByGoogleId(googleId).orElse(null);

        if (user == null) {
            // Check if user exists by email
            user = userRepository.findByEmail(email).orElse(null);
            
            if (user != null) {
                // Link existing account with Google
                user.setGoogleId(googleId);
                user = userRepository.save(user);
                logger.info("Linked existing user {} with Google account", user.getUsername());
            } else {
                // Create new user
                user = createNewGoogleUser(googleId, email, name, picture);
                logger.info("Created new user from Google OAuth: {}", user.getUsername());
            }
        } else {
            // Update user info from Google
            if (name != null && !name.equals(user.getUsername())) {
                // Optionally update name/profile info
                logger.info("Google user {} logged in", user.getUsername());
            }
        }

        // Generate JWT tokens
        UserDetailsImpl userDetails = UserDetailsImpl.build(user);
        String jwt = jwtUtils.generateToken(userDetails);
        String refreshToken = jwtUtils.generateRefreshToken(userDetails);

        // Save refresh token
        authService.saveRefreshToken(user, refreshToken);

        UserResponse userResponse = authService.convertToUserResponse(user);
        
        logger.info("Google OAuth2 login successful for user: {}", user.getUsername());
        return new AuthResponse(jwt, refreshToken, "Bearer", userResponse, "Google OAuth2 login successful");
    }

    /**
     * Create new user from Google OAuth2 data
     */
    private User createNewGoogleUser(String googleId, String email, String name, String picture) {
        // Generate username from email or name
        String username = generateUsernameFromEmail(email);
        
        // Ensure username is unique
        String finalUsername = ensureUniqueUsername(username);

        User user = new User();
        user.setUsername(finalUsername);
        user.setEmail(email);
        user.setGoogleId(googleId);
        user.setEnabled(true);
        user.setStatus(User.UserStatus.APPROVED);
        
        // No password needed for OAuth users
        user.setPassword(""); // Empty password for OAuth users

        // Assign NORMAL_USER role
        Set<Role> roles = new HashSet<>();
        Role userRole = roleRepository.findByName(RoleName.NORMAL_USER)
                .orElseThrow(() -> new BusinessException("Default user role not found", HttpStatus.INTERNAL_SERVER_ERROR));
        roles.add(userRole);
        user.setRoles(roles);

        return userRepository.save(user);
    }

    /**
     * Generate username from email
     */
    private String generateUsernameFromEmail(String email) {
        if (email == null || !email.contains("@")) {
            return "user" + System.currentTimeMillis();
        }
        
        String username = email.substring(0, email.indexOf("@"));
        // Remove special characters and make it alphanumeric
        username = username.replaceAll("[^a-zA-Z0-9]", "");
        
        if (username.length() < 3) {
            username = "user" + username;
        }
        
        return username.toLowerCase();
    }

    /**
     * Ensure username is unique by appending numbers if needed
     */
    private String ensureUniqueUsername(String baseUsername) {
        String username = baseUsername;
        int counter = 1;
        
        while (userRepository.existsByUsername(username)) {
            username = baseUsername + counter;
            counter++;
        }
        
        return username;
    }
} 