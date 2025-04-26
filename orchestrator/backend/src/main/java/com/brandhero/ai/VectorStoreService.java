package com.brandhero.ai;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.ai.document.Document;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.embedding.EmbeddingOptions;
import org.springframework.ai.embedding.EmbeddingRequest;
import org.springframework.ai.embedding.EmbeddingResponse;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class VectorStoreService {

    private final VectorStore vectorStore;


    public VectorStoreService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;

    }

    public void save(JsonNode jsonNode) {
        String content = jsonNode.toString();

        // Optional metadata extraction
        Map<String, Object> metadata = new HashMap<>();
        if (jsonNode.has("type")) {
            metadata.put("type", jsonNode.get("type").asText());
        }
        if (jsonNode.has("page_id")) {
            metadata.put("company_id", jsonNode.get("page_id").asText());
        }
        // Create document
        Document document = new Document(content, metadata);

        // Save to vector store
        vectorStore.add(List.of(document));
    }
}
