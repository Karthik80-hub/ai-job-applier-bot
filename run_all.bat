@echo off
cd /d %~dp0

echo Activating environment (if needed)...
REM Uncomment below if using conda or venv
REM call conda activate your_env_name
REM call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt || (
    pip install streamlit streamlit-autorefresh python-dotenv matplotlib psycopg2-binary openai schedule playwright
    playwright install
)

echo Starting AI Job Applier Bot...
start /min cmd /k "python main.py --interval 60"

echo Launching Streamlit Dashboard...
start streamlit run dashboard.py

echo All systems started successfully.
pause
