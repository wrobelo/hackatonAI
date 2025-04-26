package com.brandhero.repository;

import java.util.Optional;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import com.brandhero.model.UserSession;

/**
 * Repository for managing UserSession entities in MongoDB.
 */
@Repository
public interface UserSessionRepository extends MongoRepository<UserSession, String> {
    
    /**
     * Find a user session by username.
     * 
     * @param username the username to search for
     * @return an Optional containing the user session if found
     */
    Optional<UserSession> findByUsername(String username);
    
    /**
     * Find a user session by access token.
     * 
     * @param accessToken the Facebook access token
     * @return an Optional containing the user session if found
     */
    Optional<UserSession> findByAccessToken(String accessToken);
}
