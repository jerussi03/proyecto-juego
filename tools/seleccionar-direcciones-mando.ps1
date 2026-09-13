param(
    [ValidateSet('analogico', 'cruceta')]
    [string]$Modo = 'analogico',
    [ValidateRange(0, 4)]
    [int]$Jugador = 0
)

# Jugador 0 applies to all four controller slots. Keyboard/buttons are preserved.
$gameRoot = Split-Path -Parent $PSScriptRoot
$configPath = Join-Path $gameRoot 'save/config.ini'
$configText = [IO.File]::ReadAllText($configPath)
$backupFolder = Join-Path $gameRoot 'backups/mandos-analogicos'
[IO.Directory]::CreateDirectory($backupFolder) | Out-Null
$backupFile = Join-Path $backupFolder ('config-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '.ini')
[IO.File]::Copy($configPath, $backupFile, $false)

$directions = if ($Modo -eq 'analogico') {
    @{ up = 'LS_Y-'; down = 'LS_Y+'; left = 'LS_X-'; right = 'LS_X+' }
} else {
    @{ up = 'DP_U'; down = 'DP_D'; left = 'DP_L'; right = 'DP_R' }
}

$configText = [regex]::Replace($configText, '(?ms)^\[Joystick_P([1-4])\][^\[]*', {
    param($section)
    if ($Jugador -ne 0 -and [int]$section.Groups[1].Value -ne $Jugador) {
        return $section.Value
    }
    $result = $section.Value
    foreach ($direction in @('up', 'down', 'left', 'right')) {
        $result = [regex]::Replace($result, '(?m)^(' + $direction + '\s*=\s*)[^\r\n]*', '${1}' + $directions[$direction])
    }
    return $result
})
if ($Modo -eq 'analogico') {
    $configText = [regex]::Replace($configText, '(?m)^(ControllerStickSensitivity\s*=\s*)[^\r\n]*', '${1}0.35')
}
[IO.File]::WriteAllText($configPath, $configText, (New-Object Text.UTF8Encoding($false)))
Write-Output "Direcciones: $Modo. Jugador: $Jugador (0 = todos). Reinicia Ikemen para aplicar."
