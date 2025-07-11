start_streamlit:
	uv run -- streamlit run "streamlit-app/app.py"

create_kernel:
	uv run -- python -m ipykernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=green-fashion
# 	uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=project
