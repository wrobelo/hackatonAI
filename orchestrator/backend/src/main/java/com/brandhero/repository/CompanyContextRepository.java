package com.brandhero.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import com.brandhero.model.CompanyContext;

/**
 * Repository for managing CompanyContext entities in MongoDB.
 */
@Repository
public interface CompanyContextRepository extends MongoRepository<CompanyContext, String> {
    
    /**
     * Find a company context by page ID.
     * 
     * @param pageId the Facebook page ID
     * @return an Optional containing the company context if found
     */
    Optional<CompanyContext> findByPageId(String pageId);
    
    /**
     * Find all company contexts for a specific user.
     * 
     * @param userId the user ID
     * @return a list of company contexts
     */
    List<CompanyContext> findByUserId(String userId);
    
    /**
     * Find all company contexts for a specific username.
     * 
     * @param username the username
     * @return a list of company contexts
     */
    List<CompanyContext> findByUsername(String username);
    
    /**
     * Find a company context by page ID and username.
     * 
     * @param pageId the Facebook page ID
     * @param username the username
     * @return an Optional containing the company context if found
     */
    Optional<CompanyContext> findByPageIdAndUsername(String pageId, String username);
}
