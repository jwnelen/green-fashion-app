start_streamlit:
	uv run -- streamlit run streamlit_app/wardrobe_manager.py

start_streamlit_matcher:
	uv run -- streamlit run streamlit_app/matcher.py

create_kernel:
	uv run -- python -m ipykernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=green-fashion
# 	uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=project
