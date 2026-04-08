# DarkmoorAI RAG Test Script
Write-Host "🧠 Testing DarkmoorAI RAG System" -ForegroundColor Cyan
Write-Host "="*50

# Register test user
Write-Host "`n1. Registering test user..." -ForegroundColor Yellow
$registerBody = @{
    email = "ragtest@darkmoor.ai"
    username = "ragtest"
    password = "test123"
} | ConvertTo-Json

try {
    $user = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method POST -ContentType "application/json" -Body $registerBody -ErrorAction SilentlyContinue
    Write-Host "✅ User registered: $($user.email)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ User may already exist, trying to login..." -ForegroundColor Yellow
}

# Login
Write-Host "`n2. Logging in..." -ForegroundColor Yellow
$loginBody = "username=ragtest@darkmoor.ai&password=test123"
try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -ContentType "application/x-www-form-urlencoded" -Body $loginBody
    $token = $loginResponse.access_token
    Write-Host "✅ Logged in, token: $($token.Substring(0,20))..." -ForegroundColor Green
} catch {
    Write-Host "❌ Login failed: $_" -ForegroundColor Red
    exit
}

# Test chat with research mode
Write-Host "`n3. Testing chat with research mode..." -ForegroundColor Yellow
$headers = @{Authorization = "Bearer $token"}
$chatBody = @{
    message = "What is biochar and its benefits?"
    use_web_search = $true
    research_mode = $true
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/chat/chat" -Method POST -Headers $headers -ContentType "application/json" -Body $chatBody
    Write-Host "✅ Chat response received!" -ForegroundColor Green
    Write-Host "`nAnswer: $($response.answer)" -ForegroundColor White
    Write-Host "`nSources: $($response.sources.Count)" -ForegroundColor Yellow
    if ($response.sources.Count -gt 0) {
        foreach ($source in $response.sources) {
            Write-Host "  - $($source.type): $($source.title)" -ForegroundColor Cyan
        }
    }
    Write-Host "`nCost: `$$($response.cost)" -ForegroundColor Yellow
    Write-Host "Tokens: $($response.tokens_used)" -ForegroundColor Yellow
    Write-Host "Processing Time: $($response.processing_time) seconds" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "`nCheck backend terminal for details" -ForegroundColor Yellow
}

Write-Host "`n" + "="*50
Write-Host "✅ Test complete!" -ForegroundColor Green