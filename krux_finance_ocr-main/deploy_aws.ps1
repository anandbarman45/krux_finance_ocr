# AWS ECR Deployment Script for KruxOCR

param(
    [string]$AwsRegion = "ap-south-1",
    [string]$EcrRepoName = "krux-ocr"
)

# 1. Check for Docker
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not in PATH."
    exit 1
}

# 2. Get AWS Account ID
Write-Host "🔍 Getting AWS Account ID..." -ForegroundColor Cyan
try {
    $AccountId = aws sts get-caller-identity --query Account --output text
    if (-not $AccountId) { throw "Could not get Account ID" }
    Write-Host "✅ AWS Account ID: $AccountId" -ForegroundColor Green
}
catch {
    Write-Error "Failed to get AWS Account ID. Please ensure 'aws configure' is run."
    exit 1
}

$EcrUri = "$AccountId.dkr.ecr.$AwsRegion.amazonaws.com"
$FullImageName = "$EcrUri/$EcrRepoName`:latest"

# 3. Login to ECR
Write-Host "🔑 Logging in to ECR..." -ForegroundColor Cyan
aws ecr get-login-password --region $AwsRegion | docker login --username AWS --password-stdin $EcrUri
if ($LASTEXITCODE -ne 0) { exit 1 }

# 4. Create Repo if not exists (Optional)
Write-Host "Checking if repo exists..." -ForegroundColor Cyan
aws ecr describe-repositories --repository-names $EcrRepoName --region $AwsRegion > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Repo '$EcrRepoName' does not exist. Creating..." -ForegroundColor Yellow
    aws ecr create-repository --repository-name $EcrRepoName --region $AwsRegion
}

# 5. Build Docker Image
Write-Host "🐳 Building Docker Image..." -ForegroundColor Cyan
docker build -t $EcrRepoName .
docker tag "$EcrRepoName`:latest" $FullImageName

# 6. Push to ECR
Write-Host "🚀 Pushing to ECR ($FullImageName)..." -ForegroundColor Cyan
docker push $FullImageName

Write-Host "✅ Deployment to ECR Complete!" -ForegroundColor Green
Write-Host "You can now use this URI in ECS/App Runner: $FullImageName" -ForegroundColor White
