# Bovara Agent

Backend service for livestock management with an integrated AI assistant using Google Gemini.

## Requirements

- Docker and Docker Compose
- Python 3.11+ (if running locally without Docker)
- Google Gemini API Key

## Quick Start (Docker)

The easiest way to run the project is using Docker. This will automatically set up the PostgreSQL database, initialize the schema, seed sample data, and start the API.

1. Create a `.env` file in the root directory based on `.env.example`.
2. Run the following command in your terminal:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:3001`.

## Manual Installation

If you prefer to run the application locally without Docker:

1. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure you have a PostgreSQL database running and configure the `.env` file.

4. Initialize the database tables:
```bash
python -m src.init_db
```

5. Populate the database with sample data:
```bash
python -m src.seed_db
```

6. Start the server:
```bash
uvicorn src.main:app --reload
```

## Configuration

Create a `.env` file in the root directory with the following variables:

```properties
PROJECT_NAME=Bovara Agent
DATABASE_URL=postgresql://postgres:ganaderia_pass@localhost:5432/ganaderia_db
GOOGLE_API_KEY=your_api_key_here
```

**Note:** When running with Docker, the application automatically connects to the database container, so you do not need to change the `DATABASE_URL` for Docker execution.

## API Usage

### Documentation

Interactive API documentation (Swagger UI) is available at:
`http://localhost:3001/docs`

### Main Endpoints

#### Chat with Agent

Allows natural language queries about the livestock data.

- **URL**: `/chat`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body**:
```json
{
  "message": "When is the next vaccine for cow 504?"
}
```

- **Response Example**:
```json
{
  "response": "The next vaccine for LOTE-504 is scheduled for 2024-12-20.",
  "tool_used": "get_last_vaccine",
  "tool_result": "{...}",
  "tool_params": {
    "lote": "LOTE-504"
  }
}
```

### Example Queries & Commands

You can interact with the agent using natural language to both query data and perform actions.

#### 🔍 Queries (Consultas)

- **General Info**: "Show me all my cattle" (*Muéstrame todo mi ganado*)
- **Specific Search**: "Find the cow named Margarita" (*Busca la vaca llamada Margarita*)
- **Health**: "When is the next vaccine for cow 504?" (*¿Cuándo le toca vacuna a la vaca 504?*)
- **Reproduction**: "Which cows are pregnant?" (*¿Qué vacas están preñadas?*)
- **Reminders**: "Do I have any overdue reminders?" (*¿Tengo recordatorios vencidos?*)

#### ✍️ Actions (Inserciones)

The agent can also create new records in the database.

- **Register Cattle**:
  > "Register a new cow named Lola with lote LOTE-999 and gender female."
  > (*Registra una nueva vaca llamada Lola con lote LOTE-999 y género female*)

- **Create Reminder**:
  > "Remind me to buy feed on 2024-12-25."
  > (*Recuérdame comprar alimento el 2024-12-25*)

#### Health Check

Verifies that the service is running.

- **URL**: `/chat/health`
- **Method**: `GET`

## Project Structure

- `src/api`: API routes and controllers.
- `src/core`: Configuration and settings.
- `src/infrastructure`: Database connection and session management.
- `src/models`: SQLAlchemy database models.
- `src/repositories`: Data access layer (CRUD operations).
- `src/schemas`: Pydantic data schemas for validation.
- `src/services`: Business logic, including the AI agent and tools.
- `src/init_db.py`: Script to create database tables.
- `src/seed_db.py`: Script to populate the database with initial data.
