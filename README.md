
To start this DLMS backend:

install uv if you have not installed it yet:`pip install uv`
please male sure you are usin `requires-python = ">=3.12"` I am using 3.12
This cmnd loads all the packages which are required :`uv sync`
Please make sure you will use this cmnd to avoid modele_not_found errors: `source .venv/bin/activate`
This cmnd works by starting a server  `uvicorn server:app --reload 2>&1 | tee "logs/$(date +%Y-%m-%d_%H-%M-%S).log"`


