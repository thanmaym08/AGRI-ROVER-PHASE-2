$paths = @(
    [Environment]::GetFolderPath('Desktop'),
    "$env:USERPROFILE\Desktop",
    "$env:USERPROFILE\OneDrive\Desktop"
)

$targetDesktop = $null
foreach ($p in $paths) {
    if (![string]::IsNullOrEmpty($p) -and (Test-Path $p)) {
        $targetDesktop = $p
        break
    }
}

if ($targetDesktop) {
    Copy-Item "F:\agrirover phase 2\Agri Rover Live Cockpit.url" "$targetDesktop\Agri Rover Live Cockpit.url" -Force
    Copy-Item "F:\agrirover phase 2\Agri Rover 3D Simulator.url" "$targetDesktop\Agri Rover 3D Simulator.url" -Force
    Copy-Item "F:\agrirover phase 2\Launch Agri Rover.bat" "$targetDesktop\Launch Agri Rover.bat" -Force
    Write-Output "SUCCESS: Placed shortcuts on Desktop at: $targetDesktop"
} else {
    Write-Output "ERROR: Could not locate Desktop folder."
}
