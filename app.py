import os
import sys
import uvicorn

if __name__ == "__main__":
    print("===================================================================")
    print("AI Logistics Optimizer -- Enterprise Full-Screen HTML Suite")
    print("Launching dedicated web server (only your custom pages, nothing else)...")
    print("===================================================================")
    uvicorn.run("server:app", host="0.0.0.0", port=8501, reload=False)
