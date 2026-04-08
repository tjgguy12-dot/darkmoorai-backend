# DarkmoorAI RAG Test Script
Write-Host "🧠 Testing DarkmoorAI RAG System" -ForegroundColor Cyan

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
    Write-Host "⚠️ User may already exist" -ForegroundColor Yellow
}

# Login
Write-Host "`n2. Logging in..." -ForegroundColor Yellow
$loginBody = "username=ragtest@darkmoor.ai&password=test123"
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -ContentType "application/x-www-form-urlencoded" -Body $loginBody
$token = $loginResponse.access_token
Write-Host "✅ Logged in, token: $($token.Substring(0,20))..." -ForegroundColor Green

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
    Write-Host "Answer: $($response.answer.Substring(0, [Math]::Min(300, $response.answer.Length)))..." -ForegroundColor White
    Write-Host "Sources: $($response.sources.Count)" -ForegroundColor Yellow
    Write-Host "Cost: `$$($response.cost)" -ForegroundColor Yellow
    Write-Host "Tokens: $($response.tokens_used)" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Write-Host "`n✅ Test complete!" -ForegroundColor Green