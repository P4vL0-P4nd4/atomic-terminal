#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   █████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗
#  ██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝
#  ███████║   ██║   ██║   ██║██╔████╔██║██║██║
#  ██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║
#  ██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗
#  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝
#
# ATOMIC — Local Terminal Companion  (v3.0, SAFE MODE)
# ───────────────────────────────────────────────────────────────────────
# A serious local diagnostics, system inspection, defensive security, and
# automation terminal for your own machine. Pure Python stdlib — zero
# third-party dependencies. No offensive tooling. No network attacks.
#
# Companion to the Atomic AI browser platform: the website is the
# learning experience; this terminal is the real local power tool.
#
#   * READ-ONLY by default — atomic inspects, it does not modify.
#   * No shell passthrough, no auto-install, no unauthorized network I/O.
#   * Only runs against the local machine (with explicit `ping`/DNS to
#     hosts you give it).
#   * State and config in ~/.atomic/.
#
# Usage:   atomic               # interactive REPL
#          atomic <command>     # run a single command, non-interactive
#          atomic --help        # full command reference
#
# ───────────────────────────────────────────────────────────────────────

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import socket
import stat
import subprocess
import sys
import time
from datetime import datetime, timezone

VERSION = "3.0.0"

# ── Time helpers ──────────────────────────────────────────────────────────

def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _nowstamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")

# ── ANSI palette ──────────────────────────────────────────────────────────

def _rgb(r, g, b): return f"\033[38;2;{r};{g};{b}m"

G    = _rgb(0, 255, 153)
DG   = _rgb(0, 160, 90)
CY   = _rgb(0, 230, 255)
RD   = _rgb(255, 60, 60)
YL   = _rgb(255, 215, 0)
DM   = _rgb(30, 90, 60)
WH   = _rgb(210, 255, 230)
PK   = _rgb(255, 0, 200)
GY   = _rgb(120, 120, 120)
BOLD = "\033[1m"
RST  = "\033[0m"

USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

def _c(text: str, color: str) -> str:
    return f"{color}{text}{RST}" if USE_COLOR else text

def p(text: str = "", color: str = G, end: str = "\n"):
    print(_c(text, color), end=end, flush=True)

def pw(t): p(t, YL)
def pe(t): p(t, RD)
def pd(t): p(t, DM)
def pc(t): p(t, CY)
def pb(t): p(t, WH)
def ph(t): p(t, G)

def clr():
    if USE_COLOR:
        print("\033[2J\033[H", end="")

def rule(width: int = 60, color: str = DM):
    p("  " + "─" * width, color)

def section(title: str):
    print()
    ph(f"  {title}")
    rule()

def kv(k: str, v, width: int = 14):
    pb(f"  {k:<{width}} {v}")

# ── Premium labels ────────────────────────────────────────────────────────
# Consistent, readable status tags used by the user-facing safety commands.
# Keep these short and uppercase so a glance tells the user what happened.

def lbl_ok(t):     p(f"  [OK]       {t}", G)
def lbl_info(t):   p(f"  [INFO]     {t}", CY)
def lbl_warn(t):   p(f"  [WARNING]  {t}", YL)
def lbl_high(t):   p(f"  [HIGH RISK] {t}", RD)
def lbl_err(t):    p(f"  [ERROR]    {t}", RD)
def lbl_report(t): p(f"  [REPORT]   {t}", CY)
def lbl_next(t):   p(f"  [NEXT STEP] {t}", G)
def lbl_safety(t): p(f"  [SAFETY]   {t}", YL)

def pretty_oserror(exc: BaseException, path: str = "") -> str:
    """Convert OS exceptions into one short, user-friendly line — never a traceback."""
    if isinstance(exc, FileNotFoundError):
        return f"Path not found: {path or getattr(exc, 'filename', '')}".rstrip(": ")
    if isinstance(exc, PermissionError):
        return "Permission denied. Try a folder you own."
    if isinstance(exc, IsADirectoryError):
        return f"Expected a file, got a folder: {path}".rstrip(": ")
    if isinstance(exc, NotADirectoryError):
        return f"Expected a folder, got a file: {path}".rstrip(": ")
    if isinstance(exc, OSError):
        return f"OS error: {exc.strerror or str(exc)}"
    return str(exc) or exc.__class__.__name__

def err_path_not_found(path: str = ""):
    lbl_err("Path not found." + (f"  ({path})" if path else ""))

def err_permission(path: str = ""):
    lbl_err("Permission denied. Try a folder you own." + (f"  ({path})" if path else ""))

# ── Banner ────────────────────────────────────────────────────────────────

LOGO = [
    "   █████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗ ",
    "  ██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝ ",
    "  ███████║   ██║   ██║   ██║██╔████╔██║██║██║      ",
    "  ██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║      ",
    "  ██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗ ",
    "  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝ ",
]

def print_logo():
    for line in LOGO:
        p(line, G)

def print_banner():
    clr()
    print_logo()
    print()
    rule(60)
    pd(f"  ATOMIC TERMINAL  v{VERSION}    local diagnostics · defensive · read-only")
    rule(60)
    print()

# ── Platform detection ────────────────────────────────────────────────────

OS_NAME = platform.system()  # Darwin / Linux / Windows
IS_MAC   = OS_NAME == "Darwin"
IS_LINUX = OS_NAME == "Linux"
IS_WIN   = OS_NAME == "Windows"
IS_POSIX = IS_MAC or IS_LINUX

# ── Paths & state ─────────────────────────────────────────────────────────

HOME = os.path.expanduser("~")
APP_DIR = os.path.join(HOME, ".atomic")
STATE_PATH = os.path.join(APP_DIR, "state.json")
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
NOTES_PATH = os.path.join(APP_DIR, "notes.md")
REPORTS_DIR = os.path.join(APP_DIR, "reports")
LOG_PATH = os.path.join(APP_DIR, "session.log")

DEFAULT_STATE = {
    "version": VERSION,
    "xp": 0,
    "user": os.environ.get("USER") or os.environ.get("USERNAME") or "operator",
    "theme": "green",
    "verbose": False,
    "completed_lessons": {},
    "completed_exercises": {},
    "completed_rooms": {},
    "room_progress": {},
    "hints_used": {},
    "created_at": _utcnow_iso(),
}

DEFAULT_CONFIG = {
    "installed": True,
    "mode": "safe",
    "version": VERSION,
}

def _ensure_dirs():
    for d in (APP_DIR, REPORTS_DIR):
        try:
            os.makedirs(d, exist_ok=True)
        except Exception:
            pass

def load_state() -> dict:
    _ensure_dirs()
    if not os.path.exists(STATE_PATH):
        return dict(DEFAULT_STATE)
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return dict(DEFAULT_STATE)
        merged = dict(DEFAULT_STATE)
        merged.update(data)
        merged["version"] = VERSION
        for k in ("completed_lessons", "completed_exercises",
                  "completed_rooms", "room_progress", "hints_used"):
            if not isinstance(merged.get(k), dict):
                merged[k] = {}
        return merged
    except Exception:
        return dict(DEFAULT_STATE)

def save_state(state: dict) -> None:
    _ensure_dirs()
    try:
        tmp = STATE_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp, STATE_PATH)
    except Exception:
        pass

def load_config() -> dict:
    _ensure_dirs()
    if not os.path.exists(CONFIG_PATH):
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        if not isinstance(cfg, dict):
            return dict(DEFAULT_CONFIG)
        merged = dict(DEFAULT_CONFIG)
        merged.update(cfg)
        return merged
    except Exception:
        return dict(DEFAULT_CONFIG)

def save_config(cfg: dict) -> None:
    _ensure_dirs()
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

STATE = load_state()
CONFIG = load_config()

def log_event(msg: str):
    try:
        _ensure_dirs()
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{_utcnow_iso()}  {msg}\n")
    except Exception:
        pass

# ── Safe subprocess wrapper ───────────────────────────────────────────────

def run(cmd, timeout: float = 5.0, shell: bool = False):
    """
    Safe subprocess runner. Returns (rc, stdout, stderr). Never raises for
    normal failures. Commands are only used for READ-ONLY inspection of the
    local machine.
    """
    try:
        cp = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return cp.returncode, cp.stdout or "", cp.stderr or ""
    except FileNotFoundError:
        return 127, "", "not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except Exception as ex:
        return 1, "", str(ex)

def have(binary: str) -> bool:
    return shutil.which(binary) is not None

# ── Formatting helpers ────────────────────────────────────────────────────

def human_bytes(n: float) -> str:
    if n is None:
        return "?"
    try:
        n = float(n)
    except Exception:
        return str(n)
    for u in ("B", "KB", "MB", "GB", "TB", "PB"):
        if abs(n) < 1024.0:
            return f"{n:.1f} {u}" if u != "B" else f"{int(n)} B"
        n /= 1024.0
    return f"{n:.1f} EB"

def human_duration(seconds: float) -> str:
    try:
        seconds = int(seconds)
    except Exception:
        return "?"
    d, r = divmod(seconds, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if not parts: parts.append(f"{s}s")
    return " ".join(parts)

def _progress_bar(done, total, width=16):
    if total <= 0:
        return "[" + " " * width + "]  0%"
    filled = round(width * done / total)
    return "[" + "█" * filled + "░" * (width - filled) + f"]  {round(100 * done / total)}%"

# ── SYSTEM INFO ───────────────────────────────────────────────────────────

def os_pretty() -> str:
    if IS_MAC:
        rc, out, _ = run(["sw_vers"])
        if rc == 0:
            d = {}
            for line in out.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    d[k.strip()] = v.strip()
            name = d.get("ProductName", "macOS")
            ver  = d.get("ProductVersion", platform.mac_ver()[0])
            build = d.get("BuildVersion", "")
            return f"{name} {ver} ({build})".strip()
        return f"macOS {platform.mac_ver()[0]}"
    if IS_LINUX:
        try:
            with open("/etc/os-release") as f:
                data = {}
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        data[k] = v.strip('"')
            name = data.get("PRETTY_NAME") or data.get("NAME", "Linux")
            return name
        except Exception:
            return f"Linux {platform.release()}"
    if IS_WIN:
        return f"{platform.system()} {platform.release()} (build {platform.version()})"
    return f"{OS_NAME} {platform.release()}"

def uptime_seconds() -> float | None:
    if IS_LINUX:
        try:
            with open("/proc/uptime") as f:
                return float(f.read().split()[0])
        except Exception:
            return None
    if IS_MAC:
        rc, out, _ = run(["sysctl", "-n", "kern.boottime"])
        if rc == 0:
            m = re.search(r"sec\s*=\s*(\d+)", out)
            if m:
                return max(0.0, time.time() - int(m.group(1)))
    if IS_WIN:
        rc, out, _ = run(["net", "stats", "srv"], timeout=8)
        if rc == 0:
            m = re.search(r"since\s+(.+)$", out, re.IGNORECASE | re.MULTILINE)
            if m:
                try:
                    dt = datetime.strptime(m.group(1).strip(), "%m/%d/%Y %I:%M:%S %p")
                    return max(0.0, (datetime.now() - dt).total_seconds())
                except Exception:
                    pass
    return None

def cpu_info() -> dict:
    info = {"arch": platform.machine(), "cores_logical": os.cpu_count() or 0, "model": platform.processor() or "?"}
    if IS_MAC:
        for key, label in (("machdep.cpu.brand_string", "model"),
                           ("hw.physicalcpu", "cores_physical"),
                           ("hw.logicalcpu", "cores_logical")):
            rc, out, _ = run(["sysctl", "-n", key])
            if rc == 0 and out.strip():
                v = out.strip()
                info[label] = int(v) if v.isdigit() else v
    elif IS_LINUX:
        try:
            with open("/proc/cpuinfo") as f:
                text = f.read()
            m = re.search(r"model name\s*:\s*(.+)", text)
            if m: info["model"] = m.group(1).strip()
            phys = set(re.findall(r"physical id\s*:\s*(\d+)", text))
            info["cores_physical"] = len(phys) or info.get("cores_physical")
        except Exception:
            pass
        try:
            with open("/proc/loadavg") as f:
                la = f.read().split()
            info["loadavg"] = f"{la[0]} {la[1]} {la[2]}"
        except Exception:
            pass
    elif IS_WIN:
        rc, out, _ = run(["wmic", "cpu", "get", "Name,NumberOfCores,NumberOfLogicalProcessors", "/format:list"])
        if rc == 0:
            for line in out.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip(); v = v.strip()
                    if k == "Name": info["model"] = v
                    elif k == "NumberOfCores" and v: info["cores_physical"] = int(v)
                    elif k == "NumberOfLogicalProcessors" and v: info["cores_logical"] = int(v)
    if hasattr(os, "getloadavg") and "loadavg" not in info:
        try:
            la = os.getloadavg()
            info["loadavg"] = f"{la[0]:.2f} {la[1]:.2f} {la[2]:.2f}"
        except Exception:
            pass
    return info

def memory_info() -> dict:
    out_info = {"total": None, "available": None, "used": None}
    if IS_LINUX:
        try:
            with open("/proc/meminfo") as f:
                data = {}
                for line in f:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        m = re.match(r"\s*(\d+)", v)
                        if m: data[k.strip()] = int(m.group(1)) * 1024
            total = data.get("MemTotal")
            avail = data.get("MemAvailable", data.get("MemFree"))
            out_info["total"] = total
            out_info["available"] = avail
            if total is not None and avail is not None:
                out_info["used"] = total - avail
        except Exception:
            pass
    elif IS_MAC:
        rc, out, _ = run(["sysctl", "-n", "hw.memsize"])
        if rc == 0 and out.strip().isdigit():
            out_info["total"] = int(out.strip())
        rc, out, _ = run(["vm_stat"])
        if rc == 0:
            pages = {}
            page_size = 16384 if "Apple" in (platform.processor() or "") else 4096
            m = re.search(r"page size of (\d+) bytes", out)
            if m: page_size = int(m.group(1))
            for line in out.splitlines():
                mm = re.match(r'"?([^":]+)"?:\s+(\d+)', line)
                if mm: pages[mm.group(1).strip().lower()] = int(mm.group(2))
            free = pages.get("pages free", 0)
            spec = pages.get("pages speculative", 0)
            inactive = pages.get("pages inactive", 0)
            avail = (free + spec + inactive) * page_size
            out_info["available"] = avail
            if out_info["total"]:
                out_info["used"] = out_info["total"] - avail
    elif IS_WIN:
        rc, out, _ = run(["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize", "/format:list"])
        if rc == 0:
            d = {}
            for line in out.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    d[k.strip()] = v.strip()
            total_kb = int(d.get("TotalVisibleMemorySize", 0) or 0)
            free_kb  = int(d.get("FreePhysicalMemory", 0) or 0)
            if total_kb:
                out_info["total"] = total_kb * 1024
                out_info["available"] = free_kb * 1024
                out_info["used"] = (total_kb - free_kb) * 1024
    return out_info

def disk_list() -> list:
    disks = []
    if IS_POSIX:
        rc, out, _ = run(["df", "-P", "-k"])
        if rc == 0:
            for line in out.splitlines()[1:]:
                parts = line.split()
                if len(parts) < 6: continue
                try:
                    total = int(parts[1]) * 1024
                    used  = int(parts[2]) * 1024
                    avail = int(parts[3]) * 1024
                except Exception:
                    continue
                disks.append({
                    "device": parts[0], "total": total, "used": used,
                    "available": avail, "mount": parts[-1],
                })
    elif IS_WIN:
        rc, out, _ = run(["wmic", "logicaldisk", "get", "DeviceID,Size,FreeSpace,VolumeName", "/format:list"])
        if rc == 0:
            cur = {}
            for line in out.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    cur[k.strip()] = v.strip()
                elif not line.strip() and cur:
                    try:
                        size = int(cur.get("Size") or 0)
                        free = int(cur.get("FreeSpace") or 0)
                        if size:
                            disks.append({
                                "device": cur.get("DeviceID", "?"),
                                "total": size, "used": size - free, "available": free,
                                "mount": cur.get("DeviceID", "?"),
                            })
                    except Exception:
                        pass
                    cur = {}
    return disks

def battery_info() -> dict | None:
    if IS_MAC:
        rc, out, _ = run(["pmset", "-g", "batt"])
        if rc != 0 or not out.strip(): return None
        m = re.search(r"(\d+)%;\s*([a-z ]+);\s*([\w:]+)", out)
        if m:
            return {"percent": int(m.group(1)), "status": m.group(2).strip(), "time": m.group(3)}
        return {"raw": out.strip()}
    if IS_LINUX:
        base = "/sys/class/power_supply"
        if not os.path.isdir(base): return None
        for name in os.listdir(base):
            p_path = os.path.join(base, name)
            cap_path = os.path.join(p_path, "capacity")
            st_path  = os.path.join(p_path, "status")
            if os.path.isfile(cap_path):
                try:
                    with open(cap_path) as f: pct = int(f.read().strip())
                    st = ""
                    if os.path.isfile(st_path):
                        with open(st_path) as f: st = f.read().strip()
                    return {"percent": pct, "status": st.lower()}
                except Exception:
                    continue
        return None
    if IS_WIN:
        rc, out, _ = run(["wmic", "path", "Win32_Battery", "get", "EstimatedChargeRemaining,BatteryStatus", "/format:list"])
        if rc == 0 and out.strip():
            d = {}
            for line in out.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1); d[k.strip()] = v.strip()
            pct = d.get("EstimatedChargeRemaining")
            if pct and pct.isdigit():
                st_map = {"1":"discharging", "2":"ac", "3":"fully charged", "4":"low"}
                return {"percent": int(pct), "status": st_map.get(d.get("BatteryStatus",""), d.get("BatteryStatus",""))}
        return None
    return None

def temp_info() -> str | None:
    if IS_LINUX:
        base = "/sys/class/thermal"
        if os.path.isdir(base):
            temps = []
            for name in sorted(os.listdir(base)):
                if name.startswith("thermal_zone"):
                    tp = os.path.join(base, name, "temp")
                    if os.path.isfile(tp):
                        try:
                            with open(tp) as f:
                                t = int(f.read().strip()) / 1000.0
                            temps.append(f"{name}: {t:.1f}°C")
                        except Exception:
                            pass
            if temps:
                return " · ".join(temps)
    if IS_MAC:
        # powermetrics requires sudo; skip. Provide a clean message.
        return None
    return None

# ── COMMANDS: SYSTEM ──────────────────────────────────────────────────────

def cmd_sysinfo(_args):
    section("SYSTEM INFO")
    kv("Host",      socket.gethostname())
    kv("OS",        os_pretty())
    kv("Kernel",    platform.release())
    kv("Arch",      platform.machine())
    kv("Python",    platform.python_version())
    ut = uptime_seconds()
    if ut is not None:
        kv("Uptime", human_duration(ut))
    cpu = cpu_info()
    kv("CPU",       cpu.get("model", "?"))
    kv("Cores",     f"{cpu.get('cores_logical','?')} logical · {cpu.get('cores_physical','?')} physical")
    if "loadavg" in cpu:
        kv("Load avg", cpu["loadavg"])
    mem = memory_info()
    if mem["total"]:
        pct = (mem["used"] / mem["total"] * 100) if mem["used"] else 0
        kv("Memory",  f"{human_bytes(mem['used'])} / {human_bytes(mem['total'])}  ({pct:.0f}% used)")
    disks = disk_list()
    if disks:
        print()
        pc("  Disks")
        for d in disks[:8]:
            pct = (d["used"] / d["total"] * 100) if d["total"] else 0
            pb(f"    {d['mount']:<20} {human_bytes(d['used'])} / {human_bytes(d['total'])}  ({pct:.0f}% used)  {d['device']}")
    bat = battery_info()
    if bat:
        print()
        if "percent" in bat:
            kv("Battery", f"{bat['percent']}%  ({bat.get('status','?')})")
        else:
            kv("Battery", bat.get("raw", "?"))

def cmd_os(_args):
    pb(f"  {os_pretty()}")

def cmd_hostname(_args):
    pb(f"  {socket.gethostname()}")

def cmd_uptime(_args):
    ut = uptime_seconds()
    if ut is None:
        pw("  uptime unavailable on this platform")
        return
    pb(f"  {human_duration(ut)}  ({int(ut)}s)")

def cmd_cpu(_args):
    section("CPU")
    c = cpu_info()
    kv("Model",    c.get("model", "?"))
    kv("Arch",     c.get("arch", "?"))
    kv("Logical",  c.get("cores_logical", "?"))
    kv("Physical", c.get("cores_physical", "?"))
    if "loadavg" in c:
        kv("Loadavg", c["loadavg"])

def cmd_memory(_args):
    section("MEMORY")
    m = memory_info()
    if not m["total"]:
        pw("  memory stats unavailable on this platform")
        return
    total = m["total"]; used = m["used"] or 0; avail = m["available"] or (total - used)
    pct = used / total * 100 if total else 0
    kv("Total",     human_bytes(total))
    kv("Used",      f"{human_bytes(used)}  ({pct:.0f}%)")
    kv("Available", human_bytes(avail))
    pd("  " + _progress_bar(used, total, 40))

def cmd_disk(_args):
    section("DISKS")
    disks = disk_list()
    if not disks:
        pw("  no disks reported"); return
    pc(f"  {'MOUNT':<24}{'USED':>12}{'TOTAL':>12}{'FREE':>12}  {'DEVICE'}")
    for d in disks:
        pb(f"  {d['mount'][:22]:<24}{human_bytes(d['used']):>12}{human_bytes(d['total']):>12}{human_bytes(d['available']):>12}  {d['device']}")

def cmd_battery(_args):
    bat = battery_info()
    if not bat:
        pw("  no battery detected (or unavailable)"); return
    section("BATTERY")
    if "percent" in bat:
        kv("Charge", f"{bat['percent']}%")
        kv("Status", bat.get("status", "?"))
        if "time" in bat: kv("Time",   bat["time"])
    else:
        pb("  " + bat.get("raw", ""))

def cmd_temp(_args):
    t = temp_info()
    if not t:
        pw("  temperature sensors not available on this platform without elevated privileges"); return
    pb("  " + t)

def cmd_env(args):
    section("ENVIRONMENT")
    keys = sorted(os.environ.keys())
    if args:
        keys = [k for k in keys if args[0].lower() in k.lower()]
    # Redact obvious secrets.
    redact_pat = re.compile(r"(TOKEN|KEY|SECRET|PASS|PWD|CREDENTIAL|API)", re.I)
    for k in keys:
        v = os.environ[k]
        if redact_pat.search(k):
            v = "[redacted]"
        if len(v) > 120:
            v = v[:117] + "…"
        pb(f"  {k:<28} {v}")

def cmd_users(_args):
    section("USERS")
    if IS_POSIX and have("who"):
        rc, out, _ = run(["who"])
        if rc == 0 and out.strip():
            for line in out.splitlines(): pb("  " + line)
            return
    if IS_WIN:
        rc, out, _ = run(["query", "user"])
        if rc == 0 and out.strip():
            for line in out.splitlines(): pb("  " + line)
            return
    pb(f"  current: {STATE['user']}")

def cmd_sessions(_args):
    cmd_users(_args)

# ── COMMANDS: PROCESSES ───────────────────────────────────────────────────

def _list_processes(limit: int = 0) -> list:
    procs = []
    if IS_POSIX:
        rc, out, _ = run(["ps", "-axo", "pid,ppid,user,%cpu,%mem,comm"], timeout=6)
        if rc == 0:
            lines = out.splitlines()[1:]
            for line in lines:
                parts = line.split(None, 5)
                if len(parts) < 6: continue
                try:
                    procs.append({
                        "pid": int(parts[0]), "ppid": int(parts[1]),
                        "user": parts[2], "cpu": float(parts[3]),
                        "mem": float(parts[4]), "name": parts[5],
                    })
                except ValueError:
                    continue
    elif IS_WIN:
        rc, out, _ = run(["tasklist", "/FO", "CSV", "/NH"], timeout=8)
        if rc == 0:
            import csv, io
            for row in csv.reader(io.StringIO(out)):
                if len(row) < 5: continue
                try:
                    pid = int(row[1])
                except ValueError:
                    continue
                mem_kb = re.sub(r"[^\d]", "", row[4]) or "0"
                procs.append({
                    "pid": pid, "ppid": 0, "user": "",
                    "cpu": 0.0, "mem": float(mem_kb) / 1024.0,
                    "name": row[0],
                })
    procs.sort(key=lambda x: x["cpu"], reverse=True)
    if limit > 0:
        return procs[:limit]
    return procs

def cmd_processes(args):
    n = 25
    if args and args[0].isdigit():
        n = int(args[0])
    procs = _list_processes()
    section(f"PROCESSES  (top {n} by CPU · {len(procs)} total)")
    pc(f"  {'PID':>7}  {'USER':<12}  {'CPU%':>6}  {'MEM%':>6}  NAME")
    for pr in procs[:n]:
        pb(f"  {pr['pid']:>7}  {pr['user'][:12]:<12}  {pr['cpu']:>5.1f}  {pr['mem']:>5.1f}  {pr['name']}")

def cmd_top(args):
    cmd_processes(args or ["15"])

def cmd_psfind(args):
    if not args:
        pe("  usage:  psfind <name>"); return
    needle = args[0].lower()
    procs = _list_processes()
    hits = [x for x in procs if needle in x["name"].lower()]
    if not hits:
        pw(f"  no processes match '{needle}'"); return
    section(f"PSFIND · {needle}  ({len(hits)} match)")
    pc(f"  {'PID':>7}  {'USER':<12}  {'CPU%':>6}  {'MEM%':>6}  NAME")
    for pr in hits:
        pb(f"  {pr['pid']:>7}  {pr['user'][:12]:<12}  {pr['cpu']:>5.1f}  {pr['mem']:>5.1f}  {pr['name']}")

def cmd_process(args):
    if not args:
        pe("  usage:  process <pid>"); return
    try:
        pid = int(args[0])
    except ValueError:
        pe("  pid must be numeric"); return
    procs = _list_processes()
    match = next((x for x in procs if x["pid"] == pid), None)
    if not match:
        pw(f"  no process with pid {pid}"); return
    section(f"PROCESS {pid}")
    for k in ("pid", "ppid", "user", "cpu", "mem", "name"):
        kv(k.upper(), match[k])

def cmd_startup_items(_args):
    section("STARTUP / LOGIN ITEMS")
    shown = False
    if IS_MAC:
        paths = [
            "/Library/LaunchDaemons",
            "/Library/LaunchAgents",
            os.path.expanduser("~/Library/LaunchAgents"),
        ]
        for d in paths:
            if os.path.isdir(d):
                pc(f"  {d}")
                try:
                    for name in sorted(os.listdir(d)):
                        if name.endswith(".plist"):
                            pb(f"    {name}")
                            shown = True
                except Exception:
                    pass
    elif IS_LINUX:
        paths = [
            "/etc/systemd/system",
            "/etc/init.d",
            os.path.expanduser("~/.config/autostart"),
        ]
        for d in paths:
            if os.path.isdir(d):
                pc(f"  {d}")
                try:
                    for name in sorted(os.listdir(d)):
                        pb(f"    {name}")
                        shown = True
                except Exception:
                    pass
    elif IS_WIN:
        rc, out, _ = run(["wmic", "startup", "get", "Caption,Command,Location", "/format:list"])
        if rc == 0:
            for line in out.splitlines():
                if line.strip(): pb("  " + line.strip()); shown = True
    if not shown:
        pd("  no startup locations readable")

def cmd_services(_args):
    section("SERVICES")
    if IS_MAC and have("launchctl"):
        rc, out, _ = run(["launchctl", "list"], timeout=8)
        if rc == 0:
            lines = out.splitlines()
            pc(f"  {lines[0] if lines else ''}")
            for line in lines[1:80]:
                pb("  " + line)
            if len(lines) > 80:
                pd(f"  … ({len(lines)-80} more)")
            return
    if IS_LINUX and have("systemctl"):
        rc, out, _ = run(["systemctl", "list-units", "--type=service", "--no-pager", "--no-legend"], timeout=8)
        if rc == 0 and out.strip():
            for line in out.splitlines()[:60]:
                pb("  " + line)
            return
    if IS_WIN:
        rc, out, _ = run(["sc", "query", "state=", "all"], timeout=8)
        if rc == 0:
            for line in out.splitlines()[:120]:
                pb("  " + line)
            return
    pw("  no service manager accessible")

def cmd_scheduled(_args):
    section("SCHEDULED / CRON")
    if IS_POSIX:
        rc, out, _ = run(["crontab", "-l"])
        if rc == 0 and out.strip():
            pc("  user crontab:")
            for line in out.splitlines():
                if line.strip() and not line.strip().startswith("#"):
                    pb("  " + line)
        else:
            pd("  no user crontab")
        for d in ("/etc/crontab", "/etc/cron.d", "/etc/cron.daily", "/etc/cron.hourly"):
            if os.path.exists(d):
                pc(f"\n  {d}")
                if os.path.isdir(d):
                    try:
                        for n in sorted(os.listdir(d)): pb(f"    {n}")
                    except Exception: pass
                else:
                    try:
                        with open(d) as f:
                            for line in f:
                                if line.strip() and not line.strip().startswith("#"):
                                    pb("  " + line.rstrip())
                    except Exception: pass
    elif IS_WIN:
        rc, out, _ = run(["schtasks", "/query", "/fo", "LIST"], timeout=8)
        if rc == 0:
            for line in out.splitlines()[:200]:
                pb("  " + line)

# ── COMMANDS: NETWORK ─────────────────────────────────────────────────────

def _local_ip() -> str | None:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(0.5)
        s.connect(("1.1.1.1", 80))
        return s.getsockname()[0]
    except Exception:
        return None
    finally:
        try: s.close()
        except: pass

def _interfaces_posix():
    rc, out, _ = run(["ifconfig" if IS_MAC else "ip", "-a" if IS_LINUX else "a"]) \
        if IS_LINUX else run(["ifconfig"])
    # Try both regardless
    if rc != 0:
        rc, out, _ = run(["ip", "-a"])
    return out

def cmd_interfaces(_args):
    section("NETWORK INTERFACES")
    if IS_POSIX:
        bin_name = "ifconfig" if IS_MAC else ("ip" if have("ip") else "ifconfig")
        if bin_name == "ip":
            rc, out, _ = run(["ip", "addr"])
        else:
            rc, out, _ = run([bin_name])
        if rc == 0 and out.strip():
            for line in out.splitlines(): pb("  " + line)
            return
    elif IS_WIN:
        rc, out, _ = run(["ipconfig", "/all"], timeout=8)
        if rc == 0:
            for line in out.splitlines(): pb("  " + line)
            return
    pw("  interface data unavailable")

def cmd_netinfo(_args):
    section("NETWORK")
    kv("Hostname", socket.gethostname())
    lip = _local_ip()
    kv("Local IP", lip or "unknown")
    try:
        fqdn = socket.getfqdn()
        kv("FQDN", fqdn)
    except Exception:
        pass
    # DNS
    pc("\n  DNS servers")
    servers = _dns_servers()
    for s in servers or ["(unknown)"]:
        pb(f"    {s}")
    # gateway (best-effort)
    gw = _default_gateway()
    if gw:
        kv("Gateway", gw)

def _dns_servers() -> list:
    servers = []
    if IS_POSIX:
        try:
            with open("/etc/resolv.conf") as f:
                for line in f:
                    if line.startswith("nameserver"):
                        parts = line.split()
                        if len(parts) >= 2: servers.append(parts[1])
        except Exception:
            pass
        if IS_MAC and not servers:
            rc, out, _ = run(["scutil", "--dns"])
            if rc == 0:
                servers = list(dict.fromkeys(re.findall(r"nameserver\[\d+\]\s*:\s*([\d.:a-f]+)", out)))
    elif IS_WIN:
        rc, out, _ = run(["ipconfig", "/all"], timeout=8)
        if rc == 0:
            for m in re.finditer(r"DNS Servers[^:]*:\s*([\d.:a-f]+)", out):
                servers.append(m.group(1))
    return servers

def _default_gateway() -> str | None:
    if IS_MAC:
        rc, out, _ = run(["route", "-n", "get", "default"])
        if rc == 0:
            m = re.search(r"gateway:\s*(\S+)", out)
            if m: return m.group(1)
    elif IS_LINUX:
        if have("ip"):
            rc, out, _ = run(["ip", "route", "show", "default"])
            if rc == 0:
                m = re.search(r"default via (\S+)", out)
                if m: return m.group(1)
    elif IS_WIN:
        rc, out, _ = run(["ipconfig"], timeout=5)
        if rc == 0:
            m = re.search(r"Default Gateway[^:]*:\s*([\d.]+)", out)
            if m: return m.group(1)
    return None

def cmd_route(_args):
    section("ROUTING TABLE")
    if IS_MAC or IS_LINUX:
        if have("ip"):
            rc, out, _ = run(["ip", "route"])
        else:
            rc, out, _ = run(["netstat", "-rn"])
    else:
        rc, out, _ = run(["route", "print"], timeout=8)
    if rc == 0:
        for line in out.splitlines()[:80]: pb("  " + line)
    else:
        pw("  route table unavailable")

def cmd_dns(_args):
    section("DNS")
    for s in _dns_servers() or ["(none configured)"]:
        pb("  " + s)

def cmd_publicip(_args):
    # Opt-in outbound request to a well-known IP-echo service. Read-only.
    import urllib.request
    pd("  fetching public IP (opt-in HTTPS request to api.ipify.org)…")
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=text", timeout=4) as r:
            ip = r.read().decode("ascii").strip()
        pb("  " + ip)
    except Exception as ex:
        pe(f"  failed: {ex}")
        pd("  (offline? set http_proxy env var if behind a proxy)")

def cmd_localip(_args):
    lip = _local_ip()
    if lip: pb("  " + lip)
    else:   pw("  could not determine local IP")

def cmd_ports(_args):
    section("ALL SOCKETS")
    _print_sockets(all_sockets=True)

def cmd_listening(_args):
    section("LISTENING PORTS")
    _print_sockets(all_sockets=False)

def _print_sockets(all_sockets=False):
    lines = _socket_table(all_sockets)
    if not lines:
        pw("  no socket data available"); return
    pc(f"  {'PROTO':<6}{'LOCAL':<30}{'REMOTE':<30}{'STATE':<14}PID")
    for row in lines[:200]:
        pb(f"  {row['proto']:<6}{row['local'][:28]:<30}{row['remote'][:28]:<30}{row['state'][:12]:<14}{row['pid']}")
    if len(lines) > 200:
        pd(f"  … ({len(lines)-200} more)")

def _socket_table(all_sockets=False) -> list:
    rows = []
    if IS_MAC:
        rc, out, _ = run(["lsof", "-i", "-P", "-n"], timeout=8)
        if rc == 0:
            for line in out.splitlines()[1:]:
                parts = line.split()
                if len(parts) < 9: continue
                name = parts[8]; state = ""
                if len(parts) >= 10: state = parts[9].strip("()")
                proto = parts[7].lower()
                # NAME like 127.0.0.1:80 or 1.2.3.4:5->6.7.8.9:80
                local = name; remote = ""
                if "->" in name:
                    local, remote = name.split("->", 1)
                if not all_sockets and "LISTEN" not in state.upper() and not remote:
                    # Skip non-listening if listening mode
                    if not (proto == "udp" and not remote):
                        continue
                if not all_sockets and "LISTEN" not in state.upper():
                    continue
                rows.append({
                    "proto": proto, "local": local, "remote": remote,
                    "state": state or ("LISTEN" if proto == "tcp" else ""),
                    "pid": parts[1],
                })
    elif IS_LINUX:
        if have("ss"):
            rc, out, _ = run(["ss", "-tunap" if all_sockets else "-tunlp"], timeout=6)
        else:
            rc, out, _ = run(["netstat", "-tunap" if all_sockets else "-tunlp"], timeout=6)
        if rc == 0:
            for line in out.splitlines()[1:]:
                parts = line.split()
                if len(parts) < 5: continue
                proto = parts[0].lower()
                state = parts[1] if proto.startswith("tcp") else ""
                # ss: Netid State Recv-Q Send-Q Local Peer
                if have("ss"):
                    if len(parts) >= 6:
                        local = parts[4]; remote = parts[5]
                    else:
                        continue
                    pid = ""
                    m = re.search(r"pid=(\d+)", line)
                    if m: pid = m.group(1)
                else:
                    local  = parts[3] if len(parts) > 3 else ""
                    remote = parts[4] if len(parts) > 4 else ""
                    pid = ""
                    m = re.search(r"(\d+)/", line)
                    if m: pid = m.group(1)
                rows.append({"proto": proto, "local": local, "remote": remote, "state": state, "pid": pid})
    elif IS_WIN:
        rc, out, _ = run(["netstat", "-ano" if all_sockets else "-ano"], timeout=6)
        if rc == 0:
            for line in out.splitlines():
                parts = line.split()
                if len(parts) < 4: continue
                if parts[0].lower() not in ("tcp", "udp"): continue
                proto = parts[0].lower()
                local = parts[1]; remote = parts[2]
                if proto == "tcp":
                    state = parts[3]; pid = parts[4] if len(parts) > 4 else ""
                else:
                    state = ""; pid = parts[3] if len(parts) > 3 else ""
                if not all_sockets and state.upper() != "LISTENING" and proto == "tcp":
                    continue
                rows.append({"proto": proto, "local": local, "remote": remote, "state": state, "pid": pid})
    return rows

def cmd_wifi_info(_args):
    section("WI-FI")
    if IS_MAC:
        airport = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
        if os.path.exists(airport):
            rc, out, _ = run([airport, "-I"])
            if rc == 0 and out.strip():
                for line in out.splitlines(): pb("  " + line.strip())
                return
    if IS_LINUX:
        for cmd in (["iwconfig"], ["nmcli", "-f", "active,ssid,signal", "dev", "wifi"]):
            rc, out, _ = run(cmd)
            if rc == 0 and out.strip():
                for line in out.splitlines(): pb("  " + line)
                return
    if IS_WIN:
        rc, out, _ = run(["netsh", "wlan", "show", "interfaces"], timeout=6)
        if rc == 0 and out.strip():
            for line in out.splitlines(): pb("  " + line.rstrip())
            return
    pw("  Wi-Fi info unavailable on this system")

def cmd_ping(args):
    if not args:
        pe("  usage:  ping <host> [count]"); return
    host = args[0]
    count = "4"
    if len(args) > 1 and args[1].isdigit():
        count = args[1]
    flag = "-c" if IS_POSIX else "-n"
    if not re.match(r"^[a-zA-Z0-9._:\-]+$", host):
        pe("  invalid hostname"); return
    section(f"PING {host}")
    rc, out, err = run(["ping", flag, count, host], timeout=int(count) * 2 + 5)
    out = out or err
    for line in out.splitlines(): pb("  " + line)

def cmd_traceroute_lite(args):
    if not args:
        pe("  usage:  traceroute-lite <host>"); return
    host = args[0]
    if not re.match(r"^[a-zA-Z0-9._:\-]+$", host):
        pe("  invalid hostname"); return
    section(f"TRACEROUTE-LITE {host}  (best effort, up to 15 hops)")
    bin_name = "traceroute" if IS_POSIX else "tracert"
    if not have(bin_name):
        pw(f"  {bin_name} not available on this system"); return
    args_cmd = [bin_name, "-m", "15", host] if IS_POSIX else [bin_name, "-h", "15", host]
    rc, out, _ = run(args_cmd, timeout=30)
    for line in out.splitlines(): pb("  " + line)

def cmd_localhost_scan(_args):
    """Probe 127.0.0.1 on common ports. READ-ONLY — localhost only."""
    section("LOCALHOST PORT PROBE  (127.0.0.1)")
    common = [22, 53, 80, 88, 111, 139, 143, 389, 443, 445, 465, 500, 515,
              548, 587, 631, 636, 873, 993, 995, 1080, 1433, 1521, 1723,
              2049, 2375, 2376, 3000, 3128, 3306, 3389, 3690, 4000, 4333,
              4444, 5000, 5432, 5555, 5672, 5900, 5984, 6379, 7000, 8000,
              8008, 8080, 8081, 8086, 8443, 8888, 9000, 9092, 9200, 9300,
              11211, 27017, 50070]
    open_ports = []
    for port in common:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.12)
        try:
            r = s.connect_ex(("127.0.0.1", port))
            if r == 0:
                open_ports.append(port)
        except Exception:
            pass
        finally:
            try: s.close()
            except: pass
    if not open_ports:
        ph("  no common ports open on loopback"); return
    pc(f"  {len(open_ports)} open port(s) on 127.0.0.1:")
    svc = {22:"ssh",53:"dns",80:"http",443:"https",3306:"mysql",3389:"rdp",
           5432:"postgres",6379:"redis",8080:"http-alt",27017:"mongo"}
    for pport in open_ports:
        pb(f"    {pport:>5}/tcp  {svc.get(pport,'unknown')}")

def cmd_firewall(_args):
    section("FIREWALL")
    if IS_MAC:
        rc, out, _ = run(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"])
        if rc == 0: pb("  " + out.strip())
        rc, out, _ = run(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getstealthmode"])
        if rc == 0: pb("  " + out.strip())
    elif IS_LINUX:
        for cmd in (["ufw", "status"], ["firewall-cmd", "--state"], ["iptables", "-L", "-n"]):
            if have(cmd[0]):
                rc, out, _ = run(cmd, timeout=6)
                if rc == 0 and out.strip():
                    for line in out.splitlines()[:40]: pb("  " + line)
                    return
        pw("  no firewall tool accessible")
    elif IS_WIN:
        rc, out, _ = run(["netsh", "advfirewall", "show", "allprofiles", "state"], timeout=6)
        if rc == 0:
            for line in out.splitlines(): pb("  " + line.rstrip())

# ── COMMANDS: FILESYSTEM ──────────────────────────────────────────────────

def _safe_abspath(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))

def cmd_ls(args):
    path = _safe_abspath(args[0]) if args else os.getcwd()
    if not os.path.exists(path):
        pe(f"  no such path: {path}"); return
    if os.path.isfile(path):
        cmd_fileinfo([path]); return
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        pe(f"  permission denied: {path}"); return
    section(f"LS · {path}")
    for name in entries:
        full = os.path.join(path, name)
        try:
            st = os.lstat(full)
            kind = "d" if stat.S_ISDIR(st.st_mode) else ("l" if stat.S_ISLNK(st.st_mode) else "f")
            size = "-" if kind == "d" else human_bytes(st.st_size)
            mtime = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
            mode = stat.filemode(st.st_mode) if IS_POSIX else ""
            pb(f"  {kind} {mode:<10} {size:>10}  {mtime}  {name}")
        except OSError:
            pd(f"  ?  {name}  (stat failed)")

def cmd_tree(args):
    path = _safe_abspath(args[0]) if args else os.getcwd()
    max_depth = 3
    if len(args) > 1 and args[1].isdigit():
        max_depth = int(args[1])
    if not os.path.isdir(path):
        pe(f"  not a directory: {path}"); return
    section(f"TREE · {path}  (depth {max_depth})")
    count = [0]
    LIMIT = 500
    def walk(d, prefix="", depth=0):
        if count[0] >= LIMIT: return
        if depth >= max_depth: return
        try:
            entries = sorted(os.listdir(d))
        except Exception:
            return
        for i, name in enumerate(entries):
            if count[0] >= LIMIT:
                pd(f"  … (truncated at {LIMIT} entries)"); return
            full = os.path.join(d, name)
            last = (i == len(entries) - 1)
            branch = "└── " if last else "├── "
            pb(f"  {prefix}{branch}{name}")
            count[0] += 1
            if os.path.isdir(full) and not os.path.islink(full):
                ext = "    " if last else "│   "
                walk(full, prefix + ext, depth + 1)
    walk(path)

def cmd_du(args):
    path = _safe_abspath(args[0]) if args else os.getcwd()
    if not os.path.exists(path):
        pe(f"  no such path: {path}"); return
    section(f"DU · {path}")
    if os.path.isfile(path):
        pb(f"  {human_bytes(os.path.getsize(path))}  {path}"); return
    sizes = []
    for entry in sorted(os.listdir(path)):
        full = os.path.join(path, entry)
        try:
            total = _dir_size(full)
        except Exception:
            total = 0
        sizes.append((total, entry))
    sizes.sort(reverse=True)
    grand = sum(s for s, _ in sizes)
    for size, name in sizes[:30]:
        pb(f"  {human_bytes(size):>10}  {name}")
    rule(60)
    ph(f"  {human_bytes(grand):>10}  TOTAL  ({len(sizes)} entries)")

def _dir_size(path, max_entries=50000) -> int:
    total = 0
    count = 0
    if os.path.isfile(path) or os.path.islink(path):
        try: return os.path.getsize(path)
        except: return 0
    for root, dirs, files in os.walk(path, onerror=lambda e: None):
        for f in files:
            fp = os.path.join(root, f)
            try:
                if not os.path.islink(fp):
                    total += os.path.getsize(fp)
            except OSError:
                pass
            count += 1
            if count > max_entries: return total
    return total

def cmd_fileinfo(args):
    if not args:
        pe("  usage:  fileinfo <path>"); return
    path = _safe_abspath(args[0])
    if not os.path.exists(path):
        pe(f"  no such path: {path}"); return
    st = os.stat(path)
    section(f"FILEINFO · {path}")
    kv("Type",     "dir" if os.path.isdir(path) else "symlink" if os.path.islink(path) else "file")
    kv("Size",     human_bytes(st.st_size) if os.path.isfile(path) else "—")
    kv("Mode",     stat.filemode(st.st_mode))
    kv("Owner",    f"{st.st_uid}" + (f" ({_uid_name(st.st_uid)})" if IS_POSIX else ""))
    kv("Group",    f"{st.st_gid}")
    kv("Created",  datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d %H:%M:%S"))
    kv("Modified", datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
    kv("Accessed", datetime.fromtimestamp(st.st_atime).strftime("%Y-%m-%d %H:%M:%S"))
    if os.path.isfile(path) and st.st_size < 50 * 1024 * 1024:
        try:
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            kv("SHA-256", h.hexdigest())
        except Exception:
            pass

def _uid_name(uid):
    try:
        import pwd
        return pwd.getpwuid(uid).pw_name
    except Exception:
        return str(uid)

def cmd_perms(args):
    if not args:
        pe("  usage:  perms <path>"); return
    path = _safe_abspath(args[0])
    if not os.path.exists(path):
        pe(f"  no such path: {path}"); return
    st = os.stat(path)
    pb(f"  {stat.filemode(st.st_mode)}  {oct(st.st_mode & 0o7777)}  {path}")

def cmd_recent_files(args):
    path = _safe_abspath(args[0]) if args else HOME
    days = 7
    if len(args) > 1 and args[1].isdigit():
        days = int(args[1])
    cutoff = time.time() - days * 86400
    section(f"RECENT FILES · {path}  (last {days} days)")
    count = 0
    for root, dirs, files in os.walk(path, onerror=lambda e: None):
        # prune deep/hidden
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "__pycache__")]
        for f in files:
            fp = os.path.join(root, f)
            try:
                mt = os.path.getmtime(fp)
            except OSError:
                continue
            if mt >= cutoff:
                pb(f"  {datetime.fromtimestamp(mt).strftime('%Y-%m-%d %H:%M')}  {fp}")
                count += 1
                if count >= 60:
                    pd("  … (truncated)"); return

def cmd_large_files(args):
    path = _safe_abspath(args[0]) if args else HOME
    n = 15
    if len(args) > 1 and args[1].isdigit():
        n = int(args[1])
    section(f"LARGE FILES · {path}  (top {n})")
    heap = []
    scanned = 0
    for root, dirs, files in os.walk(path, onerror=lambda e: None):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "venv", "__pycache__")]
        for f in files:
            fp = os.path.join(root, f)
            try:
                size = os.path.getsize(fp)
            except OSError:
                continue
            heap.append((size, fp))
            scanned += 1
            if scanned > 150000:
                pd("  … scan truncated"); break
        if scanned > 150000: break
    heap.sort(reverse=True)
    for size, fp in heap[:n]:
        pb(f"  {human_bytes(size):>10}  {fp}")

def cmd_search_file(args):
    if len(args) < 1:
        pe("  usage:  search-file <pattern> [path]"); return
    pattern = args[0].lower()
    root_path = _safe_abspath(args[1]) if len(args) > 1 else os.getcwd()
    section(f"SEARCH-FILE · '{pattern}' in {root_path}")
    count = 0
    for root, dirs, files in os.walk(root_path, onerror=lambda e: None):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv")]
        for f in files:
            if pattern in f.lower():
                pb(f"  {os.path.join(root, f)}")
                count += 1
                if count >= 100:
                    pd("  … (truncated at 100)"); return
    if count == 0:
        pw("  no matches")

def cmd_search_text(args):
    if len(args) < 1:
        pe("  usage:  search-text <text> [path]"); return
    needle = args[0]
    root_path = _safe_abspath(args[1]) if len(args) > 1 else os.getcwd()
    section(f"SEARCH-TEXT · '{needle}' in {root_path}")
    TEXT_EXTS = {".txt", ".md", ".py", ".js", ".ts", ".tsx", ".jsx", ".json",
                 ".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf", ".sh",
                 ".bash", ".zsh", ".c", ".h", ".cpp", ".hpp", ".java", ".rs",
                 ".go", ".rb", ".php", ".html", ".css", ".scss", ".sql",
                 ".xml", ".csv", ".log"}
    count = 0
    pat = needle.lower()
    for root, dirs, files in os.walk(root_path, onerror=lambda e: None):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", "venv", "dist", "build")]
        for f in files:
            if os.path.splitext(f)[1].lower() not in TEXT_EXTS: continue
            fp = os.path.join(root, f)
            try:
                size = os.path.getsize(fp)
            except OSError:
                continue
            if size > 5 * 1024 * 1024: continue
            try:
                with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, 1):
                        if pat in line.lower():
                            pb(f"  {fp}:{i}: {line.rstrip()[:140]}")
                            count += 1
                            if count >= 80:
                                pd("  … (truncated at 80)"); return
            except Exception:
                continue
    if count == 0: pw("  no matches")

# ── COMMANDS: INTEGRITY / DEFENSIVE SECURITY ──────────────────────────────

def cmd_hash(args):
    if not args:
        pe("  usage:  hash <file> [algo]"); return
    path = _safe_abspath(args[0])
    algo = (args[1] if len(args) > 1 else "sha256").lower()
    if not os.path.isfile(path):
        pe(f"  not a file: {path}"); return
    if algo not in ("md5", "sha1", "sha256", "sha512"):
        pe("  algo must be: md5 | sha1 | sha256 | sha512"); return
    h = hashlib.new(algo)
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
    except Exception as ex:
        pe(f"  read failed: {ex}"); return
    pb(f"  {algo}  {h.hexdigest()}  {path}")

def cmd_integrity(args):
    if not args:
        pe("  usage:  integrity <path>"); return
    path = _safe_abspath(args[0])
    section(f"INTEGRITY · {path}")
    if os.path.isfile(path):
        cmd_hash([path]); return
    if not os.path.isdir(path):
        pe(f"  no such path: {path}"); return
    count = 0
    for root, dirs, files in os.walk(path, onerror=lambda e: None):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            fp = os.path.join(root, f)
            try:
                h = hashlib.sha256()
                with open(fp, "rb") as fh:
                    for chunk in iter(lambda: fh.read(1 << 20), b""):
                        h.update(chunk)
                pb(f"  {h.hexdigest()}  {os.path.relpath(fp, path)}")
                count += 1
                if count >= 500:
                    pd("  … (truncated at 500)"); return
            except Exception:
                continue

def cmd_weak_perms(_args):
    section("WEAK PERMISSIONS SCAN  (home directory, world-writable)")
    if not IS_POSIX:
        pw("  POSIX-only check"); return
    count = 0
    for root, dirs, files in os.walk(HOME, onerror=lambda e: None):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in files + dirs:
            fp = os.path.join(root, name)
            try:
                st = os.lstat(fp)
            except OSError:
                continue
            if st.st_mode & stat.S_IWOTH:
                pw(f"  WORLD-WRITABLE  {stat.filemode(st.st_mode)}  {fp}")
                count += 1
                if count >= 50:
                    pd("  … (truncated at 50)"); return
    if count == 0: ph("  ✓ no world-writable entries in home")

def cmd_world_writable(_args):
    cmd_weak_perms(_args)

def cmd_suspicious_startup(_args):
    section("SUSPICIOUS STARTUP CHECK  (best-effort)")
    flagged = 0
    if IS_MAC:
        paths = ["/Library/LaunchDaemons", "/Library/LaunchAgents",
                 os.path.expanduser("~/Library/LaunchAgents")]
        for d in paths:
            if not os.path.isdir(d): continue
            for name in os.listdir(d):
                if not name.endswith(".plist"): continue
                full = os.path.join(d, name)
                try:
                    with open(full, "rb") as f:
                        data = f.read(8192).decode("utf-8", errors="ignore")
                except Exception:
                    continue
                # Flag very basic patterns.
                if re.search(r"(curl\s+http|wget\s+http|/tmp/|nc\s+-e|bash\s+-i|base64\s+-d)", data, re.I):
                    pw(f"  ⚠  {full}")
                    m = re.search(r"<string>([^<]*(curl|wget|/tmp/|base64|nc )[^<]*)</string>", data, re.I)
                    if m: pd(f"     {m.group(1)[:140]}")
                    flagged += 1
    elif IS_LINUX:
        for d in ("/etc/systemd/system", os.path.expanduser("~/.config/autostart")):
            if not os.path.isdir(d): continue
            for name in os.listdir(d):
                full = os.path.join(d, name)
                try:
                    with open(full, "r", errors="ignore") as f: data = f.read(8192)
                except Exception: continue
                if re.search(r"(curl\s+http|wget\s+http|/tmp/|nc\s+-e|bash\s+-i|base64\s+-d)", data, re.I):
                    pw(f"  ⚠  {full}"); flagged += 1
    if flagged == 0:
        ph("  ✓ nothing obviously suspicious in checked startup locations")

def cmd_ssh_check(_args):
    section("SSH CLIENT / SERVER CHECK")
    ssh_dir = os.path.expanduser("~/.ssh")
    if os.path.isdir(ssh_dir):
        pb(f"  ~/.ssh exists ({ssh_dir})")
        try:
            st = os.stat(ssh_dir)
            mode = stat.S_IMODE(st.st_mode)
            if IS_POSIX and mode & 0o077:
                pw(f"  ⚠  ~/.ssh permissions are {oct(mode)} — should be 0700")
            else:
                ph(f"  ✓ permissions {oct(mode)}")
        except Exception: pass
        for fname in ("authorized_keys", "known_hosts", "config", "id_rsa", "id_ed25519"):
            fp = os.path.join(ssh_dir, fname)
            if os.path.exists(fp):
                try:
                    st = os.stat(fp); mode = stat.S_IMODE(st.st_mode)
                    warn = ""
                    if IS_POSIX and fname.startswith("id_") and mode & 0o077:
                        warn = "   ⚠ too permissive (expected 0600)"
                    pb(f"    {fname:<20}  {oct(mode)}  {human_bytes(st.st_size)}{warn}")
                except Exception: pass
    else:
        pd("  ~/.ssh not present")
    # sshd listening?
    rows = _socket_table(all_sockets=False)
    ssh_listen = [r for r in rows if r.get("local", "").endswith(":22")]
    if ssh_listen:
        pw(f"  sshd listening on port 22 ({len(ssh_listen)} socket[s])")
    else:
        pd("  sshd not listening on :22")

def cmd_antivirus_status(_args):
    section("ANTIVIRUS / PROTECTION STATUS")
    if IS_MAC:
        rc, out, _ = run(["spctl", "--status"])
        if rc == 0: pb("  Gatekeeper: " + out.strip())
        rc, out, _ = run(["csrutil", "status"])
        if rc == 0: pb("  " + out.strip())
    elif IS_WIN:
        rc, out, _ = run(["powershell", "-NoProfile", "-Command",
                          "Get-MpComputerStatus | Select AMServiceEnabled,RealTimeProtectionEnabled,AntivirusEnabled,AntispywareEnabled | Format-List"],
                         timeout=8)
        if rc == 0 and out.strip():
            for line in out.splitlines(): pb("  " + line)
    elif IS_LINUX:
        for n in ("clamav", "clamd", "rkhunter", "chkrootkit"):
            if have(n): pb(f"  {n}: installed")
        if not any(have(x) for x in ("clamav", "clamd", "rkhunter", "chkrootkit")):
            pd("  no common AV/rootkit tools detected")

def cmd_updates_check(_args):
    section("UPDATES CHECK")
    if IS_MAC:
        if have("softwareupdate"):
            pd("  querying softwareupdate (may take a moment)…")
            rc, out, _ = run(["softwareupdate", "--list"], timeout=30)
            if rc == 0:
                for line in out.splitlines(): pb("  " + line)
            else: pw("  softwareupdate call failed")
        if have("brew"):
            rc, out, _ = run(["brew", "outdated"], timeout=20)
            if rc == 0 and out.strip():
                pc("\n  brew outdated:")
                for line in out.splitlines(): pb("  " + line)
    elif IS_LINUX:
        if have("apt"):
            rc, out, _ = run(["apt", "list", "--upgradable"], timeout=20)
            if rc == 0:
                for line in out.splitlines()[:60]: pb("  " + line)
        elif have("dnf"):
            rc, out, _ = run(["dnf", "check-update"], timeout=20)
            for line in out.splitlines()[:60]: pb("  " + line)
        elif have("pacman"):
            rc, out, _ = run(["pacman", "-Qu"], timeout=10)
            for line in out.splitlines()[:60]: pb("  " + line)
        else:
            pd("  no recognized package manager")
    elif IS_WIN:
        pd("  Windows Update check requires elevation — try:")
        pb("    powershell -Command Get-WindowsUpdate")

def cmd_security_checklist(_args):
    section("SECURITY CHECKLIST  (local, defensive)")
    checks = []
    # firewall
    def check(name, ok, note=""):
        checks.append((name, ok, note))
    # Gatekeeper on mac / ufw on linux / defender on win
    if IS_MAC:
        rc, out, _ = run(["spctl", "--status"])
        check("Gatekeeper", rc == 0 and "enabled" in out, out.strip() if rc == 0 else "unknown")
        rc, out, _ = run(["/usr/libexec/ApplicationFirewall/socketfilterfw", "--getglobalstate"])
        check("Application Firewall", rc == 0 and "enabled" in out.lower(), out.strip() if rc == 0 else "unknown")
    elif IS_LINUX:
        if have("ufw"):
            rc, out, _ = run(["ufw", "status"])
            check("UFW firewall", rc == 0 and "active" in out.lower(), out.strip() if rc == 0 else "")
    # disk encryption hint
    if IS_MAC:
        rc, out, _ = run(["fdesetup", "status"])
        check("FileVault", rc == 0 and "On" in out, out.strip() if rc == 0 else "")
    # screen lock? ssh keys mode?
    ssh_dir = os.path.expanduser("~/.ssh")
    if os.path.isdir(ssh_dir) and IS_POSIX:
        try:
            m = stat.S_IMODE(os.stat(ssh_dir).st_mode)
            check("~/.ssh permissions", m == 0o700, oct(m))
        except Exception: pass
    # world-writable in home (quick)
    ww = 0
    for root, dirs, files in os.walk(HOME, onerror=lambda e: None):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for name in files:
            fp = os.path.join(root, name)
            try:
                if os.lstat(fp).st_mode & stat.S_IWOTH:
                    ww += 1
                    if ww >= 5: break
            except OSError: pass
        if ww >= 5: break
    check("No world-writable files in $HOME", ww == 0, f"{ww}+ found" if ww else "clean")
    # listening sockets count
    rows = _socket_table(all_sockets=False)
    check("Listening services", True, f"{len(rows)} sockets")
    # print
    if not checks:
        pd("  no checks available on this platform"); return
    for name, ok, note in checks:
        icon = "✓" if ok else "✗"
        color = G if ok else YL
        p(f"  {icon}  {name:<38} {note}", color)

def cmd_audit(args):
    mode = "quick"
    if args: mode = args[0].lower()
    section(f"AUDIT ({mode})")
    cmd_security_checklist([])
    print()
    cmd_ssh_check([])
    print()
    cmd_suspicious_startup([])
    if mode == "full":
        print(); cmd_listening([])
        print(); cmd_weak_perms([])
        print(); cmd_antivirus_status([])
    print()
    pc("  Tip:  export-audit   to save a full audit report to disk")

def cmd_doctor(args):
    mode = "quick"
    if args: mode = args[0].lower()
    section(f"DOCTOR · setup health ({mode})")
    # Python
    ver = platform.python_version()
    ok = tuple(int(x) for x in ver.split(".")[:2]) >= (3, 8)
    p(f"  {'✓' if ok else '✗'}  Python {ver} (need 3.8+)", G if ok else RD)
    # Install paths
    p(f"  {'✓' if os.path.isdir(APP_DIR) else '✗'}  {APP_DIR}", G if os.path.isdir(APP_DIR) else RD)
    p(f"  {'✓' if os.path.isfile(STATE_PATH) else '·'}  state file {STATE_PATH}", G if os.path.isfile(STATE_PATH) else DM)
    # Network reachability (non-intrusive DNS resolve)
    try:
        socket.gethostbyname("example.com")
        ph("  ✓  DNS resolution ok")
    except Exception:
        pw("  !  DNS resolution failed (offline mode OK)")
    # Useful local tools
    checks = [("ps", "process list"), ("df", "disk usage")]
    if IS_MAC: checks += [("sysctl", "system tunables"), ("lsof", "socket table")]
    if IS_LINUX: checks += [("ss", "socket table"), ("ip", "network tools")]
    if IS_WIN: checks += [("tasklist", "process list"), ("netstat", "socket table")]
    for b, label in checks:
        p(f"  {'✓' if have(b) else '·'}  {b} ({label})", G if have(b) else DM)
    # Quarantine + reports + risk hooks (added in v3 polish)
    p(f"  {'✓' if os.path.isdir(REPORTS_DIR) else '·'}  reports dir {REPORTS_DIR}",
      G if os.path.isdir(REPORTS_DIR) else DM)
    qdir = os.path.join(APP_DIR, "quarantine")
    p(f"  {'✓' if os.path.isdir(qdir) else '·'}  quarantine  {qdir}",
      G if os.path.isdir(qdir) else DM)
    if mode == "full":
        print()
        cmd_sysinfo([])
        print()
        cmd_netinfo([])
    print()
    pd("  doctor checks the terminal itself, not your whole system.")
    pd("  run  selftest         for a deeper health check of Atomic")
    pd("  run  audit quick      for a security audit of this machine")

# ── COMMANDS: LOGS ────────────────────────────────────────────────────────

def cmd_logs(args):
    n = 100
    if args and args[0].isdigit(): n = int(args[0])
    section(f"SYSTEM LOGS  (last {n} lines)")
    if IS_MAC:
        rc, out, _ = run(["log", "show", "--last", "10m", "--style", "compact"], timeout=10)
        if rc == 0 and out.strip():
            for line in out.splitlines()[-n:]: pb("  " + line)
            return
    if IS_LINUX:
        if have("journalctl"):
            rc, out, _ = run(["journalctl", "--no-pager", "-n", str(n)], timeout=10)
            if rc == 0:
                for line in out.splitlines(): pb("  " + line)
                return
        for pth in ("/var/log/syslog", "/var/log/messages"):
            if os.path.exists(pth):
                _tail_file(pth, n); return
    if IS_WIN:
        rc, out, _ = run(["powershell", "-NoProfile", "-Command",
                          f"Get-WinEvent -LogName System -MaxEvents {n} | Format-Table -AutoSize"], timeout=15)
        if rc == 0:
            for line in out.splitlines(): pb("  " + line.rstrip())
            return
    pw("  no log source reachable")

def _tail_file(path, n=100):
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            block = 4096
            data = b""
            while size > 0 and data.count(b"\n") <= n:
                size = max(0, size - block)
                f.seek(size)
                data = f.read() + data if size else f.read()
                if size == 0: break
            lines = data.decode("utf-8", errors="replace").splitlines()[-n:]
        for line in lines: pb("  " + line)
    except Exception as ex:
        pe(f"  {ex}")

def cmd_authlogs(args):
    n = 60
    if args and args[0].isdigit(): n = int(args[0])
    section(f"AUTH LOGS  (last {n})")
    if IS_MAC:
        rc, out, _ = run(["log", "show", "--predicate",
                          'process == "sshd" OR process == "loginwindow" OR subsystem == "com.apple.sharing"',
                          "--last", "1d", "--style", "compact"], timeout=15)
        if rc == 0 and out.strip():
            for line in out.splitlines()[-n:]: pb("  " + line)
            return
    if IS_LINUX:
        for pth in ("/var/log/auth.log", "/var/log/secure"):
            if os.path.exists(pth):
                _tail_file(pth, n); return
        if have("journalctl"):
            rc, out, _ = run(["journalctl", "-u", "ssh", "-u", "sshd", "--no-pager", "-n", str(n)], timeout=10)
            if rc == 0:
                for line in out.splitlines(): pb("  " + line)
                return
    if IS_WIN:
        rc, out, _ = run(["powershell", "-NoProfile", "-Command",
                          f"Get-WinEvent -LogName Security -MaxEvents {n} | Format-Table -AutoSize"], timeout=15)
        if rc == 0:
            for line in out.splitlines(): pb("  " + line.rstrip())
            return
    pw("  auth logs unreachable (likely requires elevation)")

def cmd_bootlogs(args):
    n = 60
    if args and args[0].isdigit(): n = int(args[0])
    section(f"BOOT LOGS  (last {n})")
    if IS_LINUX and have("journalctl"):
        rc, out, _ = run(["journalctl", "-b", "--no-pager", "-n", str(n)], timeout=10)
        if rc == 0:
            for line in out.splitlines(): pb("  " + line)
            return
    if IS_MAC:
        rc, out, _ = run(["log", "show", "--predicate", 'eventType == "boot"',
                          "--last", "1d", "--style", "compact"], timeout=12)
        if rc == 0:
            for line in out.splitlines()[-n:]: pb("  " + line)
            return
    pw("  boot logs unreachable")

def cmd_errors(args):
    n = 50
    if args and args[0].isdigit(): n = int(args[0])
    section(f"RECENT ERRORS  (last {n})")
    if IS_LINUX and have("journalctl"):
        rc, out, _ = run(["journalctl", "-p", "err", "--no-pager", "-n", str(n)], timeout=10)
        if rc == 0:
            for line in out.splitlines(): pb("  " + line)
            return
    if IS_MAC:
        rc, out, _ = run(["log", "show", "--predicate", 'messageType == error',
                          "--last", "1h", "--style", "compact"], timeout=12)
        if rc == 0:
            for line in out.splitlines()[-n:]: pb("  " + line)
            return
    pw("  error logs unreachable")

def cmd_warnings(args):
    n = 50
    if args and args[0].isdigit(): n = int(args[0])
    section(f"RECENT WARNINGS  (last {n})")
    if IS_LINUX and have("journalctl"):
        rc, out, _ = run(["journalctl", "-p", "warning", "--no-pager", "-n", str(n)], timeout=10)
        if rc == 0:
            for line in out.splitlines(): pb("  " + line)
            return
    if IS_MAC:
        rc, out, _ = run(["log", "show", "--predicate",
                          'messageType == error OR messageType == fault',
                          "--last", "1h", "--style", "compact"], timeout=12)
        if rc == 0:
            for line in out.splitlines()[-n:]: pb("  " + line)
            return
    pw("  warnings unreachable")

def cmd_journal(args):
    cmd_logs(args)

def cmd_app_logs(args):
    if IS_MAC:
        target = os.path.expanduser("~/Library/Logs")
        if os.path.isdir(target):
            section("APP LOGS · ~/Library/Logs"); cmd_ls([target]); return
    pw("  no standard app-log location on this platform")

# ── COMMANDS: REPORTS & EXPORT ────────────────────────────────────────────

def _collect_report() -> dict:
    ut = uptime_seconds()
    return {
        "generated_at": _utcnow_iso(),
        "atomic_version": VERSION,
        "host": {
            "hostname": socket.gethostname(),
            "os": os_pretty(),
            "kernel": platform.release(),
            "arch": platform.machine(),
            "python": platform.python_version(),
            "uptime_seconds": ut,
            "uptime_human": human_duration(ut) if ut else None,
        },
        "cpu": cpu_info(),
        "memory": memory_info(),
        "disks": disk_list(),
        "battery": battery_info(),
        "network": {
            "local_ip": _local_ip(),
            "dns_servers": _dns_servers(),
            "default_gateway": _default_gateway(),
            "listening_sockets": _socket_table(all_sockets=False),
        },
        "processes_top": _list_processes(limit=20),
    }

def _write_report(obj: dict, fname_base: str) -> str:
    _ensure_dirs()
    stamp = _nowstamp()
    json_path = os.path.join(REPORTS_DIR, f"{fname_base}_{stamp}.json")
    txt_path  = os.path.join(REPORTS_DIR, f"{fname_base}_{stamp}.txt")
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, default=str)
    except Exception as ex:
        pe(f"  json write failed: {ex}")
    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(_report_to_text(obj))
    except Exception as ex:
        pe(f"  txt write failed: {ex}")
    return txt_path

def _report_to_text(r: dict) -> str:
    lines = []
    lines.append("ATOMIC TERMINAL — SYSTEM REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {r.get('generated_at')}")
    lines.append(f"Atomic:    v{r.get('atomic_version')}")
    lines.append("")
    h = r.get("host", {})
    lines.append("HOST")
    for k in ("hostname", "os", "kernel", "arch", "python", "uptime_human"):
        lines.append(f"  {k:<12} {h.get(k)}")
    lines.append("")
    c = r.get("cpu", {})
    lines.append("CPU")
    for k, v in c.items(): lines.append(f"  {k:<12} {v}")
    lines.append("")
    m = r.get("memory", {})
    lines.append("MEMORY")
    for k, v in m.items():
        lines.append(f"  {k:<12} {human_bytes(v) if isinstance(v, (int, float)) else v}")
    lines.append("")
    lines.append("DISKS")
    for d in r.get("disks", []):
        lines.append(f"  {d['mount']:<20} {human_bytes(d['used'])}/{human_bytes(d['total'])}  {d['device']}")
    lines.append("")
    bat = r.get("battery")
    if bat:
        lines.append("BATTERY")
        for k, v in bat.items(): lines.append(f"  {k:<12} {v}")
        lines.append("")
    n = r.get("network", {})
    lines.append("NETWORK")
    lines.append(f"  local_ip       {n.get('local_ip')}")
    lines.append(f"  gateway        {n.get('default_gateway')}")
    lines.append(f"  dns_servers    {', '.join(n.get('dns_servers') or []) or '(none)'}")
    lines.append("")
    lines.append("LISTENING SOCKETS")
    for s in (n.get("listening_sockets") or [])[:60]:
        lines.append(f"  {s.get('proto',''):<5} {s.get('local',''):<28} {s.get('state',''):<10} pid={s.get('pid','')}")
    lines.append("")
    lines.append("TOP PROCESSES (by CPU)")
    for p_ in r.get("processes_top", []):
        lines.append(f"  pid={p_['pid']:<6} cpu={p_['cpu']:<5.1f} mem={p_['mem']:<5.1f} {p_['name']}")
    return "\n".join(lines) + "\n"

def cmd_export_report(_args):
    section("EXPORT · system report")
    r = _collect_report()
    path = _write_report(r, "atomic_report")
    ph(f"  ✓ wrote {path}")
    pd(f"    (plus JSON next to it in {REPORTS_DIR})")

def cmd_export_audit(_args):
    section("EXPORT · audit report")
    r = _collect_report()
    # enrich with audit-specific checks
    audit = {}
    ssh_dir = os.path.expanduser("~/.ssh")
    if os.path.isdir(ssh_dir) and IS_POSIX:
        try:
            audit["ssh_dir_mode"] = oct(stat.S_IMODE(os.stat(ssh_dir).st_mode))
        except Exception: pass
    r["audit"] = audit
    path = _write_report(r, "atomic_audit")
    ph(f"  ✓ wrote {path}")

def cmd_export_netinfo(_args):
    data = {
        "generated_at": _utcnow_iso(),
        "hostname": socket.gethostname(),
        "local_ip": _local_ip(),
        "dns": _dns_servers(),
        "gateway": _default_gateway(),
        "listening": _socket_table(all_sockets=False),
        "sockets_all": _socket_table(all_sockets=True),
    }
    _ensure_dirs()
    path = os.path.join(REPORTS_DIR, f"atomic_netinfo_{_nowstamp()}.json")
    with open(path, "w") as f: json.dump(data, f, indent=2, default=str)
    ph(f"  ✓ wrote {path}")

def cmd_export_processes(_args):
    data = {"generated_at": _utcnow_iso(), "processes": _list_processes()}
    _ensure_dirs()
    path = os.path.join(REPORTS_DIR, f"atomic_processes_{_nowstamp()}.json")
    with open(path, "w") as f: json.dump(data, f, indent=2, default=str)
    ph(f"  ✓ wrote {path}")

def cmd_save_session(_args):
    _ensure_dirs()
    path = os.path.join(REPORTS_DIR, f"session_{_nowstamp()}.json")
    with open(path, "w") as f: json.dump(STATE, f, indent=2)
    ph(f"  ✓ session state saved to {path}")

def cmd_support_bundle(_args):
    section("SUPPORT BUNDLE  (diagnostic info for troubleshooting)")
    r = _collect_report()
    r["env_pruned"] = {k: v for k, v in os.environ.items()
                      if not re.search(r"(TOKEN|KEY|SECRET|PASS|PWD|CREDENTIAL|API)", k, re.I)}
    r["atomic_state_summary"] = {
        "user": STATE.get("user"),
        "xp": STATE.get("xp"),
        "completed_lessons": len(STATE.get("completed_lessons", {})),
        "completed_exercises": len(STATE.get("completed_exercises", {})),
        "completed_rooms": len(STATE.get("completed_rooms", {})),
    }
    path = _write_report(r, "atomic_support_bundle")
    ph(f"  ✓ wrote {path}")
    pd("  share this file with support if asked — secrets-looking env vars redacted.")

# ── COMMANDS: UTILITY ─────────────────────────────────────────────────────

def cmd_cat(args):
    if not args:
        pe("  usage:  cat <path>"); return
    path = _safe_abspath(args[0])
    if not os.path.isfile(path):
        pe(f"  not a file: {path}"); return
    try:
        size = os.path.getsize(path)
        if size > 2 * 1024 * 1024:
            pw(f"  large file ({human_bytes(size)}) — showing first 2 MB")
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            sys.stdout.write(f.read(2 * 1024 * 1024))
            sys.stdout.flush()
        print()
    except Exception as ex:
        pe(f"  {ex}")

def cmd_jsonview(args):
    if not args:
        pe("  usage:  jsonview <path>"); return
    path = _safe_abspath(args[0])
    if not os.path.isfile(path):
        pe(f"  not a file: {path}"); return
    try:
        with open(path, "r", encoding="utf-8") as f: data = json.load(f)
        print(json.dumps(data, indent=2, default=str))
    except Exception as ex:
        pe(f"  {ex}")

def cmd_open(args):
    if not args:
        pe("  usage:  open <path|url>"); return
    target = args[0]
    if IS_MAC:
        run(["open", target])
    elif IS_LINUX:
        if have("xdg-open"): run(["xdg-open", target])
        else: pw("  xdg-open not available")
    elif IS_WIN:
        run(["cmd", "/c", "start", "", target], shell=False)
    ph(f"  requested OS to open: {target}")

def cmd_clip(args):
    if not args:
        pe("  usage:  clip <text>"); return
    text = " ".join(args)
    try:
        if IS_MAC and have("pbcopy"):
            p_ = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p_.communicate(text.encode("utf-8")); ph("  copied to clipboard"); return
        if IS_LINUX:
            for tool in (["xclip", "-selection", "clipboard"], ["wl-copy"]):
                if have(tool[0]):
                    p_ = subprocess.Popen(tool, stdin=subprocess.PIPE)
                    p_.communicate(text.encode("utf-8")); ph("  copied to clipboard"); return
        if IS_WIN:
            p_ = subprocess.Popen(["clip"], stdin=subprocess.PIPE, shell=True)
            p_.communicate(text.encode("utf-16le")); ph("  copied to clipboard"); return
    except Exception as ex:
        pe(f"  clipboard failed: {ex}"); return
    pw("  no clipboard tool found on this platform")

def cmd_copy_hash(args):
    if not args:
        pe("  usage:  copy-hash <file>"); return
    path = _safe_abspath(args[0])
    if not os.path.isfile(path):
        pe(f"  not a file: {path}"); return
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    digest = h.hexdigest()
    pb(f"  sha256  {digest}")
    cmd_clip([digest])

def cmd_note(args):
    if not args:
        try:
            with open(NOTES_PATH, "r", encoding="utf-8") as f: sys.stdout.write(f.read())
            print()
        except FileNotFoundError:
            pd("  no notes yet. usage:  note <text>")
        return
    text = " ".join(args)
    _ensure_dirs()
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(f"- [{_nowstamp()}] {text}\n")
    ph("  saved note")

# ── COMMANDS: META ────────────────────────────────────────────────────────

def cmd_version(_args):
    pb(f"  atomic {VERSION}")

def cmd_config(args):
    cfg = load_config()
    if not args:
        section("CONFIG")
        for k, v in cfg.items(): kv(k, v)
        pd(f"\n  usage:  config <key> <value>    (e.g. config theme green)")
        return
    if len(args) == 1:
        pb(f"  {args[0]} = {cfg.get(args[0], '(unset)')}"); return
    key, val = args[0], " ".join(args[1:])
    cfg[key] = val
    save_config(cfg)
    ph(f"  set {key} = {val}")

def cmd_theme(args):
    if not args:
        pb(f"  current theme: {STATE.get('theme','green')}"); return
    new = args[0].lower()
    STATE["theme"] = new; save_state(STATE)
    ph(f"  theme set to {new}  (applies to future sessions where supported)")

def cmd_restart(_args):
    ph("  restarting atomic terminal…")
    log_event("restart")
    os.execv(sys.executable, [sys.executable] + sys.argv)

def cmd_uninstall(_args):
    section("UNINSTALL")
    lbl_warn("This removes ~/.atomic, including:")
    pb("    · config + state")
    pb("    · session and device logs")
    pb(f"    · ALL reports in {REPORTS_DIR}")
    qdir = os.path.join(APP_DIR, "quarantine")
    if os.path.isdir(qdir):
        try:
            qcount = len([n for n in os.listdir(qdir) if n != "index.json"])
        except Exception:
            qcount = 0
        if qcount:
            print()
            lbl_high(f"WARNING: quarantine still holds {qcount} file(s).")
            pd("  Run  undo  first to restore anything you want back BEFORE uninstalling.")
    print()
    pw("  You can also remove the 'atomic' symlink or shell alias manually.")
    pw("  Type:  uninstall confirm")

def cmd_uninstall_confirm(_args):
    try:
        shutil.rmtree(APP_DIR)
        ph("  ~/.atomic removed. Goodbye, operator.")
        sys.exit(0)
    except (PermissionError, OSError) as ex:
        lbl_err(f"uninstall failed: {pretty_oserror(ex)}")
    except Exception as ex:
        lbl_err(f"uninstall failed: {ex}")

def cmd_update(_args):
    section("UPDATE")
    pb("  Atomic Terminal is self-contained. To update, re-run the installer:")
    pb("    curl -fsSL https://raw.githubusercontent.com/P4vL0-P4nd4/atomic-terminal/main/install.sh | bash")
    pd("  (or download a fresh install.sh/install.ps1 and run it)")

def cmd_status(args):
    mode = "summary"
    if args: mode = args[0].lower()
    section("STATUS")
    ut = uptime_seconds()
    lip = _local_ip()
    mem = memory_info()
    disks = disk_list()
    kv("Host",     socket.gethostname())
    kv("OS",       os_pretty())
    if ut: kv("Uptime",   human_duration(ut))
    if lip: kv("Local IP", lip)
    if mem["total"]:
        pct = (mem["used"]/mem["total"]*100) if mem["used"] else 0
        kv("Memory",   f"{pct:.0f}% used")
    if disks:
        d = disks[0]
        pct = (d["used"]/d["total"]*100) if d["total"] else 0
        kv("Disk",     f"{d['mount']}  {pct:.0f}% used")
    bat = battery_info()
    if bat and "percent" in bat: kv("Battery", f"{bat['percent']}%  {bat.get('status','')}")
    if mode == "full":
        print()
        cmd_listening([])
        print()
        cmd_processes(["10"])

# ── ACADEMY CONTENT (preserved from v2) ───────────────────────────────────

LESSONS = [
    {"id":"l-intro","title":"Welcome to Atomic","branch":"fundamentals","difficulty":"easy","xp":25,"requires":[],
     "summary":"Meet the simulator, its terminal, and its safety model.",
     "body":[("h","What Atomic is"),("p","Atomic is a sandboxed training platform. Every command maps to a real security concept, but nothing here touches real networks or accounts."),
             ("h","Golden rule"),("p","Never run the real versions of these tools on systems you do not own or have explicit written permission to test.")],
     "check":{"prompt":"Which command opens the learning area?","answers":["academy","learn"]}},
    {"id":"l-terminal","title":"Terminal Basics","branch":"fundamentals","difficulty":"easy","xp":35,"requires":["l-intro"],
     "summary":"CLI anatomy, flags, and the universal help convention.",
     "body":[("h","Anatomy"),("p","A command is usually: tool subcommand --flag value positional."),
             ("h","Help first"),("p","tool --help or man tool prints usage. Here, help <topic> narrows it.")],
     "check":{"prompt":"Which flag commonly shows help for a CLI tool?","answers":["-h","--help","help","-h/--help"]}},
    {"id":"l-cia","title":"The CIA Triad","branch":"fundamentals","difficulty":"easy","xp":30,"requires":["l-intro"],
     "summary":"Confidentiality, Integrity, Availability.",
     "body":[("h","C — Confidentiality"),("p","Only the right people read the data."),
             ("h","I — Integrity"),("p","The data is unchanged except by authorized actors."),
             ("h","A — Availability"),("p","The service is up when needed.")],
     "check":{"prompt":"Which pillar does a SHA-256 checksum primarily protect?","answers":["integrity","i"]}},
    {"id":"l-net","title":"Networking 101","branch":"networking","difficulty":"easy","xp":40,"requires":["l-terminal"],
     "summary":"IPs, ports, TCP vs UDP.",
     "body":[("h","Addressing"),("p","IP = host, port = service. 80/TCP HTTP, 443/TCP HTTPS, 22/TCP SSH, 53/UDP DNS."),
             ("h","Protocols"),("p","TCP connects and retransmits; UDP fires and forgets.")],
     "check":{"prompt":"Which port is typically HTTPS?","answers":["443","443/tcp","tcp/443"]}},
    {"id":"l-http","title":"HTTP Requests","branch":"web","difficulty":"easy","xp":40,"requires":["l-net"],
     "summary":"Methods, status families, security headers.",
     "body":[("h","Methods"),("p","GET retrieves, POST submits, PUT replaces, PATCH updates, DELETE removes."),
             ("h","Status families"),("p","2xx success, 3xx redirect, 4xx client error, 5xx server error.")],
     "check":{"prompt":"Which HTTP status family indicates a client error?","answers":["4xx","4","client"]}},
    {"id":"l-sqli","title":"SQL Injection","branch":"web","difficulty":"medium","xp":60,"requires":["l-http"],
     "summary":"Why string-concatenated SQL is catastrophic.",
     "body":[("h","The pattern"),("p","Concatenating user input into SQL = an attacker rewrites your query."),
             ("h","The fix"),("p","Parameterized queries (prepared statements).")],
     "check":{"prompt":"Canonical defense against SQL injection (two words)?","answers":["parameterized queries","prepared statements","bind parameters"]}},
    {"id":"l-crypto","title":"Crypto Fundamentals","branch":"crypto","difficulty":"medium","xp":55,"requires":["l-cia"],
     "summary":"Hash vs encryption, symmetric vs asymmetric.",
     "body":[("h","Hash"),("p","One-way. Use for integrity and password storage with a KDF (Argon2id/bcrypt)."),
             ("h","Encryption"),("p","Reversible with the key. AES-GCM for symmetric; RSA/ECDSA for asymmetric.")],
     "check":{"prompt":"Which algorithm family is appropriate for storing user passwords?","answers":["argon2","argon2id","bcrypt","scrypt","pbkdf2","kdf"]}},
    {"id":"l-hashing","title":"Hash Identification","branch":"crypto","difficulty":"medium","xp":45,"requires":["l-crypto"],
     "summary":"Recognize common hashes by length and prefix.",
     "body":[("h","Length"),("p","MD5 32, SHA-1 40, SHA-256 64, SHA-512 128 hex characters."),
             ("h","Prefix"),("p","$2b$ bcrypt, $argon2id$ Argon2id, $6$ SHA-512 crypt.")],
     "check":{"prompt":"A 64-character hex string is most likely which hash?","answers":["sha256","sha-256"]}},
    {"id":"l-forensics","title":"Forensics Intro","branch":"forensics","difficulty":"medium","xp":50,"requires":["l-terminal"],
     "summary":"Volatility order, chain of custody, baseline tools.",
     "body":[("h","Volatility"),("p","Collect in order of how fast it disappears: CPU, memory, net state, processes, disk."),
             ("h","Chain of custody"),("p","Log every transfer. Hash before and after.")],
     "check":{"prompt":"Which tool identifies file type by magic bytes?","answers":["file","file(1)"]}},
]

EXERCISES = [
    {"id":"e-help","title":"First Contact","branch":"fundamentals","difficulty":"easy","xp":10,"requires":["l-intro"],
     "prompt":"Which command lists every top-level feature?","answers":["help","?"],
     "hint":"Four letters.","hint_cost":5,"explain":"help prints the command reference."},
    {"id":"e-flags","title":"Read a Flag","branch":"fundamentals","difficulty":"easy","xp":15,"requires":["l-terminal"],
     "prompt":"In nmap -sV -p 80 target, which flag asks for service/version detection?","answers":["-sv","sv","service version","-sv (service version)"],
     "hint":"Starts with -s and a capital letter.","hint_cost":5,"explain":"-sV probes open ports for banner/version info."},
    {"id":"e-ports","title":"Name that Port","branch":"networking","difficulty":"easy","xp":15,"requires":["l-net"],
     "prompt":"Which port is SSH by default?","answers":["22","22/tcp","tcp/22","ssh","port 22"],
     "hint":"Two digits, below 30.","hint_cost":5,"explain":"22/TCP is SSH."},
    {"id":"e-status-404","title":"Status Code","branch":"web","difficulty":"easy","xp":15,"requires":["l-http"],
     "prompt":"Which HTTP status code says the resource is missing?","answers":["404","not found"],
     "hint":"The meme code.","hint_cost":3,"explain":"404 — client error, resource not found."},
    {"id":"e-sqli-fix","title":"Fix the Injection","branch":"web","difficulty":"medium","xp":30,"requires":["l-sqli"],
     "prompt":"Name the canonical SQL-injection defense (two words).","answers":["parameterized queries","prepared statements","bind parameters"],
     "hint":"Data binds separately from the compiled query.","hint_cost":10,"explain":"Parameterized queries separate plan from data."},
    {"id":"e-hash-id","title":"Identify the Hash","branch":"crypto","difficulty":"medium","xp":25,"requires":["l-hashing"],
     "prompt":"5f4dcc3b5aa765d61d8327deb882cf99 — which algorithm?","answers":["md5"],
     "hint":"32 hex = 128 bits.","hint_cost":8,"explain":"32 hex characters is MD5."},
    {"id":"e-bcrypt","title":"Spot the Prefix","branch":"crypto","difficulty":"medium","xp":25,"requires":["l-hashing"],
     "prompt":"A hash starts with $2b$12$...  Which algorithm?","answers":["bcrypt"],
     "hint":"Password-hashing workhorse.","hint_cost":6,"explain":"$2a$, $2b$, $2y$ are all bcrypt."},
    {"id":"e-cia","title":"Map to a Pillar","branch":"fundamentals","difficulty":"easy","xp":15,"requires":["l-cia"],
     "prompt":"DDoS primarily threatens which CIA pillar?","answers":["availability","a"],
     "hint":"The uptime one.","hint_cost":4,"explain":"Floods kill availability."},
    {"id":"e-file","title":"Trust the Magic Bytes","branch":"forensics","difficulty":"medium","xp":25,"requires":["l-forensics"],
     "prompt":"Which command identifies file type by content, not extension?","answers":["file","file(1)"],
     "hint":"Canonical Unix identifier.","hint_cost":8,"explain":"file reads magic bytes."},
]

ROOMS = [
    {"id":"r-recon","title":"Recon Range","branch":"networking","difficulty":"easy","xp":120,"requires":["l-net"],
     "brief":"Passive reconnaissance of the training host sim.local.",
     "steps":[
         {"id":"s1","intro":"Step 1 — DNS resolution. Use `dig sim.local`.",
          "prompt":"What IPv4 does sim.local resolve to?","answers":["10.10.42.7"],
          "hint":"Run dig sim.local.","xp":20},
         {"id":"s2","intro":"Step 2 — Service discovery. Use `scan sim.local`.",
          "prompt":"Which TCP port for SSH is open?","answers":["22","22/tcp"],
          "hint":"Run scan sim.local and read the SSH line.","xp":25},
         {"id":"s3","intro":"Step 3 — Banner grab. Use `banner sim.local 80`.",
          "prompt":"What web server banner is returned on port 80?","answers":["nginx/1.24.0","nginx","nginx 1.24.0"],
          "hint":"Look at the Server: header.","xp":25},
     ]},
    {"id":"r-web","title":"Web Shakedown","branch":"web","difficulty":"medium","xp":160,"requires":["l-sqli"],
     "brief":"Review a deliberately-vulnerable training web app.",
     "steps":[
         {"id":"s1","intro":"Step 1 — identify the class.",
          "prompt":"A login query is built as WHERE user='\" + input + \"'. Vulnerability class?","answers":["sqli","sql injection","injection"],
          "hint":"Concatenated SQL.","xp":30},
         {"id":"s2","intro":"Step 2 — recommend the fix.",
          "prompt":"What is the canonical fix (two words)?","answers":["parameterized queries","prepared statements"],
          "hint":"The plan compiles once.","xp":30},
         {"id":"s3","intro":"Step 3 — classify the comments bug.",
          "prompt":"A comments feature renders user text via innerHTML. Vulnerability class?","answers":["xss","stored xss","cross-site scripting"],
          "hint":"Inserting raw HTML.","xp":30},
     ]},
    {"id":"r-crypto","title":"Crypto Locker","branch":"crypto","difficulty":"medium","xp":140,"requires":["l-hashing"],
     "brief":"Classify leaked training hashes.",
     "steps":[
         {"id":"s1","intro":"Step 1 — identify by length.",
          "prompt":"e10adc3949ba59abbe56e057f20f883e (32 hex). Algorithm?","answers":["md5"],
          "hint":"32 hex = 128 bits.","xp":25},
         {"id":"s2","intro":"Step 2 — identify by prefix.",
          "prompt":"$2b$12$Kix6y...  Algorithm?","answers":["bcrypt"],
          "hint":"The $2b$ prefix.","xp":25},
         {"id":"s3","intro":"Step 3 — decode a base64 string.",
          "prompt":"Decode c2FmZS1tb2Rl to its plaintext.","answers":["safe-mode","safe mode","safemode"],
          "hint":"Run decode b64 c2FmZS1tb2Rl.","xp":30},
     ]},
]

BRANCHES = {"fundamentals":"Fundamentals","networking":"Networking","web":"Web","crypto":"Crypto","forensics":"Forensics"}
RANKS = [(0,"Initiate"),(150,"Recruit"),(400,"Operator"),(800,"Analyst"),(1400,"Specialist"),(2200,"Engineer"),(3200,"Architect"),(4500,"Master")]

DISABLED_OFFENSIVE = {
    "hydra","sqlmap","metasploit","msfconsole","exploit","keylog","phish",
    "spray","mimikatz","backdoor","aircrack","beef","burp","nikto",
    "masscan","wpscan","gobuster","dirb","ettercap","responder","john",
}

def xp_needed(level): return 100 + (level - 1) * 75
def get_level():
    xp = STATE["xp"]; lvl = 1
    while xp >= xp_needed(lvl) and lvl < 99:
        xp -= xp_needed(lvl); lvl += 1
    return {"level":lvl,"into":xp,"needed":xp_needed(lvl)}
def get_rank():
    cur = RANKS[0][1]
    for xp, name in RANKS:
        if STATE["xp"] >= xp: cur = name
    return cur

def _find(col, q):
    q = (q or "").strip().lower()
    if not q: return None
    if q.isdigit():
        idx = int(q) - 1
        return col[idx] if 0 <= idx < len(col) else None
    for it in col:
        if it["id"].lower() == q: return it
    for it in col:
        if it["title"].lower() == q: return it
    for it in col:
        if q in it["id"].lower() or q in it["title"].lower(): return it
    return None

def is_lesson_done(x):   return x in STATE["completed_lessons"]
def is_exercise_done(x): return x in STATE["completed_exercises"]
def is_room_done(x):     return x in STATE["completed_rooms"]

def _reqs_met(reqs):
    if not reqs: return True
    for r in reqs:
        if is_lesson_done(r) or is_exercise_done(r) or is_room_done(r): continue
        return False
    return True

def is_lesson_unlocked(l):   return _reqs_met(l.get("requires") or [])
def is_exercise_unlocked(e): return _reqs_met(e.get("requires") or [])
def is_room_unlocked(r):     return _reqs_met(r.get("requires") or [])

def grant_xp(amount, reason=""):
    STATE["xp"] = max(0, STATE["xp"] + amount); save_state(STATE)
    sign = "+" if amount >= 0 else ""
    ph(f"  {sign}{amount} XP  ({reason})" if reason else f"  {sign}{amount} XP")

def complete_lesson(l):
    if is_lesson_done(l["id"]): pd("  already complete."); return False
    STATE["completed_lessons"][l["id"]] = _utcnow_iso(); save_state(STATE)
    grant_xp(l["xp"], f"lesson: {l['title']}"); return True

def complete_exercise(e):
    if is_exercise_done(e["id"]): pd("  already complete."); return False
    STATE["completed_exercises"][e["id"]] = _utcnow_iso(); save_state(STATE)
    grant_xp(e["xp"], f"exercise: {e['title']}"); return True

def complete_room(r):
    if is_room_done(r["id"]): pd("  already complete."); return False
    STATE["completed_rooms"][r["id"]] = _utcnow_iso()
    bonus = sum(s.get("xp",0) for s in r["steps"]); save_state(STATE)
    grant_xp(r["xp"]+bonus, f"room: {r['title']}"); return True

def recommend():
    l = next((x for x in LESSONS if not is_lesson_done(x["id"]) and is_lesson_unlocked(x)), None)
    e = next((x for x in EXERCISES if not is_exercise_done(x["id"]) and is_exercise_unlocked(x)), None)
    r = next((x for x in ROOMS if not is_room_done(x["id"]) and is_room_unlocked(x)), None)
    return l, e, r

def _norm(s): return re.sub(r"\s+", " ", (s or "").strip().lower())
def match_answer(user, answers):
    n = _norm(user)
    if not n: return False
    return any(_norm(a) == n for a in answers)

# ── SIM (sandbox only) ────────────────────────────────────────────────────

SIM_HOSTS = {
    "sim.local": {
        "ip":"10.10.42.7",
        "whois":["Domain Name: SIM.LOCAL","Registry: ATOMIC-SIM","Registrant: Atomic Training Platform",
                 "Status: active (training sandbox)","Nameservers: ns1.sim.local, ns2.sim.local"],
        "dns":{"A":["10.10.42.7"],"AAAA":["fd00:42::7"],"MX":["10 mail.sim.local"],
               "NS":["ns1.sim.local","ns2.sim.local"],
               "TXT":['"v=spf1 ip4:10.10.42.0/24 -all"','"atomic-training=true"']},
        "ports":{22:{"state":"open","banner":"SSH-2.0-OpenSSH_9.6p1"},
                 80:{"state":"open","banner":"HTTP/1.1 200 OK | Server: nginx/1.24.0"},
                 443:{"state":"open","banner":"TLS/1.3 · SNI sim.local · cert: sim.local (training CA)"},
                 3306:{"state":"filtered","banner":""},
                 8080:{"state":"open","banner":"HTTP/1.1 200 OK | Server: Werkzeug/3.0.0"}},
        "ping":[0.48,0.55,0.51,0.62]},
    "shop.sim.local":{"ip":"10.10.42.80","whois":["Domain: SHOP.SIM.LOCAL","Training vhost of sim.local"],
        "dns":{"A":["10.10.42.80"],"CNAME":["sim.local."]},
        "ports":{80:{"state":"open","banner":"HTTP/1.1 200 OK | Server: nginx/1.24.0"}},"ping":[0.51,0.55]},
    "ctf.sim.local":{"ip":"10.10.42.31","whois":["Domain: CTF.SIM.LOCAL","CTF training range"],
        "dns":{"A":["10.10.42.31"]},
        "ports":{22:{"state":"open","banner":"SSH-2.0-OpenSSH_8.4p1"},
                 80:{"state":"open","banner":"HTTP/1.1 200 OK | Server: Apache/2.4.54"}},
        "ping":[0.80,0.90,0.85]},
}

def _sim_host(name): return SIM_HOSTS.get((name or "").lower()) if name else None

def _reject(kind, host):
    pw(f"  [sim] `{kind}` only operates on sandbox hosts.")
    pd("  Allowed targets (academy only):")
    for h in SIM_HOSTS: pd(f"    {h}")
    pd(f"  Example:  {kind} sim.local")

def cmd_dig(args):
    if not args:
        pe("  usage:  dig <host> [A|MX|TXT|NS|ANY]"); return
    host, rtype = args[0], (args[1] if len(args)>1 else "ANY").upper()
    h = _sim_host(host)
    if not h: _reject("dig", host); return
    pd(f"  ; <<>> atomic-dig (sim) <<>>  {host} {rtype}")
    pd("  ;; ANSWER SECTION:")
    types = ["A","AAAA","MX","NS","TXT","CNAME"] if rtype=="ANY" else [rtype]
    any_printed = False
    for t in types:
        for v in h["dns"].get(t, []):
            ph(f"  {host:<24} IN {t:<5} {v}"); any_printed = True
    if not any_printed: pd(f"  ;; no records for {rtype}")

def cmd_whois(args):
    if not args: pe("  usage:  whois <host>"); return
    h = _sim_host(args[0])
    if not h: _reject("whois", args[0]); return
    for line in h["whois"]: ph(f"  {line}")

def cmd_scan_sim(args):
    if not args: pe("  usage:  scan <host>  (sim targets only)"); return
    host = args[0]; h = _sim_host(host)
    if not h: _reject("scan", host); return
    pd(f"  [sim] Deterministic scan of {host} ({h['ip']})")
    pc("  PORT      STATE      SERVICE     BANNER")
    svc = {22:"ssh",80:"http",443:"https",3306:"mysql",8080:"http-proxy"}
    for port in sorted(h["ports"].keys()):
        info = h["ports"][port]
        banner = (info.get("banner") or "").split(" | ")[0][:60]
        ph(f"  {str(port):<9}{info['state']:<11}{svc.get(port,'unknown'):<12}{banner}")
    pd("  [sim] complete — no real sockets opened")

def cmd_banner(args):
    if len(args) < 2: pe("  usage:  banner <host> <port>"); return
    try: port = int(args[1])
    except ValueError: pe("  port must be numeric"); return
    h = _sim_host(args[0])
    if not h: _reject("banner", args[0]); return
    info = h["ports"].get(port)
    if not info or info["state"] != "open":
        pw(f"  {args[0]}:{port} — no banner (port {info['state'] if info else 'closed'})"); return
    for line in (info.get("banner") or "").split(" | "): ph(f"  {line}")

def cmd_sim_ping(args):
    if not args: pe("  usage:  simping <host>"); return
    h = _sim_host(args[0])
    if not h: _reject("simping", args[0]); return
    pd(f"  PING {args[0]} ({h['ip']})  [sim]")
    for i, rtt in enumerate(h["ping"]):
        ph(f"  64 bytes from {h['ip']}: seq={i} ttl=64 time={rtt} ms")
    avg = sum(h["ping"])/len(h["ping"])
    ph(f"  rtt min/avg/max = {min(h['ping'])}/{avg:.2f}/{max(h['ping'])} ms")

def cmd_decode(args):
    if len(args) < 2: pe("  usage:  decode <b64|hex|rot13|url> <value>"); return
    kind = args[0].lower(); value = " ".join(args[1:])
    try:
        if kind in ("b64","base64"):
            import base64; out = base64.b64decode(value, validate=False).decode("utf-8", errors="replace")
        elif kind == "hex":
            out = bytes.fromhex(re.sub(r"[^0-9a-fA-F]", "", value)).decode("utf-8", errors="replace")
        elif kind == "rot13":
            import codecs; out = codecs.decode(value, "rot_13")
        elif kind == "url":
            from urllib.parse import unquote; out = unquote(value)
        else: pe(f"  unknown encoding: {kind}"); return
        ph(f"  {out}")
    except Exception as ex: pe(f"  decode failed: {ex}")

def cmd_encode(args):
    if len(args) < 2: pe("  usage:  encode <b64|hex|rot13|url> <value>"); return
    kind = args[0].lower(); value = " ".join(args[1:])
    try:
        if kind in ("b64","base64"):
            import base64; out = base64.b64encode(value.encode("utf-8")).decode("ascii")
        elif kind == "hex": out = value.encode("utf-8").hex()
        elif kind == "rot13":
            import codecs; out = codecs.encode(value, "rot_13")
        elif kind == "url":
            from urllib.parse import quote; out = quote(value)
        else: pe(f"  unknown encoding: {kind}"); return
        ph(f"  {out}")
    except Exception as ex: pe(f"  encode failed: {ex}")

def cmd_hashid(args):
    if not args: pe("  usage:  hashid <value>"); return
    value = args[0].strip()
    guesses = []
    if re.match(r"^\$2[aby]\$\d{2}\$", value):   guesses.append("bcrypt")
    elif re.match(r"^\$argon2(id|i|d)\$", value): guesses.append("argon2")
    elif value.startswith("$6$"):                 guesses.append("SHA-512 crypt")
    elif value.startswith("$5$"):                 guesses.append("SHA-256 crypt")
    elif value.startswith("$1$"):                 guesses.append("MD5 crypt")
    elif re.match(r"^[a-fA-F0-9]{32}$", value):   guesses += ["MD5","NTLM (Windows hash)"]
    elif re.match(r"^[a-fA-F0-9]{40}$", value):   guesses.append("SHA-1")
    elif re.match(r"^[a-fA-F0-9]{64}$", value):   guesses.append("SHA-256")
    elif re.match(r"^[a-fA-F0-9]{128}$", value):  guesses.append("SHA-512")
    elif re.match(r"^[A-Za-z0-9+/=]{24,}$", value): guesses.append("Base64-encoded digest (decode first)")
    if not guesses: pw("  no confident guess for this value."); return
    ph("  candidate(s):")
    for g in guesses: ph(f"    • {g}")
    pd("  hashid is an educational identifier, not a cracker.")

# ── Academy listing / play ────────────────────────────────────────────────

def _list_kind(kind, collection, done_fn, unlocked_fn):
    print(); ph(f"  {kind.upper()}S"); rule()
    for i, it in enumerate(collection, 1):
        done = done_fn(it["id"]); unlocked = unlocked_fn(it)
        status = "✓" if done else "·" if unlocked else "✗"
        color = G if done else WH if unlocked else DM
        branch = BRANCHES.get(it["branch"], it["branch"])
        line = f"  {i:>2} {status}  {branch:<12}  {it.get('difficulty','easy'):<6}  {it['title']}  (+{it['xp']} XP)"
        p(line, color)
    print(); pd(f"  open:  {kind} <number>    e.g.  {kind} 1")

def cmd_lessons(_): _list_kind("lesson", LESSONS, is_lesson_done, is_lesson_unlocked)
def cmd_exercises(_): _list_kind("exercise", EXERCISES, is_exercise_done, is_exercise_unlocked)
def cmd_rooms(_): _list_kind("room", ROOMS, is_room_done, is_room_unlocked)

def _read_line(prompt):
    try: return input(_c(prompt, G))
    except KeyboardInterrupt: print(); raise
    except EOFError: raise

def play_lesson(l):
    print(); ph(f"  LESSON · {l['title']}"); rule()
    pd(f"  {BRANCHES.get(l['branch'], l['branch'])} · {l.get('difficulty','easy')} · +{l['xp']} XP")
    if l.get("summary"): pb(f"  {l['summary']}")
    print()
    for kind, text in l.get("body", []):
        (pc if kind == "h" else pb)(f"  {text}"); print()
    print(); pd("  Checkpoint:"); pb(f"  {l['check']['prompt']}")
    while True:
        try: ans = _read_line("  answer> ")
        except (EOFError, KeyboardInterrupt): print(); pd("  exiting lesson."); return
        if ans.strip().lower() in ("exit","quit",":q"): pd("  exiting lesson."); return
        if match_answer(ans, l["check"]["answers"]): ph("  ✓ correct"); complete_lesson(l); return
        pe("  ✗ not quite. try again (or exit).")

def play_exercise(e):
    print(); ph(f"  EXERCISE · {e['title']}"); rule()
    pd(f"  {BRANCHES.get(e['branch'], e['branch'])} · {e.get('difficulty','easy')} · +{e['xp']} XP")
    print(); pb(f"  {e['prompt']}")
    while True:
        try: ans = _read_line("  answer> ")
        except (EOFError, KeyboardInterrupt): print(); pd("  exiting."); return
        cmd = ans.strip().lower()
        if cmd in ("exit","quit",":q"): pd("  exiting."); return
        if cmd == "hint":
            key = f"ex:{e['id']}"
            if STATE["hints_used"].get(key): pd("  hint already revealed")
            else:
                STATE["hints_used"][key] = True
                STATE["xp"] = max(0, STATE["xp"] - e.get("hint_cost",5)); save_state(STATE)
                pw(f"  hint: {e['hint']}"); pd(f"  −{e.get('hint_cost',5)} XP")
            continue
        if match_answer(ans, e["answers"]):
            ph("  ✓ correct"); pb(f"  {e['explain']}"); complete_exercise(e); return
        pe("  ✗ incorrect.  type hint for a hint, exit to leave.")

def play_room(r):
    print(); ph(f"  ROOM · {r['title']}"); rule()
    pd(f"  {BRANCHES.get(r['branch'], r['branch'])} · {r.get('difficulty','medium')} · +{r['xp']} XP base")
    pb(f"  {r.get('brief','')}")
    prog = STATE["room_progress"].setdefault(r["id"], {"step":0,"hints":{}})
    if is_room_done(r["id"]):
        ph("  ★ room already complete. replay allowed, no new XP.")
    while prog["step"] < len(r["steps"]):
        step = r["steps"][prog["step"]]
        print(); pc(f"  STEP {prog['step']+1} of {len(r['steps'])}")
        pb(f"  {step.get('intro','')}"); pb(f"  {step['prompt']}")
        try: ans = _read_line("  answer> ")
        except (EOFError, KeyboardInterrupt): print(); pd("  exiting room (saved)."); save_state(STATE); return
        cmd = ans.strip().lower()
        if cmd in ("exit","quit",":q"): pd("  exiting room (saved)."); save_state(STATE); return
        if cmd == "hint":
            key = f"room:{r['id']}:{step['id']}"
            if STATE["hints_used"].get(key): pd("  hint already revealed")
            else:
                STATE["hints_used"][key] = True
                STATE["xp"] = max(0, STATE["xp"] - 10); save_state(STATE)
                pw(f"  hint: {step.get('hint','no hint')}"); pd("  −10 XP")
            continue
        parts = ans.strip().split()
        if parts and parts[0].lower() in SIM_COMMAND_TABLE:
            SIM_COMMAND_TABLE[parts[0].lower()](parts[1:]); continue
        if match_answer(ans, step["answers"]):
            ph("  ✓ correct")
            if step.get("xp"): grant_xp(step["xp"], "step")
            prog["step"] += 1; save_state(STATE)
        else:
            pe("  ✗ incorrect.  type hint, or try a sim command.")
    if not is_room_done(r["id"]): complete_room(r)

def cmd_lesson(args):
    if not args: pe("  usage:  lesson <id or number>"); return
    l = _find(LESSONS, " ".join(args))
    if not l: pe("  no such lesson"); return
    if not is_lesson_unlocked(l): pw(f"  locked: {l['title']}"); return
    play_lesson(l)

def cmd_exercise(args):
    if not args: pe("  usage:  exercise <id or number>"); return
    e = _find(EXERCISES, " ".join(args))
    if not e: pe("  no such exercise"); return
    if not is_exercise_unlocked(e): pw(f"  locked: {e['title']}"); return
    play_exercise(e)

def cmd_room(args):
    if not args: pe("  usage:  room <id or number>"); return
    r = _find(ROOMS, " ".join(args))
    if not r: pe("  no such room"); return
    if not is_room_unlocked(r): pw(f"  locked: {r['title']}"); return
    play_room(r)

def cmd_stats(_):
    lvl = get_level()
    l = len(STATE["completed_lessons"]); e = len(STATE["completed_exercises"]); rr = len(STATE["completed_rooms"])
    section("OPERATOR PROFILE")
    kv("User", STATE["user"]); kv("Rank", get_rank())
    kv("Level", f"{lvl['level']}  ({lvl['into']} / {lvl['needed']} into next)")
    kv("Total XP", f"{STATE['xp']:,}")
    print()
    kv("Lessons", f"{l} / {len(LESSONS)}  complete")
    kv("Exercises", f"{e} / {len(EXERCISES)}  complete")
    kv("Rooms", f"{rr} / {len(ROOMS)}  complete")

def cmd_roadmap(_):
    section("ROADMAP · BRANCH PROGRESS")
    for key, name in BRANCHES.items():
        l_tot = [x for x in LESSONS if x["branch"]==key]
        e_tot = [x for x in EXERCISES if x["branch"]==key]
        r_tot = [x for x in ROOMS if x["branch"]==key]
        l_done = sum(1 for x in l_tot if is_lesson_done(x["id"]))
        e_done = sum(1 for x in e_tot if is_exercise_done(x["id"]))
        r_done = sum(1 for x in r_tot if is_room_done(x["id"]))
        total_done = l_done + e_done + r_done
        total_all = len(l_tot)+len(e_tot)+len(r_tot)
        bar = _progress_bar(total_done, total_all)
        ph(f"  {name:<14} {bar}  L:{l_done}/{len(l_tot)}  E:{e_done}/{len(e_tot)}  R:{r_done}/{len(r_tot)}")
    rec_l, rec_e, rec_r = recommend(); print()
    if rec_l: pc(f"  Next lesson   → {rec_l['title']}  (lesson {LESSONS.index(rec_l)+1})")
    if rec_e: pc(f"  Next exercise → {rec_e['title']}  (exercise {EXERCISES.index(rec_e)+1})")
    if rec_r: pc(f"  Next room     → {rec_r['title']}  (room {ROOMS.index(rec_r)+1})")
    if not (rec_l or rec_e or rec_r): ph("  curriculum complete — nice work, operator.")

def cmd_academy(_):
    lvl = get_level()
    l = len(STATE["completed_lessons"]); e = len(STATE["completed_exercises"]); rr = len(STATE["completed_rooms"])
    section("ATOMIC ACADEMY")
    kv("Rank", f"{get_rank()}  · level {lvl['level']}  · {STATE['xp']} XP")
    kv("Progress", f"Lessons {l}/{len(LESSONS)}  ·  Exercises {e}/{len(EXERCISES)}  ·  Rooms {rr}/{len(ROOMS)}")
    rec_l, rec_e, rec_r = recommend(); print()
    if rec_l: pc(f"  next lesson   → lesson {LESSONS.index(rec_l)+1}  ({rec_l['title']})")
    if rec_e: pc(f"  next exercise → exercise {EXERCISES.index(rec_e)+1}  ({rec_e['title']})")
    if rec_r: pc(f"  next room     → room {ROOMS.index(rec_r)+1}  ({rec_r['title']})")
    if not (rec_l or rec_e or rec_r): ph("  curriculum complete.")
    print(); pd("  Type  lessons / exercises / rooms  to browse.")

def cmd_whoami(_): pb(f"  {STATE['user']}"); pd(f"  host: {socket.gethostname()}   session: local")

def cmd_reset(args):
    if args and args[0].lower() == "confirm":
        new_state = dict(DEFAULT_STATE); new_state["user"] = STATE["user"]
        globals()["STATE"] = new_state; save_state(STATE)
        ph("  wiped. profile reset."); return
    pw("  This will wipe XP, completions, and notes metadata.")
    pw("  Type:  reset confirm")

def cmd_about(_):
    section("ABOUT ATOMIC TERMINAL")
    pb("  Atomic Terminal is the local companion to the Atomic AI website.")
    pb("  It is a read-only local diagnostics, inspection, and defensive")
    pb("  security terminal for your own machine.")
    print()
    pd("  • Pure Python stdlib — no third-party dependencies")
    pd("  • No shell passthrough · no offensive tooling")
    pd("  • State in:  " + APP_DIR)
    pd("  • Reports in: " + REPORTS_DIR)

def cmd_safety(_):
    section("SAFETY MODEL")
    pb("  Atomic Terminal is defensive-only. These command names print a")
    pb("  notice instead of running anything:")
    for x in sorted(DISABLED_OFFENSIVE):
        pe(f"    {x}")
    print()
    pb("  Atomic Terminal is for diagnosing and inspecting YOUR own")
    pb("  machine. Use the Atomic Academy content to learn offensive")
    pb("  concepts in the simulator.")

def cmd_clear(_): clr()

# ── DEVICE CHECKUP (consent-gated, defensive) ─────────────────────────────
#
#  Atomic Device Checkup is a real, terminal-only tool that inspects YOUR
#  own device with explicit consent. It is read-only by default; any change
#  to disk requires typing an exact confirmation phrase. No silent action,
#  no payload generation, no exploit logic, no offensive scanning of
#  remote hosts. POSIX & Windows aware.

DEVICE_CONSENT_PHRASE = "I OWN THIS DEVICE AND ALLOW ATOMIC TO CHECK IT"
DEVICE_LOG_PATH = os.path.join(APP_DIR, "logs.txt")

# In-memory findings populated by scanners; consumed by `fix`.
DEVICE_FINDINGS = {
    "files":     [],   # [{"path": str, "reason": str}]
    "startup":   [],   # [{"path": str, "reason": str}]
    "processes": [],   # [{...proc fields, "reason": str}]
    "network":   [],   # [{"row": dict,  "reason": str}]
}

SUSPICIOUS_NAME_PATTERNS = re.compile(
    r"(crack|keygen|payload|exploit|trojan|backdoor|botnet|miner|stealer|"
    r"ransom|dropper|rootkit|c2[_\- ]?beacon|unknown_agent|updater_service)"
    r"|(?:^|[\.\-_ ])rat(?=[\.\-_ ]|$)",
    re.I,
)
RISKY_EXTS = {".exe", ".bat", ".cmd", ".com", ".scr", ".vbs", ".vbe",
              ".ps1", ".jse", ".wsf", ".jar", ".pif", ".reg", ".msi",
              ".sh", ".js", ".docm", ".xlsm", ".dmg", ".pkg"}
DOUBLE_EXT_PATTERN = re.compile(
    # doc-looking extension followed ONLY by an executable/script extension
    # (the actual phishing trick — pretends to be a document, runs as code)
    r"\.(pdf|jpg|jpeg|png|gif|doc|docx|xls|xlsx|txt|zip|rar|mp3|mp4|mov|csv)"
    r"\.(exe|bat|cmd|com|scr|vbs|vbe|ps1|jse|wsf|jar|pif|reg|msi|sh|js)$",
    re.I,
)

def _device_log(msg: str):
    try:
        _ensure_dirs()
        with open(DEVICE_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{_utcnow_iso()}] {msg}\n")
    except Exception:
        pass
    # Also append to ~/.atomic/session.log so a single timeline lives there too.
    try:
        log_event("device: " + msg)
    except Exception:
        pass

# Paths Atomic refuses to delete from, ever. Defence in depth on top of
# the user-confirmation phrase.
_SYSTEM_PATH_PREFIXES_POSIX = (
    "/System/", "/usr/", "/bin/", "/sbin/", "/Library/",
    "/private/var/", "/etc/", "/lib/", "/lib64/", "/var/db/",
    "/Applications/", "/boot/", "/dev/", "/proc/", "/sys/",
)
_SYSTEM_PATH_PREFIXES_WIN = (
    r"c:\windows", r"c:\program files", r"c:\program files (x86)",
    r"c:\programdata",
)

def _is_system_path(path: str) -> bool:
    if not path:
        return True
    if IS_WIN:
        norm = os.path.normpath(path).lower()
        return any(norm.startswith(p) for p in _SYSTEM_PATH_PREFIXES_WIN)
    return any(path.startswith(p) for p in _SYSTEM_PATH_PREFIXES_POSIX)

def _detect_os_label() -> str:
    if IS_MAC:   return "macOS"
    if IS_LINUX: return "Linux"
    if IS_WIN:   return "Windows"
    return OS_NAME or "unknown"

def _print_device_banner():
    section("ATOMIC DEVICE CHECKUP — LEGAL USE REQUIRED")
    pb("  This tool inspects your OWN device for security issues.")
    print()
    pb("  Atomic will:")
    pb("    · only scan what you allow")
    pb("    · never run hidden actions")
    pb("    · never delete files without confirmation")
    print()
    pb("  You confirm:")
    pb("    1. You own this device")
    pb("    2. You allow Atomic to inspect selected files/folders")
    pb("    3. You take responsibility for actions you approve")

def _has_device_consent() -> bool:
    cfg = load_config()
    return bool(cfg.get("deviceConsent"))

def _grant_device_consent() -> bool:
    _print_device_banner()
    print()
    pc("  Type EXACTLY:")
    pb(f"    {DEVICE_CONSENT_PHRASE}")
    print()
    try:
        answer = input(_c("  > ", G))
    except (EOFError, KeyboardInterrupt):
        print(); pe("  consent rejected (no input)")
        _device_log("consent rejected: no input")
        return False
    if answer.strip() != DEVICE_CONSENT_PHRASE:
        pe("  ✗ consent phrase did not match exactly. Aborting.")
        _device_log("consent rejected: phrase mismatch")
        return False
    cfg = load_config()
    cfg["deviceConsent"] = True
    cfg["deviceConsentAt"] = _utcnow_iso()
    cfg["consentTimestamp"] = int(time.time())
    cfg["consentTimestampISO"] = _utcnow_iso()
    save_config(cfg)
    print()
    ph("  ✓ consent recorded in ~/.atomic/config.json")
    _device_log("consent granted")
    return True

def _require_device_consent() -> bool:
    if _has_device_consent():
        return True
    pw("  device checkup consent required.")
    pd("  run:  device     to read the agreement and grant consent.")
    return False

def cmd_device_checkup(_args):
    """Hub command. First run prompts for consent; afterward shows the guided menu."""
    if not _has_device_consent():
        if not _grant_device_consent():
            return
    print()
    pc("  [ATOMIC]")
    pb(f"  System detected: {_detect_os_label()}")
    print()
    section("[ATOMIC DEVICE CHECKUP]")
    pb("  What do you want to check?")
    print()
    pb("    1. Full quick check")
    pb("    2. Folder scan")
    pb("    3. Startup items")
    pb("    4. Processes")
    pb("    5. Network connections")
    pb("    6. Browser safety")
    pb("    7. Fix suspicious item")
    print()
    pd("  also:  amihacked  · device-logs  · scan suspicious")
    print()
    _device_log("device checkup hub opened")
    try:
        choice = input(_c("  choose [1-7] (Enter to skip): ", G)).strip()
    except (EOFError, KeyboardInterrupt):
        print(); return
    if not choice:
        return
    handlers = {
        "1": (cmd_scan_device,     []),
        "2": (cmd_scan_folder,     []),
        "3": (cmd_scan_startup,    []),
        "4": (cmd_scan_processes,  []),
        "5": (cmd_scan_network,    []),
        "6": (cmd_browser_safety,  []),
        "7": (cmd_fix,             []),
    }
    sel = handlers.get(choice)
    if not sel:
        pe("  invalid choice."); return
    fn, fn_args = sel
    _device_log(f"hub menu choice: {choice}")
    fn(fn_args)

# ---- Folder scan ---------------------------------------------------------

def _classify_file(name: str, full_path: str, st) -> str | None:
    low = name.lower()
    if SUSPICIOUS_NAME_PATTERNS.search(low):
        return "name pattern (crack/keygen/payload/etc.)"
    if DOUBLE_EXT_PATTERN.search(low):
        return "double extension"
    ext = os.path.splitext(low)[1]
    if ext in RISKY_EXTS:
        return f"executable extension ({ext})"
    if name.startswith(".") and not stat.S_ISDIR(st.st_mode) and len(name) > 1:
        return "hidden file"
    return None

def cmd_scan_folder(args):
    if not _require_device_consent(): return
    if args:
        path = _safe_abspath(" ".join(args))
    else:
        try:
            raw = input(_c("  Enter folder path to scan: ", G))
        except (EOFError, KeyboardInterrupt):
            print(); return
        path = _safe_abspath(raw.strip())
    if not path or not os.path.exists(path):
        err_path_not_found(path); return
    if not os.path.isdir(path):
        lbl_err(f"not a directory: {path}"); return
    if not os.access(path, os.R_OK):
        err_permission(path); return

    _device_log(f"folder scan start: {path}")
    section(f"FOLDER SCAN · {path}")

    suspicious, safe, recent = [], [], []
    cutoff = time.time() - 7 * 86400
    scanned = 0
    LIMIT = 5000
    for root, dirs, files in os.walk(path, onerror=lambda e: None):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "__pycache__", "venv", ".git")]
        for fname in files:
            full = os.path.join(root, fname)
            try:
                st = os.lstat(full)
            except OSError:
                continue
            reason = _classify_file(fname, full, st)
            if reason:
                suspicious.append({"path": full, "reason": reason})
            else:
                safe.append(full)
            try:
                if st.st_mtime >= cutoff:
                    recent.append(full)
            except Exception:
                pass
            scanned += 1
            if scanned >= LIMIT:
                pd(f"  … scan truncated at {LIMIT} files"); break
        if scanned >= LIMIT: break

    pc(f"  [SCAN RESULT]   {scanned} file(s) scanned")
    print()
    if suspicious:
        pw(f"  Suspicious files:  ({len(suspicious)})")
        for entry in suspicious[:60]:
            pw(f"    ⚠  {entry['path']}")
            pd(f"        reason: {entry['reason']}")
        if len(suspicious) > 60:
            pd(f"    … +{len(suspicious)-60} more")
    else:
        ph("  ✓ no files matched the suspicious heuristics")

    print()
    pc(f"  Recently modified (last 7d): {len(recent)}")
    for fp in recent[:8]:
        try:
            ts = datetime.fromtimestamp(os.path.getmtime(fp)).strftime('%Y-%m-%d %H:%M')
        except Exception:
            ts = "?"
        pb(f"    {ts}  {fp}")
    if len(recent) > 8:
        pd(f"    … +{len(recent)-8} more")

    print()
    pd(f"  Safe files: {len(safe)}  (showing first 5)")
    for fp in safe[:5]:
        pb(f"    {fp}")

    DEVICE_FINDINGS["files"] = suspicious
    _device_log(f"folder scan done: {len(suspicious)} suspicious / {scanned} scanned in {path}")
    if suspicious:
        print()
        pc("  next:  type  fix   to review & act on these findings")

# ---- System / processes / startup / network scans ------------------------

def cmd_scan_system(_args):
    if not _require_device_consent(): return
    _device_log("system scan")
    pc("  [ATOMIC]")
    pb(f"  System detected: {_detect_os_label()}")
    cmd_sysinfo([])

def cmd_scan_processes(_args):
    if not _require_device_consent(): return
    _device_log("process scan")
    procs = _list_processes()
    section(f"PROCESS SCAN  ({len(procs)} total)")
    flagged = []
    for pr in procs:
        reason = None
        name = pr.get("name", "") or ""
        if SUSPICIOUS_NAME_PATTERNS.search(name):
            reason = "suspicious name pattern"
        elif pr.get("cpu", 0) >= 80.0:
            reason = f"very high CPU ({pr['cpu']:.1f}%)"
        elif pr.get("mem", 0) >= 25.0:
            reason = f"very high memory ({pr['mem']:.1f}%)"
        if reason:
            flagged.append({**pr, "reason": reason})
    if flagged:
        pw(f"  Flagged processes: {len(flagged)}")
        pc(f"  {'PID':>7}  {'CPU%':>6}  {'MEM%':>6}  NAME")
        for pr in flagged:
            pw(f"  {pr['pid']:>7}  {pr['cpu']:>5.1f}  {pr['mem']:>5.1f}  {pr['name']}")
            pd(f"           reason: {pr['reason']}")
    else:
        ph("  ✓ nothing unusual in the process list")

    print()
    pc("  Top by CPU (informational)")
    pc(f"  {'PID':>7}  {'USER':<12}  {'CPU%':>6}  {'MEM%':>6}  NAME")
    for pr in procs[:10]:
        pb(f"  {pr['pid']:>7}  {(pr.get('user') or '')[:12]:<12}  {pr['cpu']:>5.1f}  {pr['mem']:>5.1f}  {pr['name']}")
    DEVICE_FINDINGS["processes"] = flagged

def _scan_startup_entries() -> list:
    flagged = []
    suspicious_cmd_re = re.compile(
        r"(curl\s+http|wget\s+http|/tmp/|nc\s+-e|bash\s+-i|base64\s+-d|powershell.*-enc)", re.I)
    if IS_MAC:
        for d in ("/Library/LaunchDaemons", "/Library/LaunchAgents",
                  os.path.expanduser("~/Library/LaunchAgents")):
            if not os.path.isdir(d): continue
            try: names = os.listdir(d)
            except Exception: continue
            for name in names:
                if not name.endswith(".plist"): continue
                full = os.path.join(d, name)
                try:
                    with open(full, "rb") as f:
                        data = f.read(8192).decode("utf-8", errors="ignore")
                except Exception:
                    continue
                if suspicious_cmd_re.search(data):
                    flagged.append({"path": full, "reason": "remote/temp/encoded command in plist"})
                elif SUSPICIOUS_NAME_PATTERNS.search(name):
                    flagged.append({"path": full, "reason": "suspicious filename"})
    elif IS_LINUX:
        for d in ("/etc/systemd/system", os.path.expanduser("~/.config/autostart")):
            if not os.path.isdir(d): continue
            try: names = os.listdir(d)
            except Exception: continue
            for name in names:
                full = os.path.join(d, name)
                try:
                    with open(full, "r", errors="ignore") as f:
                        data = f.read(8192)
                except Exception:
                    continue
                if suspicious_cmd_re.search(data):
                    flagged.append({"path": full, "reason": "remote/temp/encoded command in unit"})
                elif SUSPICIOUS_NAME_PATTERNS.search(name):
                    flagged.append({"path": full, "reason": "suspicious filename"})
    elif IS_WIN:
        rc, out, _ = run(["wmic", "startup", "get", "Caption,Command,Location", "/format:list"], timeout=8)
        if rc == 0:
            block = {}
            for line in out.splitlines() + [""]:
                if "=" in line:
                    k, v = line.split("=", 1)
                    block[k.strip()] = v.strip()
                elif not line.strip() and block:
                    cmd_str = block.get("Command", "")
                    cap     = block.get("Caption", "")
                    if suspicious_cmd_re.search(cmd_str) or re.search(r"\\Temp\\", cmd_str, re.I):
                        flagged.append({"path": cap or cmd_str,
                                        "reason": "remote/encoded/temp command"})
                    elif SUSPICIOUS_NAME_PATTERNS.search(cap):
                        flagged.append({"path": cap, "reason": "suspicious name"})
                    block = {}
    return flagged

def cmd_scan_startup(_args):
    if not _require_device_consent(): return
    _device_log("startup scan")
    cmd_startup_items([])
    print()
    section("STARTUP SCAN — flagged entries")
    flagged = _scan_startup_entries()
    if flagged:
        pw(f"  Flagged: {len(flagged)}")
        for entry in flagged:
            pw(f"    ⚠  {entry['path']}")
            pd(f"        reason: {entry['reason']}")
        print()
        pc("  next:  type  fix   to disable an entry")
    else:
        ph("  ✓ nothing obviously suspicious in checked startup locations")
    DEVICE_FINDINGS["startup"] = flagged

def cmd_scan_network(_args):
    if not _require_device_consent(): return
    _device_log("network scan")
    rows = _socket_table(all_sockets=False)
    all_rows = _socket_table(all_sockets=True)

    section("NETWORK SCAN — listening sockets")
    if rows:
        pc(f"  {'PROTO':<6}{'LOCAL':<28}{'STATE':<14}PID")
        for r in rows[:60]:
            pb(f"  {r['proto']:<6}{r['local'][:26]:<28}{r['state'][:12]:<14}{r['pid']}")
        if len(rows) > 60:
            pd(f"  … +{len(rows)-60} more")
    else:
        pd("  no listening sockets reported")

    common_listen = {22, 53, 80, 88, 123, 137, 138, 139, 143, 443, 445, 465,
                     587, 631, 993, 995, 1900, 3306, 3389, 5353, 5432, 5900,
                     8000, 8080, 8443, 17500}
    flagged = []
    for r in rows:
        local = r.get("local", "")
        m = re.search(r":(\d+)$", local)
        if not m: continue
        try:
            port = int(m.group(1))
        except ValueError:
            continue
        if port not in common_listen:
            flagged.append({"row": r, "reason": f"unusual listen port :{port}"})
    print()
    if flagged:
        pw(f"  Flagged: {len(flagged)}")
        for entry in flagged[:30]:
            r = entry["row"]
            pw(f"    ⚠  {r['proto']:<5}  {r['local']}  pid={r['pid']}")
            pd(f"        {entry['reason']}")
    else:
        ph("  ✓ no unusual listen ports")
    DEVICE_FINDINGS["network"] = flagged

    print()
    sample = [r for r in all_rows if r.get("remote")][:20]
    pc(f"  Active connections sample ({len(sample)} of {sum(1 for r in all_rows if r.get('remote'))}):")
    for r in sample:
        pb(f"    {r['proto']:<5}  {r['local']:<28} → {r['remote']:<28}  {r['state']}")

def cmd_scan(args):
    if not args:
        section("ATOMIC SCAN")
        pb("  usage:")
        pb("    scan folder       inspect a folder for risky files")
        pb("    scan system       host overview")
        pb("    scan processes    running processes")
        pb("    scan startup      login / launch items")
        pb("    scan network      listening sockets + connections")
        return
    sub = args[0].lower()
    rest = args[1:]
    fn = {
        "folder":    cmd_scan_folder,
        "system":    cmd_scan_system,
        "processes": cmd_scan_processes,
        "process":   cmd_scan_processes,
        "proc":      cmd_scan_processes,
        "startup":   cmd_scan_startup,
        "network":   cmd_scan_network,
        "net":       cmd_scan_network,
    }.get(sub)
    if fn:
        fn(rest); return
    pe(f"  unknown scan: {sub}")
    pd("  try:  scan folder | scan system | scan processes | scan startup | scan network")

# ---- Combined scans / walkthroughs --------------------------------------

def cmd_scan_device(_args):
    """Full quick check — runs the read-only scanners back to back."""
    if not _require_device_consent(): return
    _device_log("scan device (full quick check)")
    section("FULL QUICK CHECK")
    pc("  [ATOMIC]")
    pb(f"  System detected: {_detect_os_label()}")
    print(); cmd_scan_system([])
    print(); cmd_scan_processes([])
    print(); cmd_scan_startup([])
    print(); cmd_scan_network([])
    print()
    ph("  full quick check done.")
    pd("  type  fix suspicious   to act on flagged file or startup items.")

def cmd_scan_suspicious(_args):
    """Read-only audit-style sweep using existing safe checks."""
    if not _require_device_consent(): return
    _device_log("scan suspicious (audit sweep)")
    section("SCAN · SUSPICIOUS  (read-only audit sweep)")
    print(); pc("  · startup items");           cmd_startup_items([])
    print(); pc("  · suspicious startup heuristics"); cmd_suspicious_startup([])
    print(); pc("  · top processes (by CPU)");  cmd_processes(["10"])
    print(); pc("  · listening sockets");       cmd_listening([])
    print(); pc("  · weak permissions in $HOME"); cmd_weak_perms([])
    print(); pc("  · firewall");                cmd_firewall([])
    print(); pc("  · updates");                 cmd_updates_check([])
    print()
    ph("  audit sweep complete.")
    pd("  next:  scan folder <path>   for a specific folder")
    pd("         fix suspicious        to act on flagged items")

# ---- Browser safety (read-only metadata only) ---------------------------

def _count_dir_entries(path: str, hidden: bool = False) -> int | None:
    if not os.path.isdir(path):
        return None
    try:
        entries = os.listdir(path)
    except Exception:
        return None
    if not hidden:
        entries = [e for e in entries if not e.startswith(".")]
    return len(entries)

def _browser_locations() -> list:
    if IS_MAC:
        sup = os.path.expanduser("~/Library/Application Support")
        return [
            ("Chrome",   os.path.join(sup, "Google", "Chrome")),
            ("Brave",    os.path.join(sup, "BraveSoftware", "Brave-Browser")),
            ("Edge",     os.path.join(sup, "Microsoft Edge")),
            ("Firefox",  os.path.join(sup, "Firefox")),
            ("Safari",   os.path.expanduser("~/Library/Safari")),
        ]
    if IS_LINUX:
        return [
            ("Chrome",   os.path.expanduser("~/.config/google-chrome")),
            ("Chromium", os.path.expanduser("~/.config/chromium")),
            ("Brave",    os.path.expanduser("~/.config/BraveSoftware/Brave-Browser")),
            ("Firefox",  os.path.expanduser("~/.mozilla/firefox")),
        ]
    if IS_WIN:
        local   = os.environ.get("LOCALAPPDATA", "")
        roaming = os.environ.get("APPDATA", "")
        return [
            ("Chrome",  os.path.join(local,   "Google", "Chrome", "User Data")),
            ("Edge",    os.path.join(local,   "Microsoft", "Edge", "User Data")),
            ("Firefox", os.path.join(roaming, "Mozilla", "Firefox")),
            ("Brave",   os.path.join(local,   "BraveSoftware", "Brave-Browser", "User Data")),
        ]
    return []

def cmd_browser_safety(_args):
    """List installed-browser profile dirs and extension counts. Read-only."""
    if not _require_device_consent(): return
    _device_log("browser safety scan")
    section("BROWSER SAFETY  (read-only metadata only)")
    pd("  Atomic does NOT read cookies, history, passwords, or saved form data.")
    pd("  This check only lists profile directories and extension counts.")
    print()
    found_any = False
    for name, path in _browser_locations():
        if os.path.isdir(path):
            found_any = True
            pc(f"  {name}")
            pb(f"    profile dir : {path}")
            ext_count = None
            for sub in ("Default/Extensions", "Profile 1/Extensions"):
                cand = os.path.join(path, *sub.split("/"))
                ext_count = _count_dir_entries(cand)
                if ext_count is not None:
                    pb(f"    extensions  : {ext_count}    ({cand})")
                    break
            if ext_count is None and name == "Firefox":
                # Firefox profiles
                profiles = []
                try:
                    for entry in os.listdir(path):
                        if entry.endswith(".default") or ".default-release" in entry:
                            profiles.append(entry)
                except Exception:
                    pass
                if profiles:
                    pb(f"    profiles    : {', '.join(profiles)}")
        else:
            pd(f"  {name}: not installed (no profile dir)")
    if not found_any:
        pd("  no recognised browser profile dirs found.")
    print()
    pb("  Recommended manual checks (in your browser UI, not in Atomic):")
    pd("    · review the installed extension list — uninstall anything you don't recognise")
    pd("    · clear cookies/cache for sessions you no longer use")
    pd("    · turn on auto-update for the browser itself")

# ---- Am I hacked? walkthrough -------------------------------------------

def cmd_amihacked(_args):
    """Guided sequence of read-only checks the user steps through."""
    if not _has_device_consent():
        if not _grant_device_consent():
            return
    _device_log("amihacked walkthrough started")
    section("AM I HACKED? — guided walkthrough")
    detected = _detect_os_label()
    pb(f"  detected OS: {detected}")
    pb("  if that's wrong, type one of:  mac · windows · linux  (Enter to keep detected):")
    try:
        choice = input(_c("  > ", G)).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print(); return
    if choice in ("mac", "macos", "darwin"):
        os_label = "macOS"
    elif choice in ("windows", "win", "win32"):
        os_label = "Windows"
    elif choice in ("linux",):
        os_label = "Linux"
    else:
        os_label = detected
    pc(f"  running checks for: {os_label}")
    print()
    pd("  press Enter after each step to continue, or Ctrl+C to stop.")
    steps = [
        ("processes",          cmd_processes,           ["15"]),
        ("startup items",      cmd_startup_items,       []),
        ("listening sockets",  cmd_listening,           []),
        ("firewall",           cmd_firewall,            []),
        ("suspicious startup", cmd_suspicious_startup,  []),
        ("audit quick",        cmd_audit,               ["quick"]),
    ]
    for label, fn, fn_args in steps:
        section(f"step · {label}")
        try:
            fn(fn_args)
        except Exception as ex:
            pe(f"  step failed: {ex}")
        try:
            input(_c("  press Enter to continue ", DM))
        except (EOFError, KeyboardInterrupt):
            print(); break
    print()
    ph("  walkthrough complete.")
    pd("  none of these alone proves compromise. Look for COMBINATIONS:")
    pd("    · unfamiliar listening ports + unknown processes")
    pd("    · suspicious startup items + recently modified unknown files")
    pd("    · firewall disabled + unexpected outbound connections")
    pd("  if anything looks wrong, run:  scan folder <path>   then   fix suspicious")
    _device_log("amihacked walkthrough complete")

# ---- Fix mode (consent + exact-phrase confirmation per action) -----------

def _collect_fix_issues() -> list:
    out = []
    for entry in DEVICE_FINDINGS.get("files", []):
        out.append({"kind": "file",    "path": entry["path"], "reason": entry["reason"]})
    for entry in DEVICE_FINDINGS.get("startup", []):
        out.append({"kind": "startup", "path": entry["path"], "reason": entry["reason"]})
    return out

def cmd_fix(_args):
    if not _require_device_consent(): return
    _device_log("fix suspicious opened")
    section("FIX SUSPICIOUS")
    issues = _collect_fix_issues()
    if not issues:
        pd("  no findings yet. run a scan first:")
        pb("    scan folder       (populates removable file findings)")
        pb("    scan startup      (populates disable-able startup findings)")
        pb("    scan suspicious   (broad read-only sweep)")
        return
    pb(f"  Issues found: {len(issues)}")
    for i, it in enumerate(issues, 1):
        pw(f"    {i}. [{it['kind']}] {it['path']}")
        pd(f"        why: {it['reason']}")
    print()
    pc("  Recommended order — try MANUAL removal first:")
    pb("    1. open the file's location in Finder / Explorer / your file manager")
    pb("    2. inspect the file before deleting (right-click → Get Info / Properties)")
    pb("    3. only use Atomic to delete files you cannot reach manually")
    print()
    pc("  Action options:")
    pb("    1. remove a file       (single file; needs phrase 'DELETE THIS FILE')")
    pb("    2. disable startup     (rename to .disabled; needs 'DISABLE STARTUP')")
    pb("    3. ignore              (do nothing)")
    try:
        choice = input(_c("  choice [1/2/3]: ", G)).strip()
    except (EOFError, KeyboardInterrupt):
        print(); return
    if choice in ("3", ""):
        pd("  no action taken."); _device_log("fix: ignored"); return
    if choice == "1":
        _fix_remove_file(issues); return
    if choice == "2":
        _fix_disable_startup(issues); return
    pe("  invalid choice. nothing done.")

def _pick_issue(issues, kinds):
    matches = [it for it in issues if it["kind"] in kinds]
    if not matches:
        pd(f"  no findings of kind: {', '.join(kinds)}"); return None
    pc("  which entry?")
    for i, it in enumerate(matches, 1):
        pb(f"    {i}. {it['path']}")
        pd(f"        {it['reason']}")
    try:
        idx = input(_c("  number: ", G)).strip()
    except (EOFError, KeyboardInterrupt):
        print(); return None
    if not idx.isdigit(): return None
    n = int(idx)
    if not (1 <= n <= len(matches)): return None
    return matches[n-1]

def _fix_remove_file(issues):
    pick = _pick_issue(issues, kinds=("file",))
    if not pick: return
    target = pick["path"]
    # Hard guards — beyond the user phrase.
    if os.path.isdir(target):
        pe("  refused: target is a folder. Atomic only removes single files.")
        _device_log(f"delete refused (folder): {target}")
        return
    if os.path.islink(target):
        pe("  refused: target is a symlink. Resolve & inspect manually.")
        _device_log(f"delete refused (symlink): {target}")
        return
    if not os.path.isfile(target):
        pe(f"  refused: not a regular file: {target}"); return
    if _is_system_path(target):
        pe("  refused: this looks like a SYSTEM path. Atomic will not delete system files.")
        pd("  (matched against /System, /usr, /bin, /Library, /Applications, %WinDir%, …)")
        _device_log(f"delete refused (system path): {target}")
        return
    print()
    pw("  [CONFIRMATION REQUIRED]")
    pw("  You are about to delete:")
    pb(f"    {target}")
    print()
    pc("  Type EXACTLY:")
    pb("    DELETE THIS FILE")
    try:
        confirm = input(_c("  > ", G))
    except (EOFError, KeyboardInterrupt):
        print(); pd("  cancelled."); return
    if confirm.strip() != "DELETE THIS FILE":
        pe("  ✗ phrase did not match. NOT deleted.")
        _device_log(f"delete refused (phrase mismatch): {target}")
        return
    try:
        os.remove(target)
        ph(f"  ✓ removed: {target}")
        _device_log(f"deleted: {target}")
        DEVICE_FINDINGS["files"] = [e for e in DEVICE_FINDINGS["files"] if e["path"] != target]
    except Exception as ex:
        pe(f"  delete failed: {ex}")
        _device_log(f"delete failed: {target} :: {ex}")

def _fix_disable_startup(issues):
    if not IS_POSIX:
        pw("  on Windows, disable startup entries via Task Manager → Startup tab.")
        pd("  Atomic will not edit the Windows registry from a checkup.")
        return
    pick = _pick_issue(issues, kinds=("startup",))
    if not pick: return
    target = pick["path"]
    if not os.path.isfile(target):
        pe(f"  not a regular file: {target}"); return
    print()
    pw("  [CONFIRMATION REQUIRED]")
    pw("  You are about to disable (rename → .disabled):")
    pb(f"    {target}")
    print()
    pc("  Type EXACTLY:")
    pb("    DISABLE STARTUP")
    try:
        confirm = input(_c("  > ", G))
    except (EOFError, KeyboardInterrupt):
        print(); pd("  cancelled."); return
    if confirm.strip() != "DISABLE STARTUP":
        pe("  ✗ phrase did not match. NOT changed.")
        _device_log(f"disable refused: {target}")
        return
    new_path = target + ".disabled"
    if os.path.exists(new_path):
        pe(f"  destination already exists: {new_path}"); return
    try:
        os.rename(target, new_path)
        ph(f"  ✓ renamed → {new_path}")
        _device_log(f"disabled startup: {target} -> {new_path}")
        DEVICE_FINDINGS["startup"] = [e for e in DEVICE_FINDINGS["startup"] if e["path"] != target]
    except PermissionError:
        pe("  permission denied. system locations may need elevated rights.")
        pd("  Atomic does not request elevation; do this manually if you intend to.")
        _device_log(f"disable perm-denied: {target}")
    except Exception as ex:
        pe(f"  rename failed: {ex}")
        _device_log(f"disable failed: {target} :: {ex}")

# ---- Health, quarantine, undo, checkall ---------------------------------

QUARANTINE_DIR   = os.path.join(APP_DIR, "quarantine")
QUARANTINE_INDEX = os.path.join(QUARANTINE_DIR, "index.json")
CHECKALL_PHRASE  = "START CHECKALL"

def _ensure_quarantine_dir():
    try:
        os.makedirs(QUARANTINE_DIR, exist_ok=True)
    except Exception:
        pass

def _load_quarantine_index() -> list:
    _ensure_quarantine_dir()
    if not os.path.isfile(QUARANTINE_INDEX):
        return []
    try:
        with open(QUARANTINE_INDEX, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _save_quarantine_index(index: list):
    _ensure_quarantine_dir()
    try:
        tmp = QUARANTINE_INDEX + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2)
        os.replace(tmp, QUARANTINE_INDEX)
    except Exception as ex:
        pe(f"  index write failed: {ex}")

def _hash_file_sha256(path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def _firewall_state_summary() -> str:
    if IS_MAC:
        rc, out, _ = run(["/usr/libexec/ApplicationFirewall/socketfilterfw",
                          "--getglobalstate"])
        if rc == 0 and out.strip():
            return out.strip().splitlines()[0]
    elif IS_LINUX:
        for c in (["ufw", "status"], ["firewall-cmd", "--state"]):
            if have(c[0]):
                rc, out, _ = run(c, timeout=5)
                if rc == 0 and out.strip():
                    return out.strip().splitlines()[0]
        return "no firewall tool detected"
    elif IS_WIN:
        rc, out, _ = run(["netsh", "advfirewall", "show", "currentprofile",
                          "state"], timeout=5)
        if rc == 0:
            for line in out.splitlines():
                if "State" in line:
                    return line.strip()
    return "unknown"

def _updates_summary() -> str:
    if IS_MAC:
        return "use 'updates-check' to query softwareupdate"
    if IS_LINUX:
        if have("apt"):    return "apt available — try 'updates-check'"
        if have("dnf"):    return "dnf available"
        if have("pacman"): return "pacman available"
    if IS_WIN:
        return "Windows Update — check via system settings"
    return "unknown"

def _firewall_is_off(state: str) -> bool:
    s = state.lower()
    return ("disabled" in s) or (" off" in s) or s.endswith("off") or "inactive" in s

def cmd_health(_args):
    section("[ATOMIC HEALTH]")
    risk = 0
    notes = []

    pb(f"  OS:        {os_pretty()}")
    pb(f"  Hostname:  {socket.gethostname()}")
    ut = uptime_seconds()
    if ut is not None:
        pb(f"  Uptime:    {human_duration(ut)}")

    disks = disk_list()
    if disks:
        for d in disks[:3]:
            pct = (d['used'] / d['total'] * 100) if d['total'] else 0
            if pct > 95:
                risk += 15; notes.append(f"disk {d['mount']} {pct:.0f}% full")
            elif pct > 85:
                risk += 5;  notes.append(f"disk {d['mount']} {pct:.0f}% full")
            pb(f"  Disk:      {d['mount']:<24} {human_bytes(d['used'])}/"
               f"{human_bytes(d['total'])}  ({pct:.0f}%)")

    mem = memory_info()
    if mem.get("total"):
        used = mem.get("used") or 0
        pct = used / mem["total"] * 100 if mem["total"] else 0
        if pct > 90:
            risk += 10; notes.append(f"memory {pct:.0f}% used")
        pb(f"  Memory:    {human_bytes(used)}/{human_bytes(mem['total'])}  "
           f"({pct:.0f}%)")

    cpu = cpu_info()
    if "loadavg" in cpu:
        pb(f"  CPU:       loadavg {cpu['loadavg']}  ({cpu.get('cores_logical','?')} logical)")
    else:
        pb(f"  CPU:       {cpu.get('model','?')}  ({cpu.get('cores_logical','?')} logical)")

    bat = battery_info()
    if bat and "percent" in bat:
        pb(f"  Battery:   {bat['percent']}%  ({bat.get('status','?')})")
        if bat['percent'] < 15 and (bat.get('status') or '').lower() not in ("ac", "charging"):
            risk += 5; notes.append("battery low and not charging")

    fw = _firewall_state_summary()
    pb(f"  Firewall:  {fw}")
    if _firewall_is_off(fw):
        risk += 20; notes.append("firewall appears off")

    pb(f"  Updates:   {_updates_summary()}")

    risk = min(risk, 100)
    label = "low" if risk <= 25 else "medium" if risk <= 60 else "high"
    color = G if label == "low" else (YL if label == "medium" else RD)
    print()
    p(f"  Risk:      {risk}/100  ({label})", color)
    for n in notes:
        pd(f"             · {n}")
    log_event(f"health: risk={risk} ({label})")

def cmd_quarantine(args):
    if not args:
        lbl_err("usage:  quarantine <file>")
        pd("  example:  quarantine ~/Downloads/strange-installer.exe")
        pd("  also:     quarantine list   (show all quarantined files)")
        return
    if args and args[0].lower() == "list":
        cmd_quarantine_list(args[1:]); return
    path = _safe_abspath(" ".join(args))
    if not os.path.exists(path):
        err_path_not_found(path); return
    if os.path.isdir(path):
        lbl_safety("refused: target is a folder. quarantine moves single files only.")
        return
    if os.path.islink(path):
        lbl_safety("refused: target is a symlink. resolve & inspect manually first.")
        return
    if not os.path.isfile(path):
        lbl_err(f"refused: not a regular file: {path}"); return
    if not os.access(path, os.R_OK):
        err_permission(path); return
    if _is_system_path(path):
        lbl_safety("refused: this looks like a SYSTEM path. Atomic will not move system files.")
        log_event(f"quarantine refused (system path): {path}")
        return

    section(f"QUARANTINE · {path}")
    pb("  This will MOVE the file (not delete it) into:")
    pb(f"    {QUARANTINE_DIR}")
    print()
    pc("  Type QUARANTINE to move this file safely:")
    try:
        confirm = input(_c("  > ", G))
    except (EOFError, KeyboardInterrupt):
        print(); pd("  cancelled."); return
    if confirm.strip() != "QUARANTINE":
        pe("  ✗ phrase did not match. Nothing moved.")
        log_event(f"quarantine refused (phrase): {path}")
        return

    _ensure_quarantine_dir()
    sha = _hash_file_sha256(path)
    stamp = _nowstamp()
    base = os.path.basename(path) or "file"
    qpath = os.path.join(QUARANTINE_DIR, f"{stamp}__{base}")
    suffix = 1
    while os.path.exists(qpath):
        qpath = os.path.join(QUARANTINE_DIR, f"{stamp}_{suffix}__{base}")
        suffix += 1
    try:
        shutil.move(path, qpath)
    except Exception as ex:
        pe(f"  move failed: {ex}")
        log_event(f"quarantine move failed: {path} :: {ex}")
        return
    try:
        os.chmod(qpath, 0o600)
    except Exception:
        pass

    entry = {
        "originalPath":   path,
        "quarantinePath": qpath,
        "timestamp":      _utcnow_iso(),
        "sha256":         sha,
        "reason":         "manual quarantine",
        "restored":       False,
    }
    index = _load_quarantine_index()
    index.append(entry)
    _save_quarantine_index(index)
    ph(f"  ✓ moved to: {qpath}")
    pd(f"    sha256:   {sha or '(unavailable)'}")
    pd(f"    index :   {QUARANTINE_INDEX}")
    pd("  to put it back:  undo")
    log_event(f"quarantined: {path} -> {qpath} sha256={sha}")

def cmd_undo(_args):
    section("UNDO QUARANTINE")
    index = _load_quarantine_index()
    pending = [(i, e) for i, e in enumerate(index) if not e.get("restored")]
    if not pending:
        pd("  nothing to restore. quarantine index is empty (or all restored).")
        return
    idx, most = pending[-1]
    pb("  Most recent quarantined file:")
    pb(f"    original   : {most.get('originalPath','?')}")
    pb(f"    quarantine : {most.get('quarantinePath','?')}")
    pb(f"    timestamp  : {most.get('timestamp','?')}")
    if most.get("sha256"):
        pd(f"    sha256     : {most['sha256']}")
    print()
    pc("  Type RESTORE to put it back:")
    try:
        confirm = input(_c("  > ", G))
    except (EOFError, KeyboardInterrupt):
        print(); pd("  cancelled."); return
    if confirm.strip() != "RESTORE":
        pe("  ✗ phrase did not match. Nothing restored.")
        log_event(f"undo refused: {most.get('quarantinePath')}")
        return

    qpath = most.get("quarantinePath", "")
    orig  = most.get("originalPath", "")
    if not qpath or not os.path.isfile(qpath):
        pe(f"  quarantine file missing: {qpath}")
        return
    orig_dir = os.path.dirname(orig)
    if not orig_dir or not os.path.isdir(orig_dir):
        pe(f"  original folder missing: {orig_dir}")
        pd("  Atomic will not auto-create the folder. Move it manually if needed.")
        return
    target = orig
    if os.path.exists(target):
        target = os.path.join(orig_dir, "restored_" + os.path.basename(orig))
        n = 1
        while os.path.exists(target):
            target = os.path.join(orig_dir, f"restored_{n}_{os.path.basename(orig)}")
            n += 1
        pw(f"  original path occupied; restoring as:  {target}")
    try:
        shutil.move(qpath, target)
    except Exception as ex:
        pe(f"  restore failed: {ex}")
        log_event(f"undo failed: {qpath} :: {ex}")
        return
    index[idx]["restored"]   = True
    index[idx]["restoredTo"] = target
    index[idx]["restoredAt"] = _utcnow_iso()
    _save_quarantine_index(index)
    ph(f"  ✓ restored: {target}")
    log_event(f"restored: {qpath} -> {target}")

def cmd_checkall(_args):
    if not _has_device_consent():
        if not _grant_device_consent():
            return
    section("[ATOMIC CHECKALL]")
    pb("  This will scan common user folders for suspicious filenames,")
    pb("  extensions, startup items, processes, network connections, and")
    pb("  system health.")
    print()
    pb("  Atomic will not delete anything.")
    pb("  Atomic will not upload anything.")
    pb("  Atomic will not read file contents by default.")
    print()
    pc(f"  Type {CHECKALL_PHRASE} to continue:")
    try:
        confirm = input(_c("  > ", G))
    except (EOFError, KeyboardInterrupt):
        print(); pd("  cancelled."); return
    if confirm.strip() != CHECKALL_PHRASE:
        pe(f"  ✗ phrase did not match. Type exactly:  {CHECKALL_PHRASE}")
        log_event("checkall refused")
        return

    log_event("checkall started")
    started = _utcnow_iso()

    folders = []
    for sub in ("Downloads", "Desktop", "Documents"):
        cand = os.path.join(HOME, sub)
        if os.path.isdir(cand) and not os.path.islink(cand):
            folders.append(cand)

    pc("  scanning user folders (metadata only, no symlinks followed):")
    for folder in folders:
        pb(f"    · {folder}")
    if not folders:
        pd("    none of Downloads/Desktop/Documents found in $HOME")
    print()

    suspicious_files = []
    files_checked = 0
    LIMIT = 20000

    for folder in folders:
        for root, dirs, files in os.walk(folder, onerror=lambda e: None,
                                         followlinks=False):
            # don't follow symlinks
            dirs[:] = [d for d in dirs
                       if not os.path.islink(os.path.join(root, d))]
            # never descend into system paths
            dirs[:] = [d for d in dirs
                       if not _is_system_path(os.path.join(root, d))]
            # treat .app and .pkg as opaque bundles
            for dname in list(dirs):
                low = dname.lower()
                if low.endswith(".app") or low.endswith(".pkg"):
                    suspicious_files.append({
                        "path":   os.path.join(root, dname),
                        "reason": f"bundle ({os.path.splitext(low)[1]})",
                        "size":   None,
                        "mtime":  None,
                        "kind":   "bundle",
                    })
                    try: dirs.remove(dname)
                    except ValueError: pass

            for fname in files:
                full = os.path.join(root, fname)
                try:
                    st = os.lstat(full)
                except OSError:
                    continue
                files_checked += 1
                if files_checked >= LIMIT:
                    pd(f"  … truncated at {LIMIT} files (checkall safety cap)")
                    break
                reason = _classify_file(fname, full, st)
                if reason:
                    suspicious_files.append({
                        "path":   full,
                        "reason": reason,
                        "size":   st.st_size,
                        "mtime":  st.st_mtime,
                        "kind":   "file",
                    })
            if files_checked >= LIMIT: break
        if files_checked >= LIMIT: break

    procs = _list_processes()
    flagged_procs = []
    for pr in procs:
        nm = pr.get("name", "") or ""
        if SUSPICIOUS_NAME_PATTERNS.search(nm):
            flagged_procs.append({**pr, "reason": "suspicious name"})
        elif pr.get("cpu", 0) >= 80.0:
            flagged_procs.append({**pr, "reason": f"high CPU {pr['cpu']:.1f}%"})

    startup_flags = _scan_startup_entries()
    listening = _socket_table(all_sockets=False)
    fw_state = _firewall_state_summary()
    disks_data = disk_list()
    mem = memory_info()

    risk = 0
    if suspicious_files: risk += min(40, len(suspicious_files) * 5)
    if flagged_procs:    risk += min(20, len(flagged_procs) * 5)
    if startup_flags:    risk += min(20, len(startup_flags) * 10)
    if _firewall_is_off(fw_state): risk += 20
    risk = min(risk, 100)
    risk_label = "low" if risk <= 25 else "medium" if risk <= 60 else "high"

    DEVICE_FINDINGS["files"]     = [{"path": s["path"], "reason": s["reason"]}
                                    for s in suspicious_files
                                    if s.get("kind") == "file"]
    DEVICE_FINDINGS["startup"]   = startup_flags
    DEVICE_FINDINGS["processes"] = flagged_procs

    lines = []
    lines.append("ATOMIC CHECKALL REPORT")
    lines.append("=" * 60)
    lines.append(f"Started     : {started}")
    lines.append(f"Finished    : {_utcnow_iso()}")
    lines.append(f"Host        : {socket.gethostname()}")
    lines.append(f"OS          : {os_pretty()}")
    lines.append(f"Atomic      : v{VERSION}")
    lines.append("")
    lines.append("FOLDERS SCANNED")
    for folder in folders:
        lines.append(f"  · {folder}")
    if not folders:
        lines.append("  (none)")
    lines.append("")
    lines.append(f"FILES CHECKED            : {files_checked}")
    lines.append(f"SUSPICIOUS FILE FINDINGS : {len(suspicious_files)}")
    for s in suspicious_files[:200]:
        sz = human_bytes(s["size"]) if s["size"] is not None else "-"
        lines.append(f"  ⚠  {s['path']}    ({s['reason']}, {sz})")
    if len(suspicious_files) > 200:
        lines.append(f"  … +{len(suspicious_files)-200} more (truncated)")
    lines.append("")
    lines.append(f"STARTUP FINDINGS         : {len(startup_flags)}")
    for s in startup_flags:
        lines.append(f"  ⚠  {s['path']}    ({s['reason']})")
    lines.append("")
    lines.append(f"PROCESS FINDINGS         : {len(flagged_procs)}")
    for pr in flagged_procs[:50]:
        lines.append(
            f"  ⚠  pid={pr['pid']:<6} cpu={pr['cpu']:<5.1f} "
            f"mem={pr['mem']:<5.1f} {pr['name']}    ({pr['reason']})")
    lines.append("")
    lines.append(f"NETWORK (listening)      : {len(listening)}")
    for r in listening[:30]:
        lines.append(f"  {r['proto']:<5} {r['local']:<28} "
                     f"{r['state']:<10} pid={r['pid']}")
    if len(listening) > 30:
        lines.append(f"  … +{len(listening)-30} more")
    lines.append("")
    lines.append("HEALTH SUMMARY")
    if disks_data:
        for d in disks_data[:5]:
            pct = (d['used'] / d['total'] * 100) if d['total'] else 0
            lines.append(f"  disk   {d['mount']:<22} "
                         f"{human_bytes(d['used'])}/{human_bytes(d['total'])}  "
                         f"({pct:.0f}%)")
    if mem.get("total"):
        used = mem.get("used") or 0
        pct = used / mem['total'] * 100 if mem['total'] else 0
        lines.append(f"  memory {human_bytes(used)}/"
                     f"{human_bytes(mem['total'])}  ({pct:.0f}%)")
    lines.append(f"  firewall: {fw_state}")
    lines.append("")
    lines.append(f"RISK SCORE  : {risk}/100  ({risk_label})")
    lines.append("")
    lines.append("RECOMMENDED ACTIONS")
    if suspicious_files:
        lines.append("  · review listed suspicious files in your file manager FIRST")
        lines.append("  · neutralise without deleting:    quarantine <file>")
    if flagged_procs:
        lines.append("  · cross-reference flagged processes with their parent/path")
    if startup_flags:
        lines.append("  · disable unfamiliar startup entries:  fix suspicious")
    if _firewall_is_off(fw_state):
        lines.append("  · enable your OS firewall in System Settings / Control Panel")
    if not (suspicious_files or flagged_procs or startup_flags
            or _firewall_is_off(fw_state)):
        lines.append("  · nothing flagged. keep auto-updates on and re-run periodically.")
    lines.append("")
    lines.append("NEXT COMMANDS")
    lines.append("  quarantine <file>   move a file out of harm's way (reversible)")
    lines.append("  undo                restore the most recent quarantined file")
    lines.append("  report              export a system report")
    lines.append("  health              show device health")
    lines.append("")

    _ensure_dirs()
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    report_path  = os.path.join(REPORTS_DIR, f"checkall-{stamp}.txt")
    json_path    = os.path.join(REPORTS_DIR, f"checkall-{stamp}.json")

    # Build structured findings for the JSON report (no file contents).
    json_findings = []
    for s in suspicious_files:
        # Re-classify for severity/confidence so the JSON carries a full record.
        try:
            st = os.lstat(s["path"])
        except Exception:
            st = None
        finding = (classify_file_v2(os.path.basename(s["path"]), s["path"], st)
                   if st else None)
        if finding is None:
            finding = make_finding(
                type_="file", path=s["path"], reason=s.get("reason", "?"),
                severity="medium", confidence="medium",
                recommended_action="review manually",
            )
        if s.get("size") is not None: finding["size"] = s["size"]
        json_findings.append(finding)
    for s in startup_flags:
        json_findings.append(make_finding(
            type_="startup", path=s.get("path", "?"), reason=s.get("reason", "?"),
            severity="high", confidence="medium",
            recommended_action="disable via 'fix suspicious' if unfamiliar",
        ))
    for pr in flagged_procs:
        json_findings.append(make_finding(
            type_="process",
            path=f"pid={pr.get('pid','?')} {pr.get('name','?')}",
            reason=pr.get("reason", "?"),
            severity="medium", confidence="medium",
            recommended_action="cross-reference parent / image path",
        ))

    recommendations = []
    if suspicious_files:
        recommendations.append("review listed suspicious files in your file manager FIRST")
        recommendations.append("neutralise without deleting:    quarantine <file>")
    if flagged_procs:
        recommendations.append("cross-reference flagged processes with their parent/path")
    if startup_flags:
        recommendations.append("disable unfamiliar startup entries:  fix suspicious")
    if _firewall_is_off(fw_state):
        recommendations.append("enable your OS firewall in System Settings / Control Panel")
    if not recommendations:
        recommendations.append("nothing flagged. keep auto-updates on and re-run periodically.")

    json_doc = {
        "scanTime":         started,
        "finishedTime":     _utcnow_iso(),
        "atomicVersion":    VERSION,
        "host":             socket.gethostname(),
        "os":               os_pretty(),
        "foldersScanned":   folders,
        "filesChecked":     files_checked,
        "findings":         json_findings,
        "listening":        len(listening),
        "firewall":         fw_state,
        "riskScore":        risk,
        "riskLabel":        risk_label,
        "recommendations":  recommendations,
    }

    write_errors = []
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except (PermissionError, OSError) as ex:
        write_errors.append(("txt", ex))
    try:
        tmp = json_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(json_doc, f, indent=2)
        os.replace(tmp, json_path)
    except (PermissionError, OSError) as ex:
        write_errors.append(("json", ex))
    if write_errors:
        for kind, ex in write_errors:
            lbl_err(f"could not write {kind} report: {pretty_oserror(ex)}")
        log_event(f"checkall report write errors: {write_errors}")
        if len(write_errors) == 2:
            return  # both failed; abort

    _save_risk(risk, risk_label.upper(),
               reasons=[r for r in recommendations][:6],
               source="checkall",
               recommended=("downloadcheck" if suspicious_files else
                            "fix suspicious" if startup_flags else "health"))

    print()
    section("[CHECKALL COMPLETE]")
    pb(f"  Files checked    : {files_checked}")
    pb(f"  Suspicious items : {len(suspicious_files)}")
    pb(f"  Startup flags    : {len(startup_flags)}")
    pb(f"  Process flags    : {len(flagged_procs)}")
    pb(f"  Listening ports  : {len(listening)}")
    color = G if risk_label == "low" else (YL if risk_label == "medium" else RD)
    p(f"  Risk score       : {risk}/100  ({risk_label})", color)
    if not any(k == "txt" for k, _ in write_errors):
        lbl_report(f"TXT  : {report_path}")
    if not any(k == "json" for k, _ in write_errors):
        lbl_report(f"JSON : {json_path}")
    print()
    lbl_next("Run:")
    pb("    quarantine <file>   move a file out of harm's way (reversible)")
    pb("    fix suspicious      review actions for findings")
    pb("    health              device health snapshot")
    pb("    risk                show the latest score")
    log_event(f"checkall complete; risk={risk}; report={report_path}")

def cmd_device_logs(_args):
    section("ATOMIC DEVICE CHECKUP — ACTIVITY LOG")
    if not os.path.isfile(DEVICE_LOG_PATH):
        pd(f"  no log file yet at {DEVICE_LOG_PATH}")
        return
    try:
        with open(DEVICE_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as ex:
        pe(f"  read failed: {ex}"); return
    for line in lines[-200:]:
        pb("  " + line.rstrip())
    pd(f"  ({len(lines)} entr{'y' if len(lines)==1 else 'ies'} · {DEVICE_LOG_PATH})")

# ── FINDINGS ENGINE v2 ────────────────────────────────────────────────────
# Structured finding records used by quickscan / downloadcheck / checkall.
# Output is intentionally honest: confidence + severity are separate so the
# user can judge for themselves rather than be scared by every false positive.

SEVERITY_RANK    = {"low": 1, "medium": 2, "high": 3, "critical": 4}
CONFIDENCE_RANK  = {"low": 1, "medium": 2, "high": 3}

# Filenames a normal user would NOT see on a clean machine. Matched only on
# basenames, never on whole paths, to avoid spurious matches on parent dirs.
HIGH_SEVERITY_NAME = re.compile(
    r"(crack|keygen|payload|exploit|trojan|backdoor|botnet|miner|stealer|"
    r"ransom|dropper|rootkit|c2[_\- ]?beacon)"
    r"|(?:^|[\.\-_ ])rat(?=[\.\-_ ]|$)",
    re.I,
)
INSTALLER_EXTS  = {".dmg", ".pkg", ".msi", ".deb", ".rpm", ".appimage"}
EXEC_EXTS       = {".exe", ".bat", ".cmd", ".com", ".scr", ".vbs", ".vbe",
                   ".ps1", ".jse", ".wsf", ".jar", ".pif", ".reg"}
SCRIPT_EXTS     = {".sh", ".js", ".py", ".rb"}
MACRO_DOC_EXTS  = {".docm", ".xlsm", ".pptm"}

def make_finding(*, type_: str, path: str, reason: str,
                 confidence: str = "medium", severity: str = "medium",
                 recommended_action: str = "review manually") -> dict:
    return {
        "type":              type_,
        "path":              path,
        "name":              os.path.basename(path) if path else "",
        "reason":            reason,
        "confidence":        confidence if confidence in CONFIDENCE_RANK else "medium",
        "severity":          severity   if severity   in SEVERITY_RANK   else "medium",
        "recommendedAction": recommended_action,
    }

def classify_file_v2(name: str, full_path: str, st) -> dict | None:
    """Return a structured finding for a single file or None if not suspicious.

    Heuristics are conservative: most files return None. Severity scales
    with how much the name itself implies malicious intent. We never read
    file contents — only metadata.
    """
    # never flag inside system paths
    if _is_system_path(full_path):
        return None
    low = name.lower()
    if HIGH_SEVERITY_NAME.search(low):
        return make_finding(
            type_="file", path=full_path,
            reason="filename contains a known malicious-tool keyword",
            confidence="high", severity="high",
            recommended_action="quarantine if you do not recognise it",
        )
    if DOUBLE_EXT_PATTERN.search(low):
        return make_finding(
            type_="file", path=full_path,
            reason="double extension (looks like a doc but is executable)",
            confidence="high", severity="high",
            recommended_action="quarantine if you do not recognise it",
        )
    ext = os.path.splitext(low)[1]
    in_downloads = "/Downloads/" in full_path or "\\Downloads\\" in full_path
    if ext in EXEC_EXTS:
        return make_finding(
            type_="file", path=full_path,
            reason=f"executable extension ({ext})",
            confidence="high",
            severity=("high" if in_downloads else "medium"),
            recommended_action=("quarantine if you did not download it on purpose"
                                if in_downloads else "review before opening"),
        )
    if ext in SCRIPT_EXTS:
        return make_finding(
            type_="file", path=full_path,
            reason=f"script file ({ext})",
            confidence="medium",
            severity=("medium" if in_downloads else "low"),
            recommended_action=("review before running" if in_downloads else "informational"),
        )
    if ext in INSTALLER_EXTS:
        return make_finding(
            type_="file", path=full_path,
            reason=f"installer / package ({ext})",
            confidence="medium",
            severity=("medium" if in_downloads else "low"),
            recommended_action="install only if you trust the source",
        )
    if ext in MACRO_DOC_EXTS:
        return make_finding(
            type_="file", path=full_path,
            reason=f"document with macros ({ext})",
            confidence="medium", severity="medium",
            recommended_action="open in protected view; disable macros unless you trust the sender",
        )
    return None

def _print_finding_line(f: dict, idx: int | None = None):
    sev = f.get("severity", "medium").upper()
    conf = f.get("confidence", "medium")
    color = {"LOW": DM, "MEDIUM": YL, "HIGH": RD, "CRITICAL": RD}.get(sev, WH)
    head = f"  {('· ' + str(idx)+'.') if idx is not None else '·'}  {f.get('name') or f.get('path')}"
    p(head, color)
    pb(f"      Reason     : {f.get('reason','?')}")
    pb(f"      Severity   : {sev}")
    pb(f"      Confidence : {conf}")
    pb(f"      Action     : {f.get('recommendedAction','review manually')}")

# ── RISK STATE ────────────────────────────────────────────────────────────

RISK_PATH = os.path.join(APP_DIR, "risk.json")

def _load_risk_history() -> list:
    _ensure_dirs()
    if not os.path.isfile(RISK_PATH):
        return []
    try:
        with open(RISK_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []

def _save_risk(score: int, label: str, reasons: list,
               source: str, recommended: str = ""):
    history = _load_risk_history()
    history.append({
        "timestamp":   _utcnow_iso(),
        "score":       int(score),
        "label":       label,
        "reasons":     list(reasons or [])[:20],
        "source":      source,
        "recommended": recommended,
    })
    history = history[-200:]  # cap on disk
    try:
        tmp = RISK_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
        os.replace(tmp, RISK_PATH)
    except Exception:
        pass

def _latest_risk() -> dict | None:
    h = _load_risk_history()
    return h[-1] if h else None

def _risk_label(score: int) -> str:
    return "LOW" if score <= 25 else ("MEDIUM" if score <= 60 else "HIGH")

def _risk_color(label: str) -> str:
    return G if label == "LOW" else (YL if label == "MEDIUM" else RD)

# ── VERBOSE ───────────────────────────────────────────────────────────────

def cmd_verbose(args):
    if not args:
        cur = "on" if STATE.get("verbose") else "off"
        lbl_info(f"verbose is {cur}")
        pd("  usage:  verbose on  ·  verbose off")
        return
    sub = args[0].lower()
    if sub == "on":
        STATE["verbose"] = True;  save_state(STATE); lbl_ok("verbose mode ON  (full details + tracebacks)")
    elif sub == "off":
        STATE["verbose"] = False; save_state(STATE); lbl_ok("verbose mode OFF (clean output)")
    elif sub in ("status", "show"):
        lbl_info(f"verbose is {'on' if STATE.get('verbose') else 'off'}")
    else:
        lbl_err("usage:  verbose on | verbose off")

# ── SELFTEST ──────────────────────────────────────────────────────────────

def _selftest_checks() -> list:
    """Return list of (label, ok, detail) tuples."""
    out = []
    out.append(("~/.atomic exists",   os.path.isdir(APP_DIR),       APP_DIR))
    out.append(("config.json",        os.path.isfile(CONFIG_PATH),  CONFIG_PATH))
    # state.json may not exist on first run — tolerate it
    state_ok = os.path.isfile(STATE_PATH) or isinstance(STATE, dict)
    out.append(("state",              state_ok,                     STATE_PATH))
    out.append(("reports dir",        os.path.isdir(REPORTS_DIR),   REPORTS_DIR))
    out.append(("quarantine dir",     os.path.isdir(QUARANTINE_DIR),QUARANTINE_DIR))
    out.append(("session log",        os.path.isfile(LOG_PATH) or _try_touch(LOG_PATH),  LOG_PATH))
    py_ok = sys.version_info[:2] >= (3, 8)
    out.append((f"python {platform.python_version()}", py_ok, "need 3.8+"))
    out.append((f"OS detected ({_detect_os_label()})", bool(OS_NAME), OS_NAME or ""))
    out.append(("command registry",   isinstance(COMMANDS, dict) and len(COMMANDS) > 50,
                f"{len(COMMANDS) if isinstance(COMMANDS, dict) else 0} commands"))
    out.append(("health callable",    callable(globals().get("cmd_health")), ""))
    out.append(("checkall safety cap",
                isinstance(CHECKALL_PHRASE, str) and CHECKALL_PHRASE == "START CHECKALL",
                f"phrase='{CHECKALL_PHRASE}'"))
    # quarantine index read/write smoke
    qidx_ok = True
    try:
        idx = _load_quarantine_index()
        _save_quarantine_index(idx)  # round-trip
    except Exception as ex:
        qidx_ok = False
        out.append(("quarantine index r/w", False, str(ex)))
    if qidx_ok:
        out.append(("quarantine index r/w", True, QUARANTINE_INDEX))
    # required stdlib modules
    required = ("hashlib", "json", "os", "platform", "re", "shutil",
                "socket", "stat", "subprocess", "sys", "time")
    missing = [m for m in required if m not in sys.modules and __import__(m, fromlist=[''])]
    out.append(("stdlib modules",     not missing, "all present" if not missing else f"missing: {missing}"))
    return out

def _try_touch(path: str) -> bool:
    try:
        _ensure_dirs()
        if not os.path.isfile(path):
            with open(path, "a", encoding="utf-8") as f:
                f.write("")
        return os.path.isfile(path)
    except Exception:
        return False

def cmd_selftest(_args):
    section("[ATOMIC SELFTEST]")
    checks = _selftest_checks()
    groups = {
        "Config":      ["~/.atomic exists", "config.json"],
        "State":       ["state"],
        "Reports":     ["reports dir"],
        "Quarantine":  ["quarantine dir", "quarantine index r/w"],
        "Commands":    ["command registry", "health callable"],
        "Safety":      ["checkall safety cap"],
    }
    by_label = {label: (ok, detail) for label, ok, detail in checks}
    failed_any = False
    for group, labels in groups.items():
        oks = []
        for lab in labels:
            if lab in by_label:
                oks.append(by_label[lab][0])
        ok = bool(oks) and all(oks)
        if not ok: failed_any = True
        line = f"  {group:<12} {'OK' if ok else 'FAIL'}"
        p(line, G if ok else RD)
    print()
    pd("  details:")
    for label, ok, detail in checks:
        icon = "✓" if ok else "✗"
        clr  = G  if ok else RD
        det  = f"  ({detail})" if detail else ""
        p(f"    {icon}  {label}{det}", clr)
        if not ok: failed_any = True
    print()
    if failed_any:
        lbl_err("Atomic Terminal selftest reported failures.")
        pd("  fix the failing items above (e.g. re-run install.sh).")
        log_event("selftest: FAIL")
    else:
        lbl_ok("Atomic Terminal is healthy.")
        log_event("selftest: OK")

# ── QUICKSCAN ─────────────────────────────────────────────────────────────

def _scan_downloads_metadata(limit: int = 1000) -> tuple[list, int]:
    """Return (findings, files_checked). Metadata only — no contents read."""
    findings, checked = [], 0
    dl = os.path.join(HOME, "Downloads")
    if not os.path.isdir(dl):
        return findings, 0
    cutoff = time.time() - 14 * 86400
    for root, dirs, files in os.walk(dl, onerror=lambda e: None, followlinks=False):
        dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
        for fname in files:
            full = os.path.join(root, fname)
            try: st = os.lstat(full)
            except OSError: continue
            checked += 1
            f = classify_file_v2(fname, full, st)
            if f:
                try:
                    if st.st_mtime >= cutoff:
                        f["recentlyModified"] = True
                except Exception:
                    pass
                findings.append(f)
            if checked >= limit:
                return findings, checked
    return findings, checked

def cmd_quickscan(_args):
    if not _require_device_consent(): return
    section("[ATOMIC QUICKSCAN]")
    pd("  fast, read-only, metadata-only scan. nothing is opened, deleted, or uploaded.")
    print()

    # Health summary inline
    fw = _firewall_state_summary()
    fw_off = _firewall_is_off(fw)
    pb(f"  Firewall   : {fw}")
    disks = disk_list()
    if disks:
        d = disks[0]
        pct = (d['used'] / d['total'] * 100) if d['total'] else 0
        pb(f"  Disk       : {d['mount']}  {human_bytes(d['used'])}/{human_bytes(d['total'])}  ({pct:.0f}%)")
    mem = memory_info()
    if mem.get("total"):
        used = mem.get("used") or 0
        pct = used / mem["total"] * 100 if mem["total"] else 0
        pb(f"  Memory     : {human_bytes(used)}/{human_bytes(mem['total'])}  ({pct:.0f}%)")

    findings, files_checked = _scan_downloads_metadata(limit=1000)
    procs = _list_processes(limit=10)
    startup_flags = _scan_startup_entries()
    listening = _socket_table(all_sockets=False)

    pb(f"  Downloads  : {files_checked} files checked, {len(findings)} flagged")
    pb(f"  Startup    : {len(startup_flags)} flagged")
    pb(f"  Processes  : top {len(procs)} sampled")
    pb(f"  Listening  : {len(listening)} ports")

    # Risk score (capped buckets so a noisy Downloads doesn't dominate)
    score = 0; reasons = []
    if findings:
        sev_count = {"high": 0, "medium": 0, "low": 0}
        for f in findings:
            sev_count[f.get("severity", "medium")] = sev_count.get(f.get("severity", "medium"), 0) + 1
        score += min(40, sev_count.get("high", 0) * 12 + sev_count.get("medium", 0) * 5
                     + sev_count.get("low", 0) * 1)
        reasons.append(f"{len(findings)} suspicious downloads")
    if startup_flags:
        score += min(20, len(startup_flags) * 10)
        reasons.append(f"{len(startup_flags)} suspicious startup item(s)")
    if fw_off:
        score += 20; reasons.append("firewall appears off")
    score = min(100, score)
    label = _risk_label(score)
    DEVICE_FINDINGS["files"] = [{"path": f["path"], "reason": f["reason"]} for f in findings]
    DEVICE_FINDINGS["startup"] = startup_flags

    print()
    section("[QUICKSCAN COMPLETE]")
    p(f"  Risk: {score}/100  {label}", _risk_color(label))
    if reasons:
        pb("  Findings:")
        for r in reasons:
            pb(f"    - {r}")
    else:
        ph("  - nothing flagged on the fast pass")
    print()
    next_cmd = "downloadcheck" if findings else ("checkall" if not fw_off else "health")
    lbl_next("Run:")
    pb(f"    {next_cmd}")
    if findings:
        pb("    quarantine <file>   (move a file out of harm's way)")
    pb("    report              (export a system report)")

    _save_risk(score, label, reasons, source="quickscan",
               recommended=next_cmd)
    log_event(f"quickscan complete; risk={score} {label}")

# ── DOWNLOADCHECK ─────────────────────────────────────────────────────────

def cmd_downloadcheck(_args):
    if not _require_device_consent(): return
    dl = os.path.join(HOME, "Downloads")
    if not os.path.isdir(dl):
        section("[ATOMIC DOWNLOADCHECK]")
        err_path_not_found(dl)
        pd("  no Downloads folder for this user. nothing to scan.")
        return
    section(f"[ATOMIC DOWNLOADCHECK]   {dl}")
    pd("  read-only, metadata-only. nothing is opened, deleted, or uploaded.")
    print()
    findings, checked = _scan_downloads_metadata(limit=2000)
    if not findings:
        ph(f"  ✓ no suspicious files in Downloads ({checked} checked).")
        DEVICE_FINDINGS["files"] = []
        log_event(f"downloadcheck: 0 flags / {checked} checked")
        print()
        lbl_next("Run:")
        pb("    quickscan        (full fast pass)")
        pb("    health           (device health snapshot)")
        return
    findings.sort(key=lambda f: (-SEVERITY_RANK.get(f.get("severity","medium"), 0),
                                 -CONFIDENCE_RANK.get(f.get("confidence","medium"), 0)))
    pw(f"  {len(findings)} flagged file(s) of {checked} checked:")
    print()
    for i, f in enumerate(findings[:60], 1):
        _print_finding_line(f, idx=i)
        print()
    if len(findings) > 60:
        pd(f"  … +{len(findings)-60} more (truncated)")
    DEVICE_FINDINGS["files"] = [{"path": f["path"], "reason": f["reason"]} for f in findings]
    log_event(f"downloadcheck: {len(findings)} flags / {checked} checked")
    print()
    lbl_next("Recommended next:")
    pb("    quarantine <file>     (move a file safely out of the way)")
    pb("    fix suspicious        (review actions for findings)")

# ── CHECKPATH ─────────────────────────────────────────────────────────────

def cmd_checkpath(args):
    if not _require_device_consent(): return
    if not args:
        lbl_err("usage:  checkpath <folder>")
        pd("  example:  checkpath ~/Downloads")
        return
    raw = " ".join(args)
    path = _safe_abspath(raw)
    if not os.path.exists(path):
        err_path_not_found(path); return
    if not os.path.isdir(path):
        lbl_err(f"not a folder: {path}"); return
    if not os.access(path, os.R_OK):
        err_permission(path); return
    in_system = _is_system_path(path)
    section(f"[ATOMIC CHECKPATH]   {path}")
    pd("  read-only, metadata-only. nothing is opened, deleted, or uploaded.")
    if in_system:
        print()
        lbl_safety("This path is inside a SYSTEM area.")
        pd("  Atomic will not flag system files by default.")
        pb("  Type the exact path again to confirm a deeper read-only scan,")
        pb("  or press Enter to cancel:")
        try:
            confirm = input(_c("  > ", G))
        except (EOFError, KeyboardInterrupt):
            print(); pd("  cancelled."); return
        if confirm.strip() != path:
            pd("  cancelled (path did not match exactly).")
            return
    else:
        print()
        pc("  Type CHECK to begin (or Enter to cancel):")
        try:
            confirm = input(_c("  > ", G))
        except (EOFError, KeyboardInterrupt):
            print(); pd("  cancelled."); return
        if confirm.strip().upper() != "CHECK":
            pd("  cancelled."); return

    findings, checked = [], 0
    LIMIT = 5000
    for root, dirs, files in os.walk(path, onerror=lambda e: None, followlinks=False):
        dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
        if not in_system:
            dirs[:] = [d for d in dirs if not _is_system_path(os.path.join(root, d))]
        for fname in files:
            full = os.path.join(root, fname)
            try: st = os.lstat(full)
            except OSError: continue
            checked += 1
            f = classify_file_v2(fname, full, st) if not in_system else _classify_system_file(fname, full, st)
            if f: findings.append(f)
            if checked >= LIMIT:
                pd(f"  … truncated at {LIMIT} files (safety cap)")
                break
        if checked >= LIMIT: break
    print()
    if not findings:
        ph(f"  ✓ no suspicious files ({checked} checked).")
    else:
        findings.sort(key=lambda f: (-SEVERITY_RANK.get(f.get("severity","medium"), 0),
                                     -CONFIDENCE_RANK.get(f.get("confidence","medium"), 0)))
        pw(f"  {len(findings)} flagged file(s) of {checked} checked:")
        print()
        for i, f in enumerate(findings[:60], 1):
            _print_finding_line(f, idx=i); print()
        if len(findings) > 60:
            pd(f"  … +{len(findings)-60} more")
    DEVICE_FINDINGS["files"] = [{"path": f["path"], "reason": f["reason"]} for f in findings]
    log_event(f"checkpath {path}: {len(findings)} flags / {checked} checked")
    if findings:
        print()
        lbl_next("Run:")
        pb("    quarantine <file>     (move a file safely)")
        pb("    fix suspicious        (review actions)")

def _classify_system_file(name: str, full_path: str, st) -> dict | None:
    """Stricter rules when user explicitly opted into a system path."""
    low = name.lower()
    if HIGH_SEVERITY_NAME.search(low):
        return make_finding(
            type_="file", path=full_path,
            reason="malicious-tool keyword in system path",
            confidence="high", severity="critical",
            recommended_action="investigate but DO NOT delete from system; consult support",
        )
    return None

# ── RISK ──────────────────────────────────────────────────────────────────

def cmd_risk(_args):
    section("[ATOMIC RISK SCORE]")
    latest = _latest_risk()
    if not latest:
        pd("  no risk score recorded yet.")
        print()
        lbl_next("Run one of:")
        pb("    quickscan")
        pb("    checkall")
        pb("    health")
        return
    score = latest.get("score", 0)
    label = latest.get("label", _risk_label(score))
    p(f"  ATOMIC RISK SCORE: {score}/100", _risk_color(label))
    p(f"  Status: {label}",                _risk_color(label))
    pb(f"  Source: {latest.get('source','?')}    Recorded: {latest.get('timestamp','?')}")
    reasons = latest.get("reasons") or []
    if reasons:
        print()
        pb("  Reasons:")
        for r in reasons:
            pb(f"    - {r}")
    rec = latest.get("recommended") or ""
    if rec:
        print()
        lbl_next("Recommended next:")
        pb(f"    {rec}")
    else:
        print()
        lbl_next("Run:")
        pb("    downloadcheck     (focus on Downloads)")
        pb("    checkall          (full safe scan)")

# ── EXPLAIN ───────────────────────────────────────────────────────────────

EXPLAIN_RULES = [
    # (regex, summary, why_it_matters, suggested_next)
    (re.compile(r"\.docm\b", re.I),
     "A .docm is a Word document with macros enabled.",
     "Macros can run code when you open the document. They are a common phishing vector.",
     "Open in Protected View only. If you don't trust the sender, do not enable macros."),
    (re.compile(r"\.xlsm\b", re.I),
     "An .xlsm is an Excel workbook with macros enabled.",
     "Same risk as .docm — macros can execute code.",
     "Open in Protected View; never 'Enable Content' for files you didn't expect."),
    (re.compile(r"\b\w+\.pdf\.exe\b|\b\w+\.docx\.exe\b|\b\w+\.jpg\.exe\b", re.I),
     "This is a double-extension trick: it pretends to be a document but is an executable.",
     "Windows hides the real .exe extension by default, so users think they're opening a doc.",
     "Quarantine the file. Do NOT double-click."),
    (re.compile(r"\.exe\b|\.scr\b|\.bat\b|\.cmd\b|\.com\b|\.pif\b|\.vbs\b|\.ps1\b", re.I),
     "An executable / script extension on Windows.",
     "Files with these extensions can change your system. Inside Downloads, that's risky.",
     "Only run if you know exactly where the file came from."),
    (re.compile(r"^launch\s*agent|launchd|\.plist$", re.I),
     "A launchd / LaunchAgent / LaunchDaemon entry on macOS.",
     "These run code automatically at login or boot. Malware uses them for persistence.",
     "Run 'scan startup' to list them; disable any you do not recognise."),
    (re.compile(r"\bport\s*22\b|\bssh\b", re.I),
     "Port 22 / SSH — remote shell login.",
     "Open SSH means the machine can be logged into over the network. Fine if you set it up; risky if you didn't.",
     "Check System Settings → Sharing (macOS) or sshd_config (Linux). Disable if unused."),
    (re.compile(r"firewall\s*off|firewall\s*disabled", re.I),
     "Your OS firewall appears to be off.",
     "Without a firewall, every listening service on this machine is reachable from your network.",
     "Enable it: macOS → System Settings → Network → Firewall;  Windows → Windows Security."),
    (re.compile(r"\b(rat|trojan|backdoor|keylogger|stealer|miner)\b", re.I),
     "A keyword commonly seen in malicious-tool filenames.",
     "Malware authors and 'crack' bundles often label their samples this way.",
     "Quarantine if you don't know exactly what the file is."),
    (re.compile(r"\bcrack\b|\bkeygen\b", re.I),
     "Crack / keygen — software that bypasses paid licensing.",
     "These are routinely bundled with droppers, miners, or info-stealers.",
     "Delete or quarantine. There's no safe way to run them."),
    (re.compile(r"\.dmg$|\.pkg$", re.I),
     "A macOS installer.",
     "Installers can change your system. Only safe if downloaded from a source you trust.",
     "Verify the developer / publisher signature before opening."),
    (re.compile(r"\.msi$", re.I),
     "A Windows installer.",
     "Installers run with high privileges. Only safe from a source you trust.",
     "Verify publisher signature in the file's Properties → Digital Signatures tab."),
    (re.compile(r"\.sh$", re.I),
     "A shell script.",
     "Shell scripts execute commands. Inside Downloads, treat them like an .exe.",
     "Open in a text editor (TextEdit / VS Code) and read it BEFORE running."),
]

def cmd_explain(args):
    section("[ATOMIC EXPLAIN]")
    if not args:
        pd("  usage:  explain <text or filename>")
        pd("  examples:")
        pd("    explain invoice.pdf.exe")
        pd("    explain .docm")
        pd("    explain firewall off")
        pd("    explain port 22")
        return
    query = " ".join(args).strip()
    pb(f"  Query: {query}")
    print()
    matched = False
    for rx, summary, why, nxt in EXPLAIN_RULES:
        if rx.search(query):
            matched = True
            lbl_info(summary)
            pb(f"  Why it matters : {why}")
            pb(f"  What to do     : {nxt}")
            print()
    if not matched:
        lbl_warn("I cannot be fully sure from this alone.")
        pd("  Try one of:")
        pd("    quickscan         (fast safe scan of your machine)")
        pd("    downloadcheck     (only the Downloads folder)")
        pd("    checkpath <folder>")
        pd("  …or paste more context (e.g. include the file extension or the exact warning).")

# ── QUARANTINE LIST + USAGE TIGHTENING ────────────────────────────────────

def cmd_quarantine_list(_args):
    section("[QUARANTINE LIST]")
    index = _load_quarantine_index()
    if not index:
        pd("  quarantine is empty.")
        return
    pb(f"  {len(index)} entry(ies):")
    print()
    for i, e in enumerate(index, 1):
        state = "restored" if e.get("restored") else "quarantined"
        clr   = DM        if e.get("restored") else YL
        p(f"  {i:>3}. [{state}]  {e.get('originalPath','?')}", clr)
        pb(f"        moved   : {e.get('quarantinePath','?')}")
        pb(f"        time    : {e.get('timestamp','?')}")
        if e.get("sha256"):
            pd(f"        sha256  : {e['sha256']}")
        if e.get("restored"):
            pd(f"        restored: {e.get('restoredAt','?')} → {e.get('restoredTo','?')}")
    print()
    lbl_next("Run:")
    pb("    undo                (restore the most recent unrestored item)")

# ── Refusal stubs ─────────────────────────────────────────────────────────

def make_refusal(name):
    def _stub(_):
        pw(f"  [safety] `{name}` is not a command in Atomic Terminal.")
        pd("  Atomic Terminal is a local, defensive, read-only tool.")
        pd("  Learn the concept in the Academy:  lessons · exercises · rooms")
    return _stub

# ── HELP ──────────────────────────────────────────────────────────────────

HELP_GROUPS = [
    ("General",     [("help [cmd]",    "list commands · or detail one"),
                     ("version",       "show Atomic version"),
                     ("status [full]", "quick system status snapshot"),
                     ("doctor [full]", "health/setup check"),
                     ("config [k v]",  "view/set local config"),
                     ("theme [name]",  "set color theme"),
                     ("clear",         "clear screen"),
                     ("restart",       "restart the terminal process"),
                     ("update",        "how to update Atomic Terminal"),
                     ("uninstall",     "remove ~/.atomic"),
                     ("exit / quit",   "leave the REPL")]),
    ("System",      [("sysinfo",       "all-in-one system overview"),
                     ("os · hostname · uptime", "quick single values"),
                     ("cpu · memory · disk",    "resource details"),
                     ("battery · temp",         "power and thermal"),
                     ("env [filter]",  "environment variables (secrets redacted)"),
                     ("users · sessions", "active users/sessions")]),
    ("Processes",   [("processes [n]", "top N processes by CPU"),
                     ("top [n]",       "alias of processes"),
                     ("psfind <name>", "find processes matching name"),
                     ("process <pid>", "detail one process"),
                     ("startup-items", "login/startup entries"),
                     ("services",      "service manager state"),
                     ("scheduled · cron","scheduled tasks / cron entries")]),
    ("Network",     [("netinfo",       "network summary"),
                     ("interfaces",    "NICs (ifconfig/ip/ipconfig)"),
                     ("listening",     "listening TCP/UDP sockets"),
                     ("ports",         "all sockets"),
                     ("route · dns",   "routing table · DNS resolvers"),
                     ("localip · publicip", "your IPs"),
                     ("wifi-info",     "Wi-Fi status"),
                     ("ping <host> [n]",     "real ICMP ping"),
                     ("traceroute-lite <h>", "traceroute (up to 15 hops)"),
                     ("localhost-scan",      "TCP probe of loopback"),
                     ("firewall",      "firewall state")]),
    ("Filesystem",  [("ls [path]",     "list directory"),
                     ("tree [p] [d]",  "directory tree (depth d)"),
                     ("du [path]",     "disk usage breakdown"),
                     ("fileinfo <p>",  "stat + sha256"),
                     ("perms <path>",  "mode bits"),
                     ("recent-files [p] [d]", "files modified in last d days"),
                     ("large-files [p] [n]",  "top N largest files"),
                     ("search-file <pat> [p]",  "find files by name"),
                     ("search-text <text> [p]", "grep text in text files")]),
    ("Security",    [("hash <f> [algo]",      "file hash"),
                     ("integrity <path>",     "sha256 every file in a tree"),
                     ("weak-perms-scan",      "world-writable scan"),
                     ("world-writable-scan",  "alias of above"),
                     ("suspicious-startup",   "flag suspicious startup items"),
                     ("audit [quick|full]",   "defensive audit"),
                     ("security-checklist",   "quick posture checks"),
                     ("updates-check",        "outdated software / patches"),
                     ("antivirus-status",     "AV / protection status"),
                     ("ssh-check",            "~/.ssh hygiene + sshd")]),
    ("Device Checkup", [("device · checkup",   "consent + open the guided checkup menu"),
                        ("amihacked",           "guided 'am I hacked?' walkthrough"),
                        ("quickscan",           "fast safe scan (Downloads + startup + ports + firewall)"),
                        ("downloadcheck",       "scan only the Downloads folder, with severity"),
                        ("checkpath <folder>",  "scan a specific folder you choose (read-only)"),
                        ("scan",                "scan menu (folder/system/device/suspicious/…)"),
                        ("scan folder",         "inspect a folder for risky files"),
                        ("scan device",         "full quick check of this machine"),
                        ("scan suspicious",     "broad read-only audit sweep"),
                        ("scan system",         "host overview (read-only)"),
                        ("scan processes",      "scan running processes"),
                        ("scan startup",        "scan login/launch items"),
                        ("scan network",        "listening sockets + connections"),
                        ("browser-safety",      "list installed browsers & extension counts"),
                        ("fix suspicious",      "review & act on findings (exact confirmation)"),
                        ("health",              "device health snapshot + risk score"),
                        ("checkall",            "full defensive read-only scan + JSON & TXT report"),
                        ("risk",                "show latest device risk score + reasons"),
                        ("explain <text>",      "explain a finding / file / port in plain language"),
                        ("quarantine <file>",   "safely move a file out of harm's way (reversible)"),
                        ("quarantine list",     "show all quarantined items"),
                        ("undo",                "restore the most recent quarantined file"),
                        ("selftest",            "verify Atomic's own install + safety hooks"),
                        ("verbose on · off",    "toggle full details / clean output"),
                        ("device-logs",         "show ~/.atomic/logs.txt activity")]),
    ("Logs",        [("logs [n]",      "recent system log"),
                     ("authlogs [n]",  "auth / SSH log"),
                     ("bootlogs [n]",  "boot log"),
                     ("errors [n]",    "recent errors"),
                     ("warnings [n]",  "recent warnings"),
                     ("journal [n]",   "alias of logs"),
                     ("app-logs",      "application logs (macOS ~/Library/Logs)")]),
    ("Export",      [("export-report",     "system report (JSON + TXT)"),
                     ("export-audit",      "audit report"),
                     ("export-netinfo",    "network state JSON"),
                     ("export-processes",  "process list JSON"),
                     ("save-session",      "dump Atomic state"),
                     ("support-bundle",    "diagnostics bundle (secrets redacted)")]),
    ("Utility",     [("cat <file>",        "print a file"),
                     ("jsonview <file>",   "pretty-print JSON"),
                     ("open <path|url>",   "open with OS default"),
                     ("clip <text>",       "copy to clipboard"),
                     ("copy-hash <file>",  "sha256 → clipboard"),
                     ("note [text]",       "read / append a personal note"),
                     ("hash <f> · hashid <v>", "hashing utilities")]),
    ("Academy",     [("academy",       "academy overview"),
                     ("lessons · lesson <n>",   "browse / open lessons"),
                     ("exercises · exercise <n>","browse / open exercises"),
                     ("rooms · room <n>",       "browse / open CTF rooms"),
                     ("stats · roadmap",        "profile and branch progress"),
                     ("reset confirm",          "wipe academy progress")]),
    ("Simulations", [("dig <host>",         "SIM DNS lookup"),
                     ("whois <host>",       "SIM whois"),
                     ("simscan <host>",     "SIM port scan (academy targets only)"),
                     ("banner <host> <p>",  "SIM banner grab"),
                     ("simping <host>",     "SIM ICMP"),
                     ("decode <k> <v>",     "b64/hex/rot13/url decode"),
                     ("encode <k> <v>",     "b64/hex/rot13/url encode"),
                     ("hashid <v>",         "identify hash family")]),
]

DETAIL_HELP = {
    "device":         "Open the Atomic Device Checkup. First run shows the legal notice and requires you to type the exact consent phrase. Decision is recorded in ~/.atomic/config.json (deviceConsent / deviceConsentAt). Then shows a guided 1–7 menu.",
    "checkup":        "Alias of 'device'.",
    "amihacked":      "Guided walkthrough of read-only checks (processes, startup, listening, firewall, suspicious-startup, audit quick). Asks which OS you're on and pauses between steps.",
    "scan":           "Scan family (consent-gated). Subcommands: folder · device · suspicious · system · processes · startup · network. Every scan is read-only.",
    "scan device":    "Full quick check of this machine (system + processes + startup + network).",
    "scan suspicious":"Broad read-only audit sweep using existing checks (startup, processes, listening, weak permissions, firewall, updates).",
    "browser-safety": "Read-only browser hygiene check: lists installed-browser profile dirs and extension counts. Atomic does NOT read cookies, history, or passwords.",
    "fix":            "Alias of 'fix suspicious'. Review findings from prior scans. File deletion requires typing 'DELETE THIS FILE'. Disabling a startup item requires 'DISABLE STARTUP'. Atomic refuses to delete folders, symlinks, or any system path (/System, /usr, /Library, %WinDir%, …).",
    "device-logs":    "Show the device checkup activity log (~/.atomic/logs.txt). Every check and action is also written to ~/.atomic/session.log.",
    "health":         "Print a device health snapshot: OS, hostname, uptime, disk, memory, CPU, battery, firewall, updates, and a 0–100 risk score (low/medium/high). Read-only.",
    "checkall":       "Full defensive read-only scan. Requires consent and the literal phrase 'START CHECKALL'. Walks ~/Downloads, ~/Desktop, ~/Documents (skipping symlinks and system paths), inspects processes / startup / network / firewall, computes a risk score, and writes a timestamped report (TXT + JSON) to ~/.atomic/reports/.",
    "quarantine":     "Move a single file into ~/.atomic/quarantine/ with a timestamped name. Requires the literal phrase 'QUARANTINE'. Refuses folders, symlinks, and system paths. Records sha256 + original path in ~/.atomic/quarantine/index.json so 'undo' can restore it.  Tip:  quarantine list  shows all quarantined items.",
    "undo":           "Restore the most recently quarantined file to its original location. Requires the literal phrase 'RESTORE'. If a file already exists at the original path, restores as 'restored_<filename>' instead of overwriting.",
    "selftest":       "Verify Atomic's own install + safety hooks: ~/.atomic, config, state, reports, quarantine, session log, Python version, OS, command registry, health callable, checkall safety phrase, quarantine index r/w, required stdlib modules.  Also runnable with  atomic --selftest.",
    "quickscan":      "Fast safe scan (≈seconds). Combines a health summary, Downloads metadata scan, startup items, top processes, listening ports and firewall state. Produces a 0–100 risk score and a one-line next-step.",
    "downloadcheck":  "Scan only the ~/Downloads folder. Flags double extensions, executables/scripts, installers, and macro documents — each with severity (low/medium/high) and confidence (low/medium/high).",
    "checkpath":      "Scan a specific folder you choose. Read-only, metadata-only. Skips symlinks and system paths by default; system paths require typing the full path again to confirm.",
    "risk":           "Show the most recent device risk score with reasons and a recommended next command. Risk history is persisted to ~/.atomic/risk.json.",
    "explain":        "Plain-language explanation of common security terms: extensions (.docm, .exe, .pkg…), patterns (double extensions, RAT/keygen names), or system concepts (firewall off, port 22, launch agents). Rule-based — no AI required.",
    "verbose":        "Toggle verbose mode. Use 'verbose on' to include full details and tracebacks on errors; 'verbose off' to keep output clean. Persists in state.json.",
    "sysinfo":      "Complete system overview: OS, kernel, CPU, memory, disks, battery.",
    "doctor":       "Sanity-check Atomic's setup and common local tools. Use 'doctor full' for a deeper check.",
    "audit":        "Run a defensive security audit. Modes: 'audit quick' (default) or 'audit full'.",
    "processes":    "List processes sorted by CPU. Pass a number to set the limit: 'processes 50'.",
    "listening":    "Show only listening TCP/UDP sockets. For all connections use 'ports'.",
    "localhost-scan":"TCP-probe common ports on 127.0.0.1 (your own loopback) to see local services.",
    "ping":         "Real ICMP ping via your OS ping tool. Usage: 'ping example.com [count]'.",
    "publicip":     "Opt-in outbound HTTPS request to api.ipify.org. No other data leaves your machine.",
    "integrity":    "Hash every file under a path. Useful to baseline a directory.",
    "export-report":"Write a system report to ~/.atomic/reports/ as both JSON and human-readable text.",
    "support-bundle":"Collect a full diagnostic bundle, with secrets-looking env vars redacted.",
    "note":         "Append a timestamped note to ~/.atomic/notes.md. Without args, prints the file.",
}

def cmd_help(args):
    if args:
        topic = args[0].lower()
        # Detailed help first
        if topic in DETAIL_HELP:
            pc(f"  {topic}")
            pb(f"    {DETAIL_HELP[topic]}")
            # also show the one-liner from groups if present
            for _, entries in HELP_GROUPS:
                for cmd, desc in entries:
                    if cmd.split()[0] == topic:
                        pd(f"    usage: {cmd}  —  {desc}"); return
            return
        # Fallback: search group entries
        for _, entries in HELP_GROUPS:
            for cmd, desc in entries:
                if cmd.split()[0] == topic:
                    pc(f"  {cmd}"); pb(f"    {desc}"); return
        pd(f"  no help entry for: {topic}"); return
    section(f"ATOMIC TERMINAL  v{VERSION}  —  Commands")
    for group, entries in HELP_GROUPS:
        pc(f"  {group}")
        for cmd, desc in entries:
            ph(f"    {cmd:<26} {desc}")
        print()
    pd("  Tips:")
    pd("    sysinfo · listening · audit quick · export-report")
    pd("    help <command>   for detail on any command")

# ── Command tables ────────────────────────────────────────────────────────

SIM_COMMAND_TABLE = {
    "dig":     cmd_dig,
    "whois":   cmd_whois,
    "simscan": cmd_scan_sim,
    "banner":  cmd_banner,
    "simping": cmd_sim_ping,
    "decode":  cmd_decode,
    "encode":  cmd_encode,
    "hashid":  cmd_hashid,
}

COMMANDS = {
    # general
    "help": cmd_help, "?": cmd_help, "h": cmd_help,
    "version": cmd_version, "v": cmd_version, "--version": cmd_version,
    "status": cmd_status, "doctor": cmd_doctor,
    "config": cmd_config, "theme": cmd_theme,
    "clear": cmd_clear, "cls": cmd_clear,
    "restart": cmd_restart, "update": cmd_update,
    "uninstall": cmd_uninstall,
    "about": cmd_about, "safety": cmd_safety,
    # device checkup
    "device": cmd_device_checkup, "checkup": cmd_device_checkup,
    "device-checkup": cmd_device_checkup,
    "amihacked": cmd_amihacked, "am-i-hacked": cmd_amihacked,
    "scan": cmd_scan,
    "scan-folder": cmd_scan_folder,
    "scan-system": cmd_scan_system,
    "scan-device": cmd_scan_device,
    "scan-suspicious": cmd_scan_suspicious,
    "scan-processes": cmd_scan_processes, "scan-process": cmd_scan_processes,
    "scan-startup": cmd_scan_startup,
    "scan-network": cmd_scan_network,
    "browser-safety": cmd_browser_safety, "browsers": cmd_browser_safety,
    "fix": cmd_fix, "fix-suspicious": cmd_fix,
    "device-logs": cmd_device_logs, "checkup-logs": cmd_device_logs,
    "health": cmd_health,
    "quarantine": cmd_quarantine, "quarantine-list": cmd_quarantine_list,
    "undo": cmd_undo,
    "checkall": cmd_checkall, "check-all": cmd_checkall,
    "selftest": cmd_selftest, "self-test": cmd_selftest,
    "quickscan": cmd_quickscan, "quick-scan": cmd_quickscan,
    "downloadcheck": cmd_downloadcheck, "download-check": cmd_downloadcheck,
    "checkpath": cmd_checkpath, "check-path": cmd_checkpath,
    "risk": cmd_risk,
    "explain": cmd_explain,
    "verbose": cmd_verbose,
    # system
    "sysinfo": cmd_sysinfo, "system": cmd_sysinfo, "sys": cmd_sysinfo,
    "os": cmd_os, "hostname": cmd_hostname, "uptime": cmd_uptime,
    "cpu": cmd_cpu, "memory": cmd_memory, "mem": cmd_memory, "ram": cmd_memory,
    "disk": cmd_disk, "disks": cmd_disk, "storage": cmd_disk,
    "battery": cmd_battery, "temp": cmd_temp, "temperature": cmd_temp,
    "env": cmd_env, "environment": cmd_env,
    "users": cmd_users, "sessions": cmd_sessions, "who": cmd_users,
    # processes
    "processes": cmd_processes, "ps": cmd_processes, "top": cmd_top,
    "psfind": cmd_psfind, "findproc": cmd_psfind,
    "process": cmd_process,
    "startup-items": cmd_startup_items, "startup": cmd_startup_items,
    "services": cmd_services, "scheduled": cmd_scheduled,
    "cron": cmd_scheduled, "tasks": cmd_scheduled,
    # network
    "netinfo": cmd_netinfo, "network": cmd_netinfo,
    "interfaces": cmd_interfaces, "ifconfig": cmd_interfaces, "ipconfig": cmd_interfaces,
    "ports": cmd_ports, "listening": cmd_listening, "listen": cmd_listening,
    "route": cmd_route, "routes": cmd_route, "dns": cmd_dns,
    "publicip": cmd_publicip, "myip": cmd_publicip,
    "localip": cmd_localip, "wifi-info": cmd_wifi_info, "wifi": cmd_wifi_info,
    "ping": cmd_ping, "traceroute-lite": cmd_traceroute_lite, "traceroute": cmd_traceroute_lite,
    "localhost-scan": cmd_localhost_scan, "localhost-ports": cmd_localhost_scan,
    "firewall": cmd_firewall, "firewall-status": cmd_firewall,
    # filesystem
    "ls": cmd_ls, "dir": cmd_ls, "tree": cmd_tree,
    "du": cmd_du, "fileinfo": cmd_fileinfo, "stat": cmd_fileinfo,
    "perms": cmd_perms, "recent-files": cmd_recent_files, "recent": cmd_recent_files,
    "large-files": cmd_large_files, "largest": cmd_large_files,
    "search-file": cmd_search_file, "find-file": cmd_search_file,
    "search-text": cmd_search_text, "grep": cmd_search_text,
    # security
    "hash": cmd_hash, "integrity": cmd_integrity,
    "weak-perms-scan": cmd_weak_perms, "weak-perms": cmd_weak_perms,
    "world-writable-scan": cmd_world_writable,
    "suspicious-startup": cmd_suspicious_startup,
    "audit": cmd_audit,
    "security-checklist": cmd_security_checklist, "checklist": cmd_security_checklist,
    "updates-check": cmd_updates_check, "updates": cmd_updates_check,
    "antivirus-status": cmd_antivirus_status, "av-status": cmd_antivirus_status,
    "ssh-check": cmd_ssh_check,
    # logs
    "logs": cmd_logs, "syslog": cmd_logs,
    "authlogs": cmd_authlogs, "authlog": cmd_authlogs, "auth-log": cmd_authlogs,
    "bootlogs": cmd_bootlogs, "boot-log": cmd_bootlogs,
    "errors": cmd_errors, "warnings": cmd_warnings,
    "journal": cmd_journal, "app-logs": cmd_app_logs,
    # export
    "export-report": cmd_export_report, "report": cmd_export_report,
    "export-audit": cmd_export_audit,
    "export-netinfo": cmd_export_netinfo,
    "export-processes": cmd_export_processes,
    "save-session": cmd_save_session,
    "support-bundle": cmd_support_bundle, "bundle": cmd_support_bundle,
    # utility
    "cat": cmd_cat, "show": cmd_cat,
    "jsonview": cmd_jsonview, "json": cmd_jsonview,
    "open": cmd_open, "xdg-open": cmd_open,
    "clip": cmd_clip, "copy": cmd_clip,
    "copy-hash": cmd_copy_hash, "hash-copy": cmd_copy_hash,
    "note": cmd_note, "notes": cmd_note,
    # academy
    "academy": cmd_academy, "learn": cmd_academy,
    "lessons": cmd_lessons, "lesson": cmd_lesson,
    "exercises": cmd_exercises, "exercise": cmd_exercise,
    "rooms": cmd_rooms, "ctf": cmd_rooms, "room": cmd_room,
    "stats": cmd_stats, "xp": cmd_stats, "level": cmd_stats,
    "roadmap": cmd_roadmap, "progress": cmd_roadmap,
    "whoami": cmd_whoami,
    "reset": cmd_reset,
}
COMMANDS.update(SIM_COMMAND_TABLE)

# Compound alias handling: "audit full", "status full", "doctor full",
# "system info", "firewall status", "report export", "export report",
# "startup items" etc. are handled at parse time.

COMPOUNDS = {
    "device checkup": "device",
    "device check":   "device",
    "device logs":    "device-logs",
    "checkup logs":   "device-logs",
    "scan folder":     "scan-folder",
    "scan system":     "scan-system",
    "scan device":     "scan-device",
    "scan suspicious": "scan-suspicious",
    "scan processes":  "scan-processes",
    "scan process":    "scan-processes",
    "scan startup":    "scan-startup",
    "scan network":    "scan-network",
    "fix suspicious":  "fix-suspicious",
    "browser safety":  "browser-safety",
    "am i hacked":     "amihacked",
    "check all":       "checkall",
    "device health":   "health",
    "self test":       "selftest",
    "quick scan":      "quickscan",
    "download check":  "downloadcheck",
    "check path":      "checkpath",
    "quarantine list": "quarantine-list",
    "verbose on":      ("verbose", ["on"]),
    "verbose off":     ("verbose", ["off"]),
    "verbose status":  ("verbose", ["status"]),
    "system info": "sysinfo",
    "system status": "status",
    "doctor full": ("doctor", ["full"]),
    "audit quick": ("audit", ["quick"]),
    "audit full":  ("audit", ["full"]),
    "status full": ("status", ["full"]),
    "report export": "export-report",
    "export report": "export-report",
    "audit export":  "export-audit",
    "export audit":  "export-audit",
    "firewall status": "firewall",
    "startup items":   "startup-items",
    "suspicious startup": "suspicious-startup",
    "security checklist": "security-checklist",
    "ssh check": "ssh-check",
    "updates check": "updates-check",
    "antivirus status": "antivirus-status",
    "large files": "large-files",
    "recent files": "recent-files",
    "search file": "search-file",
    "search text": "search-text",
    "last log": "logs",
    "boot log": "bootlogs",
    "auth log": "authlogs",
    "support bundle": "support-bundle",
    "save session": "save-session",
    "wifi info": "wifi-info",
    "local ip": "localip",
    "public ip": "publicip",
    "my ip":     "publicip",
    "world writable": "world-writable-scan",
    "world writable scan": "world-writable-scan",
    "weak perms": "weak-perms-scan",
    "weak perms scan": "weak-perms-scan",
    "copy hash": "copy-hash",
    "net info":  "netinfo",
}

for name in DISABLED_OFFENSIVE:
    COMMANDS[name] = make_refusal(name)

# ── Fuzzy suggest ─────────────────────────────────────────────────────────

def _lev(a, b):
    if not a: return len(b)
    if not b: return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j]+1, cur[j-1]+1, prev[j-1]+(0 if ca==cb else 1)))
        prev = cur
    return prev[-1]

def suggest(cmd):
    best, bd = None, 99
    for c in COMMANDS.keys():
        d = _lev(cmd, c)
        if d < bd: bd, best = d, c
    return best if bd <= 2 else None

# ── Input parsing ─────────────────────────────────────────────────────────

def dispatch(raw: str):
    raw = (raw or "").strip()
    if not raw: return
    low = raw.lower()
    if low in ("exit", "quit", ":q"): raise SystemExit(0)

    # Uninstall confirm
    if low == "uninstall confirm":
        cmd_uninstall_confirm([]); return

    # Compound aliases (2-3 token)
    for prefix in (3, 2):
        key = " ".join(low.split()[:prefix])
        if key in COMPOUNDS:
            target = COMPOUNDS[key]
            rest = raw.split()[prefix:]
            if isinstance(target, tuple):
                name, extra = target
                _run_cmd(name, extra + rest); return
            _run_cmd(target, rest); return

    parts = raw.split()
    cmd = parts[0].lower()
    args = parts[1:]
    _run_cmd(cmd, args)

def _run_cmd(cmd, args):
    handler = COMMANDS.get(cmd)
    if handler:
        try:
            handler(args)
            log_event(f"cmd {cmd} {' '.join(args)}")
        except KeyboardInterrupt:
            print(); pd("  cancelled.")
        except SystemExit:
            raise
        except (FileNotFoundError, PermissionError, IsADirectoryError,
                NotADirectoryError, OSError) as ex:
            lbl_err(pretty_oserror(ex))
            log_event(f"cmd {cmd} oserror: {ex}")
            if STATE.get("verbose"):
                import traceback; traceback.print_exc()
        except Exception as ex:
            lbl_err(f"command failed: {ex.__class__.__name__}: {ex}")
            pd("  this is unexpected. enable details with:  verbose on")
            log_event(f"cmd {cmd} crashed: {ex}")
            if STATE.get("verbose"):
                import traceback; traceback.print_exc()
        return
    lbl_err(f"unknown command: {cmd}")
    s = suggest(cmd)
    if s: pw(f"  did you mean:  {s}")
    pd("  type  help  for the command list")

# ── Boot + REPL ───────────────────────────────────────────────────────────

def first_run_hint():
    if not os.path.isfile(STATE_PATH) and len(STATE["completed_lessons"]) == 0:
        pc("  first run detected.")
        pc("  try:  selftest      — verify Atomic's install")
        pc("        quickscan     — fast safe device scan")
        pc("        downloadcheck — scan only your Downloads folder")
        pc("        checkall      — full defensive read-only scan + report")
        pc("        academy       — start the learning track")
    else:
        rec_l, rec_e, rec_r = recommend()
        total_done = len(STATE["completed_lessons"]) + len(STATE["completed_exercises"]) + len(STATE["completed_rooms"])
        if total_done == 0:
            pc("  Fresh profile. Try:  doctor    or   lesson 1")
        elif rec_l or rec_e or rec_r:
            rec = rec_l or rec_e or rec_r
            kind = "lesson" if rec_l else "exercise" if rec_e else "room"
            lst = LESSONS if kind == "lesson" else EXERCISES if kind == "exercise" else ROOMS
            pc(f"  Welcome back. Next academy item:  {kind} {lst.index(rec)+1}  — {rec['title']}")
        else:
            pc("  Curriculum cleared.")

def boot():
    print_banner()
    quick_ok = [
        (f"[OK]  platform: {os_pretty()}", G),
        (f"[OK]  python {platform.python_version()} · arch {platform.machine()}", G),
        ("[OK]  read-only local mode · no shell passthrough", G),
        ("[OK]  reports dir: " + REPORTS_DIR, G),
    ]
    for line, color in quick_ok:
        p("  " + line, color); time.sleep(0.04)
    print()
    first_run_hint()
    pd("  type  help  for commands   ·   doctor  for a setup check")
    log_event("boot")

def repl():
    while True:
        try:
            raw = input(_c(f"atomic@{socket.gethostname()}:{STATE['user']}$ ", G))
        except (EOFError, KeyboardInterrupt):
            print(); ph("  bye."); return
        try:
            dispatch(raw)
        except SystemExit:
            ph("  bye."); return

def main():
    argv = sys.argv[1:]
    if argv and argv[0] in ("-h", "--help", "help"):
        cmd_help(argv[1:]); return
    if argv and argv[0] in ("-v", "--version", "version"):
        cmd_version([]); return
    if argv and argv[0] in ("--about",):
        cmd_about([]); return
    if argv and argv[0] in ("--selftest", "-selftest"):
        try: cmd_selftest([])
        except SystemExit: pass
        return
    if argv and argv[0] in ("--doctor", "-doctor"):
        try: cmd_doctor(argv[1:])
        except SystemExit: pass
        return
    if argv:
        # Treat argv as a single command line; preserve multi-token.
        try: dispatch(" ".join(argv))
        except SystemExit: pass
        return
    boot()
    repl()

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        pe(f"  fatal: {ex}")
        sys.exit(1)
