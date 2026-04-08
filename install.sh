#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#   ATOMIC TERMINAL — Installer
#   Built by Pavlopanda
#   https://atomicai.pavlopanda.com
# ─────────────────────────────────────────────────────────────────────────────

set -e

# ── COLORS ────────────────────────────────────────────────────────────────────
G='\033[38;2;0;255;153m'
DG='\033[38;2;0;160;90m'
CY='\033[38;2;0;230;255m'
RD='\033[38;2;255;60;60m'
YL='\033[38;2;255;215;0m'
DM='\033[38;2;30;90;60m'
WH='\033[38;2;210;255;230m'
PK='\033[38;2;255;0;200m'
BD='\033[1m'
RST='\033[0m'

GLITCH_POOL='!@#$%^&*<>?|{}[]░▒▓'
ATOMIC_URL="https://raw.githubusercontent.com/pavlopanda/atomic-terminal/main/atomic.py"
INSTALL_DIR="$HOME/.atomic"
BIN_TARGET="/usr/local/bin/atomic"

# ── UTILS ─────────────────────────────────────────────────────────────────────
clr() { printf '\033[2J\033[H'; }
p()   { printf "${G}%s${RST}\n" "$1"; }
pc()  { printf "${CY}%s${RST}\n" "$1"; }
pw()  { printf "${YL}%s${RST}\n" "$1"; }
pe()  { printf "${RD}%s${RST}\n" "$1"; }
pd()  { printf "${DM}%s${RST}\n" "$1"; }

sleep_ms() { sleep "$(echo "scale=3; $1/1000" | bc 2>/dev/null || echo 0.05)"; }

glitch_line() {
  local text="$1"
  local iters="${2:-8}"
  local colors=("$G" "$CY" "$PK" "$YL" "$RD")
  for i in $(seq 1 "$iters"); do
    local out=""
    for (( j=0; j<${#text}; j++ )); do
      ch="${text:$j:1}"
      r=$((RANDOM % 10))
      if [[ "$ch" != " " && $r -lt 3 ]]; then
        idx=$((RANDOM % ${#GLITCH_POOL}))
        out+="${GLITCH_POOL:$idx:1}"
      else
        out+="$ch"
      fi
    done
    c="${colors[$((RANDOM % ${#colors[@]}))]}"
    printf "\r${c}%s${RST}" "$out"
    sleep 0.06
  done
  printf "\r${G}${BD}%s${RST}\n" "$text"
}

progress_bar() {
  local label="$1"
  local width=38
  local steps=$((20 + RANDOM % 16))
  printf "${CY}  %-22s${RST}  " "$label"
  for i in $(seq 1 "$steps"); do
    filled=$(( i * width / steps ))
    empty=$(( width - filled ))
    pct=$(( i * 100 / steps ))
    bar=$(printf "${G}%${filled}s${RST}${DM}%${empty}s${RST}" | tr ' ' '█' | sed 's/\(${RST}\)/\1/g')
    # simpler approach
    B1=$(printf '%0.s█' $(seq 1 $filled))
    B2=$(printf '%0.s░' $(seq 1 $empty))
    printf "\r${CY}  %-22s${RST}  ${G}%s${DM}%s${RST}  ${WH}%3d%%${RST}" \
      "$label" "$B1" "$B2" "$pct"
    sleep 0.$(printf '%02d' $((40 + RANDOM % 80)))
  done
}

# ── INTRO ANIMATION ───────────────────────────────────────────────────────────
show_intro() {
  clr
  sleep 0.1

  # Glitch passes
  local logo=(
    "   █████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗ "
    "  ██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝ "
    "  ███████║   ██║   ██║   ██║██╔████╔██║██║██║      "
    "  ██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║      "
    "  ██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗ "
    "  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝ "
  )

  for pass in 1 2 3 4 5 6 7; do
    clr
    for line in "${logo[@]}"; do
      colors=("$G" "$CY" "$PK" "$YL" "$G" "$DG")
      c="${colors[$((RANDOM % ${#colors[@]}))]}"
      if (( RANDOM % 3 == 0 )); then
        # Glitch the line
        out=""
        for (( j=0; j<${#line}; j++ )); do
          ch="${line:$j:1}"
          r=$((RANDOM % 10))
          if [[ "$ch" != " " && $r -lt 2 ]]; then
            idx=$((RANDOM % ${#GLITCH_POOL}))
            out+="${GLITCH_POOL:$idx:1}"
          else
            out+="$ch"
          fi
        done
        printf "${c}%s${RST}\n" "$out"
      else
        printf "${DG}%s${RST}\n" "$line"
      fi
    done
    sleep 0.08
  done

  # Final clean logo
  clr
  for line in "${logo[@]}"; do
    printf "${G}${BD}%s${RST}\n" "$line"
    sleep 0.04
  done

  printf "\n"
  printf "${DM}%s${RST}\n" "  ──────────────────────────────────────────────────────"
  printf "${DG}  TERMINAL INSTALLER            Built by Pavlopanda${RST}\n"
  printf "${DM}%s${RST}\n" "  ──────────────────────────────────────────────────────"
  printf "\n"
  sleep 0.5
}

# ── LEGAL ─────────────────────────────────────────────────────────────────────
show_legal() {
  printf "${RD}%s${RST}\n" "  ════════════════════════════════════════════════════════"
  printf "${RD}${BD}  ⚠  LEGAL WARNING — READ BEFORE CONTINUING${RST}\n"
  printf "${RD}%s${RST}\n" "  ════════════════════════════════════════════════════════"
  printf "\n"
  printf "${WH}  Atomic Terminal installs real security testing tools.${RST}\n"
  printf "${WH}  These tools are for AUTHORIZED use only:${RST}\n"
  printf "\n"
  printf "${DG}  • Systems you OWN${RST}\n"
  printf "${DG}  • Systems with EXPLICIT WRITTEN PERMISSION to test${RST}\n"
  printf "${DG}  • CTF competitions and authorized security research${RST}\n"
  printf "\n"
  printf "${RD}  ILLEGAL USE IS A CRIMINAL OFFENCE.${RST}\n"
  printf "${RD}  CFAA (USA) · Computer Misuse Act (UK) · EU 2013/40/EU${RST}\n"
  printf "${RD}  Penalties: imprisonment and heavy fines.${RST}\n"
  printf "\n"
  printf "${YL}  Pavlopanda and Atomic Terminal bear ZERO liability${RST}\n"
  printf "${YL}  for any misuse. You are solely responsible for all${RST}\n"
  printf "${YL}  actions taken with this software.${RST}\n"
  printf "\n"
  printf "${RD}%s${RST}\n" "  ════════════════════════════════════════════════════════"
  printf "\n"

  printf "${YL}  Type  I AGREE  to accept all terms and continue: ${RST}"
  read -r answer
  if [[ "$answer" != "I AGREE" ]]; then
    printf "\n"
    pe "  Aborted. You must agree to the terms."
    exit 0
  fi
  printf "\n"
}

# ── DETECT OS ─────────────────────────────────────────────────────────────────
detect_os() {
  OS_TYPE="$(uname -s)"
  if [[ "$OS_TYPE" == "Darwin" ]]; then
    PLATFORM="macos"
    PKG_INSTALL="brew install"
  elif [[ "$OS_TYPE" == "Linux" ]]; then
    PLATFORM="linux"
    if command -v apt-get &>/dev/null; then
      PKG_INSTALL="sudo apt-get install -y"
    elif command -v pacman &>/dev/null; then
      PKG_INSTALL="sudo pacman -S --noconfirm"
    else
      PKG_INSTALL="echo"
    fi
  else
    pe "  Unsupported OS: $OS_TYPE"
    exit 1
  fi

  printf "${CY}  Detected: ${WH}%s${RST}\n" "$OS_TYPE"
  sleep 0.3
  printf "\n"
}

# ── INSTALL SEQUENCE ──────────────────────────────────────────────────────────
install_sequence() {
  pc "  Installing security tools..."
  printf "\n"

  tools=(
    "nmap" "masscan" "sqlmap" "hydra" "john"
    "hashcat" "aircrack-ng" "nikto" "gobuster"
    "curl" "wget" "ncat" "netcat"
  )

  for tool in "${tools[@]}"; do
    progress_bar "$tool"
    # Try to install silently
    if [[ "$PLATFORM" == "macos" ]]; then
      brew install "$tool" &>/dev/null 2>&1 || true
    elif [[ "$PLATFORM" == "linux" ]]; then
      sudo apt-get install -y "$tool" &>/dev/null 2>&1 || true
    fi

    # Check
    if command -v "${tool%%-*}" &>/dev/null; then
      printf "  ${G}✓${RST}\n"
    else
      printf "  ${YL}○${RST}\n"
    fi
  done

  printf "\n"
  pc "  Installing Python packages..."
  printf "\n"

  py_pkgs=("requests" "python-whois" "dnspython")
  for pkg in "${py_pkgs[@]}"; do
    progress_bar "pip: $pkg"
    python3 -m pip install "$pkg" -q &>/dev/null 2>&1 || true
    printf "  ${G}✓${RST}\n"
  done
}

# ── DOWNLOAD ATOMIC ───────────────────────────────────────────────────────────
download_atomic() {
  printf "\n"
  pc "  Downloading Atomic Terminal..."
  printf "\n"

  mkdir -p "$INSTALL_DIR"

  # Fake download animation
  printf "${CY}  %-22s${RST}  " "atomic.py"
  for i in $(seq 1 40); do
    B1=$(printf '%0.s█' $(seq 1 $i))
    B2=$(printf '%0.s░' $(seq 1 $((40-i))))
    pct=$(( i * 100 / 40 ))
    printf "\r${CY}  %-22s${RST}  ${G}%s${DM}%s${RST}  ${WH}%3d%%${RST}" \
      "atomic.py" "$B1" "$B2" "$pct"
    sleep 0.04
  done

  # Actual download
  if curl -fsSL "$ATOMIC_URL" -o "$INSTALL_DIR/atomic.py" 2>/dev/null; then
    printf "  ${G}✓${RST}\n"
  else
    # Fallback: copy from current directory if exists
    if [[ -f "./atomic.py" ]]; then
      cp "./atomic.py" "$INSTALL_DIR/atomic.py"
      printf "  ${G}✓ (local copy)${RST}\n"
    else
      printf "  ${RD}✗ (download failed — place atomic.py in ~/.atomic manually)${RST}\n"
    fi
  fi

  chmod +x "$INSTALL_DIR/atomic.py"
}

# ── INSTALL CLI COMMAND ───────────────────────────────────────────────────────
install_command() {
  printf "\n"
  pc "  Creating  atomic  command..."

  # Create launcher script
  cat > "$INSTALL_DIR/launcher.sh" << 'LAUNCHER'
#!/usr/bin/env bash
python3 "$HOME/.atomic/atomic.py" "$@"
LAUNCHER
  chmod +x "$INSTALL_DIR/launcher.sh"

  # Try to link to /usr/local/bin (macOS/Linux standard)
  if [[ -w "/usr/local/bin" ]]; then
    ln -sf "$INSTALL_DIR/launcher.sh" "$BIN_TARGET"
    printf "${G}  ✓  Linked to /usr/local/bin/atomic${RST}\n"
  else
    sudo ln -sf "$INSTALL_DIR/launcher.sh" "$BIN_TARGET" 2>/dev/null || {
      # Fallback: add to shell profile
      PROFILE="$HOME/.zshrc"
      [[ -f "$HOME/.bashrc" ]] && PROFILE="$HOME/.bashrc"
      echo "alias atomic='python3 $INSTALL_DIR/atomic.py'" >> "$PROFILE"
      printf "${YL}  ✓  Added alias to %s${RST}\n" "$PROFILE"
      printf "${YL}    Run: source %s${RST}\n" "$PROFILE"
    }
  fi
}

# ── DONE SCREEN ───────────────────────────────────────────────────────────────
done_screen() {
  printf "\n"
  sleep 0.3

  clr

  # Final glitch logo
  logo=(
    "   █████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗ "
    "  ██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝ "
    "  ███████║   ██║   ██║   ██║██╔████╔██║██║██║      "
    "  ██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║      "
    "  ██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗ "
    "  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝ "
  )

  for pass in 1 2 3; do
    clr
    for line in "${logo[@]}"; do
      c_idx=$((RANDOM % 4))
      case $c_idx in
        0) c="$G" ;; 1) c="$CY" ;; 2) c="$PK" ;; *) c="$YL" ;;
      esac
      printf "${c}%s${RST}\n" "$line"
    done
    sleep 0.1
  done

  clr
  for line in "${logo[@]}"; do
    printf "${G}${BD}%s${RST}\n" "$line"
  done

  printf "\n"
  printf "${DM}%s${RST}\n" "  ────────────────────────────────────────────────────"
  printf "\n"
  printf "${G}  ✓  Installation complete.${RST}\n"
  printf "\n"
  printf "${WH}  Installed to:  ${G}~/.atomic/${RST}\n"
  printf "${WH}  Launch with:   ${G}atomic${RST}\n"
  printf "\n"
  printf "${DM}  Requires: Atomic Pro or Max plan to access.${RST}\n"
  printf "${DM}  Upgrade:  atomicai.pavlopanda.com${RST}\n"
  printf "\n"
  printf "${DM}%s${RST}\n" "  ────────────────────────────────────────────────────"
  printf "\n"

  # Typewriter effect
  msg="  Launching Atomic Terminal..."
  for (( i=0; i<${#msg}; i++ )); do
    printf "${G}%s${RST}" "${msg:$i:1}"
    sleep 0.025
  done
  printf "\n\n"
  sleep 1

  # Launch it
  if command -v atomic &>/dev/null; then
    exec atomic
  else
    exec python3 "$INSTALL_DIR/atomic.py"
  fi
}

# ── MAIN ──────────────────────────────────────────────────────────────────────
main() {
  show_intro
  show_legal
  detect_os
  install_sequence
  download_atomic
  install_command
  done_screen
}

main
