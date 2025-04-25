package com.brandhero.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.brandhero.dto.LoginRequest;
import com.brandhero.model.UserSession;
import com.brandhero.service.UserSessionService;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Controller for authentication endpoints.
 */
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Slf4j
public class AuthController {
    
    private final UserSessionService userSessionService;
    
    /**
     * Login endpoint.
     * 
     * @param loginRequest the login request
     * @return a response entity with the user session
     */
    @PostMapping("/login")
    public ResponseEntity<UserSession> login(@Valid @RequestBody LoginRequest loginRequest) {
        log.info("Login request for user: {}", loginRequest.getUsername());
        
        UserSession session = userSessionService.createOrUpdateSession(
                loginRequest.getUsername(), 
                loginRequest.getAccessToken()
        );
        
        return new ResponseEntity<>(session, HttpStatus.OK);
    }
}
