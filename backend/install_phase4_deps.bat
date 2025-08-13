@echo off
echo Installing Phase 4 Dependencies for Advanced Features...
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Installing real-time notifications and WebSocket libraries...
pip install websockets==12.0
pip install redis==5.0.1
echo.
echo Installing background tasks and message queuing...
pip install celery==5.3.4
echo.
echo Installing machine learning and analytics libraries...
pip install scikit-learn==1.3.2
pip install plotly==5.17.0
pip install dash==2.14.2
pip install pandas-profiling==3.6.6
echo.
echo Installing performance and monitoring libraries...
pip install prometheus-client==0.19.0
echo.
echo Installing updated requirements...
pip install -r requirements.txt
echo.
echo Phase 4 dependencies installation completed!
echo.
echo Testing enhanced imports...
python -c "import websockets; print('✅ WebSockets available')"
python -c "import redis; print('✅ Redis available')"
python -c "import celery; print('✅ Celery available')"
python -c "import sklearn; print('✅ Scikit-learn available')"
python -c "import plotly; print('✅ Plotly available')"
python -c "import dash; print('✅ Dash available')"
echo.
echo Press any key to exit...
pause > nul
