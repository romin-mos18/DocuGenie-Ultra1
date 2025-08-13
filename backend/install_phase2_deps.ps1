Write-Host "Installing Phase 2 Dependencies for Enhanced Document Processing..." -ForegroundColor Green
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Installing enhanced document processing libraries..." -ForegroundColor Yellow
pip install PyMuPDF==1.23.8
pip install python-docx==1.1.0
pip install pandas==2.1.4
pip install openpyxl==3.1.2
pip install Pillow==10.2.0
pip install pytesseract==0.3.10
Write-Host ""
Write-Host "Installing updated requirements..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host ""
Write-Host "Phase 2 dependencies installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Testing enhanced imports..." -ForegroundColor Yellow
python -c "import fitz; print('✅ PyMuPDF available')"
python -c "from docx import Document; print('✅ python-docx available')"
python -c "import pandas; print('✅ pandas available')"
python -c "from PIL import Image; print('✅ Pillow available')"
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
