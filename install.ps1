#Requires -Version 5.0
# Atomic Terminal — Windows Installer
# Run as: iwr https://raw.githubusercontent.com/P4vL0-P4nd4/atomic-terminal/main/install.ps1 | iex

$ErrorActionPreference = 'SilentlyContinue'

$G  = "`e[38;2;0;255;153m"
$YL = "`e[38;2;255;204;0m"
$RD = "`e[38;2;255;50;50m"
$WH = "`e[97m"
$DM = "`e[38;2;60;60;60m"
$CY = "`e[96m"
$PK = "`e[95m"
$RS = "`e[0m"

$ATOMIC_URL  = "https://raw.githubusercontent.com/P4vL0-P4nd4/atomic-terminal/main/atomic.py"
$INSTALL_DIR = "$env:USERPROFILE\.atomic"
$VERSION     = "1.0.0"

function Write-Color($msg, $color='') { Write-Host "$color$msg$RS" }

function Show-Glitch {
    $logo = @(
        "  ██████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗ ",
        "  ██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝ ",
        "  ███████║   ██║   ██║   ██║██╔████╔██║██║██║      ",
        "  ██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║      ",
        "  ██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗ ",
        "  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝ "
    )
    $glitch = '!@#$%^&*<>?|\/~`'
    Clear-Host
    for ($pass = 0; $pass -lt 6; $pass++) {
        Clear-Host
        foreach ($line in $logo) {
            if ((Get-Random -Max 3) -eq 0) {
                $gl = ''
                foreach ($c in $line.ToCharArray()) {
                    if ($c -ne ' ' -and (Get-Random -Max 4) -eq 0) {
                        $gl += $glitch[(Get-Random -Max $glitch.Length)]
                    } else { $gl += $c }
                }
                Write-Host "$RD$gl$RS"
            } else {
                Write-Host "$G$line$RS"
            }
        }
        Start-Sleep -Milliseconds 80
    }
    Clear-Host
    foreach ($line in $logo) { Write-Host "$G$line$RS" }
    Write-Host ""
    Write-Color "  TERMINAL v$VERSION              Built by Pavlopanda" $DM
    Write-Host ""
}

function Show-Legal {
    Write-Color "  ┌─────────────────────────────────────────────────────────────┐" $RD
    Write-Color "  │              ⚠  LEGAL WARNING — READ CAREFULLY  ⚠           │" $RD
    Write-Color "  ├─────────────────────────────────────────────────────────────┤" $RD
    Write-Color "  │  Atomic Terminal provides real offensive security tools.     │" $WH
    Write-Color "  │  Using these tools against systems without written consent   │" $WH
    Write-Color "  │  is ILLEGAL under the Computer Fraud and Abuse Act (CFAA),  │" $WH
    Write-Color "  │  the UK Computer Misuse Act, EU Directive 2013/40/EU,       │" $WH
    Write-Color "  │  and equivalent laws in most countries.                     │" $WH
    Write-Color "  │                                                             │" $WH
    Write-Color "  │  By continuing you confirm:                                 │" $WH
    Write-Color "  │   • You will only test systems you own or have permission   │" $WH
    Write-Color "  │   • You accept full legal responsibility for all actions    │" $WH
    Write-Color "  │   • All activity is logged and tied to your account         │" $WH
    Write-Color "  │   • Pavlopanda bears zero liability for misuse              │" $WH
    Write-Color "  └─────────────────────────────────────────────────────────────┘" $RD
    Write-Host ""
    Write-Color "  Type  I AGREE  in capitals to accept and continue:" $YL
    $answer = Read-Host "  "
    if ($answer -cne "I AGREE") {
        Write-Host ""
        Write-Color "  Agreement required. Exiting." $RD
        exit 1
    }
    Write-Host ""
}

function Show-Bar($label, $steps=10, $delay=0.08) {
    $bar = ""
    Write-Host -NoNewline "  $G[$RS  $label"
    for ($i = 0; $i -lt $steps; $i++) {
        Start-Sleep -Milliseconds ($delay * 1000)
        Write-Host -NoNewline "$G.$RS"
    }
    Write-Color "  done $G✓$RS" ""
}

function Install-Tools {
    Write-Color "  Checking tools..." $DM
    Write-Host ""

    # pip packages
    $pips = @('requests')
    foreach ($pkg in $pips) {
        Show-Bar $pkg 8 0.05
        python -m pip install $pkg -q --break-system-packages 2>$null
    }

    # winget tools (best effort)
    $tools = @(
        @{name='nmap';    id='Nmap.Nmap'},
        @{name='python';  id='Python.Python.3'}
    )
    foreach ($t in $tools) {
        $exists = Get-Command $t.name -ErrorAction SilentlyContinue
        if (-not $exists) {
            Show-Bar $t.name 10 0.08
            winget install --id $t.id -e --silent 2>$null | Out-Null
        } else {
            Show-Bar $t.name 5 0.03
        }
    }

    Write-Host ""
}

function Get-Atomic {
    Write-Color "  Downloading Atomic..." $DM
    New-Item -ItemType Directory -Force -Path $INSTALL_DIR | Out-Null
    try {
        Invoke-WebRequest -Uri $ATOMIC_URL -OutFile "$INSTALL_DIR\atomic.py" -UseBasicParsing
        Write-Color "  atomic.py downloaded  $G✓$RS" ""
    } catch {
        Write-Color "  Download failed: $_" $RD
        exit 1
    }

    # Write config so no double install
    @{installed=$true; disclaimer_accepted=$true; version=$VERSION} |
        ConvertTo-Json | Set-Content "$INSTALL_DIR\config.json"

    # Create launcher batch file
    $bat = "@echo off`npython `"$INSTALL_DIR\atomic.py`" %*"
    Set-Content "$INSTALL_DIR\atomic.bat" $bat

    # Add to PATH if not already there
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$INSTALL_DIR*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$INSTALL_DIR", "User")
        Write-Color "  Added to PATH  $G✓$RS" ""
        Write-Color "  $DM(Restart PowerShell after install for 'atomic' command to work)$RS" ""
    }
    Write-Host ""
}

# ── MAIN ──────────────────────────────────────────────────────────────────────
Show-Glitch
Write-Host ""
Write-Color "  $DM────────────────────────────────────────────────────────$RS" ""
Write-Color "    ATOMIC TERMINAL — WINDOWS INSTALLER" $G
Write-Color "  $DM────────────────────────────────────────────────────────$RS" ""
Write-Host ""

# Check Python
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Color "  Python not found. Installing via winget..." $YL
    winget install --id Python.Python.3 -e --silent
    Write-Host ""
}

Show-Legal
Install-Tools
Get-Atomic

Write-Color "  $DM────────────────────────────────────────────────────────$RS" ""
Write-Color "    ATOMIC TERMINAL INSTALLED" $G
Write-Color "  $DM────────────────────────────────────────────────────────$RS" ""
Write-Host ""
Write-Color "  Restart PowerShell, then type:  atomic" $WH
Write-Host ""
Write-Color "  Launching now..." $DM
Write-Host ""

python "$INSTALL_DIR\atomic.py"
