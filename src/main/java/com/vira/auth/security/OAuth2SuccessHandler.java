package com.vira.auth.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vira.auth.dto.AuthResponse;
import com.vira.auth.service.OAuth2Service;
import com.vira.common.dto.ApiResponse;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

@Component
public class OAuth2SuccessHandler extends SimpleUrlAuthenticationSuccessHandler {

    private static final Logger logger = LoggerFactory.getLogger(OAuth2SuccessHandler.class);

    @Autowired
    private OAuth2Service oauth2Service;

    @Value("${app.oauth2.redirect-url:http://localhost:3000/auth/oauth2/redirect}")
    private String redirectUrl;

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response,
                                      Authentication authentication) throws IOException, ServletException {
        
        logger.info("OAuth2 authentication successful");

        try {
            OAuth2User oauth2User = (OAuth2User) authentication.getPrincipal();
            
            // Process OAuth2 user and generate JWT
            AuthResponse authResponse = oauth2Service.processGoogleOAuth2User(oauth2User);
            
            // For development/API testing, return JSON response
            if (isApiRequest(request)) {
                response.setContentType("application/json");
                response.setCharacterEncoding("UTF-8");
                
                ApiResponse<AuthResponse> apiResponse = ApiResponse.success(authResponse, "Google OAuth2 login successful");
                ObjectMapper mapper = new ObjectMapper();
                response.getWriter().write(mapper.writeValueAsString(apiResponse));
                return;
            }
            
            // For frontend integration, redirect with tokens in URL parameters
            String finalRedirectUrl = buildRedirectUrl(authResponse);
            logger.info("Redirecting to: {}", finalRedirectUrl);
            
            getRedirectStrategy().sendRedirect(request, response, finalRedirectUrl);
            
        } catch (Exception e) {
            logger.error("Error during OAuth2 authentication success handling", e);
            
            // Redirect to error page
            String errorUrl = redirectUrl + "?error=" + URLEncoder.encode("Authentication failed", StandardCharsets.UTF_8);
            getRedirectStrategy().sendRedirect(request, response, errorUrl);
        }
    }

    private boolean isApiRequest(HttpServletRequest request) {
        String acceptHeader = request.getHeader("Accept");
        return acceptHeader != null && acceptHeader.contains("application/json");
    }

    private String buildRedirectUrl(AuthResponse authResponse) {
        try {
            StringBuilder url = new StringBuilder(redirectUrl);
            url.append("?token=").append(URLEncoder.encode(authResponse.getToken(), StandardCharsets.UTF_8));
            url.append("&refreshToken=").append(URLEncoder.encode(authResponse.getRefreshToken(), StandardCharsets.UTF_8));
            url.append("&user=").append(URLEncoder.encode(authResponse.getUser().getUsername(), StandardCharsets.UTF_8));
            url.append("&type=oauth2");
            
            return url.toString();
        } catch (Exception e) {
            logger.error("Error building redirect URL", e);
            return redirectUrl + "?error=redirect_error";
        }
    }
} 