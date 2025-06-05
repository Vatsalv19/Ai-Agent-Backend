from pydantic import BaseModel
from typing import List
from fastapi import FastAPI, HTTPException
from ai_agent import get_response_from_ai_agent

class RequestState(BaseModel):
    model_name: str
    model_provider: str
    system_prompt: str
    messages: List[str]
    allow_search: bool

# Fixed the typo in model name
ALLOWED_MODEL_NAMES = ["llama3-70b-8192", "gpt-4o-mini"]
ALLOWED_PROVIDERS = ["groq", "openai"]

app = FastAPI(title="LangGraph AI Agent")

@app.post("/chat")
def chat_endpoint(request: RequestState):
    """
    API endpoint to interact with the Chatbot using LangGraph and search tools.
    It dynamically selects the model specified in the request and processes the messages.
    """
    try:
        # Validate model name
        if request.model_name not in ALLOWED_MODEL_NAMES:
            raise HTTPException(
                status_code=400, 
                detail=f"Model '{request.model_name}' not allowed. Allowed models: {ALLOWED_MODEL_NAMES}"
            )
        
        # Validate provider
        if request.model_provider not in ALLOWED_PROVIDERS:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{request.model_provider}' not allowed. Allowed providers: {ALLOWED_PROVIDERS}"
            )
        
        # Validate messages
        if not request.messages:
            raise HTTPException(status_code=400, detail="Messages cannot be empty")
        
        llm_id = request.model_name
        # Handle multiple messages - join them or take the last one
        query = " ".join(request.messages) if len(request.messages) > 1 else request.messages[0]
        allow_search = request.allow_search
        system_prompt = request.system_prompt  # Fixed: was request.prompt
        provider = request.model_provider

        response = get_response_from_ai_agent(
            llm_id=llm_id, 
            query=query, 
            allow_search=allow_search, 
            provider=provider, 
            system_prompt=system_prompt
        )

        return {"response": response, "status": "success"}
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
def root():
    """Health check endpoint"""
    return {"message": "LangGraph AI Agent API is running"}

@app.get("/models")
def get_allowed_models():
    """Get list of allowed models and providers"""
    return {
        "allowed_models": ALLOWED_MODEL_NAMES,
        "allowed_providers": ALLOWED_PROVIDERS
    }
from mangum import Mangum

handler = Mangum(app)  # Add this at the bottom


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)