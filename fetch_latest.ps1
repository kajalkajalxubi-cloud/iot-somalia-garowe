try {
    $res = Invoke-RestMethod -Uri 'http://localhost:8000/api/latest' -UseBasicParsing -ErrorAction Stop
    $json = $res | ConvertTo-Json -Depth 6
    Write-Output $json
} catch {
    Write-Output "Error: $_"
}
