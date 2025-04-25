package com.brandhero.model;

import java.time.LocalDateTime;
import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Represents a Facebook post from a page.
 * This is used when fetching posts for company context generation.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FacebookPost {
    
    private String id;
    private String message;
    private LocalDateTime createdTime;
    private String type; // photo, video, status, link, etc.
    private String permalink;
    
    // Engagement metrics
    private long likesCount;
    private long commentsCount;
    private long sharesCount;
    
    // Media attachments
    private List<String> imageUrls;
    private String videoUrl;
    private String linkUrl;
    private String linkTitle;
    private String linkDescription;
}
