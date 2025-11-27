# Run the entire stack
up:
    docker-compose up --build

# Stop the stack
down:
    docker-compose down

# View logs
logs:
    docker-compose logs -f

# Run API only
api:
    uvicorn api:app --reload

# Run UI only
ui:
    streamlit run ui.py
