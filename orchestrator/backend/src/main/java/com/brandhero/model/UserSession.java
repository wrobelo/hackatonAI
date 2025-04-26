package com.brandhero.model;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Represents a user session with Facebook authentication details.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "user_sessions")
public class UserSession {
    
    @Id
    private String id;
    
    private String username;
    
    private String accessToken;
    
    /**
     * Map of page IDs to their respective access tokens.
     * This allows storing access tokens for multiple pages that a user manages.
     */
    @Builder.Default
    private Map<String, String> pageAccessTokens = new HashMap<>();
    
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
    
    @Builder.Default
    private LocalDateTime lastAccessedAt = LocalDateTime.now();
    
    private LocalDateTime expiresAt;
    
    /**
     * Updates the last accessed timestamp.
     */
    public void updateLastAccessed() {
        this.lastAccessedAt = LocalDateTime.now();
    }
    
    /**
     * Checks if the session is still valid.
     * 
     * @return true if the session is valid, false otherwise
     */
    public boolean isValid() {
        return expiresAt == null || LocalDateTime.now().isBefore(expiresAt);
    }
}
