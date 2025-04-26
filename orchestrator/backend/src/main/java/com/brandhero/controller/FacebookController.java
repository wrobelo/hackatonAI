package com.brandhero.controller;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.brandhero.dto.PageResponse;
import com.brandhero.dto.PostRequest;
import com.brandhero.model.FacebookPage;
import com.brandhero.model.FacebookPost;
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
        
        // Store page IDs and access tokens in the user session
        for (FacebookPage page : pages) {
            userSession.getPageAccessTokens().put(page.getId(), page.getAccessToken());
        }
        userSessionService.updateSession(userSession);
        
        PageResponse response = PageResponse.from(username, pages);
        
        return new ResponseEntity<>(response, HttpStatus.OK);
    }
    
    /**
     * Create a text-only post on a Facebook page.
     * 
     * @param username the username
     * @param request the post request containing pageId and message
     * @return a response entity with the created post
     */
    @PostMapping("/post/{username}")
    public ResponseEntity<FacebookPost> createPost(
            @PathVariable String username,
            @RequestBody PostRequest request) {
        
        log.info("Creating text post for user: {} on page: {}", username, request.getPageId());
        
        Optional<UserSession> userSessionOpt = userSessionService.getSessionByUsername(username);
        
        if (userSessionOpt.isEmpty() || !userSessionOpt.get().isValid()) {
            log.warn("User session not found or invalid for username: {}", username);
            return new ResponseEntity<>(HttpStatus.UNAUTHORIZED);
        }
        
        UserSession userSession = userSessionOpt.get();
        String pageId = request.getPageId();
        
        // Get the page access token from the user session
        String pageAccessToken = userSession.getPageAccessTokens().get(pageId);
        
        // If page access token is not found, return an error
        if (pageAccessToken == null) {
            log.error("Page access token not found for page ID: {}. User needs to fetch pages first.", pageId);
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
        
        // If linkUrl is provided, create a post with link
        if (request.getLinkUrl() != null && !request.getLinkUrl().isEmpty()) {
            FacebookPost post = facebookService.createPostWithLink(
                    pageId,
                    pageAccessToken,
                    request.getMessage(),
                    request.getLinkUrl()
            );
            return new ResponseEntity<>(post, HttpStatus.CREATED);
        }
        
        // Otherwise create a text-only post
        FacebookPost post = facebookService.createPost(
                pageId,
                pageAccessToken,
                request.getMessage()
        );
        
        return new ResponseEntity<>(post, HttpStatus.CREATED);
    }
    
    /**
     * Create a post with an image on a Facebook page.
     * 
     * @param username the username
     * @param pageId the Facebook page ID
     * @param message the message content of the post
     * @param image the image file to upload
     * @return a response entity with the created post
     */
    @PostMapping(value = "/post/{username}/image", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<FacebookPost> createPostWithImage(
            @PathVariable String username,
            @RequestParam String pageId,
            @RequestParam String message,
            @RequestPart MultipartFile image) {
        
        log.info("Creating image post for user: {} on page: {}", username, pageId);
        
        Optional<UserSession> userSessionOpt = userSessionService.getSessionByUsername(username);
        
        if (userSessionOpt.isEmpty() || !userSessionOpt.get().isValid()) {
            log.warn("User session not found or invalid for username: {}", username);
            return new ResponseEntity<>(HttpStatus.UNAUTHORIZED);
        }
        
        if (image.isEmpty()) {
            log.warn("No image provided for image post");
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
        
        UserSession userSession = userSessionOpt.get();
        
        // Get the page access token from the user session
        String pageAccessToken = userSession.getPageAccessTokens().get(pageId);
        
        // If page access token is not found, return an error
        if (pageAccessToken == null) {
            log.error("Page access token not found for page ID: {}. User needs to fetch pages first.", pageId);
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
        
        try {
            FacebookPost post = facebookService.createPostWithImage(
                    pageId,
                    pageAccessToken,
                    message,
                    image.getBytes(),
                    image.getOriginalFilename()
            );
            
            return new ResponseEntity<>(post, HttpStatus.CREATED);
        } catch (Exception e) {
            log.error("Error creating post with image", e);
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    
    /**
     * Create a post with an image from a URL on a Facebook page.
     * 
     * @param username the username
     * @param pageId the Facebook page ID
     * @param message the message content of the post
     * @param imageUrl the URL of the image to download and upload
     * @return a response entity with the created post
     */
    @PostMapping("/post/{username}/image-url")
    public ResponseEntity<FacebookPost> createPostWithImageURL(
            @PathVariable String username,
            @RequestParam String pageId,
            @RequestParam String message,
            @RequestParam String imageUrl) {
        
        log.info("Creating image post from URL for user: {} on page: {}", username, pageId);
        
        Optional<UserSession> userSessionOpt = userSessionService.getSessionByUsername(username);
        
        if (userSessionOpt.isEmpty() || !userSessionOpt.get().isValid()) {
            log.warn("User session not found or invalid for username: {}", username);
            return new ResponseEntity<>(HttpStatus.UNAUTHORIZED);
        }
        
        if (imageUrl == null || imageUrl.isEmpty()) {
            log.warn("No image URL provided for image post");
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
        
        UserSession userSession = userSessionOpt.get();
        
        // Get the page access token from the user session
        String pageAccessToken = userSession.getPageAccessTokens().get(pageId);
        
        // If page access token is not found, return an error
        if (pageAccessToken == null) {
            log.error("Page access token not found for page ID: {}. User needs to fetch pages first.", pageId);
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
        
        try {
            // Create a temporary file to store the downloaded image
            String originalFilename = getFilenameFromUrl(imageUrl);
            Path tempFile = Files.createTempFile("fb-image-", originalFilename);
            
            // Download the image from the URL
            try (InputStream in = new URL(imageUrl).openStream()) {
                Files.copy(in, tempFile, StandardCopyOption.REPLACE_EXISTING);
            }
            
            // Read the image bytes
            byte[] imageBytes = Files.readAllBytes(tempFile);
            
            // Delete the temporary file
            Files.delete(tempFile);
            
            // Create the post with the image
            FacebookPost post = facebookService.createPostWithImage(
                    pageId,
                    pageAccessToken,
                    message,
                    imageBytes,
                    originalFilename
            );
            
            return new ResponseEntity<>(post, HttpStatus.CREATED);
        } catch (IOException e) {
            log.error("Error downloading or processing image from URL: {}", imageUrl, e);
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        } catch (Exception e) {
            log.error("Error creating post with image from URL", e);
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    
    /**
     * Extract a filename from a URL.
     * 
     * @param url the URL
     * @return the filename
     */
    private String getFilenameFromUrl(String url) {
        String filename = url.substring(url.lastIndexOf('/') + 1);
        
        // If there's no extension, add .jpg as default
        if (!filename.contains(".")) {
            filename = filename + ".jpg";
        }
        
        // If filename is empty or just contains parameters, generate a random name
        if (filename.isEmpty() || filename.startsWith("?")) {
            filename = UUID.randomUUID().toString() + ".jpg";
        }
        
        return filename;
    }
}
