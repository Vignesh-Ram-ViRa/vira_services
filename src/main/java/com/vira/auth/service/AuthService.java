package com.vira.auth.service;

import com.vira.auth.dto.*;
import com.vira.auth.model.RefreshToken;
import com.vira.auth.model.Role;
import com.vira.auth.model.RoleName;
import com.vira.auth.model.User;
import com.vira.auth.repository.RefreshTokenRepository;
import com.vira.auth.repository.RoleRepository;
import com.vira.auth.repository.UserRepository;
import com.vira.auth.security.JwtUtils;
import com.vira.auth.security.UserDetailsImpl;
import com.vira.common.exception.BusinessException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Service class for handling authentication operations.
 */
@Service
@Transactional
public class AuthService {

    private static final Logger logger = LoggerFactory.getLogger(AuthService.class);

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private RoleRepository roleRepository;

    @Autowired
    private RefreshTokenRepository refreshTokenRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtUtils jwtUtils;

    /**
     * Register a new user.
     */
    public AuthResponse register(RegisterRequest request) {
        logger.info("Registering new user: {}", request.getUsername());

        // Validate if username already exists
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new BusinessException("Username is already taken!", HttpStatus.BAD_REQUEST);
        }

        // Validate if email already exists
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException("Email is already in use!", HttpStatus.BAD_REQUEST);
        }

        // Create new user
        User user = new User(
                request.getUsername(),
                request.getEmail(),
                passwordEncoder.encode(request.getPassword())
        );

        // Assign default NORMAL_USER role
        Set<Role> roles = new HashSet<>();
        Role userRole = roleRepository.findByName(RoleName.NORMAL_USER)
                .orElseThrow(() -> new BusinessException("Default user role not found", HttpStatus.INTERNAL_SERVER_ERROR));
        roles.add(userRole);
        user.setRoles(roles);

        // Save user
        user = userRepository.save(user);

        // Generate tokens
        UserDetailsImpl userDetails = UserDetailsImpl.build(user);
        String jwt = jwtUtils.generateToken(userDetails);
        String refreshToken = jwtUtils.generateRefreshToken(userDetails);

        // Save refresh token
        saveRefreshToken(user, refreshToken);

        logger.info("User registered successfully: {}", user.getUsername());

        return new AuthResponse(jwt, refreshToken, convertToUserResponse(user));
    }

    /**
     * Authenticate user login.
     */
    public AuthResponse login(LoginRequest request) {
        logger.info("Attempting login for user: {}", request.getUsername());

        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
        );

        SecurityContextHolder.getContext().setAuthentication(authentication);
        UserDetailsImpl userDetails = (UserDetailsImpl) authentication.getPrincipal();

        String jwt = jwtUtils.generateToken(userDetails);
        String refreshToken = jwtUtils.generateRefreshToken(userDetails);

        // Get user entity for response
        User user = userRepository.findById(userDetails.getId())
                .orElseThrow(() -> new BusinessException("User not found", HttpStatus.NOT_FOUND));

        // Save refresh token
        saveRefreshToken(user, refreshToken);

        logger.info("User logged in successfully: {}", user.getUsername());

        return new AuthResponse(jwt, refreshToken, convertToUserResponse(user));
    }

    /**
     * Refresh JWT token using refresh token.
     */
    public AuthResponse refreshToken(RefreshTokenRequest request) {
        String requestRefreshToken = request.getRefreshToken();

        RefreshToken refreshToken = refreshTokenRepository.findByToken(requestRefreshToken)
                .orElseThrow(() -> new BusinessException("Refresh token not found", HttpStatus.NOT_FOUND));

        if (refreshToken.isExpired()) {
            refreshTokenRepository.delete(refreshToken);
            throw new BusinessException("Refresh token expired", HttpStatus.UNAUTHORIZED);
        }

        User user = refreshToken.getUser();
        UserDetailsImpl userDetails = UserDetailsImpl.build(user);

        String newJwt = jwtUtils.generateToken(userDetails);
        String newRefreshToken = jwtUtils.generateRefreshToken(userDetails);

        // Update refresh token
        refreshToken.setToken(newRefreshToken);
        refreshToken.setExpiresAt(LocalDateTime.now().plusSeconds(jwtUtils.getRefreshExpirationMs() / 1000));
        refreshTokenRepository.save(refreshToken);

        logger.info("Token refreshed for user: {}", user.getUsername());

        return new AuthResponse(newJwt, newRefreshToken, convertToUserResponse(user));
    }

    /**
     * Logout user by invalidating refresh token.
     */
    public void logout(String refreshToken) {
        if (refreshToken != null) {
            refreshTokenRepository.deleteByToken(refreshToken);
            logger.info("User logged out successfully");
        }
    }

    /**
     * Get current authenticated user information.
     */
    public UserResponse getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        
        if (authentication == null || !authentication.isAuthenticated()) {
            throw new BusinessException("User not authenticated", HttpStatus.UNAUTHORIZED);
        }

        UserDetailsImpl userDetails = (UserDetailsImpl) authentication.getPrincipal();
        User user = userRepository.findById(userDetails.getId())
                .orElseThrow(() -> new BusinessException("User not found", HttpStatus.NOT_FOUND));

        return convertToUserResponse(user);
    }

    /**
     * Save or update refresh token for user.
     */
    public void saveRefreshToken(User user, String tokenValue) {
        // Remove existing refresh token for user
        refreshTokenRepository.findByUser(user).ifPresent(refreshTokenRepository::delete);

        // Create new refresh token
        RefreshToken refreshToken = new RefreshToken(
                user,
                tokenValue,
                LocalDateTime.now().plusSeconds(jwtUtils.getRefreshExpirationMs() / 1000)
        );

        refreshTokenRepository.save(refreshToken);
    }

    /**
     * Register a new super user (requires admin approval).
     */
    public AuthResponse registerSuperUser(SuperUserRequest request) {
        logger.info("Registering new super user: {}", request.getUsername());

        // Validate if username already exists
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new BusinessException("Username is already taken!", HttpStatus.BAD_REQUEST);
        }

        // Validate if email already exists
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException("Email is already in use!", HttpStatus.BAD_REQUEST);
        }

        // Create new user with pending approval status
        User user = new User(
                request.getUsername(),
                request.getEmail(),
                passwordEncoder.encode(request.getPassword())
        );
        
        user.setStatus(User.UserStatus.PENDING_APPROVAL);
        user.setRequestedRole(RoleName.SUPER_USER);
        user.setApprovalNotes(buildApprovalNotes(request));
        user.setEnabled(false); // Disabled until approved

        // Assign GUEST role temporarily
        Set<Role> roles = new HashSet<>();
        Role guestRole = roleRepository.findByName(RoleName.GUEST)
                .orElseThrow(() -> new BusinessException("Guest role not found", HttpStatus.INTERNAL_SERVER_ERROR));
        roles.add(guestRole);
        user.setRoles(roles);

        // Save user
        user = userRepository.save(user);

        logger.info("Super user registration submitted for approval: {}", user.getUsername());

        return new AuthResponse(
                null, // No token until approved
                null, // No refresh token until approved
                "Bearer",
                convertToUserResponse(user),
                "Registration submitted for admin approval"
        );
    }

    /**
     * Approve or reject a super user request (admin only).
     */
    public UserResponse approveSuperUser(ApprovalRequest request, Authentication adminAuth) {
        logger.info("Processing super user approval for user ID: {}", request.getUserId());

        User user = userRepository.findById(request.getUserId())
                .orElseThrow(() -> new BusinessException("User not found", HttpStatus.NOT_FOUND));

        if (!user.isPendingApproval()) {
            throw new BusinessException("User is not pending approval", HttpStatus.BAD_REQUEST);
        }

        UserDetailsImpl adminDetails = (UserDetailsImpl) adminAuth.getPrincipal();
        User admin = userRepository.findById(adminDetails.getId())
                .orElseThrow(() -> new BusinessException("Admin not found", HttpStatus.NOT_FOUND));

        if (request.getApproved()) {
            // Approve the user
            user.setStatus(User.UserStatus.APPROVED);
            user.setEnabled(true);
            user.setApprovedBy(admin.getId());
            user.setApprovedAt(LocalDateTime.now());
            user.setApprovalNotes(request.getNotes());

            // Assign SUPER_USER role
            Set<Role> roles = new HashSet<>();
            Role superUserRole = roleRepository.findByName(RoleName.SUPER_USER)
                    .orElseThrow(() -> new BusinessException("Super user role not found", HttpStatus.INTERNAL_SERVER_ERROR));
            roles.add(superUserRole);
            user.setRoles(roles);

            logger.info("Super user approved: {} by admin: {}", user.getUsername(), admin.getUsername());
        } else {
            // Reject the user
            user.setStatus(User.UserStatus.REJECTED);
            user.setApprovalNotes(request.getNotes());
            user.setApprovedBy(admin.getId());
            user.setApprovedAt(LocalDateTime.now());

            logger.info("Super user rejected: {} by admin: {}", user.getUsername(), admin.getUsername());
        }

        user = userRepository.save(user);
        return convertToUserResponse(user);
    }

    /**
     * Get all pending super user requests (admin only).
     */
    public Set<UserResponse> getPendingApprovals() {
        return userRepository.findByStatus(User.UserStatus.PENDING_APPROVAL)
                .stream()
                .map(this::convertToUserResponse)
                .collect(Collectors.toSet());
    }

    /**
     * Update user role (admin only).
     */
    public UserResponse updateUserRole(Long userId, RoleName newRole, Authentication adminAuth) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException("User not found", HttpStatus.NOT_FOUND));

        Role role = roleRepository.findByName(newRole)
                .orElseThrow(() -> new BusinessException("Role not found", HttpStatus.NOT_FOUND));

        Set<Role> roles = new HashSet<>();
        roles.add(role);
        user.setRoles(roles);

        user = userRepository.save(user);

        UserDetailsImpl adminDetails = (UserDetailsImpl) adminAuth.getPrincipal();
        logger.info("User role updated: {} to {} by admin: {}", 
                user.getUsername(), newRole, adminDetails.getUsername());

        return convertToUserResponse(user);
    }

    /**
     * Build approval notes from super user request.
     */
    private String buildApprovalNotes(SuperUserRequest request) {
        StringBuilder notes = new StringBuilder();
        notes.append("Justification: ").append(request.getJustification());
        
        if (request.getOrganization() != null && !request.getOrganization().isEmpty()) {
            notes.append(" | Organization: ").append(request.getOrganization());
        }
        
        if (request.getPosition() != null && !request.getPosition().isEmpty()) {
            notes.append(" | Position: ").append(request.getPosition());
        }
        
        return notes.toString();
    }

    /**
     * Convert User entity to UserResponse DTO.
     */
    public UserResponse convertToUserResponse(User user) {
        Set<String> roleNames = user.getRoles().stream()
                .map(role -> role.getName().name())
                .collect(Collectors.toSet());

        return new UserResponse(
                user.getId(),
                user.getUsername(),
                user.getEmail(),
                user.getEnabled(),
                roleNames,
                user.getCreatedAt()
        );
    }
} 