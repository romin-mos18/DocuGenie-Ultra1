# PowerShell script to start Docker Desktop and services

Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow

# Try to start Docker Desktop
$dockerPath = "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe"
if (Test-Path $dockerPath) {
    Start-Process $dockerPath
    Write-Host "Docker Desktop starting. Please wait..." -ForegroundColor Yellow
    
    # Wait for Docker to be ready
    $maxAttempts = 30
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 2
        docker info > $null 2>&1
        if ($?) {
            Write-Host "`n✓ Docker is ready!" -ForegroundColor Green
            break
        }
        $attempt++
        Write-Host "." -NoNewline
    }
    
    if ($attempt -eq $maxAttempts) {
        Write-Host "`n✗ Docker failed to start. Please start it manually." -ForegroundColor Red
        exit 1
    }
    
    # Start services
    Write-Host "`nStarting DocuGenie services..." -ForegroundColor Yellow
    docker-compose up -d
    
    Write-Host "`n✓ All services started!" -ForegroundColor Green
    docker-compose ps
} else {
    Write-Host "Docker Desktop not found. Please install Docker Desktop from:" -ForegroundColor Red
    Write-Host "https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
}
