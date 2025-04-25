package com.brandhero.service;

import java.time.LocalDateTime;
import java.util.Optional;

import org.springframework.stereotype.Service;

import com.brandhero.model.UserSession;
import com.brandhero.repository.UserSessionRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Service for managing user sessions.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class UserSessionService {
    
    private final UserSessionRepository userSessionRepository;
    
    /**
     * Create or update a user session.
     * 
     * @param username the username
     * @param accessToken the Facebook access token
     * @return the created or updated user session
     */
    public UserSession createOrUpdateSession(String username, String accessToken) {
        log.info("Creating or updating session for user: {}", username);
        
        Optional<UserSession> existingSession = userSessionRepository.findByUsername(username);
        
        if (existingSession.isPresent()) {
            UserSession session = existingSession.get();
            session.setAccessToken(accessToken);
            session.updateLastAccessed();
            return userSessionRepository.save(session);
        } else {
            UserSession newSession = UserSession.builder()
                    .username(username)
                    .accessToken(accessToken)
                    .createdAt(LocalDateTime.now())
                    .lastAccessedAt(LocalDateTime.now())
                    .build();
            return userSessionRepository.save(newSession);
        }
    }
    
    /**
     * Get a user session by username.
     * 
     * @param username the username
     * @return an Optional containing the user session if found
     */
    public Optional<UserSession> getSessionByUsername(String username) {
        log.debug("Getting session for user: {}", username);
        return userSessionRepository.findByUsername(username);
    }
    
    /**
     * Get a user session by access token.
     * 
     * @param accessToken the Facebook access token
     * @return an Optional containing the user session if found
     */
    public Optional<UserSession> getSessionByAccessToken(String accessToken) {
        log.debug("Getting session by access token");
        return userSessionRepository.findByAccessToken(accessToken);
    }
    
    /**
     * Validate a user session.
     * 
     * @param username the username
     * @param accessToken the Facebook access token
     * @return true if the session is valid, false otherwise
     */
    public boolean validateSession(String username, String accessToken) {
        log.debug("Validating session for user: {}", username);
        
        Optional<UserSession> session = userSessionRepository.findByUsername(username);
        
        if (session.isPresent()) {
            UserSession userSession = session.get();
            boolean isValid = userSession.isValid() && userSession.getAccessToken().equals(accessToken);
            
            if (isValid) {
                userSession.updateLastAccessed();
                userSessionRepository.save(userSession);
            }
            
            return isValid;
        }
        
        return false;
    }
}
