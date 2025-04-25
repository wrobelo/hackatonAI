package com.brandhero.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for creating a company context request.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreateContextRequest {
    
    @NotBlank(message = "Page ID is required")
    private String pageId;
    
    private String pageName;
    
    /**
     * Number of posts to fetch for context generation.
     * Default value is defined in application.yaml.
     */
    @Min(value = 1, message = "Post limit must be at least 1")
    private Integer postLimit;
}
