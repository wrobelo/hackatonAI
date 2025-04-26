# BrandHero Backend

This is the backend for the BrandHero application, which provides APIs for authenticating with Facebook, retrieving Facebook pages, and generating company contexts based on Facebook page data.

## Technologies Used

- Java 21
- Spring Boot 3.2.4
- MongoDB
- RestFB (Facebook Graph API client)
- Lombok
- Maven

## Prerequisites

- Java 21 or higher
- Maven
- MongoDB

## Getting Started

1. Clone the repository
2. Navigate to the `orchestrator/backend` directory
3. Configure MongoDB connection in `src/main/resources/application.properties`
4. Build the project: `mvn clean install`
5. Run the application: `mvn spring-boot:run`

The application will start on port 8080 by default.

## API Endpoints

### Authentication

- **POST /api/auth/login**: Authenticate a user with Facebook access token
  - Request body: `{ "username": "string", "accessToken": "string" }`
  - Response: User session object

### Facebook Pages

- **GET /api/facebook/pages/{username}**: Get Facebook pages for a user
  - Path parameter: `username` - The username of the authenticated user
  - Response: List of Facebook pages

### Company Context

- **POST /api/context/{username}**: Create a company context for a Facebook page
  - Path parameter: `username` - The username of the authenticated user
  - Request body: `{ "pageId": "string", "pageName": "string", "postLimit": number }`
  - Response: Company context object

- **GET /api/context/{id}**: Get a company context by ID
  - Path parameter: `id` - The ID of the company context
  - Response: Company context object

- **GET /api/context/user/{username}**: Get all company contexts for a user
  - Path parameter: `username` - The username of the authenticated user
  - Response: List of company contexts

## Configuration

The application can be configured through the `application.properties` file:

```properties
# Server configuration
server.port=8080

# MongoDB configuration
spring.data.mongodb.host=localhost
spring.data.mongodb.port=27017
spring.data.mongodb.database=brandhero

# Facebook Graph API configuration
facebook.api.version=v18.0
facebook.api.base-url=https://graph.facebook.com/

# Agent configuration
agent.endpoint.url=http://localhost:5000/api/agent
agent.post.limit=10
```

## Project Structure

- `com.brandhero.model`: Entity classes
- `com.brandhero.dto`: Data Transfer Objects
- `com.brandhero.repository`: MongoDB repositories
- `com.brandhero.service`: Service classes
- `com.brandhero.controller`: REST controllers
- `com.brandhero.config`: Configuration classes
- `com.brandhero.exception`: Exception handling

## Authentication Flow

1. The frontend authenticates the user with Facebook and obtains an access token
2. The frontend sends the access token and username to the backend
3. The backend stores the access token and username in MongoDB
4. The backend uses the access token to make requests to the Facebook Graph API

## Company Context Generation

1. The frontend requests a company context for a Facebook page
2. The backend fetches the page information and posts from Facebook
3. The backend sends the page information and posts to the agent
4. The agent generates a company context based on the page information and posts
5. The backend stores the company context in MongoDB
6. The backend returns the company context to the frontend
