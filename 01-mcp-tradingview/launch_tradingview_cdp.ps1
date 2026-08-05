# Lanza TradingView Desktop (instalado por MSIX) con depuracion remota CDP en :9222,
# que es lo que necesita el MCP de TradingView para conectarse.
# tv_launch del MCP no lo encuentra porque el .exe vive en C:\Program Files\WindowsApps (oculto);
# aqui resolvemos la ruta real con Get-AppxPackage.
$ErrorActionPreference = 'SilentlyContinue'

function Test-Cdp {
    try { return (Invoke-WebRequest "http://127.0.0.1:9222/json/version" -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200 }
    catch { return $false }
}

if (Test-Cdp) { Write-Host "CDP ya activo en :9222. Listo para usar el MCP de TradingView."; exit 0 }

$pkg = Get-AppxPackage *TradingView*
if (-not $pkg) { Write-Host "TradingView Desktop no esta instalado (MSIX no encontrado)."; exit 1 }

$exe = Join-Path $pkg.InstallLocation 'TradingView.exe'
Write-Host "Lanzando $($pkg.Name) $($pkg.Version) con CDP..."
Start-Process -FilePath $exe -ArgumentList "--remote-debugging-port=9222"

for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    if (Test-Cdp) { Write-Host "CDP ACTIVO en :9222 (tras $($i+1)s). Ya puedes usar el MCP de TradingView."; exit 0 }
}
Write-Host "TradingView lanzado, pero CDP no respondio en 30s. Reintenta o revisa que la app abrio."
exit 2
