package com.vira.auth.service;

import com.vira.auth.model.User;
import com.vira.auth.repository.UserRepository;
import com.vira.auth.security.UserDetailsImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Implementation of Spring Security UserDetailsService.
 * Loads user-specific data for authentication.
 */
@Service
public class UserDetailsServiceImpl implements UserDetailsService {

    @Autowired
    private UserRepository userRepository;

    @Override
    @Transactional
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByUsernameAndEnabled(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found: " + username));

        return UserDetailsImpl.build(user);
    }
} 