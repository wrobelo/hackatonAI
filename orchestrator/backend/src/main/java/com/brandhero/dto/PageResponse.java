package com.brandhero.dto;

import java.util.List;

import com.brandhero.model.FacebookPage;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for returning a list of Facebook pages.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PageResponse {
    
    private String username;
    private List<FacebookPage> pages;
    private int count;
    
    /**
     * Static factory method to create a PageResponse from a list of FacebookPage objects.
     * 
     * @param username the username
     * @param pages the list of Facebook pages
     * @return a new PageResponse
     */
    public static PageResponse from(String username, List<FacebookPage> pages) {
        return PageResponse.builder()
                .username(username)
                .pages(pages)
                .count(pages.size())
                .build();
    }
}
