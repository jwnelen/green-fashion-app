start_streamlit:
	uv run -- streamlit run streamlit_app/wardrobe_manager.py

start_streamlit_matcher:
	uv run -- streamlit run streamlit_app/matcher.py

start_classifier:
	uv run uvicorn "classifier_api.main:app" --port "8001" --workers 1

create_kernel:
	uv run -- python -m ipykernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=green-fashion
# 	uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=project

run-api:
	cd services/api && VIRTUAL_ENV="" uv run uvicorn src.main:app --reload

run-classifier:
	cd services/classifier_api && VIRTUAL_ENV="" uv run uvicorn src.main:app --port 8001 --reload
