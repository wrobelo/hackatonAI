package com.brandhero.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Represents a Facebook page belonging to a user.
 * This is a DTO class used for transferring Facebook page data.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FacebookPage {
    
    private String id;
    private String name;
    private String category;
    private String accessToken;
    private String pictureUrl;
    
    // Additional fields that might be useful
    private Long fanCount;
    private String about;
    private String description;
    private String website;
}
