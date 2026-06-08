$p = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($p) {
    $pid = $p.OwningProcess
    Write-Output "Listener PID: $pid"
    Get-Process -Id $pid -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,StartTime,Path | Format-List
} else {
    Write-Output "No listener found on port 8000."
}

Write-Output "--- Searching for python processes with target scripts ---"
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'iot_system.py|simulate_iot.py' } | Select-Object ProcessId,CommandLine | Format-List
