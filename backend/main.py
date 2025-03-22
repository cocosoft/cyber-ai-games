import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse

# Load environment variables from .env file
load_dotenv()

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from backend.app_config import create_app
from backend.routes import router
from backend.middleware import middleware

app = create_app()

# 挂载路由
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080, help='Port to run the server on')
    args = parser.parse_args()
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)
