#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#   ATOMIC TERMINAL — Installer
#   Built by Pavlopanda
# ─────────────────────────────────────────────────────────────────────────────

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

ATOMIC_URL="https://raw.githubusercontent.com/P4vL0-P4nd4/atomic-terminal/main/atomic.py"
INSTALL_DIR="$HOME/.atomic"
GLITCH='!@#$%^&*<>?|{}[]░▒▓█▄▀■□×÷±≈∞'

clr() { printf '\033[2J\033[H'; }

# ── LOGO LINES ────────────────────────────────────────────────────────────────
LOGO=(
  "   █████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗ "
  "  ██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝ "
  "  ███████║   ██║   ██║   ██║██╔████╔██║██║██║      "
  "  ██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║      "
  "  ██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗ "
  "  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝ "
)

# ── GLITCH ONE LINE ───────────────────────────────────────────────────────────
glitch_line() {
  local text="$1" intensity="${2:-30}"
  local out="" ch r idx
  for (( j=0; j<${#text}; j++ )); do
    ch="${text:$j:1}"
    r=$(( RANDOM % 100 ))
    if [[ "$ch" != " " && $r -lt $intensity ]]; then
      idx=$(( RANDOM % ${#GLITCH} ))
      out+="${GLITCH:$idx:1}"
    else
      out+="$ch"
    fi
  done
  echo "$out"
}

pick_color() {
  local colors=("$G" "$CY" "$PK" "$YL" "$RD" "$DG" "$WH")
  echo "${colors[$(( RANDOM % ${#colors[@]} ))]}"
}

# ── FULL LOGO GLITCH ANIMATION ────────────────────────────────────────────────
glitch_logo_anim() {
  local passes="${1:-30}"   # number of frames
  local settle="${2:-8}"    # last N frames settle to clean

  for (( i=0; i<passes; i++ )); do
    clr
    local intensity
    if (( i < passes - settle )); then
      # wild glitch phase — high intensity, random colors per line
      intensity=$(( 60 - i * 2 ))
      (( intensity < 10 )) && intensity=10
      for line in "${LOGO[@]}"; do
        local gl c
        gl="$(glitch_line "$line" "$intensity")"
        c="$(pick_color)"
        printf "${c}%s${RST}\n" "$gl"
      done
    else
      # settle phase — less chaos, converging to green
      intensity=$(( (passes - i) * 6 ))
      for line in "${LOGO[@]}"; do
        if (( RANDOM % 4 == 0 )); then
          gl="$(glitch_line "$line" "$intensity")"
          printf "${CY}%s${RST}\n" "$gl"
        else
          printf "${G}${BD}%s${RST}\n" "$line"
        fi
      done
    fi
    sleep 0.07
  done

  # Final clean render
  clr
  for line in "${LOGO[@]}"; do
    printf "${G}${BD}%s${RST}\n" "$line"
    sleep 0.035
  done
}

# ── LEGAL SCREEN ──────────────────────────────────────────────────────────────
show_legal() {
  printf "\n"
  printf "${RD}  ════════════════════════════════════════════════════════${RST}\n"
  printf "${RD}${BD}  ⚠  LEGAL WARNING — READ BEFORE CONTINUING${RST}\n"
  printf "${RD}  ════════════════════════════════════════════════════════${RST}\n\n"
  printf "${WH}  Atomic Terminal installs real security testing tools.${RST}\n"
  printf "${WH}  These tools are for AUTHORIZED use only:${RST}\n\n"
  printf "${DG}  • Systems you OWN${RST}\n"
  printf "${DG}  • Systems with EXPLICIT WRITTEN PERMISSION to test${RST}\n"
  printf "${DG}  • CTF competitions and authorized security research${RST}\n\n"
  printf "${RD}  ILLEGAL USE IS A CRIMINAL OFFENCE.${RST}\n"
  printf "${RD}  CFAA (USA) · Computer Misuse Act (UK) · EU 2013/40/EU${RST}\n"
  printf "${RD}  Penalties: imprisonment and heavy fines.${RST}\n\n"
  printf "${YL}  Pavlopanda and Atomic Terminal bear ZERO liability${RST}\n"
  printf "${YL}  for any misuse. You are solely responsible.${RST}\n\n"
  printf "${RD}  ════════════════════════════════════════════════════════${RST}\n\n"

  printf "${YL}  Type  I AGREE  in capitals to accept and continue: ${RST}"
  local answer
  read -r answer </dev/tty
  printf "\n"
  if [[ "$answer" != "I AGREE" ]]; then
    printf "${RD}  Aborted.${RST}\n\n"
    exit 0
  fi
}

# ── PROGRESS BAR (fake, takes ~35s total across all tools) ────────────────────
draw_bar() {
  local label="$1" steps="$2" delay="$3"
  local W=36
  printf "${CY}  %-18s${RST}  " "$label"
  for (( i=1; i<=steps; i++ )); do
    local filled=$(( i * W / steps ))
    local empty=$(( W - filled ))
    local pct=$(( i * 100 / steps ))
    local B1 B2
    B1=$(printf '%0.s█' $(seq 1 $filled) 2>/dev/null || python3 -c "print('█'*$filled, end='')")
    B2=$(printf '%0.s░' $(seq 1 $empty) 2>/dev/null || python3 -c "print('░'*$empty, end='')")
    printf "\r${CY}  %-18s${RST}  ${G}%s${DM}%s${RST}  ${WH}%3d%%${RST}" \
      "$label" "$B1" "$B2" "$pct"
    sleep "$delay"
  done
}

# ── DOWNLOAD ANIMATION (35 sec total) ─────────────────────────────────────────
download_atomic_anim() {
  printf "\n"
  printf "${CY}  Downloading Atomic Terminal...${RST}\n\n"
  sleep 0.3

  # Phase 1: connecting (glitchy)
  printf "${DM}  Establishing secure connection${RST}"
  for i in 1 2 3 4 5; do
    sleep 0.18
    printf "${G}.${RST}"
  done
  printf "\n"
  sleep 0.2

  # Phase 2: glitch burst before download bar
  printf "\n"
  local glitch_lines=(
    "  [ATOMIC] Initializing payload transfer..."
    "  [ATOMIC] Bypassing standard protocols..."
    "  [ATOMIC] Encrypting channel..."
    "  [ATOMIC] Remote handshake OK"
    "  [ATOMIC] Transfer authorized"
  )
  for gl in "${glitch_lines[@]}"; do
    local glitched
    glitched="$(glitch_line "$gl" 40)"
    printf "${PK}%s${RST}\n" "$glitched"
    sleep 0.08
    printf "\r${DG}%s${RST}\n" "$gl"
    sleep 0.06
  done
  printf "\n"
  sleep 0.3

  # Phase 3: download bar — 3 seconds
  draw_bar "atomic.py" 30 0.1
  printf "  ${G}✓${RST}\n"
}

# ── INSTALL TOOLS ─────────────────────────────────────────────────────────────
install_tools() {
  printf "\n"
  printf "${CY}  Installing security tools:${RST}\n\n"

  local tools=(
    "nmap" "masscan" "sqlmap" "hydra"
    "john" "hashcat" "aircrack-ng"
    "nikto" "gobuster" "ncat" "wget"
  )

  for tool in "${tools[@]}"; do
    draw_bar "$tool" 10 0.1

    if [[ "$(uname -s)" == "Darwin" ]]; then
      timeout 8 brew install "$tool" &>/dev/null 2>&1 || true
    else
      timeout 8 sudo apt-get install -y "$tool" &>/dev/null 2>&1 || true
    fi

    local check="${tool%%-*}"
    if command -v "$check" &>/dev/null; then
      printf "  ${G}✓${RST}\n"
    else
      printf "  ${YL}○${RST}\n"
    fi
  done

  printf "\n"
  printf "${CY}  Installing Python packages:${RST}\n\n"
  local py_pkgs=("requests" "python-whois" "dnspython")
  for pkg in "${py_pkgs[@]}"; do
    draw_bar "pip: $pkg" 30 0.1
    python3 -m pip install "$pkg" -q --break-system-packages >/dev/null 2>&1 \
      || python3 -m pip install "$pkg" -q --user >/dev/null 2>&1 \
      || python3 -m pip install "$pkg" -q >/dev/null 2>&1 \
      || true
    printf "  ${G}✓${RST}\n"
  done
}

# ── DOWNLOAD atomic.py ────────────────────────────────────────────────────────
fetch_atomic() {
  mkdir -p "$INSTALL_DIR"
  curl -fsSL "$ATOMIC_URL" -o "$INSTALL_DIR/atomic.py" 2>/dev/null || {
    [[ -f "./atomic.py" ]] && cp "./atomic.py" "$INSTALL_DIR/atomic.py" || true
  }
  chmod +x "$INSTALL_DIR/atomic.py" 2>/dev/null || true

  # Write config so atomic.py knows install is done — prevents double install
  mkdir -p "$INSTALL_DIR"
  printf '{"installed":true,"disclaimer_accepted":true,"version":"%s"}\n' "1.0.0" \
    > "$INSTALL_DIR/config.json"
}

# ── INSTALL atomic COMMAND ────────────────────────────────────────────────────
install_command() {
  printf "\n"
  printf "${CY}  Creating  atomic  command...${RST}\n"

  cat > "$INSTALL_DIR/launcher.sh" << 'EOF'
#!/usr/bin/env bash
python3 "$HOME/.atomic/atomic.py" "$@"
EOF
  chmod +x "$INSTALL_DIR/launcher.sh"

  if ln -sf "$INSTALL_DIR/launcher.sh" /usr/local/bin/atomic 2>/dev/null; then
    printf "${G}  ✓  /usr/local/bin/atomic${RST}\n"
  elif sudo ln -sf "$INSTALL_DIR/launcher.sh" /usr/local/bin/atomic 2>/dev/null; then
    printf "${G}  ✓  /usr/local/bin/atomic (sudo)${RST}\n"
  else
    local profile="$HOME/.zshrc"
    [[ -f "$HOME/.bashrc" ]] && profile="$HOME/.bashrc"
    echo "alias atomic='python3 $INSTALL_DIR/atomic.py'" >> "$profile"
    printf "${YL}  ✓  alias added to %s${RST}\n" "$profile"
    printf "${YL}     Run: source %s${RST}\n" "$profile"
  fi
}

# ── DONE SCREEN ───────────────────────────────────────────────────────────────
done_screen() {
  sleep 0.4
  # One last glitch burst
  glitch_logo_anim 10 4
  printf "\n"
  printf "${DM}  ────────────────────────────────────────────────────${RST}\n\n"
  printf "${G}  ✓  Installation complete.${RST}\n\n"
  printf "${WH}  Installed to:  ${G}~/.atomic/${RST}\n"
  printf "${WH}  Launch with:   ${G}atomic${RST}\n\n"
  printf "${DM}  Requires: Atomic Pro or Max plan.${RST}\n"
  printf "${DM}  Upgrade:  atomicai.pavlopanda.com${RST}\n\n"
  printf "${DM}  ────────────────────────────────────────────────────${RST}\n\n"

  local msg="  Launching Atomic Terminal..."
  for (( i=0; i<${#msg}; i++ )); do
    printf "${G}%s${RST}" "${msg:$i:1}"
    sleep 0.028
  done
  printf "\n\n"
  sleep 1.2

  if command -v atomic &>/dev/null; then
    atomic </dev/tty
  else
    python3 "$INSTALL_DIR/atomic.py" </dev/tty
  fi
}

# ── MAIN ──────────────────────────────────────────────────────────────────────
main() {
  # Glitch intro (12 frames)
  glitch_logo_anim 12 4

  printf "\n"
  printf "${DM}  ──────────────────────────────────────────────────────${RST}\n"
  printf "${DG}  TERMINAL INSTALLER            Built by Pavlopanda${RST}\n"
  printf "${DM}  ──────────────────────────────────────────────────────${RST}\n"

  show_legal
  install_tools
  download_atomic_anim
  fetch_atomic
  install_command
  done_screen
}

main
