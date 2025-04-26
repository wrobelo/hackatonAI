package com.brandhero.service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import com.brandhero.ai.VectorStoreService;
import com.fasterxml.jackson.databind.node.ArrayNode;
import lombok.SneakyThrows;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.brandhero.dto.CreateContextRequest;
import com.brandhero.model.CompanyContext;
import com.brandhero.model.FacebookPage;
import com.brandhero.model.FacebookPost;
import com.brandhero.model.UserSession;
import com.brandhero.repository.CompanyContextRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Service for managing company contexts and interacting with the agent.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class CompanyContextService {
    
    private final CompanyContextRepository companyContextRepository;
    private final FacebookService facebookService;
    private final UserSessionService userSessionService;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private final VectorStoreService vectorStoreService;
    
    @Value("${agent.endpoint.url}")
    private String agentEndpointUrl;
    
    @Value("${agent.post.limit:10}")
    private int defaultPostLimit;
    
    /**
     * Create a company context for a Facebook page.
     * 
     * @param username the username
     * @param request the create context request
     * @return the created company context
     */
    @SneakyThrows
    public CompanyContext createCompanyContextEmbedding(String username, CreateContextRequest request) {
        log.info("Creating company context for page {} and user {}", request.getPageId(), username);

        
        // Get page info
        FacebookPage page = facebookService.getPageInfo(request.getPageId(), request.getPageAccessToken());
        
        // Get page posts
        int postLimit = request.getPostLimit() != null ? request.getPostLimit() : defaultPostLimit;
        List<FacebookPost> posts = facebookService.getPagePosts(request.getPageId(), request.getPageAccessToken(), postLimit);

        //vectorStoreService.save(objectMapper.valueToTree(page));

        // Generate context using agent
        String contextContent = generateContextWithAgent(page, posts);
        vectorStoreService.save(generateContextJsonNode(page, posts));

        // Save context to database
        CompanyContext companyContext = CompanyContext.builder()
                .pageId(page.getId())
                .pageName(page.getName())
                .username(username)
                .contextContent(contextContent)
                .createdAt(LocalDateTime.now())
                .postIds(posts.stream().map(FacebookPost::getId).collect(Collectors.toList()))
                .postsCount(posts.size())
                .build();
        
        return companyContextRepository.save(companyContext);
    }
    
    /**
     * Get a company context by ID.
     * 
     * @param id the company context ID
     * @return an Optional containing the company context if found
     */
    public Optional<CompanyContext> getCompanyContextById(String id) {
        log.debug("Getting company context by ID: {}", id);
        return companyContextRepository.findById(id);
    }
    
    /**
     * Get a company context by page ID.
     * 
     * @param pageId the Facebook page ID
     * @return an Optional containing the company context if found
     */
    public Optional<CompanyContext> getCompanyContextByPageId(String pageId) {
        log.debug("Getting company context by page ID: {}", pageId);
        return companyContextRepository.findByPageId(pageId);
    }
    
    /**
     * Get all company contexts for a user.
     * 
     * @param username the username
     * @return a list of company contexts
     */
    public List<CompanyContext> getCompanyContextsByUsername(String username) {
        log.debug("Getting company contexts for user: {}", username);
        return companyContextRepository.findByUsername(username);
    }
    
    /**
     * Generate a company context using the agent.
     * 
     * @param page the Facebook page
     * @param posts the Facebook posts
     * @return the generated context
     */
    private String generateContextWithAgent(FacebookPage page, List<FacebookPost> posts) {
        log.info("Generating context with agent for page: {}", page.getName());
        
        try {
            // Prepare request to agent
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            ObjectNode requestBody = objectMapper.createObjectNode();
            requestBody.put("page_id", page.getId());
            requestBody.put("page_name", page.getName());
            requestBody.put("page_category", page.getCategory());
            requestBody.put("page_about", page.getAbout());
            requestBody.put("page_description", page.getDescription());
            requestBody.put("page_website", page.getWebsite());
            
            requestBody.putArray("posts")
                    .addAll(posts.stream()
                            .map(this::convertPostToJson)
                            .collect(Collectors.toList()));
            
//            HttpEntity<String> request = new HttpEntity<>(requestBody.toString(), headers);
//
//            // Call agent endpoint
//            String response = restTemplate.postForObject(agentEndpointUrl, request, String.class);
//
//            // Parse response
//            JsonNode responseJson = objectMapper.readTree(response);
//            return responseJson.path("context").asText();

            return requestBody.toString();
            
        } catch (Exception e) {
            log.error("Error generating context with agent", e);
            return "Failed to generate context: " + e.getMessage();
        }
    }
    
    /**
     * Convert a FacebookPost to a JsonNode.
     * 
     * @param post the FacebookPost
     * @return a JsonNode
     */
    private JsonNode convertPostToJson(FacebookPost post) {
        ObjectNode postNode = objectMapper.createObjectNode();
        postNode.put("id", post.getId());
        postNode.put("pageId", post.getPageId());
        postNode.put("message", post.getMessage());
        postNode.put("created_time", post.getCreatedTime().toString());

        if (post.getImageUrls() != null && !post.getImageUrls().isEmpty()) {
            ArrayNode imageUrlsNode = postNode.putArray("image_urls");
            post.getImageUrls().forEach(imageUrlsNode::add);
        }

        
        return postNode;
    }

    private JsonNode generateContextJsonNode(FacebookPage page, List<FacebookPost> posts) {
        log.info("Generating context with agent for page: {}", page.getName());

            // Prepare request to agent
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            ObjectNode requestBody = objectMapper.createObjectNode();
            requestBody.put("page_id", page.getId());
            requestBody.put("page_name", page.getName());
            requestBody.put("page_category", page.getCategory());
            requestBody.put("page_about", page.getAbout());
            requestBody.put("page_description", page.getDescription());
            requestBody.put("page_website", page.getWebsite());

            requestBody.putArray("posts")
                    .addAll(posts.stream()
                            .map(this::convertPostToJson)
                            .collect(Collectors.toList()));

            return requestBody;


    }
}
