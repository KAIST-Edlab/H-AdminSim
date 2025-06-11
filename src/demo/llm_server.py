import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(__file__))), 'src'))
import argparse
from sconf import Config
from pydantic import BaseModel

import uvicorn
from fastapi import FastAPI, HTTPException

from registry import PromptRequest
from tools import GeminiClient, GPTClient


app = FastAPI()


# argparse
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', type=str, required=True)
parser.add_argument('--is_develop', action='store_true', required=False)
args = parser.parse_args()


# Initialize clients and configs
config = Config(args.config)
client = GeminiClient(config.model) if 'gemini' in config.model.lower() else GPTClient(config.model)


@app.post("/llm_response")
async def generate_response(request: PromptRequest):
    user_prompt = request.user_prompt.strip()
    system_prompt = request.system_prompt.strip() if request.system_prompt else None
    response = client(
        user_prompt=user_prompt,
        system_prompt=system_prompt
    )
        
    if not user_prompt:
        raise HTTPException(status_code=400, detail="Prompt is empty")
    
    return {"response": response}



if __name__ == "__main__":
    uvicorn.run('llm_server:app', host=config.host, port=config.port, reload=args.is_develop)