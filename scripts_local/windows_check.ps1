<#
Pre-flight check for running the v2 evaluation set locally with Ollama on Windows.

ASCII-only on purpose: Windows PowerShell 5.1 reads a .ps1 as ANSI unless the file
has a BOM, so a UTF-8 file without BOM would garble any non-ASCII text in it.

Usage (from the repo root):
    powershell -ExecutionPolicy Bypass -File scripts_local\windows_check.ps1
    powershell -ExecutionPolicy Bypass -File scripts_local\windows_check.ps1 -Model qwen2.5:14b-instruct-q4_k_m

Exit code 0 = ready to run, 1 = at least one blocking problem.
#>
param(
    [string]$Model  = "qwen2.5:14b-instruct-q4_k_m",
    [string]$Python = ""
)

$ErrorActionPreference = "Continue"
$env:PYTHONUTF8 = "1"   # keep Python's stdout UTF-8 so Chinese logs do not crash

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$script:blocking = 0
$script:warnings = 0

function Report {
    param([string]$Name, [bool]$Ok, [string]$Detail, [switch]$WarnOnly)
    if ($Ok) {
        Write-Host ("  [ OK ] {0,-16} {1}" -f $Name, $Detail) -ForegroundColor Green
    } elseif ($WarnOnly) {
        Write-Host ("  [WARN] {0,-16} {1}" -f $Name, $Detail) -ForegroundColor Yellow
        $script:warnings++
    } else {
        Write-Host ("  [FAIL] {0,-16} {1}" -f $Name, $Detail) -ForegroundColor Red
        $script:blocking++
    }
}

Write-Host ""
Write-Host "=== Moling v2 eval - Windows pre-flight ===" -ForegroundColor Cyan
Write-Host "repo: $Root"
Write-Host ""

# ---------------------------------------------------------------- hardware
Write-Host "[1/6] Hardware" -ForegroundColor Cyan
try {
    $os  = Get-CimInstance Win32_OperatingSystem
    $cs  = Get-CimInstance Win32_ComputerSystem
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
    Write-Host ("  {0} (build {1})" -f $os.Caption, $os.BuildNumber)
    Write-Host ("  CPU  : {0} / {1} cores / {2} threads" -f $cpu.Name.Trim(), $cpu.NumberOfCores, $cpu.NumberOfLogicalProcessors)
    Write-Host ("  RAM  : {0:N1} GB" -f ($cs.TotalPhysicalMemory / 1GB))
    Report "OS" ($os.ProductType -eq 1 -or $os.ProductType -eq 3) "Windows detected"
} catch {
    Report "OS" $false "WMI query failed: $_"
}

$smi = $null
$smiCmd = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($smiCmd) {
    $smi = $smiCmd.Source
} elseif (Test-Path "C:\Windows\System32\nvidia-smi.exe") {
    $smi = "C:\Windows\System32\nvidia-smi.exe"
} elseif (Test-Path "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe") {
    $smi = "C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe"
}

if ($smi) {
    $gpuLine = (& $smi --query-gpu=name,memory.total,driver_version --format=csv,noheader) -join "; "
    Write-Host "  GPU  : $gpuLine"
    $vram = (& $smi --query-gpu=memory.total --format=csv,noheader,nounits | Select-Object -First 1)
    $vram = [int]($vram -replace "[^0-9]", "")
    Report "GPU" ($vram -gt 0) ("{0} MiB VRAM" -f $vram)
} else {
    Report "GPU" $false "nvidia-smi not found - Ollama would fall back to CPU and 98 samples would take hours"
}

# ---------------------------------------------------------------- python
Write-Host ""
Write-Host "[2/6] Python" -ForegroundColor Cyan
$pyExe = $null
if ($Python) {
    if (Test-Path $Python) { $pyExe = (Resolve-Path $Python).Path }
    else {
        $c = Get-Command $Python -ErrorAction SilentlyContinue
        if ($c) { $pyExe = $c.Source }
    }
    if (-not $pyExe) { Report "python" $false "-Python '$Python' not found" }
} else {
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pyCmd) { $pyCmd = Get-Command py -ErrorAction SilentlyContinue }
    if ($pyCmd) { $pyExe = $pyCmd.Source }
    if (-not $pyCmd) {
        Report "python" $false "not on PATH - install Python 3.11+ and tick 'Add python.exe to PATH'"
    }
}

if ($pyExe) {
    $pyVer = (& $pyExe -c "import sys;print('%d.%d.%d'%sys.version_info[:3])" 2>$null)
    Report "python" ($pyVer -and ([version]$pyVer -ge [version]"3.10")) ("$pyVer at $pyExe")

    # only pydantic is required to run the eval; fastapi/uvicorn are for the API server
    $depOut = (& $pyExe -c "import pydantic;print(pydantic.VERSION)" 2>&1)
    if ($LASTEXITCODE -eq 0) {
        Report "deps" $true "pydantic $depOut"
    } else {
        $firstLine = @($depOut)[0]
        Report "deps" $false ("pydantic missing for THIS interpreter - run: `"$pyExe`" -m pip install pydantic  [{0}]" -f $firstLine)
    }
    $apiOut = (& $pyExe -c "import fastapi" 2>&1)
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [WARN] fastapi        not installed - only needed for the API server, not for the eval batch" -ForegroundColor Yellow
        $script:warnings++
    }
}

# ---------------------------------------------------------------- ollama
Write-Host ""
Write-Host "[3/6] Ollama install" -ForegroundColor Cyan
$olCmd = Get-Command ollama -ErrorAction SilentlyContinue
if ($olCmd) {
    $olExe = $olCmd.Source
} else {
    $guess = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
    if (Test-Path $guess) { $olExe = $guess } else { $olExe = $null }
}
if ($olExe) {
    $olVer = (& $olExe --version 2>&1) -join " "
    Report "ollama" $true "$olVer ($olExe)"
    if (-not $olCmd) {
        Write-Host "         note: not on PATH; the tray app works but open a NEW terminal after install" -ForegroundColor DarkGray
    }
} else {
    Report "ollama" $false "not installed - get OllamaSetup.exe from https://ollama.com/download/windows"
}

# ---------------------------------------------------------------- service
Write-Host ""
Write-Host "[4/6] Ollama service (127.0.0.1:11434)" -ForegroundColor Cyan
$portOpen = $false
try {
    $client = New-Object System.Net.Sockets.TcpClient
    $portOpen = $client.ConnectAsync("127.0.0.1", 11434).Wait(3000)
    $client.Close()
} catch {
    $portOpen = $false
}

if ($portOpen) {
    # bypass any system proxy: a local proxy in the registry can swallow 127.0.0.1
    $tags = $null
    try {
        $tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 10 -UseBasicParsing `
                    -Proxy $null -ErrorAction Stop
    } catch {
        try {
            $tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 10 -UseBasicParsing
        } catch {
            $tags = $null
        }
    }
    if ($tags) {
        Report "service" $true ("reachable, {0} model(s) installed" -f $tags.models.Count)
    } else {
        Report "service" $false "port open but /api/tags failed (proxy or firewall?)"
    }
} else {
    Report "service" $false "not listening - start the Ollama tray app, or run: ollama serve"
    $tags = $null
}

# ---------------------------------------------------------------- model
Write-Host ""
Write-Host "[5/6] Target model" -ForegroundColor Cyan
if ($tags) {
    $names = @($tags.models | ForEach-Object { $_.name })
    $hit = $names | Where-Object { $_ -eq $Model -or $_ -eq "$Model`:latest" -or $_ -like "$Model*" }
    if ($hit) {
        $info = $tags.models | Where-Object { $_.name -eq $hit } | Select-Object -First 1
        Report "model" $true ("{0}  ({1:N1} GB on disk)" -f $hit, ($info.size / 1GB))
    } else {
        Report "model" $false ("{0} not pulled - run: ollama pull {0}" -f $Model)
        if ($names.Count -gt 0) { Write-Host ("         installed: {0}" -f ($names -join ", ")) -ForegroundColor DarkGray }
    }
} else {
    Report "model" $false "cannot list models while the service is down" -WarnOnly
}

# ---------------------------------------------------------------- repo
Write-Host ""
Write-Host "[6/6] Evaluation assets" -ForegroundColor Cyan
$samples = "v2_eval\samples_v2.jsonl"
$prompt  = "parsing\prompt_v2.md"
$runner  = "scripts_local\run_local_ollama.py"

if (Test-Path $samples) {
    $lines = (Get-Content $samples | Measure-Object -Line).Lines
    $dev = (Select-String -Path $samples -Pattern '"split":\s*"dev"' -AllMatches).Count
    $val = (Select-String -Path $samples -Pattern '"split":\s*"val"' -AllMatches).Count
    Report "samples" ($dev -gt 0 -and $val -gt 0) ("$lines lines (dev $dev / val $val) - expect dev 63 / val 35")
} else {
    Report "samples" $false "$samples missing - wrong directory or wrong branch"
}
Report "prompt" (Test-Path $prompt) $(if (Test-Path $prompt) { "parsing\prompt_v2.md" } else { "missing" })
Report "runner" (Test-Path $runner) $(if (Test-Path $runner) { "scripts_local\run_local_ollama.py" } else { "missing - copy scripts_local from the dev machine" })

# ---------------------------------------------------------------- verdict
Write-Host ""
Write-Host "=== verdict ===" -ForegroundColor Cyan
if ($script:blocking -eq 0) {
    Write-Host "READY. Run the batch with this one line (single line, copy as-is):" -ForegroundColor Green
    Write-Host ""
    $exeLabel = if ($pyExe) { "`"$pyExe`"" } else { "python" }
    Write-Host ("{0} scripts_local\run_local_ollama.py --model {1} --protocol v2 --samples v2_eval\samples_v2.jsonl --splits dev,val --out v2_eval\baseline\local_qwen25_14b_runs.jsonl --report v2_eval\baseline\local_qwen25_14b_report.md --tag local-qwen25-14b" -f $exeLabel, $Model)
    Write-Host ""
    exit 0
} else {
    Write-Host ("NOT READY: {0} blocking problem(s), {1} warning(s) above." -f $script:blocking, $script:warnings) -ForegroundColor Red
    exit 1
}
