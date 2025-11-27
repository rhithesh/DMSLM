
To start this DLMS backend:
This cmnd loads all the packages which are required :uv sync
uvicorn server:app --reload 2>&1 | tee "logs/$(date +%Y-%m-%d_%H-%M-%S).log"