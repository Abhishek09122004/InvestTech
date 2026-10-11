# ==============================================================================
# Azure Resource Deployment Automation Script
# AI-Powered Investor Intelligence Platform
# ==============================================================================

param (
    [string]$ResourceGroupName = "rg-investor-intelligence",
    [string]$Location = "eastus",
    [string]$PostgresAdminUser = "pgadmin",
    [string]$PostgresAdminPassword = "ChangeMe123!Secure",
    [string]$PostgresServerName = "inv-pg-$((Get-Random -Minimum 1000 -Maximum 9999))",
    [string]$SearchServiceName = "inv-search-$((Get-Random -Minimum 1000 -Maximum 9999))",
    [string]$OpenAIServiceName = "inv-openai-$((Get-Random -Minimum 1000 -Maximum 9999))"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Azure Resource Provisioning: Investor Intelligence     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Azure Login
Write-Host "`n[1/5] Checking Azure CLI authentication..." -ForegroundColor Yellow
$account = az account show --output json 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Please login to Azure first by running: az login" -ForegroundColor Red
    exit 1
}
Write-Host "Authenticated as: $($account.user.name) (Subscription: $($account.name))" -ForegroundColor Green

# 2. Create Resource Group
Write-Host "`n[2/5] Creating Resource Group: $ResourceGroupName in $Location..." -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location --output table

# 3. Create Azure Database for PostgreSQL Flexible Server
Write-Host "`n[3/5] Creating Azure PostgreSQL Flexible Server: $PostgresServerName..." -ForegroundColor Yellow
az postgres flexible-server create `
    --resource-group $ResourceGroupName `
    --name $PostgresServerName `
    --location $Location `
    --admin-user $PostgresAdminUser `
    --admin-password $PostgresAdminPassword `
    --sku-name Standard_B1ms `
    --tier Burstable `
    --storage-size 32 `
    --version 16 `
    --database-name investor_intelligence `
    --public-access 0.0.0.0 `
    --yes

# 4. Create Azure AI Search Service
Write-Host "`n[4/5] Creating Azure AI Search Service: $SearchServiceName..." -ForegroundColor Yellow
az search service create `
    --resource-group $ResourceGroupName `
    --name $SearchServiceName `
    --sku basic `
    --location $Location

$searchKey = az search admin-key show `
    --resource-group $ResourceGroupName `
    --service-name $SearchServiceName `
    --query "primaryKey" -o tsv

# 5. Create Azure OpenAI Service
Write-Host "`n[5/5] Creating Azure OpenAI Cognitive Services account: $OpenAIServiceName..." -ForegroundColor Yellow
az cognitiveservices account create `
    --name $OpenAIServiceName `
    --resource-group $ResourceGroupName `
    --location $Location `
    --kind OpenAI `
    --sku s0 `
    --yes

$openaiKey = az cognitiveservices account keys list `
    --name $OpenAIServiceName `
    --resource-group $ResourceGroupName `
    --query "key1" -o tsv

$openaiEndpoint = az cognitiveservices account show `
    --name $OpenAIServiceName `
    --resource-group $ResourceGroupName `
    --query "properties.endpoint" -o tsv

# Deploy models in Azure OpenAI
Write-Host "Deploying GPT-4o model..." -ForegroundColor Yellow
az cognitiveservices account deployment create `
    --name $OpenAIServiceName `
    --resource-group $ResourceGroupName `
    --deployment-name gpt-4o `
    --model-name gpt-4o `
    --model-version "2024-05-13" `
    --model-format OpenAI `
    --sku-capacity 10 `
    --sku-name "Standard"

Write-Host "Deploying text-embedding-ada-002 model..." -ForegroundColor Yellow
az cognitiveservices account deployment create `
    --name $OpenAIServiceName `
    --resource-group $ResourceGroupName `
    --deployment-name text-embedding-ada-002 `
    --model-name text-embedding-ada-002 `
    --model-version "2" `
    --model-format OpenAI `
    --sku-capacity 10 `
    --sku-name "Standard"

# Generate .env file
$envContent = @"
POSTGRES_HOST=$PostgresServerName.postgres.database.azure.com
POSTGRES_PORT=5432
POSTGRES_DATABASE=investor_intelligence
POSTGRES_USER=$PostgresAdminUser
POSTGRES_PASSWORD=$PostgresAdminPassword

AZURE_OPENAI_ENDPOINT=$openaiEndpoint
AZURE_OPENAI_API_KEY=$openaiKey
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

AZURE_SEARCH_ENDPOINT=https://$SearchServiceName.search.windows.net
AZURE_SEARCH_API_KEY=$searchKey
AZURE_SEARCH_INDEX_NAME=investor-intelligence
"@

Set-Content -Path ".env" -Value $envContent
Write-Host "`n>>> All Azure resources created successfully and written to .env! <<<" -ForegroundColor Green
