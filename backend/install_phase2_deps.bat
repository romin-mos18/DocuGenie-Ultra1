@echo off
echo Installing Phase 2 Dependencies for Enhanced Document Processing...
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Installing enhanced document processing libraries...
pip install PyMuPDF==1.23.8
pip install python-docx==1.1.0
pip install pandas==2.1.4
pip install openpyxl==3.1.2
pip install Pillow==10.2.0
pip install pytesseract==0.3.10
echo.
echo Installing updated requirements...
pip install -r requirements.txt
echo.
echo Phase 2 dependencies installation completed!
echo.
echo Testing enhanced imports...
python -c "import fitz; print('✅ PyMuPDF available')"
python -c "from docx import Document; print('✅ python-docx available')"
python -c "import pandas; print('✅ pandas available')"
python -c "from PIL import Image; print('✅ Pillow available')"
echo.
echo Press any key to exit...
pause > nul
