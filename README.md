# BrandHero AI

A project by Adam M., Oskar, and Daria, Adam D, Mateusz

## Requirements

- Node.js 20 or newer
- Docker and Docker Compose (for containerized setup)

## Running Locally

### Frontend

To run the frontend locally:

1. Navigate to the frontend directory:
   ```
   cd frontend/brand-hero
   ```

2. Install dependencies:
   ```
   npm i --legacy-peer-deps
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. Access the application at:
   - http://localhost:3000/pages (if login doesn't work)

### Backend (Agents Handler)

To run the backend locally, refer to the instructions in the `agents-handler` directory.

## Running with Docker

To run the entire application using Docker:

1. Build and start all services:
   ```
   docker-compose up -d
   ```

2. Access the application:
   - Frontend: http://localhost:3000
   - Agents Handler API: http://localhost:8070
   - Qdrant Dashboard: http://localhost:6334

3. To stop all services:
   ```
   docker-compose down
   ```

## Project Structure

- `frontend/brand-hero`: Next.js frontend application
- `agents-handler`: Python backend for AI agents
- `orchestrator`: Java backend for orchestration

## Notes

- The frontend requires Node.js 20 or newer
- When running locally, the frontend proxies API requests to http://localhost:8070
- In the Docker setup, services communicate over the `agents-network`
