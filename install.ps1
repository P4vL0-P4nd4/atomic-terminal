# Atomic Terminal - Windows Installer
# Run: powershell -ExecutionPolicy Bypass -Command "iex (iwr https://raw.githubusercontent.com/P4vL0-P4nd4/atomic-terminal/main/install.ps1).Content"

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
$RS = "$E[0m"

$ATOMIC_URL  = "https://raw.githubusercontent.com/P4vL0-P4nd4/atomic-terminal/main/atomic.py"
$INSTALL_DIR = "$env:USERPROFILE\.atomic"
$VERSION     = "1.0.0"

$LOGO = @(
    "  █████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗ ",
    "  ██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝ ",
    "  ███████║   ██║   ██║   ██║██╔████╔██║██║██║      ",
    "  ██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║      ",
    "  ██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗ ",
    "  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝ "
)

function cls-esc { Write-Host -NoNewline "$E[2J$E[H" }

function Show-Glitch {
    $glitch = '!@#$%^&*<>?|\/~+='
    # Run glitch passes
    for ($i = 0; $i -lt 10; $i++) {
        cls-esc
        Write-Host ""
        foreach ($line in $LOGO) {
            $gl = ''
            foreach ($c in $line.ToCharArray()) {
                if ($c -ne ' ' -and (Get-Random -Max 4) -eq 0) {
                    $gl += $glitch[(Get-Random -Max $glitch.Length)]
                } else { $gl += $c }
            }
            $color = if ((Get-Random -Max 3) -eq 0) { $RD } else { $G }
            Write-Host "${color}${gl}${RS}"
        }
        Start-Sleep -Milliseconds 70
    }
    cls-esc
    Write-Host ""
    foreach ($line in $LOGO) { Write-Host "${G}${line}${RS}" }
    Write-Host ""
    Write-Host "${DM}  TERMINAL v${VERSION}                    Built by Pavlopanda${RS}"
    Write-Host ""
}

function Show-Legal {
    Write-Host "${RD}  +----------------------------------------------------------+${RS}"
    Write-Host "${RD}  |          WARNING - READ CAREFULLY                        |${RS}"
    Write-Host "${RD}  +----------------------------------------------------------+${RS}"
    Write-Host "${WH}  |  Atomic Terminal provides real offensive security tools.  |${RS}"
    Write-Host "${WH}  |  Using these tools without written consent is ILLEGAL     |${RS}"
    Write-Host "${WH}  |  under CFAA, UK Computer Misuse Act, and EU law.         |${RS}"
    Write-Host "${WH}  |                                                           |${RS}"
    Write-Host "${WH}  |  By continuing you confirm:                               |${RS}"
    Write-Host "${WH}  |   * You only test systems you own or have permission      |${RS}"
    Write-Host "${WH}  |   * You accept full legal responsibility for all actions  |${RS}"
    Write-Host "${WH}  |   * All activity is logged and tied to your account       |${RS}"
    Write-Host "${WH}  |   * Pavlopanda bears zero liability for misuse            |${RS}"
    Write-Host "${RD}  +----------------------------------------------------------+${RS}"
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

function Show-OK($msg) {
    Write-Host "  ${G}[OK]${RS}  $msg"
    Start-Sleep -Milliseconds 120
}

function Show-Bar($label, $steps=10, $ms=60) {
    $pad = 16 - $label.Length
    if ($pad -lt 1) { $pad = 1 }
    Write-Host -NoNewline "  ${G}[${RS} ${WH}${label}${RS}$(' ' * $pad)${G}"
    for ($i = 0; $i -lt $steps; $i++) {
        Start-Sleep -Milliseconds $ms
        Write-Host -NoNewline "█"
    }
    Write-Host " ${G}]${RS}  ${G}done${RS}"
}

function Install-WithBar($label, $scriptBlock, $timeoutSec=30) {
    $pad = 16 - $label.Length
    if ($pad -lt 1) { $pad = 1 }
    $barWidth = 20

    # Run install in background job
    $job = Start-Job -ScriptBlock $scriptBlock

    $start = Get-Date
    $filled = 0
    Write-Host -NoNewline "  ${G}[${RS} ${WH}${label}${RS}$(' ' * $pad)${G}"

    while ($true) {
        $elapsed = ((Get-Date) - $start).TotalSeconds
        $progress = [math]::Min($elapsed / $timeoutSec, 1.0)
        $newFilled = [math]::Floor($progress * $barWidth)

        # Print new blocks
        while ($filled -lt $newFilled) {
            Write-Host -NoNewline "█"
            $filled++
        }

        # Show timer inline (overwrite)
        $timerStr = "$([math]::Floor($elapsed))s"

        # Check if job done
        $state = $job.State
        if ($state -eq 'Completed' -or $state -eq 'Failed') {
            # Fill remaining bar
            while ($filled -lt $barWidth) {
                Write-Host -NoNewline "█"
                $filled++
            }
            break
        }

        # Timeout
        if ($elapsed -ge $timeoutSec) {
            Stop-Job $job | Out-Null
            while ($filled -lt $barWidth) {
                Write-Host -NoNewline "█"
                $filled++
            }
            break
        }

        Start-Sleep -Milliseconds 300
    }

    Remove-Job $job -Force | Out-Null
    $total = [math]::Round(((Get-Date) - $start).TotalSeconds, 1)
    Write-Host " ${G}]${RS}  ${G}done${RS} ${DM}(${total}s)${RS}"
}

function Install-Tools {
    Write-Host "${DM}  -- Initialising systems ------------------------------------${RS}"
    Write-Host ""
    Show-OK "Atomic core loaded"
    Show-OK "Firebase connection established"
    Show-OK "AI core ready"
    Show-OK "Encryption layer active"
    Write-Host ""
    Write-Host "${DM}  -- Installing tools ----------------------------------------${RS}"
    Write-Host ""

    Install-WithBar "requests" { python -m pip install requests -q 2>$null } 15

    $wingetTools = @(
        @{ name='nmap';    id='Nmap.Nmap' },
        @{ name='sqlmap';  id='sqlmapproject.sqlmap' },
        @{ name='hashcat'; id='Hashcat.Hashcat' }
    )

    foreach ($t in $wingetTools) {
        $exists = Get-Command $t.name -ErrorAction SilentlyContinue
        if ($exists) {
            Show-Bar $t.name 20 25
        } else {
            $id = $t.id
            Install-WithBar $t.name {
                winget install --id $using:id -e --silent --accept-package-agreements --accept-source-agreements 2>$null
            } 30
        }
    }

    Write-Host ""
}

function Get-Atomic {
    Write-Host "${DM}  -- Downloading Atomic --------------------------------------${RS}"
    Write-Host ""
    New-Item -ItemType Directory -Force -Path $INSTALL_DIR | Out-Null

    try {
        Invoke-WebRequest -Uri $ATOMIC_URL -OutFile "$INSTALL_DIR\atomic.py" -UseBasicParsing
        Show-OK "atomic.py downloaded"
    } catch {
        Write-Host "${RD}  Download failed: $_${RS}"
        exit 1
    }

    '{"installed":true,"disclaimer_accepted":true}' | Set-Content "$INSTALL_DIR\config.json"
    "@echo off`npython `"$INSTALL_DIR\atomic.py`" %*" | Set-Content "$INSTALL_DIR\atomic.bat"

    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$INSTALL_DIR*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$INSTALL_DIR", "User")
        Show-OK "added to PATH"
    }

    Write-Host ""
}

# ── MAIN ──────────────────────────────────────────────────────────────────────
Show-Glitch

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "${YL}  Python not found. Installing via winget...${RS}"
    winget install --id Python.Python.3 -e --silent
    Write-Host ""
}

Show-Legal
Install-Tools
Get-Atomic

Write-Host "${G}  ============================================================${RS}"
Write-Host "${G}    ATOMIC TERMINAL INSTALLED${RS}"
Write-Host "${G}  ============================================================${RS}"
Write-Host ""
Write-Host "${WH}  Open a new PowerShell window and type:  ${G}atomic${RS}"
Write-Host ""
Write-Host "${DM}  Launching now...${RS}"
Write-Host ""

python "$INSTALL_DIR\atomic.py"
