package com.brandhero.dto;

import java.time.LocalDateTime;

import com.brandhero.model.CompanyContext;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for returning a company context.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CompanyContextResponse {
    
    private String id;
    private String pageId;
    private String pageName;
    private String username;
    private String contextContent;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private int postsCount;
    
    /**
     * Static factory method to create a CompanyContextResponse from a CompanyContext entity.
     * 
     * @param context the CompanyContext entity
     * @return a new CompanyContextResponse
     */
    public static CompanyContextResponse from(CompanyContext context) {
        return CompanyContextResponse.builder()
                .id(context.getId())
                .pageId(context.getPageId())
                .pageName(context.getPageName())
                .username(context.getUsername())
                .contextContent(context.getContextContent())
                .createdAt(context.getCreatedAt())
                .updatedAt(context.getUpdatedAt())
                .postsCount(context.getPostsCount() != null ? context.getPostsCount() : 0)
                .build();
    }
}
