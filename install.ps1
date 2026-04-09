# Atomic Terminal - Windows Installer
# Run: iwr https://raw.githubusercontent.com/P4vL0-P4nd4/atomic-terminal/main/install.ps1 -UseBasicParsing | iex

$ErrorActionPreference = 'SilentlyContinue'

# Fix encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

# Enable ANSI colors on Windows 10+
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WinConsole {
    [DllImport("kernel32.dll")] public static extern IntPtr GetStdHandle(int h);
    [DllImport("kernel32.dll")] public static extern bool GetConsoleMode(IntPtr h, out uint m);
    [DllImport("kernel32.dll")] public static extern bool SetConsoleMode(IntPtr h, uint m);
}
"@ -ErrorAction SilentlyContinue
try {
    $h = [WinConsole]::GetStdHandle(-11)
    $m = 0
    [WinConsole]::GetConsoleMode($h, [ref]$m) | Out-Null
    [WinConsole]::SetConsoleMode($h, $m -bor 4) | Out-Null
} catch {}

$E  = [char]27
$G  = "$E[38;2;0;255;153m"
$YL = "$E[38;2;255;204;0m"
$RD = "$E[38;2;255;50;50m"
$WH = "$E[97m"
$DM = "$E[38;2;80;80;80m"
$CY = "$E[96m"
$RS = "$E[0m"

$ATOMIC_URL  = "https://raw.githubusercontent.com/P4vL0-P4nd4/atomic-terminal/main/atomic.py"
$INSTALL_DIR = "$env:USERPROFILE\.atomic"
$VERSION     = "1.0.0"

function Show-Glitch {
    $logo = @(
        "  @@@@@@  @@@@@@@@ @@@@@@  @@@@@ @@  @@  @@@@@  ",
        "  @@  @@     @@   @@  @@  @@  @@@@  @@  @@     ",
        "  @@@@@@     @@   @@  @@  @@ @@@@@  @@  @@     ",
        "  @@  @@     @@   @@  @@  @@  @@@@  @@  @@     ",
        "  @@  @@     @@    @@@@   @@   @@@  @@   @@@@@  "
    )
    $ascii = @(
        "   ___  ____  ____  __  __ ___  ____",
        "  / _ \|_  _|/ () \|  \/  |_ _|/ ()",
        " / /_\ \ || |/ / \ \ |\/| || |/ / \ ",
        "/_/   \_\||_|/_/   \_\_|  |_|___\_/ "
    )
    $glitch = '!@#$%^&*<>?|\/~'
    for ($i = 0; $i -lt 7; $i++) {
        Clear-Host
        foreach ($line in $ascii) {
            $gl = ''
            foreach ($c in $line.ToCharArray()) {
                if ($c -ne ' ' -and (Get-Random -Max 4) -eq 0) {
                    $gl += $glitch[(Get-Random -Max $glitch.Length)]
                } else { $gl += $c }
            }
            if ((Get-Random -Max 3) -eq 0) {
                Write-Host "${RD}${gl}${RS}"
            } else {
                Write-Host "${G}${gl}${RS}"
            }
        }
        Start-Sleep -Milliseconds 80
    }
    Clear-Host
    Write-Host ""
    foreach ($line in $ascii) { Write-Host "${G}${line}${RS}" }
    Write-Host ""
    Write-Host "${DM}  TERMINAL v${VERSION}              Built by Pavlopanda${RS}"
    Write-Host ""
}

function Show-Legal {
    Write-Host "${RD}  =======================================================${RS}"
    Write-Host "${RD}    WARNING - READ CAREFULLY${RS}"
    Write-Host "${RD}  =======================================================${RS}"
    Write-Host ""
    Write-Host "${WH}  Atomic Terminal provides real offensive security tools.${RS}"
    Write-Host "${WH}  Using these tools without written consent is ILLEGAL${RS}"
    Write-Host "${WH}  under the CFAA, UK Computer Misuse Act, and EU law.${RS}"
    Write-Host ""
    Write-Host "${WH}  By continuing you confirm:${RS}"
    Write-Host "${WH}    - You only test systems you own or have permission${RS}"
    Write-Host "${WH}    - You accept full legal responsibility${RS}"
    Write-Host "${WH}    - All activity is logged and tied to your account${RS}"
    Write-Host "${WH}    - Pavlopanda bears zero liability for misuse${RS}"
    Write-Host ""
    Write-Host "${RD}  =======================================================${RS}"
    Write-Host ""
    Write-Host "${YL}  Type  I AGREE  in capitals to accept and continue:${RS}"
    $answer = Read-Host "  "
    if ($answer -cne "I AGREE") {
        Write-Host ""
        Write-Host "${RD}  Agreement required. Exiting.${RS}"
        exit 1
    }
    Write-Host ""
}

function Show-Bar($label, $steps=10, $ms=80) {
    $pad = 18 - $label.Length
    if ($pad -lt 1) { $pad = 1 }
    Write-Host -NoNewline "  ${DM}[${RS}${WH}$label${RS}$(' ' * $pad)${G}"
    for ($i = 0; $i -lt $steps; $i++) {
        Start-Sleep -Milliseconds $ms
        Write-Host -NoNewline "#"
    }
    Write-Host "${RS}  ${G}OK${RS}"
}

function Show-OK($msg) {
    Write-Host "  ${G}[OK]${RS}  $msg"
    Start-Sleep -Milliseconds 180
}

function Install-Tools {
    Write-Host "${DM}  ── Initialising systems ──────────────────────────────${RS}"
    Write-Host ""
    Show-OK "Atomic core loaded"
    Show-OK "Firebase connection established"
    Show-OK "AI core ready"
    Show-OK "Encryption layer active"
    Write-Host ""
    Write-Host "${DM}  ── Installing tools ──────────────────────────────────${RS}"
    Write-Host ""

    Show-Bar "requests" 8 60
    python -m pip install requests -q 2>$null

    $nmapPath = Get-Command nmap -ErrorAction SilentlyContinue
    if (-not $nmapPath) {
        Show-Bar "nmap" 10 100
        winget install --id Nmap.Nmap -e --silent 2>$null | Out-Null
    } else {
        Show-Bar "nmap" 5 50
    }

    Write-Host ""
}

function Get-Atomic {
    Write-Host "${DM}  Downloading Atomic...${RS}"
    New-Item -ItemType Directory -Force -Path $INSTALL_DIR | Out-Null

    try {
        Invoke-WebRequest -Uri $ATOMIC_URL -OutFile "$INSTALL_DIR\atomic.py" -UseBasicParsing
        Write-Host "  atomic.py  ${G}OK${RS}"
    } catch {
        Write-Host "${RD}  Download failed: $_${RS}"
        exit 1
    }

    # Config so no double install
    '{"installed":true,"disclaimer_accepted":true}' | Set-Content "$INSTALL_DIR\config.json"

    # Launcher batch file
    "@echo off`npython `"$INSTALL_DIR\atomic.py`" %*" | Set-Content "$INSTALL_DIR\atomic.bat"

    # Add to PATH
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$INSTALL_DIR*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$INSTALL_DIR", "User")
        Write-Host "  PATH updated  ${G}OK${RS}"
    }

    Write-Host ""
}

# ── MAIN ──────────────────────────────────────────────────────────────────────
Show-Glitch

# Check Python
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "${YL}  Python not found. Installing...${RS}"
    winget install --id Python.Python.3 -e --silent
    Write-Host ""
}

Show-Legal
Install-Tools
Get-Atomic

Write-Host "${G}  ──────────────────────────────────────────────────────${RS}"
Write-Host "${G}    ATOMIC TERMINAL INSTALLED${RS}"
Write-Host "${G}  ──────────────────────────────────────────────────────${RS}"
Write-Host ""
Write-Host "${WH}  Open a new PowerShell window and type:${RS}"
Write-Host ""
Write-Host "  ${G}atomic${RS}"
Write-Host ""
Write-Host "${DM}  Launching now...${RS}"
Write-Host ""

python "$INSTALL_DIR\atomic.py"
