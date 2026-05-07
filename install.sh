#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
#   ATOMIC TERMINAL — Installer  (macOS · Linux)
# ─────────────────────────────────────────────────────────────────────────
#   What this installs:
#     * atomic.py (local CLI, pure stdlib) → ~/.atomic/atomic.py
#     * launcher.sh                        → ~/.atomic/launcher.sh
#     * symlink `atomic` in /usr/local/bin if writable,
#       otherwise a shell alias in ~/.zshrc or ~/.bashrc
#
#   What this does NOT do:
#     * Install ANY third-party offensive tool (nmap, sqlmap, hydra,
#       aircrack, masscan, hashcat, john, …). Atomic Terminal is a
#       read-only local diagnostics / defensive security companion.
#     * Auto-execute any remote code.
#     * Require sudo unless /usr/local/bin is already writable.
#     * Install any pip package. Python 3.8+ stdlib only.
#
#   Actions:
#     ./install.sh                install
#     ./install.sh --update       re-copy atomic.py and refresh symlink
#     ./install.sh --uninstall    remove ~/.atomic and the symlink/alias
#     ./install.sh --yes          skip the confirmation prompt
#
#   Uninstall manually:
#     rm -rf ~/.atomic
#     rm -f /usr/local/bin/atomic
#     (edit ~/.zshrc / ~/.bashrc to remove the "alias atomic=..." line)
# ─────────────────────────────────────────────────────────────────────────

set -u

# ── Colors ───────────────────────────────────────────────────────────────
G='\033[38;2;0;255;153m'
DG='\033[38;2;0;160;90m'
CY='\033[38;2;0;230;255m'
RD='\033[38;2;255;60;60m'
YL='\033[38;2;255;215;0m'
DM='\033[38;2;30;90;60m'
WH='\033[38;2;210;255;230m'
BD='\033[1m'
RST='\033[0m'

if [[ ! -t 1 ]] || [[ -n "${NO_COLOR:-}" ]]; then
  G=''; DG=''; CY=''; RD=''; YL=''; DM=''; WH=''; BD=''; RST=''
fi

INSTALL_DIR="$HOME/.atomic"
REPORTS_DIR="$INSTALL_DIR/reports"
QUARANTINE_DIR="$INSTALL_DIR/quarantine"
SCRIPT_PATH="${BASH_SOURCE[0]:-$0}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" 2>/dev/null && pwd)"
SOURCE_PY=""
MODE="install"
AUTO_YES=0

# Resolve source atomic.py
if [[ -f "${SCRIPT_DIR}/atomic.py" ]]; then
  SOURCE_PY="${SCRIPT_DIR}/atomic.py"
elif [[ -f "./atomic.py" ]]; then
  SOURCE_PY="$(pwd)/atomic.py"
fi

# ── Parse args ───────────────────────────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --update|update)        MODE="update"    ;;
    --uninstall|uninstall)  MODE="uninstall" ;;
    --yes|-y)               AUTO_YES=1       ;;
    --help|-h|help)         MODE="help"      ;;
    *) : ;;
  esac
done

# ── Output helpers ───────────────────────────────────────────────────────
note()  { printf "${CY}  %s${RST}\n" "$*"; }
ok()    { printf "${G}  ✓ %s${RST}\n" "$*"; }
warn()  { printf "${YL}  ! %s${RST}\n" "$*"; }
err()   { printf "${RD}  ✗ %s${RST}\n" "$*"; }
dim()   { printf "${DM}  %s${RST}\n" "$*"; }
hdr()   { printf "${G}${BD}%s${RST}\n" "$*"; }

print_logo() {
  printf "${G}${BD}"
  cat <<'EOF'
   █████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗
  ██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝
  ███████║   ██║   ██║   ██║██╔████╔██║██║██║
  ██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║
  ██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗
  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝
EOF
  printf "${RST}\n"
}

# ── Help ─────────────────────────────────────────────────────────────────
show_help() {
  print_logo
  echo
  hdr "  ATOMIC TERMINAL · INSTALLER"
  printf "${DM}  ────────────────────────────────────────────────────${RST}\n"
  printf "${WH}  Installs the local Atomic CLI (stdlib only, no pip, no sudo).${RST}\n"
  echo
  printf "${WH}  Usage:${RST}\n"
  printf "    ${G}./install.sh${RST}             install\n"
  printf "    ${G}./install.sh --update${RST}    re-copy the CLI, refresh launcher\n"
  printf "    ${G}./install.sh --uninstall${RST} remove ~/.atomic + symlink\n"
  printf "    ${G}./install.sh --yes${RST}       skip confirmation\n"
  echo
  printf "${DM}  Atomic Terminal is READ-ONLY. It does not install nmap,${RST}\n"
  printf "${DM}  sqlmap, hydra, aircrack, or any offensive tool.${RST}\n"
}

# ── Safety banner ────────────────────────────────────────────────────────
banner_install() {
  clear 2>/dev/null || true
  print_logo
  printf "${DM}  ────────────────────────────────────────────────────${RST}\n"
  printf "${DG}  LOCAL INSTALLER        · read-only diagnostics terminal${RST}\n"
  printf "${DM}  ────────────────────────────────────────────────────${RST}\n"
  echo
  printf "${WH}  This installs Atomic Terminal into ${G}~/.atomic${WH}.${RST}\n"
  printf "${WH}  Atomic Terminal is a serious local power tool:${RST}\n"
  printf "${WH}    · real system diagnostics (CPU, memory, disk, battery)${RST}\n"
  printf "${WH}    · real process & network inspection (listening ports, sockets)${RST}\n"
  printf "${WH}    · defensive audit (ssh hygiene, weak perms, startup items)${RST}\n"
  printf "${WH}    · JSON/TXT reports & a support-bundle exporter${RST}\n"
  echo
  printf "${WH}  It will NOT install nmap/sqlmap/hydra/aircrack/masscan/etc.${RST}\n"
  printf "${WH}  It does NOT use sudo. It does NOT run arbitrary remote code.${RST}\n"
  echo
  if [[ $AUTO_YES -eq 1 ]]; then
    note "auto-confirm (--yes)"; return
  fi
  printf "${WH}  Continue?  ${YL}type  yes  to proceed:${RST} "
  local answer
  read -r answer </dev/tty || { err "no controlling tty; aborting"; exit 1; }
  if [[ "$answer" != "yes" && "$answer" != "y" && "$answer" != "Y" && "$answer" != "YES" ]]; then
    printf "${DM}  aborted.${RST}\n"
    exit 0
  fi
}

# ── Platform + Python ────────────────────────────────────────────────────
check_platform() {
  note "checking platform…"
  local os
  os="$(uname -s 2>/dev/null || echo unknown)"
  case "$os" in
    Darwin|Linux) ok "platform: $os" ;;
    *) warn "platform: $os (untested; continuing best-effort)" ;;
  esac
}

check_python() {
  note "checking Python…"
  if ! command -v python3 >/dev/null 2>&1; then
    err "python3 not found. Install Python 3.8+ and re-run."
    exit 1
  fi
  local ver major minor
  ver="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo 0.0)"
  major="${ver%%.*}"
  minor="${ver##*.}"
  if [[ -z "$major" || -z "$minor" ]] || (( major < 3 || (major == 3 && minor < 8) )); then
    err "python ${ver} too old. Need Python 3.8+."
    exit 1
  fi
  ok "python ${ver}"
}

# ── Install ──────────────────────────────────────────────────────────────
copy_cli() {
  mkdir -p "$INSTALL_DIR" "$REPORTS_DIR" "$QUARANTINE_DIR"
  chmod 0700 "$QUARANTINE_DIR" 2>/dev/null || true
  if [[ -z "$SOURCE_PY" ]]; then
    err "atomic.py not found next to install.sh (and not in cwd)."
    err "Run install.sh from the same directory as atomic.py."
    exit 1
  fi
  cp "$SOURCE_PY" "$INSTALL_DIR/atomic.py"
  chmod 0755 "$INSTALL_DIR/atomic.py" 2>/dev/null || true

  if [[ ! -f "$INSTALL_DIR/config.json" ]]; then
    cat > "$INSTALL_DIR/config.json" <<EOF
{
  "installed": true,
  "mode": "safe",
  "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "deviceConsent": false
}
EOF
  fi
  if [[ ! -f "$INSTALL_DIR/state.json" ]]; then
    cat > "$INSTALL_DIR/state.json" <<EOF
{
  "version": "3.0.0",
  "verbose": false,
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
  fi
  if [[ ! -f "$INSTALL_DIR/risk.json" ]]; then
    printf "[]\n" > "$INSTALL_DIR/risk.json"
  fi
  if [[ ! -f "$INSTALL_DIR/quarantine/index.json" ]]; then
    printf "[]\n" > "$INSTALL_DIR/quarantine/index.json"
  fi
  if [[ ! -f "$INSTALL_DIR/logs.txt" ]]; then
    printf "[%s] atomic installed; device checkup log initialised\n" \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$INSTALL_DIR/logs.txt"
  fi
  if [[ ! -f "$INSTALL_DIR/session.log" ]]; then
    printf "[%s] session log initialised\n" \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$INSTALL_DIR/session.log"
  fi
  ok "copied atomic.py → $INSTALL_DIR/atomic.py"
}

install_launcher() {
  note "creating launcher…"
  cat > "$INSTALL_DIR/launcher.sh" <<'EOF'
#!/usr/bin/env bash
exec python3 "$HOME/.atomic/atomic.py" "$@"
EOF
  chmod 0755 "$INSTALL_DIR/launcher.sh"

  local target="/usr/local/bin/atomic"
  local linked=0

  if [[ -w "/usr/local/bin" ]] 2>/dev/null; then
    if ln -sf "$INSTALL_DIR/launcher.sh" "$target" 2>/dev/null; then
      ok "installed symlink: $target"
      linked=1
    fi
  fi

  if [[ $linked -eq 0 ]]; then
    local profile=""
    if [[ -n "${ZSH_VERSION:-}" || "$SHELL" == *zsh ]] && [[ -f "$HOME/.zshrc" ]]; then
      profile="$HOME/.zshrc"
    elif [[ -f "$HOME/.bashrc" ]]; then
      profile="$HOME/.bashrc"
    elif [[ -f "$HOME/.bash_profile" ]]; then
      profile="$HOME/.bash_profile"
    fi
    if [[ -n "$profile" ]]; then
      local alias_line="alias atomic='python3 $INSTALL_DIR/atomic.py'"
      if ! grep -Fqs "$alias_line" "$profile" 2>/dev/null; then
        printf "\n# Added by Atomic installer\n%s\n" "$alias_line" >> "$profile"
        ok "alias added to $profile"
        warn "run:  source \"$profile\"    (or open a new shell)"
      else
        ok "alias already present in $profile"
      fi
    else
      warn "could not find a shell profile to update."
      warn "run manually:  python3 $INSTALL_DIR/atomic.py"
    fi
  fi
}

verify() {
  note "verifying install…"
  if [[ ! -f "$INSTALL_DIR/atomic.py" ]]; then
    err "atomic.py missing after copy"; exit 1
  fi
  if ! python3 -c "import ast; ast.parse(open('$INSTALL_DIR/atomic.py').read())" 2>/dev/null; then
    err "atomic.py failed a syntax check"; exit 1
  fi
  ok "atomic.py parses cleanly"
  local ver
  ver="$(python3 "$INSTALL_DIR/atomic.py" --version 2>/dev/null | tr -d ' ')"
  if [[ -n "$ver" ]]; then ok "self-check: ${ver}"; fi
  ok "install dir: $INSTALL_DIR"
  ok "reports dir: $REPORTS_DIR"
  ok "quarantine dir: $QUARANTINE_DIR"

  note "running selftest…"
  if python3 "$INSTALL_DIR/atomic.py" --selftest 2>/dev/null | tail -n 1 | grep -q "healthy"; then
    ok "selftest: healthy"
  else
    warn "selftest reported issues. Run:  atomic selftest   for details."
  fi
}

done_screen_install() {
  echo
  printf "${DM}  ────────────────────────────────────────────────────${RST}\n"
  printf "${G}  ✓ Installation complete.${RST}\n"
  printf "${DM}  ────────────────────────────────────────────────────${RST}\n"
  echo
  printf "${WH}  Launch with:          ${G}atomic${RST}\n"
  printf "${WH}  Or directly:          ${G}python3 ~/.atomic/atomic.py${RST}\n"
  echo
  printf "${WH}  Try:${RST}\n"
  printf "    ${G}atomic selftest${WH}      verify Atomic's own install + safety hooks${RST}\n"
  printf "    ${G}atomic quickscan${WH}     fast safe device scan${RST}\n"
  printf "    ${G}atomic downloadcheck${WH} scan only your Downloads folder${RST}\n"
  printf "    ${G}atomic checkall${WH}      full read-only scan + JSON & TXT report${RST}\n"
  printf "    ${G}atomic risk${WH}          show the latest risk score${RST}\n"
  printf "    ${G}atomic explain${WH} <text> plain-language explainer${RST}\n"
  echo
  printf "${WH}  Browser counterpart:  open ${G}index.html${WH} in any modern browser${RST}\n"
  echo
  printf "${DM}  Update:     ./install.sh --update${RST}\n"
  printf "${DM}  Uninstall:  ./install.sh --uninstall${RST}\n"
  echo
}

# ── Update ───────────────────────────────────────────────────────────────
do_update() {
  print_logo
  hdr "  UPDATE"
  printf "${DM}  ────────────────────────────────────────────────────${RST}\n"
  check_python
  copy_cli
  install_launcher
  verify
  echo
  ok "updated. Launch:  atomic"
}

# ── Uninstall ────────────────────────────────────────────────────────────
do_uninstall() {
  print_logo
  hdr "  UNINSTALL"
  printf "${DM}  ────────────────────────────────────────────────────${RST}\n"
  if [[ $AUTO_YES -eq 0 ]]; then
    printf "${WH}  This will remove ${G}~/.atomic${WH}, including:${RST}\n"
    printf "${WH}    · config + state${RST}\n"
    printf "${WH}    · session + device logs${RST}\n"
    printf "${WH}    · ALL reports in ${G}${REPORTS_DIR}${RST}\n"
    if [[ -d "$QUARANTINE_DIR" ]]; then
      local _qcount=0
      _qcount=$(ls -1 "$QUARANTINE_DIR" 2>/dev/null | grep -v '^index\.json$' | wc -l | tr -d ' ')
      if [[ "${_qcount:-0}" != "0" ]]; then
        echo
        printf "${RD}  WARNING:${WH} quarantine still holds ${YL}${_qcount}${WH} file(s).${RST}\n"
        printf "${WH}  Run ${G}atomic undo${WH} first to restore anything you want back.${RST}\n"
      fi
    fi
    printf "${WH}  And any ${G}/usr/local/bin/atomic${WH} symlink.${RST}\n"
    echo
    printf "${WH}  Type ${YL}yes${WH} to confirm: ${RST}"
    local a
    read -r a </dev/tty || { err "no tty; aborting"; exit 1; }
    [[ "$a" != "yes" && "$a" != "y" ]] && { dim "aborted."; exit 0; }
  fi
  if [[ -d "$INSTALL_DIR" ]]; then
    rm -rf "$INSTALL_DIR" && ok "removed $INSTALL_DIR" || err "could not remove $INSTALL_DIR"
  else
    dim "$INSTALL_DIR does not exist"
  fi
  if [[ -L "/usr/local/bin/atomic" ]] || [[ -f "/usr/local/bin/atomic" ]]; then
    rm -f /usr/local/bin/atomic 2>/dev/null && ok "removed /usr/local/bin/atomic" \
      || warn "could not remove /usr/local/bin/atomic (may need sudo)"
  fi
  dim "Note: any 'alias atomic=' line in ~/.zshrc or ~/.bashrc is left for you to remove."
}

# ── Main ─────────────────────────────────────────────────────────────────
main() {
  case "$MODE" in
    help)      show_help ;;
    uninstall) do_uninstall ;;
    update)    do_update ;;
    install)
      banner_install
      check_platform
      check_python
      copy_cli
      install_launcher
      verify
      done_screen_install
      ;;
  esac
}

main
