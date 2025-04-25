package com.brandhero.controller;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.brandhero.dto.CompanyContextResponse;
import com.brandhero.dto.CreateContextRequest;
import com.brandhero.model.CompanyContext;
import com.brandhero.model.UserSession;
import com.brandhero.service.CompanyContextService;
import com.brandhero.service.UserSessionService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Controller for company context endpoints.
 */
@RestController
@RequestMapping("/api/context")
@RequiredArgsConstructor
@Slf4j
public class CompanyContextController {
    
    private final CompanyContextService companyContextService;
    private final UserSessionService userSessionService;
    
    /**
     * Create a company context.
     * 
     * @param username the username
     * @param request the create context request
     * @return a response entity with the company context
     */
    @PostMapping("/{username}")
    public ResponseEntity<CompanyContextResponse> createCompanyContext(
            @PathVariable String username,
            @Valid @RequestBody CreateContextRequest request) {
        
        log.info("Creating company context for user: {} and page: {}", username, request.getPageId());
        
        Optional<UserSession> userSessionOpt = userSessionService.getSessionByUsername(username);
        
        if (userSessionOpt.isEmpty()) {
            log.warn("User session not found for username: {}", username);
            return new ResponseEntity<>(HttpStatus.UNAUTHORIZED);
        }
        
        UserSession userSession = userSessionOpt.get();
        
        if (!userSession.isValid()) {
            log.warn("User session is invalid for username: {}", username);
            return new ResponseEntity<>(HttpStatus.UNAUTHORIZED);
        }
        
        try {
            CompanyContext companyContext = companyContextService.createCompanyContext(username, request);
            CompanyContextResponse response = CompanyContextResponse.from(companyContext);
            return new ResponseEntity<>(response, HttpStatus.CREATED);
        } catch (Exception e) {
            log.error("Error creating company context", e);
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    
    /**
     * Get a company context by ID.
     * 
     * @param id the company context ID
     * @return a response entity with the company context
     */
    @GetMapping("/{id}")
    public ResponseEntity<CompanyContextResponse> getCompanyContextById(@PathVariable String id) {
        log.info("Getting company context by ID: {}", id);
        
        Optional<CompanyContext> companyContextOpt = companyContextService.getCompanyContextById(id);
        
        if (companyContextOpt.isEmpty()) {
            log.warn("Company context not found for ID: {}", id);
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
        
        CompanyContextResponse response = CompanyContextResponse.from(companyContextOpt.get());
        return new ResponseEntity<>(response, HttpStatus.OK);
    }
    
    /**
     * Get all company contexts for a user.
     * 
     * @param username the username
     * @return a response entity with the company contexts
     */
    @GetMapping("/user/{username}")
    public ResponseEntity<List<CompanyContextResponse>> getCompanyContextsByUsername(@PathVariable String username) {
        log.info("Getting company contexts for user: {}", username);
        
        Optional<UserSession> userSessionOpt = userSessionService.getSessionByUsername(username);
        
        if (userSessionOpt.isEmpty()) {
            log.warn("User session not found for username: {}", username);
            return new ResponseEntity<>(HttpStatus.UNAUTHORIZED);
        }
        
        UserSession userSession = userSessionOpt.get();
        
        if (!userSession.isValid()) {
            log.warn("User session is invalid for username: {}", username);
            return new ResponseEntity<>(HttpStatus.UNAUTHORIZED);
        }
        
        List<CompanyContext> companyContexts = companyContextService.getCompanyContextsByUsername(username);
        List<CompanyContextResponse> response = companyContexts.stream()
                .map(CompanyContextResponse::from)
                .collect(Collectors.toList());
        
        return new ResponseEntity<>(response, HttpStatus.OK);
    }
}
