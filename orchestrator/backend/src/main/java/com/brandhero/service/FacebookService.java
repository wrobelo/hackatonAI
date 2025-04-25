package com.brandhero.service;

import java.util.ArrayList;
import java.util.List;

import com.restfb.types.StoryAttachment;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.brandhero.model.FacebookPage;
import com.brandhero.model.FacebookPost;
import com.restfb.Connection;
import com.restfb.DefaultFacebookClient;
import com.restfb.FacebookClient;
import com.restfb.Parameter;
import com.restfb.Version;
import com.restfb.types.Page;
import com.restfb.types.Post;
import com.restfb.types.User;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Service for interacting with the Facebook Graph API.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class FacebookService {
    
    @Value("${facebook.api.version}")
    private String facebookApiVersion;
    
    @Value("${agent.post.limit:10}")
    private int defaultPostLimit;
    
    /**
     * Get the Facebook pages for a user.
     * 
     * @param accessToken the Facebook access token
     * @return a list of Facebook pages
     */
    public List<FacebookPage> getUserPages(String accessToken) {
        log.info("Getting user pages from Facebook");
        
        FacebookClient facebookClient = createFacebookClient(accessToken);
        User user = facebookClient.fetchObject("me", User.class);
        
        Connection<Page> pagesConnection = facebookClient.fetchConnection(
                "me/accounts", 
                Page.class, 
                Parameter.with("fields", "id,name,category,access_token,picture,fan_count,about,description,website")
        );
        
        List<FacebookPage> pages = new ArrayList<>();
        
        for (List<Page> pageList : pagesConnection) {
            for (Page page : pageList) {
                FacebookPage facebookPage = FacebookPage.builder()
                        .id(page.getId())
                        .name(page.getName())
                        .category(page.getCategory())
                        .accessToken(page.getAccessToken())
                        .pictureUrl(page.getPicture() != null ? page.getPicture().getUrl() : null)
                        .fanCount(page.getFanCount())
                        .about(page.getAbout())
                        .description(page.getDescription())
                        .website(page.getWebsite())
                        .build();
                
                pages.add(facebookPage);
            }
        }
        
        log.info("Found {} pages for user {}", pages.size(), user.getName());
        return pages;
    }
    
    /**
     * Get the posts for a Facebook page.
     * 
     * @param pageId the Facebook page ID
     * @param accessToken the Facebook access token
     * @param limit the maximum number of posts to fetch
     * @return a list of Facebook posts
     */
    public List<FacebookPost> getPagePosts(String pageId, String accessToken, Integer limit) {
        log.info("Getting posts for page {}", pageId);
        
        int postLimit = limit != null ? limit : defaultPostLimit;
        FacebookClient facebookClient = createFacebookClient(accessToken);
        
        Connection<Post> postsConnection = facebookClient.fetchConnection(
                pageId + "/posts", 
                Post.class, 
                Parameter.with("fields", "id,message,created_time,type,permalink_url,likes.summary(true),comments.summary(true),shares,attachments"),
                Parameter.with("limit", postLimit)
        );
        
        List<FacebookPost> posts = new ArrayList<>();
        
        for (List<Post> postList : postsConnection) {
            for (Post post : postList) {
                if (posts.size() >= postLimit) {
                    break;
                }
                
                FacebookPost facebookPost = convertToFacebookPost(post);
                posts.add(facebookPost);
            }
            
            if (posts.size() >= postLimit) {
                break;
            }
        }
        
        log.info("Found {} posts for page {}", posts.size(), pageId);
        return posts;
    }
    
    /**
     * Get information about a Facebook page.
     * 
     * @param pageId the Facebook page ID
     * @param accessToken the Facebook access token
     * @return the Facebook page
     */
    public FacebookPage getPageInfo(String pageId, String accessToken) {
        log.info("Getting info for page {}", pageId);
        
        FacebookClient facebookClient = createFacebookClient(accessToken);
        Page page = facebookClient.fetchObject(
                pageId, 
                Page.class, 
                Parameter.with("fields", "id,name,category,access_token,picture,fan_count,about,description,website")
        );
        
        return FacebookPage.builder()
                .id(page.getId())
                .name(page.getName())
                .category(page.getCategory())
                .accessToken(page.getAccessToken())
                .pictureUrl(page.getPicture() != null ? page.getPicture().getUrl() : null)
                .fanCount(page.getFanCount())
                .about(page.getAbout())
                .description(page.getDescription())
                .website(page.getWebsite())
                .build();
    }
    
    /**
     * Create a FacebookClient with the given access token.
     * 
     * @param accessToken the Facebook access token
     * @return a FacebookClient
     */
    private FacebookClient createFacebookClient(String accessToken) {
        return new DefaultFacebookClient(accessToken, Version.VERSION_22_0);
    }
    
    /**
     * Convert a RestFB Post to our FacebookPost model.
     * 
     * @param post the RestFB Post
     * @return a FacebookPost
     */
    private FacebookPost convertToFacebookPost(Post post) {
        List<String> imageUrls = new ArrayList<>();
        String videoUrl = null;
        String linkUrl = null;
        String linkTitle = null;
        String linkDescription = null;
        
        if (post.getAttachments() != null && !post.getAttachments().getData().isEmpty()) {
            StoryAttachment attachment = post.getAttachments().getData().get(0);
            
            if (attachment.getMedia() != null && attachment.getMedia().getImage() != null) {
                imageUrls.add(attachment.getMedia().getImage().getSrc());
            }
            
            if (attachment.getType() != null && attachment.getType().equals("video_inline")) {
                videoUrl = attachment.getUrl();
            }
            
            if (attachment.getUrl() != null) {
                linkUrl = attachment.getUrl();
            }
            
            linkTitle = attachment.getTitle();
            linkDescription = attachment.getDescription();
        }
        
        return FacebookPost.builder()
                .id(post.getId())
                .message(post.getMessage())
                .createdTime(post.getCreatedTime().toInstant().atZone(java.time.ZoneId.systemDefault()).toLocalDateTime())
                .type(post.getType())
                .permalink(post.getPermalinkUrl())
                .likesCount(post.getLikes() != null ? post.getLikes().getTotalCount() : 0)
                .commentsCount(post.getComments() != null ? post.getComments().getTotalCount() : 0)
                .sharesCount(post.getShares() != null ? post.getShares().getCount() : 0)
                .imageUrls(imageUrls)
                .videoUrl(videoUrl)
                .linkUrl(linkUrl)
                .linkTitle(linkTitle)
                .linkDescription(linkDescription)
                .build();
    }
}
