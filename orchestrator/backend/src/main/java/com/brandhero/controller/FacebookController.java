package com.brandhero.controller;

import java.util.List;
import java.util.Optional;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.brandhero.dto.PageResponse;
import com.brandhero.model.FacebookPage;
import com.brandhero.model.UserSession;
import com.brandhero.service.FacebookService;
import com.brandhero.service.UserSessionService;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Controller for Facebook-related endpoints.
 */
@RestController
@RequestMapping("/api/facebook")
@RequiredArgsConstructor
@Slf4j
public class FacebookController {
    
    private final FacebookService facebookService;
    private final UserSessionService userSessionService;
    
    /**
     * Get Facebook pages for a user.
     * 
     * @param username the username
     * @return a response entity with the Facebook pages
     */
    @GetMapping("/pages/{username}")
    public ResponseEntity<PageResponse> getUserPages(@PathVariable String username) {
        log.info("Getting Facebook pages for user: {}", username);
        
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
        
        List<FacebookPage> pages = facebookService.getUserPages(userSession.getAccessToken());
        PageResponse response = PageResponse.from(username, pages);
        
        return new ResponseEntity<>(response, HttpStatus.OK);
    }
}
