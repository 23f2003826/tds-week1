import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the root and subdirectories are in Python's module search path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import the Q6 application (main.py in q6 folder)
from q6.main import app as q6_app

# Main Gateway FastAPI application for all of Week 1
app = FastAPI(
    title="TDS Week 1 Multi-Service Gateway",
    description="Unified API gateway serving all TDS Week 1 assignments under a single free instance."
)

# Enable CORS for all incoming requests (required for course graders)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import FileResponse

# Root status page to verify your service is online
@app.get("/")
def home():
    return {
        "status": "online",
        "service": "TDS Week 1 Service Gateway",
        "endpoints": {
            "q6": "/effective-config",
            "q13": "/submission.tar.gz"
        }
    }

@app.get("/submission.tar.gz")
def get_submission():
    tar_path = ROOT_DIR / "submission.tar.gz"
    return FileResponse(tar_path, media_type="application/gzip", filename="submission.tar.gz")

# ==============================================================================
# Question 6 Routes:
# Mounting Q6 router directly onto root so GET /effective-config is accessible
# at https://<your-app>.onrender.com/effective-config
# ==============================================================================
app.include_router(q6_app.router)

# ==============================================================================
# Future Questions (e.g. Question 7, Question 8):
# When you have a new service, you can simply add:
#   from q7.main import app as q7_app
#   app.include_router(q7_app.router) # or app.mount("/q7", q7_app)
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

