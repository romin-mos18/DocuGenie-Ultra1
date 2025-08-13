Write-Host "Installing Docling and updating dependencies..." -ForegroundColor Green
Write-Host ""

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Removing old OCR dependencies..." -ForegroundColor Yellow
pip uninstall paddlepaddle paddleocr opencv-python -y

Write-Host ""
Write-Host "Installing Docling and LangChain..." -ForegroundColor Yellow
pip install docling langchain langchain-community

Write-Host ""
Write-Host "Installing updated requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Docling installation completed!" -ForegroundColor Green
Write-Host ""

Write-Host "Testing Docling import..." -ForegroundColor Yellow
python -c "from docling import Docling; print('Docling import successful!')"

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
