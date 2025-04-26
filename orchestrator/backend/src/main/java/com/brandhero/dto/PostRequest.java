package com.brandhero.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request object for creating a Facebook post.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PostRequest {
    
    /**
     * The ID of the Facebook page to post to.
     */
    private String pageId;
    
    /**
     * The message content of the post.
     */
    private String message;
    
    /**
     * Optional URL to include in the post.
     */
    private String linkUrl;
}
