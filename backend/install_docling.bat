@echo off
echo Installing Docling and updating dependencies...
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Removing old OCR dependencies...
pip uninstall paddlepaddle paddleocr opencv-python -y

echo.
echo Installing Docling and LangChain...
pip install docling langchain langchain-community

echo.
echo Installing updated requirements...
pip install -r requirements.txt

echo.
echo Docling installation completed!
echo.
echo Testing Docling import...
python -c "from docling import Docling; print('Docling import successful!')"

echo.
echo Press any key to exit...
pause > nul
