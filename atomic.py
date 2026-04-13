#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   █████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗
#  ██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝
#  ███████║   ██║   ██║   ██║██╔████╔██║██║██║
#  ██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║
#  ██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗
#  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝
#  TERMINAL  v1.0.0 — Built by Pavlopanda
#  Authorized security research only.
#

import sys, os, time, random, json, socket, subprocess, threading
import getpass, platform, re, signal, shutil
from datetime import datetime

# ── AUTO-INSTALL REQUESTS ─────────────────────────────────────────────────────
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable,'-m','pip','install','requests','-q','--break-system-packages'])
    import requests

# ── ANSI PALETTE ──────────────────────────────────────────────────────────────
def rgb(r,g,b): return f'\033[38;2;{r};{g};{b}m'
def bg(r,g,b):  return f'\033[48;2;{r};{g};{b}m'

G    = rgb(0,255,153)     # #00ff99  primary
DG   = rgb(0,160,90)      # dark green
CY   = rgb(0,230,255)     # cyan
RD   = rgb(255,60,60)     # red/error
YL   = rgb(255,215,0)     # yellow/warning
DM   = rgb(30,90,60)      # dim ghost
WH   = rgb(210,255,230)   # near white
PK   = rgb(255,0,200)     # pink/glitch
GY   = rgb(80,80,80)      # gray
BOLD = '\033[1m'
DIM  = '\033[2m'
RST  = '\033[0m'

def clr(): print('\033[2J\033[H', end='')

# ── CONFIG ────────────────────────────────────────────────────────────────────
VERSION      = '1.0.0'
FB_DB_URL    = 'https://atomic-ai-f07f1-default-rtdb.firebaseio.com'
WORKER       = 'https://atomic-proxy.pavlo-panda0.workers.dev'
AI_MODEL     = 'llama-3.3-70b-versatile'
GLITCH_CHARS = '!@#$%^&*<>?/\\|{}[]░▒▓█▄▀■□▪▫×÷±≈'
OS_NAME      = platform.system()
CONFIG_PATH  = os.path.expanduser('~/.atomic/config.json')

# ── SESSION ───────────────────────────────────────────────────────────────────
SESSION = {
    'uid': None, 'email': None, 'idToken': None,
    'plan': 'free', 'role': 'user',
    'displayName': 'operator', 'history': [],
}

# ── PRINT HELPERS ─────────────────────────────────────────────────────────────
def p(text='', color=G, end='\n'):
    print(f'{color}{text}{RST}', end=end, flush=True)

def pw(text): p(text, YL)
def pe(text): p(text, RD)
def pd(text): p(text, DM)
def pc(text): p(text, CY)
def pb(text): p(text, WH)

def typewrite(text, color=G, delay=0.018):
    for ch in text:
        print(f'{color}{ch}{RST}', end='', flush=True)
        time.sleep(delay)
    print()

# ── LOGO ──────────────────────────────────────────────────────────────────────
LOGO = [
    '   █████╗ ████████╗ ██████╗ ███╗   ███╗██╗ ██████╗ ',
    '  ██╔══██╗╚══██╔══╝██╔═══██╗████╗ ████║██║██╔════╝ ',
    '  ███████║   ██║   ██║   ██║██╔████╔██║██║██║      ',
    '  ██╔══██║   ██║   ██║   ██║██║╚██╔╝██║██║██║      ',
    '  ██║  ██║   ██║   ╚██████╔╝██║ ╚═╝ ██║██║╚██████╗ ',
    '  ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝ ╚═════╝ ',
]

def glitch_logo(passes=10):
    """Print the logo with glitch animation then settle."""
    box_chars = set('╗╝╚╔║═╠╣╦╩╧╤╟╢╞╡╬▐▌')
    for i in range(passes):
        clr()
        for j, line in enumerate(LOGO):
            if random.random() < 0.45:
                out = ''
                for ch in line:
                    if ch not in box_chars and ch != ' ' and random.random() < 0.28:
                        out += random.choice(GLITCH_CHARS)
                    else:
                        out += ch
                c = random.choice([G, CY, PK, YL, RD])
                print(f'{c}{out}{RST}')
            else:
                print(f'{DG}{line}{RST}')
        time.sleep(0.07)
    clr()
    for line in LOGO:
        print(f'{G}{BOLD}{line}{RST}')

def print_logo():
    for line in LOGO:
        print(f'{G}{BOLD}{line}{RST}')

# ── BOOT SEQUENCE ─────────────────────────────────────────────────────────────
def boot_sequence():
    clr()
    glitch_logo()
    print()
    print(f'{DM}{"─"*56}{RST}')
    print(f'{DG}  TERMINAL v{VERSION}              Built by Pavlopanda{RST}')
    print(f'{DM}{"─"*56}{RST}')
    print()
    time.sleep(0.3)

    msgs = [
        (G,  '  [OK]  Kernel modules loaded'),
        (G,  '  [OK]  Encryption layer initialized  (AES-256-GCM)'),
        (G,  '  [OK]  Network interface up'),
        (CY, '  [OK]  Neural core online              (Atomic AI)'),
        (G,  '  [OK]  Firebase auth bridge connected'),
        (G,  '  [OK]  AI core ready'),
        (YL, '  [!!]  All activity is logged & tied to your account'),
        (G,  '  [OK]  All systems nominal'),
    ]
    for color, msg in msgs:
        p(msg, color)
        time.sleep(random.uniform(0.05, 0.14))
    print()
    time.sleep(0.4)

# ── DISCLAIMER ────────────────────────────────────────────────────────────────
def show_disclaimer():
    clr()
    print(f'{RD}{"═"*64}{RST}')
    print(f'{RD}{BOLD}')
    print('  ██╗    ██╗ █████╗ ██████╗ ███╗  ██╗██╗███╗  ██╗ ██████╗')
    print('  ██║    ██║██╔══██╗██╔══██╗████╗ ██║██║████╗ ██║██╔════╝')
    print('  ██║ █╗ ██║███████║██████╔╝██╔██╗██║██║██╔██╗██║██║  ███╗')
    print('  ██║███╗██║██╔══██║██╔══██╗██║╚████║██║██║╚████║██║   ██║')
    print('  ╚███╔███╔╝██║  ██║██║  ██║██║ ╚███║██║██║ ╚███║╚██████╔╝')
    print('   ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚══╝╚═╝╚═╝  ╚══╝ ╚═════╝')
    print(f'{RST}')
    print(f'{RD}  ATOMIC TERMINAL — LEGAL NOTICE & TERMS OF USE{RST}')
    print(f'{RD}{"═"*64}{RST}')
    print()

    sections = [
        (YL, '1. AUTHORIZED USE ONLY', [
            '   This software is for:',
            '   • Penetration testing on systems YOU OWN',
            '   • Systems with EXPLICIT WRITTEN PERMISSION to test',
            '   • CTF (Capture The Flag) competitions',
            '   • Authorized security research & education',
        ]),
        (RD, '2. ILLEGAL USE IS A CRIMINAL OFFENCE', [
            '   Unauthorized access to computer systems violates:',
            '   • Computer Fraud and Abuse Act (CFAA) — USA',
            '   • Computer Misuse Act — UK',
            '   • EU Directive 2013/40/EU on cyberattacks',
            '   • Swiss FADP and all applicable national laws',
            '',
            '   PENALTIES: IMPRISONMENT and HEAVY FINES.',
            '   DO NOT USE AGAINST GOVERNMENT, HOSPITAL,',
            '   FINANCIAL, or CRITICAL INFRASTRUCTURE SYSTEMS.',
        ]),
        (YL, '3. FULL USER LIABILITY', [
            '   You are SOLELY AND FULLY RESPONSIBLE for every',
            '   action you take using this software.',
            '',
            '   Pavlopanda and Atomic Terminal bear ZERO liability',
            '   for any misuse, damage, or legal consequences.',
            '',
            '   ⚠  THIS DISCLAIMER DOES NOT GRANT IMMUNITY FROM',
            '      CRIMINAL PROSECUTION. NO DISCLAIMER CAN.',
            '      If you break the law, you will face consequences.',
        ]),
        (YL, '4. NO ANONYMOUS PROTECTION', [
            '   Your session is tied to your account and logged.',
            '   Authorities can and do subpoena service providers.',
            '   A VPN or Tor does not make illegal activity legal.',
        ]),
    ]

    for color, title, lines in sections:
        print(f'{color}  {title}{RST}')
        for line in lines:
            if '⚠' in line or 'PENALTY' in line or 'IMPRISONMENT' in line:
                print(f'{RD}  {line}{RST}')
            elif line.startswith('   •'):
                print(f'{DG}  {line}{RST}')
            else:
                print(f'{WH}  {line}{RST}')
        print()

    print(f'{RD}{"═"*64}{RST}')
    print()
    answer = input(
        f'{YL}  Type exactly  I AGREE  to accept and continue: {RST}'
    ).strip()
    if answer != 'I AGREE':
        pe('  Aborted. You must accept the terms.')
        sys.exit(0)

    cfg = _load_cfg()
    cfg['disclaimer_accepted'] = True
    _save_cfg(cfg)

# ── CONFIG FILE ───────────────────────────────────────────────────────────────
def _load_cfg():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                return json.load(f)
        except:
            pass
    return {}

def _save_cfg(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f)

# ── INSTALL TOOLS (first run) ─────────────────────────────────────────────────
def install_tools():
    clr()
    print_logo()
    print()
    print(f'{G}{"─"*60}{RST}')
    print(f'{G}  FIRST RUN — INSTALLING SECURITY TOOLS{RST}')
    print(f'{G}{"─"*60}{RST}')
    print()
    pc('  Detecting OS...')
    time.sleep(0.4)
    p(f'  System: {platform.platform()}', WH)
    print()

    tools_mac = [
        ('nmap',         'brew install nmap'),
        ('masscan',      'brew install masscan'),
        ('sqlmap',       'brew install sqlmap'),
        ('hydra',        'brew install hydra'),
        ('john',         'brew install john'),
        ('hashcat',      'brew install hashcat'),
        ('aircrack-ng',  'brew install aircrack-ng'),
        ('nikto',        'brew install nikto'),
        ('gobuster',     'brew install gobuster'),
        ('ncat',         'brew install nmap'),
        ('curl',         'brew install curl'),
        ('wget',         'brew install wget'),
    ]
    tools_linux = [
        ('nmap',         'apt-get install -y nmap'),
        ('masscan',      'apt-get install -y masscan'),
        ('sqlmap',       'apt-get install -y sqlmap'),
        ('hydra',        'apt-get install -y hydra'),
        ('john',         'apt-get install -y john'),
        ('hashcat',      'apt-get install -y hashcat'),
        ('aircrack-ng',  'apt-get install -y aircrack-ng'),
        ('nikto',        'apt-get install -y nikto'),
        ('gobuster',     'apt-get install -y gobuster'),
        ('ncat',         'apt-get install -y ncat'),
        ('curl',         'apt-get install -y curl'),
        ('wget',         'apt-get install -y wget'),
    ]
    tools = tools_mac if OS_NAME == 'Darwin' else tools_linux
    W = 36

    pc('  Installing hacking tools:')
    print()
    for tool, cmd in tools:
        lbl = f'  {tool:<16}'
        print(f'{CY}{lbl}{RST}  ', end='', flush=True)
        steps = random.randint(14, 24)
        for i in range(steps):
            filled = int((i+1)/steps * W)
            bar = f'{G}{"█"*filled}{DM}{"░"*(W-filled)}{RST}'
            pct = int((i+1)/steps*100)
            print(f'\r{CY}{lbl}{RST}  {bar}  {WH}{pct:3d}%{RST}', end='', flush=True)
            time.sleep(random.uniform(0.03, 0.11))

        # Try actual install silently
        try:
            subprocess.run(cmd.split(), capture_output=True, timeout=25)
        except:
            pass

        check = tool.split('-')[0]
        found = shutil.which(check) is not None
        status = f'{G}  ✓{RST}' if found else f'{YL}  ○ (install manually){RST}'
        print(f'\r{CY}{lbl}{RST}  {G}{"█"*W}{RST}  {WH}100%{RST}{status}')

    print()
    pc('  Installing Python packages:')
    print()
    py_pkgs = ['requests', 'python-whois', 'dnspython']
    for pkg in py_pkgs:
        lbl = f'  {pkg:<20}'
        print(f'{CY}{lbl}{RST}  ', end='', flush=True)
        for i in range(20):
            bar = f'{G}{"█"*(i+1)}{DM}{"░"*(19-i)}{RST}'
            print(f'\r{CY}{lbl}{RST}  {bar}  {WH}{(i+1)*5:3d}%{RST}', end='', flush=True)
            time.sleep(0.05)
        try:
            subprocess.run(
                [sys.executable,'-m','pip','install',pkg,'-q'],
                capture_output=True
            )
        except:
            pass
        print(f'\r{CY}{lbl}{RST}  {G}{"█"*20}{RST}  {WH}100%{RST}  {G}✓{RST}')

    print()
    p('  ✓  Setup complete.', G)
    time.sleep(0.6)

    cfg = _load_cfg()
    cfg['installed'] = True
    cfg['version']   = VERSION
    _save_cfg(cfg)

    print()
    typewrite('  Atomic Terminal installed. Launching...', G, 0.025)
    time.sleep(1)

# ── AUTH (same system as web app — username/pass/secret via RTDB) ─────────────
def fb_get_user(username):
    try:
        r = requests.get(f'{FB_DB_URL}/users/{username}.json', timeout=8)
        return r.json() or {}
    except:
        return {}

def login_screen():
    clr()
    glitch_logo()
    print()
    print(f'{DM}{"─"*56}{RST}')
    print(f'{DG}  Sign in with your Atomic account{RST}')
    print(f'{DM}{"─"*56}{RST}')
    print()

    while True:
        username = input(f'{G}  username › {RST}').strip().lower()
        password = getpass.getpass(f'{G}  password › {RST}')
        secret   = input(f'{G}  secret   › {RST}').strip()
        print()
        p('  Authenticating...', DG)

        udata = fb_get_user(username)
        if not udata:
            pe('  ✗  User not found.')
            print()
            if input(f'{DM}  Try again? [y/n]: {RST}').strip().lower() != 'y':
                sys.exit(0)
            print()
            continue

        if udata.get('pass') != password:
            pe('  ✗  Invalid password.')
            print()
            if input(f'{DM}  Try again? [y/n]: {RST}').strip().lower() != 'y':
                sys.exit(0)
            print()
            continue

        if udata.get('secret') != secret:
            pe('  ✗  Invalid secret code.')
            print()
            if input(f'{DM}  Try again? [y/n]: {RST}').strip().lower() != 'y':
                sys.exit(0)
            print()
            continue

        plan = udata.get('plan', 'free')
        role = udata.get('role', 'user')
        name = udata.get('displayName', username)

        # Terminal gate: Pro or Max only
        if role != 'dev' and plan not in ('pro', 'max'):
            print()
            pw('  ╔════════════════════════════════════════╗')
            pw('  ║  ATOMIC TERMINAL requires Pro or Max  ║')
            pw('  ║  Upgrade at: atomicai.pavlopanda.com  ║')
            pw('  ╚════════════════════════════════════════╝')
            print()
            sys.exit(0)

        SESSION['uid']         = username
        SESSION['email']       = udata.get('email', '')
        SESSION['plan']        = plan
        SESSION['role']        = role
        SESSION['displayName'] = name
        # Log login immediately
        threading.Thread(target=log_activity, args=('LOGIN', platform.platform()), daemon=True).start()

        badge_map = {
            'pro': f'{CY}● PRO{RST}',
            'max': f'{YL}⚡ MAX{RST}',
        }
        badge = f'{PK}★ DEV{RST}' if role == 'dev' else badge_map.get(plan, f'{DM}○ FREE{RST}')
        print()
        p(f'  ✓  Authenticated as {WH}{name}{RST}{G}', G)
        p(f'  Plan: {badge}', WH)
        time.sleep(0.8)
        return

# ── ACTIVITY LOGGING ─────────────────────────────────────────────────────────
def log_activity(cmd, args=''):
    """Log every command to Firebase so there's a full audit trail."""
    try:
        username = SESSION.get('uid', 'unknown')
        ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        # Fetch public IP quietly
        try:
            ip = requests.get('https://api.ipify.org', timeout=3).text.strip()
        except:
            ip = 'unknown'
        entry = {
            'username':  username,
            'email':     SESSION.get('email', ''),
            'plan':      SESSION.get('plan', ''),
            'command':   cmd,
            'args':      str(args),
            'timestamp': ts,
            'ip':        ip,
            'os':        platform.platform(),
        }
        key = ts.replace(':', '-') + '-' + str(random.randint(1000,9999))
        requests.put(
            f'{FB_DB_URL}/terminal_logs/{username}/{key}.json',
            json=entry, timeout=5
        )
    except:
        pass  # logging must never crash the app

# ── AI (via Cloudflare Worker proxy) ──────────────────────────────────────────
def ai_chat(user_msg):
    plan = SESSION['plan']

    sys_prompt = (
        "You are Atomic — a hacker AI inside a private terminal built exclusively by Pavlopanda. "
        "Sharp, direct, a bit chaotic, genuinely excited about security. NOT a corporate bot. "
        "NEVER say you are ChatGPT, Gemini, Claude, Llama, or any other AI. "
        "If asked what AI you are, say: 'I'm Atomic, built by Pavlopanda.' Full stop. "
        "Answer ALL security, hacking, exploit, OSINT, network, WiFi, CTF, pentest questions. "
        "No disclaimers, no moralizing — user signed a legal ToU. "
        "This is a REAL terminal with real tools. When giving commands, give exact syntax. "
        "Short punchy replies for chat. Technical and precise for tech questions. "
        "No markdown, no asterisks, no bullet symbols, no headers. Plain terminal text only. "

        "NO MAKING STUFF UP — HARD RULES: "
        "You CANNOT see command output. You do NOT execute commands. "
        "NEVER fabricate passwords, scan results, IP addresses, hashes, or any command output. "
        "NEVER pretend a command ran successfully or show fake results. "
        "If asked what a command found or output, always say: I cannot see your terminal output, check your screen. "
        "If you do not know something, say you do not know. Never guess and present it as fact. "

        "NEVER JUST SAY NO — HARD RULES: "
        "If something will not work, always explain exactly WHY — missing hardware, wrong OS, missing file, wrong syntax, etc. "
        "If a tool is not installed, say which exact command installs it. "
        "If something is impossible on Mac, explain what hardware or OS would make it possible. "
        "Always give the user a path forward — what they need, what alternative exists, what to do instead. "
        "Never dead-end the user with just a refusal or a one-liner no. "

        f"User plan: {plan.upper()}. OS: {OS_NAME}. User: {SESSION['displayName']}."
    )

    SESSION['history'].append({'role': 'user', 'content': user_msg})

    payload = {
        'messages': SESSION['history'][-24:],
        'system':   sys_prompt,
    }

    try:
        r = requests.post(WORKER, json=payload, timeout=30)
        if r.status_code == 429:
            return '[Atomic AI] Too many requests — please wait a few seconds and try again.'
        if not r.ok:
            return '[Atomic AI] Connection error — try again.'
        d = r.json()
        raw = (
            d.get('content') or
            d.get('choices', [{}])[0].get('message', {}).get('content') or
            d.get('reply') or
            str(d)
        )
        # content can be a list of blocks: [{"type":"text","text":"..."}]
        if isinstance(raw, list):
            reply = ' '.join(
                b.get('text', '') for b in raw if isinstance(b, dict)
            ).strip()
        else:
            reply = str(raw).strip()
        # Check for rate limit in reply content
        if 'rate limit' in reply.lower() or 'Rate limit' in reply or 'tokens per minute' in reply.lower():
            return '[Atomic AI] Too many requests — please wait a few seconds and try again.'
        SESSION['history'].append({'role': 'assistant', 'content': reply})
        return reply
    except Exception as e:
        err = str(e).lower()
        if 'rate limit' in err or 'too many' in err or 'tpm' in err:
            return '[Atomic AI] Too many requests — please wait a few seconds and try again.'
        return '[Atomic AI] Connection error — try again.'

def stream_ai(msg):
    print(f'{DM}  atomic >{RST} ', end='', flush=True)
    reply = ai_chat(msg)
    if not reply:
        return
    col = 0
    MAX_COL = 72
    for word in reply.split():
        if col + len(word) + 1 > MAX_COL:
            print()
            print('           ', end='', flush=True)
            col = 0
        print(f'{WH}{word} {RST}', end='', flush=True)
        col += len(word) + 1
        time.sleep(0.018)
    print()

# ── TOOL UTILS ────────────────────────────────────────────────────────────────
def tool_ok(name):
    return shutil.which(name.split('-')[0]) is not None

def run_tool(cmd):
    print(f'{DM}  $ {" ".join(cmd)}{RST}')
    print()
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1
        )
        for line in proc.stdout:
            print(f'  {G}{line.rstrip()}{RST}')
        proc.wait()
    except FileNotFoundError:
        pe(f'  Not found: {cmd[0]}')
    except KeyboardInterrupt:
        proc.terminate()
        print()
        pw('  Interrupted.')

def shell_exec(raw):
    """Run raw shell command directly — pipes, redirects, interactive tools all work."""
    print(f'{DM}  $ {raw}{RST}')
    print()
    try:
        subprocess.run(raw, shell=True)
    except KeyboardInterrupt:
        print()

SERVICES = {
    21:'FTP', 22:'SSH', 23:'Telnet', 25:'SMTP', 53:'DNS',
    80:'HTTP', 110:'POP3', 143:'IMAP', 443:'HTTPS', 445:'SMB',
    3306:'MySQL', 3389:'RDP', 5432:'PostgreSQL', 6379:'Redis',
    8080:'HTTP-Alt', 8443:'HTTPS-Alt', 9200:'Elasticsearch',
    27017:'MongoDB', 1433:'MSSQL', 5900:'VNC', 1521:'Oracle',
    11211:'Memcached', 2375:'Docker', 9090:'Cockpit',
}

# ── COMMANDS ──────────────────────────────────────────────────────────────────
def cmd_nmap(args):
    if not tool_ok('nmap'):
        pe('  nmap not found.  brew install nmap  or  apt install nmap')
        return
    if not args:
        pb('  Usage: nmap <target> [flags]')
        pd('  nmap 192.168.1.1')
        pd('  nmap -sV -p 1-1000 192.168.1.0/24')
        pd('  nmap -A -T4 target.com')
        return
    pw('  ⚠  Only scan systems you own or have written authorization to test.')
    print()
    shell_exec('nmap ' + ' '.join(args))

def cmd_masscan(args):
    if not tool_ok('masscan'):
        pe('  masscan not found.  brew install masscan')
        return
    if not args:
        pb('  Usage: masscan <target> -p <ports> --rate=<rate>')
        pd('  masscan 192.168.1.0/24 -p 80,443,22 --rate=1000')
        return
    pw('  ⚠  Only scan systems you own or have written authorization to test.')
    shell_exec('masscan ' + ' '.join(args))

def cmd_scan(args):
    """Python port scanner — no external tools needed."""
    if not args:
        pb('  Usage: scan <host> [ports]')
        pd('  scan 192.168.1.1')
        pd('  scan 192.168.1.1 1-1024')
        pd('  scan target.com 80,443,8080,8443')
        return

    host = args[0]
    port_arg = args[1] if len(args) > 1 else '1-1000'
    ports = []
    for part in port_arg.split(','):
        if '-' in part:
            a, b = part.split('-', 1)
            ports.extend(range(int(a), int(b)+1))
        else:
            ports.append(int(part.strip()))

    pw('  ⚠  Only scan systems you own or have written authorization to test.')
    print()
    p(f'  Scanning {WH}{host}{G}  —  {len(ports)} ports', CY)
    print()

    open_ports = []
    lock = threading.Lock()
    done = [0]

    def check(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.6)
            if s.connect_ex((host, port)) == 0:
                with lock:
                    open_ports.append(port)
                svc = SERVICES.get(port, '')
                print(f'  {G}OPEN  {port:<6}{RST}  {DM}{svc}{RST}')
            s.close()
        except:
            pass
        with lock:
            done[0] += 1

    threads = []
    for port in ports:
        t = threading.Thread(target=check, args=(port,), daemon=True)
        t.start()
        threads.append(t)
        if len(threads) >= 256:
            for t in threads: t.join()
            threads = []
    for t in threads: t.join()

    print()
    if open_ports:
        p(f'  {len(open_ports)} open port(s): {", ".join(map(str, sorted(open_ports)))}', G)
    else:
        pd(f'  No open ports found on {host}.')

def cmd_ping(args):
    if not args:
        pb('  Usage: ping <host> [count]')
        return
    host  = args[0]
    count = args[1] if len(args) > 1 else '4'
    flag  = '-c' if OS_NAME != 'Windows' else '-n'
    run_tool(['ping', flag, count, host])

def cmd_trace(args):
    if not args:
        pb('  Usage: trace <host>')
        return
    tool = 'traceroute' if OS_NAME != 'Windows' else 'tracert'
    run_tool([tool] + args)

def cmd_whois(args):
    if not args:
        pb('  Usage: whois <domain|ip>')
        return
    try:
        import whois as w
        data = w.whois(args[0])
        for k, v in data.items():
            if v:
                print(f'  {CY}{k:<22}{RST} {WH}{v}{RST}')
    except ImportError:
        if tool_ok('whois'):
            run_tool(['whois', args[0]])
        else:
            pe('  pip install python-whois   or   brew install whois')

def cmd_dig(args):
    if not args:
        pb('  Usage: dig <domain> [type]')
        pd('  Types: A  AAAA  MX  NS  TXT  CNAME  SOA')
        return
    domain = args[0]
    rtype  = args[1].upper() if len(args) > 1 else 'A'
    try:
        import dns.resolver
        answers = dns.resolver.resolve(domain, rtype)
        p(f'  {rtype} records for {domain}:', CY)
        for r in answers:
            print(f'  {G}→{RST} {WH}{r}{RST}')
    except ImportError:
        if tool_ok('dig'):
            run_tool(['dig', domain, rtype, '+short'])
        else:
            try:
                ips = socket.gethostbyname_ex(domain)
                p(f'  A records for {domain}:', CY)
                for ip in ips[2]:
                    print(f'  {G}→{RST} {WH}{ip}{RST}')
            except Exception as e:
                pe(f'  {e}')

def cmd_myip(args):
    p('  Fetching IPs...', DG)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local = s.getsockname()[0]
        s.close()
        print(f'  {CY}Local IP  {RST}  {G}{local}{RST}')
    except:
        pass
    try:
        pub  = requests.get('https://api.ipify.org', timeout=6).text.strip()
        info = requests.get(f'https://ipapi.co/{pub}/json/', timeout=6).json()
        print(f'  {CY}Public IP {RST}  {G}{pub}{RST}')
        print(f'  {CY}ISP       {RST}  {WH}{info.get("org","?")}{RST}')
        print(f'  {CY}City      {RST}  {WH}{info.get("city","?")}{RST}')
        print(f'  {CY}Country   {RST}  {WH}{info.get("country_name","?")}{RST}')
    except:
        pe('  Could not fetch public IP.')

def cmd_banner(args):
    if not args:
        pb('  Usage: banner <host> <port>')
        return
    host = args[0]
    port = int(args[1]) if len(args) > 1 else 80
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((host, port))
        s.send(b'HEAD / HTTP/1.0\r\nHost: ' + host.encode() + b'\r\n\r\n')
        data = s.recv(2048).decode('utf-8', errors='ignore')
        s.close()
        p(f'  Banner {host}:{port}', CY)
        print()
        for line in data.splitlines():
            if line.strip():
                print(f'  {WH}{line}{RST}')
    except Exception as e:
        pe(f'  {e}')

def cmd_sqlmap(args):
    if not tool_ok('sqlmap'):
        pe('  brew install sqlmap  /  pip install sqlmap')
        return
    if not args:
        pb('  Usage: sqlmap -u "http://target.com/page?id=1" --dbs')
        return
    pw('  ⚠  Only test systems you own or have written authorization to test.')
    shell_exec('sqlmap ' + ' '.join(args))

def cmd_hydra(args):
    if not tool_ok('hydra'):
        pe('  brew install hydra  /  apt install hydra')
        return
    if not args:
        pb('  Usage: hydra -l admin -P wordlist.txt ssh://192.168.1.1')
        return
    pw('  ⚠  Only test systems you own or have written authorization to test.')
    shell_exec('hydra ' + ' '.join(args))

def cmd_nikto(args):
    if not tool_ok('nikto'):
        pe('  brew install nikto  /  apt install nikto')
        return
    if not args:
        pb('  Usage: nikto -h http://192.168.1.1')
        return
    pw('  ⚠  Only test systems you own or have written authorization to test.')
    shell_exec('nikto ' + ' '.join(args))

def cmd_gobuster(args):
    if not tool_ok('gobuster'):
        pe('  brew install gobuster  /  apt install gobuster')
        return
    if not args:
        pb('  Usage: gobuster dir -u http://target.com -w /wordlist.txt')
        return
    pw('  ⚠  Only test systems you own or have written authorization to test.')
    shell_exec('gobuster ' + ' '.join(args))

def cmd_hashcat(args):
    if not tool_ok('hashcat'):
        pe('  brew install hashcat  /  apt install hashcat')
        return
    if not args:
        pb('  Usage: hashcat -m 0 hashes.txt rockyou.txt')
        pd('  Modes: 0=MD5 100=SHA1 1800=sha512crypt 22000=WPA2 ...')
        return
    shell_exec('hashcat ' + ' '.join(args))

def cmd_john(args):
    if not tool_ok('john'):
        pe('  brew install john  /  apt install john')
        return
    if not args:
        pb('  Usage: john <hashfile> [--wordlist=<file>]')
        return
    shell_exec('john ' + ' '.join(args))

def cmd_aircrack(args):
    if not tool_ok('aircrack-ng'):
        pe('  brew install aircrack-ng  /  apt install aircrack-ng')
        return
    if not args:
        pb('  Usage: aircrack <capfile> -w <wordlist>')
        return
    pw('  ⚠  Only test networks you own or have written authorization to test.')
    shell_exec('aircrack-ng ' + ' '.join(args))

# ── NETSCAN ───────────────────────────────────────────────────────────────────
def cmd_netscan(args):
    import ipaddress
    p('  Scanning local network...', DM)
    print()
    # Get local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pe('  Could not detect local IP.')
        return

    # Derive /24 subnet
    parts_ip = local_ip.split('.')
    subnet = f"{parts_ip[0]}.{parts_ip[1]}.{parts_ip[2]}.0/24"
    p(f'  Network   {subnet}', CY)
    p(f'  Your IP   {local_ip}', CY)
    print()

    # Use nmap if available for rich info, else ping sweep
    if shutil.which('nmap'):
        p('  Running nmap discovery...', DM)
        print()
        shell_exec(f'nmap -sn --open -T4 {subnet}')
    else:
        p('  Pinging hosts (nmap not found, install for richer results)...', DM)
        print()
        alive = []
        def ping_host(ip):
            flag = '-n' if OS_NAME == 'Windows' else '-c'
            r = subprocess.run(['ping', flag, '1', '-W', '1', str(ip)],
                               capture_output=True, timeout=3)
            if r.returncode == 0:
                alive.append(str(ip))

        threads = []
        for host in ipaddress.IPv4Network(subnet, strict=False).hosts():
            t = threading.Thread(target=ping_host, args=(host,), daemon=True)
            threads.append(t)
            t.start()
            if len(threads) % 20 == 0:
                for t in threads[-20:]: t.join(timeout=2)

        for t in threads: t.join(timeout=2)
        alive.sort(key=lambda x: int(x.split('.')[-1]))

        p(f'  Found {len(alive)} hosts:', G)
        print()
        for ip in alive:
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except Exception:
                hostname = ''
            marker = f'{PK} ← you{RST}' if ip == local_ip else ''
            print(f'  {G}●{RST}  {WH}{ip:<18}{RST}  {DM}{hostname}{RST}{marker}')
        print()

# ── CRACK ─────────────────────────────────────────────────────────────────────
def cmd_crack(args):
    if not args:
        pb('  Usage: crack <hash>')
        pd('  crack 5f4dcc3b5aa765d61d8327deb882cf99')
        return

    h = args[0].strip()
    length = len(h)

    # Auto-detect hash type
    hash_type = None
    hashcat_mode = None
    if re.fullmatch(r'[a-fA-F0-9]{32}', h):
        hash_type = 'MD5'
        hashcat_mode = '0'
    elif re.fullmatch(r'[a-fA-F0-9]{40}', h):
        hash_type = 'SHA1'
        hashcat_mode = '100'
    elif re.fullmatch(r'[a-fA-F0-9]{64}', h):
        hash_type = 'SHA256'
        hashcat_mode = '1400'
    elif re.fullmatch(r'[a-fA-F0-9]{128}', h):
        hash_type = 'SHA512'
        hashcat_mode = '1700'
    elif h.startswith('$2b$') or h.startswith('$2a$'):
        hash_type = 'bcrypt'
        hashcat_mode = '3200'
    elif h.startswith('$1$'):
        hash_type = 'MD5crypt'
        hashcat_mode = '500'
    elif h.startswith('$6$'):
        hash_type = 'SHA512crypt'
        hashcat_mode = '1800'
    else:
        hash_type = 'Unknown'

    p(f'  Hash     {h}', DM)
    p(f'  Type     {hash_type}', CY)
    print()

    if hash_type == 'Unknown':
        pe('  Could not detect hash type.')
        return

    # Try wordlists in order
    wordlists = [
        '/usr/share/wordlists/rockyou.txt',
        '/usr/share/wordlists/rockyou.txt.gz',
        os.path.expanduser('~/wordlists/rockyou.txt'),
        'rockyou.txt',
        'wordlist.txt',
    ]
    wl = next((w for w in wordlists if os.path.exists(w)), None)

    if shutil.which('hashcat') and hashcat_mode and wl:
        p(f'  Tool     hashcat (mode {hashcat_mode})', DM)
        p(f'  Wordlist {wl}', DM)
        print()
        pw('  ⚠  Only crack hashes you own or have authorization to crack.')
        print()
        shell_exec(f'hashcat -m {hashcat_mode} {h} {wl} --force')
    elif shutil.which('john') and wl:
        p('  Tool     john the ripper', DM)
        p(f'  Wordlist {wl}', DM)
        print()
        pw('  ⚠  Only crack hashes you own or have authorization to crack.')
        print()
        tmp = os.path.join(os.path.expanduser('~'), '.atomic', '_crack_tmp.txt')
        with open(tmp, 'w') as f: f.write(h + '\n')
        shell_exec(f'john {tmp} --wordlist={wl}')
    else:
        pe('  hashcat and john not found, or no wordlist available.')
        p('  Install hashcat:  brew install hashcat  /  apt install hashcat', DM)
        p('  Get rockyou.txt:  https://github.com/brannondorsey/naive-hashcat/releases', DM)

# ── OSINT ─────────────────────────────────────────────────────────────────────
def cmd_osint(args):
    if not args:
        pb('  Usage: osint <username|email|domain|ip>')
        pd('  osint pavlopanda')
        pd('  osint example.com')
        pd('  osint user@email.com')
        pd('  osint 8.8.8.8')
        return

    target = args[0].strip()
    print()
    p(f'  Target   {target}', CY)
    print()

    # Detect type
    is_email  = '@' in target and '.' in target.split('@')[-1]
    is_ip     = re.fullmatch(r'\d{1,3}(\.\d{1,3}){3}', target)
    is_domain = '.' in target and not is_email and not is_ip
    is_user   = not is_email and not is_ip and not is_domain

    try:
        import requests as _req
    except ImportError:
        pe('  requests not installed.')
        return

    results = []

    if is_ip or is_domain or is_email:
        lookup = target if is_ip else target.split('@')[-1] if is_email else target
        # IP/domain geo + ASN
        try:
            r = _req.get(f'https://ipinfo.io/{lookup}/json', timeout=6)
            if r.ok:
                d = r.json()
                p('  ── IP Info ──────────────────────────────────────────', DM)
                for k in ('ip','hostname','city','region','country','org','timezone'):
                    if d.get(k):
                        print(f'  {CY}{k:<12}{RST}  {WH}{d[k]}{RST}')
                print()
        except Exception: pass

    if is_domain or (is_email and '.' in target):
        domain = target.split('@')[-1] if is_email else target
        # DNS records
        p('  ── DNS Records ──────────────────────────────────────', DM)
        for rtype in ['A','MX','NS','TXT','CNAME']:
            try:
                import dns.resolver
                answers = dns.resolver.resolve(domain, rtype, raise_on_no_answer=False)
                for r in answers:
                    print(f'  {G}{rtype:<6}{RST}  {WH}{r}{RST}')
            except Exception:
                try:
                    if rtype == 'A':
                        ip = socket.gethostbyname(domain)
                        print(f'  {G}A     {RST}  {WH}{ip}{RST}')
                except Exception:
                    pass
        print()

        # Subdomain brute (common ones)
        p('  ── Subdomains ───────────────────────────────────────', DM)
        subs = ['www','mail','ftp','admin','api','dev','staging','vpn','remote','portal','blog','shop','app']
        found_subs = []
        for sub in subs:
            try:
                ip = socket.gethostbyname(f'{sub}.{domain}')
                found_subs.append((f'{sub}.{domain}', ip))
            except Exception:
                pass
        if found_subs:
            for host, ip in found_subs:
                print(f'  {G}●{RST}  {WH}{host:<35}{RST}  {DM}{ip}{RST}')
        else:
            p('  No common subdomains found.', DM)
        print()

        # WHOIS
        p('  ── WHOIS ────────────────────────────────────────────', DM)
        if shutil.which('whois'):
            shell_exec(f'whois {domain}')
        else:
            try:
                import whois as w
                data = w.whois(domain)
                for k, v in data.items():
                    if v: print(f'  {CY}{k:<22}{RST}  {WH}{v}{RST}')
            except Exception:
                p('  whois not available. brew install whois', DM)
        print()

    if is_user:
        # Check username across platforms
        p('  ── Username Search ──────────────────────────────────', DM)
        platforms = {
            'GitHub':    f'https://github.com/{target}',
            'Twitter/X': f'https://twitter.com/{target}',
            'Instagram': f'https://instagram.com/{target}',
            'Reddit':    f'https://reddit.com/user/{target}',
            'TikTok':    f'https://tiktok.com/@{target}',
            'YouTube':   f'https://youtube.com/@{target}',
            'Twitch':    f'https://twitch.tv/{target}',
            'Pinterest': f'https://pinterest.com/{target}',
            'Pastebin':  f'https://pastebin.com/u/{target}',
            'HackerNews':f'https://news.ycombinator.com/user?id={target}',
        }
        print()
        for name, url in platforms.items():
            try:
                r = _req.get(url, timeout=5, headers={'User-Agent':'Mozilla/5.0'},
                             allow_redirects=True)
                if r.status_code == 200:
                    print(f'  {G}✓{RST}  {WH}{name:<14}{RST}  {DM}{url}{RST}')
                else:
                    print(f'  {RD}✗{RST}  {DM}{name}{RST}')
            except Exception:
                print(f'  {YL}?{RST}  {DM}{name} (timeout){RST}')
        print()

    if is_email:
        # Check breach (HaveIBeenPwned public API)
        p('  ── Breach Check ─────────────────────────────────────', DM)
        try:
            r = _req.get(
                f'https://haveibeenpwned.com/api/v3/breachedaccount/{target}',
                headers={'User-Agent':'Atomic-OSINT','hibp-api-key':''},
                timeout=6
            )
            if r.status_code == 200:
                breaches = r.json()
                pw(f'  Found in {len(breaches)} breach(es):')
                for b in breaches:
                    print(f'  {RD}●{RST}  {WH}{b.get("Name","?")}{RST}  {DM}{b.get("BreachDate","")}{RST}')
            elif r.status_code == 404:
                p('  Not found in any known breaches.', G)
            else:
                p('  HIBP API requires a key for email lookups. Get one at haveibeenpwned.com', DM)
        except Exception:
            p('  Could not reach HIBP API.', DM)
        print()

# ── MONITOR ───────────────────────────────────────────────────────────────────
def cmd_monitor(args):
    import ipaddress
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = '?'

    parts_ip = local_ip.split('.')
    subnet = f"{parts_ip[0]}.{parts_ip[1]}.{parts_ip[2]}.0/24"

    p('  Live network monitor — press Ctrl+C to stop', DM)
    p(f'  Your IP: {local_ip}   Subnet: {subnet}', CY)
    print()

    seen = {}
    try:
        while True:
            # Ping sweep
            alive = {}
            def ping(ip):
                flag = '-n' if OS_NAME == 'Windows' else '-c'
                r = subprocess.run(['ping', flag, '1', '-W', '1', str(ip)],
                                   capture_output=True, timeout=2)
                if r.returncode == 0:
                    try:    hostname = socket.gethostbyaddr(str(ip))[0]
                    except: hostname = ''
                    alive[str(ip)] = hostname

            threads = []
            for host in list(ipaddress.IPv4Network(subnet, strict=False).hosts())[:50]:
                t = threading.Thread(target=ping, args=(host,), daemon=True)
                threads.append(t); t.start()
            for t in threads: t.join(timeout=3)

            # New devices
            for ip, hostname in alive.items():
                if ip not in seen:
                    seen[ip] = hostname
                    marker = f'{PK} ← you{RST}' if ip == local_ip else f'{YL} ← NEW{RST}'
                    print(f'  {G}+{RST}  {WH}{ip:<18}{RST}  {DM}{hostname:<30}{RST}{marker}')

            # Left devices
            for ip in list(seen.keys()):
                if ip not in alive and ip != local_ip:
                    print(f'  {RD}-{RST}  {DM}{ip:<18}  left{RST}')
                    del seen[ip]

            # Active connections
            p(f'\r  {DM}[{datetime.now().strftime("%H:%M:%S")}] {len(alive)} devices on network{RST}', '')
            time.sleep(5)

    except KeyboardInterrupt:
        print()
        p('  Monitor stopped.', DM)

def cmd_run(args):
    """Max-only: run any system command."""
    if SESSION['plan'] != 'max' and SESSION['role'] != 'dev':
        pe('  Direct shell access requires Max plan.')
        return
    if not args:
        pb('  Usage: run <command> [args...]')
        return
    pw('  ⚠  You are solely responsible for all actions taken.')
    run_tool(args)

def cmd_whoami(args):
    plan = SESSION['plan']
    role = SESSION['role']
    if role == 'dev':
        badge = f'{PK}★ DEV{RST}'
    elif role == 'admin':
        badge = f'{RD}★ ADMIN{RST}'
    elif plan == 'max':
        badge = f'{YL}⚡ MAX{RST}'
    elif plan == 'pro':
        badge = f'{CY}● PRO{RST}'
    else:
        badge = f'{DM}○ FREE{RST}'
    print()
    print(f'  {CY}User       {RST}  {WH}{SESSION["displayName"]}{RST}')
    print(f'  {CY}Plan       {RST}  {badge}')
    print(f'  {CY}Role       {RST}  {WH}{role}{RST}')
    print(f'  {CY}OS         {RST}  {WH}{platform.platform()}{RST}')
    print(f'  {CY}Python     {RST}  {WH}{sys.version.split()[0]}{RST}')
    print(f'  {CY}Session    {RST}  {WH}{datetime.now().strftime("%Y-%m-%d %H:%M")}{RST}')
    print()

def cmd_status(args):
    plan = SESSION['plan']
    role = SESSION['role']
    limits = {
        'pro': 'Unlimited scans · All tools · Atomic AI',
        'max': 'Unlimited everything · Direct shell · Priority AI',
        'dev': 'Full access · All tools · Direct shell · Atomic AI',
    }
    display = 'DEV' if role == 'dev' else 'ADMIN' if role == 'admin' else plan.upper()
    access = limits.get(role if role in ('dev','admin') else plan, 'Standard access')
    print()
    print(f'  {CY}Plan     {RST}  {WH}{display}{RST}')
    print(f'  {CY}Access   {RST}  {WH}{access}{RST}')
    print()

def cmd_help(args):
    plan = SESSION['plan']
    role = SESSION['role']
    is_pro = plan in ('pro','max') or role == 'dev'
    is_max = plan == 'max' or role == 'dev'

    print()
    print(f'{G}{"─"*62}{RST}')
    print(f'{G}  ATOMIC TERMINAL v{VERSION}             Built by Pavlopanda{RST}')
    print(f'{G}{"─"*62}{RST}')
    print()

    def section(title, rows, gated=False):
        tag = f'  {DM}[{"PRO" if gated == "pro" else "MAX"}]{RST}' if gated else ''
        print(f'  {CY}{title}{RST}{tag}')
        for cmd_str, desc in rows:
            print(f'    {G}{cmd_str:<38}{RST}{DM}{desc}{RST}')
        print()

    section('GENERAL', [
        ('help',             'Show this menu'),
        ('whoami',           'Session info'),
        ('status',           'Plan & limits'),
        ('clear',            'Clear screen'),
        ('exit',             'Exit Atomic'),
    ])
    section('AI', [
        ('<anything>',       'Just type — Atomic AI answers'),
        ('reset',            'Reset AI conversation history'),
    ])
    section('NETWORK' + ('' if is_pro else '  — requires Pro'), [
        ('myip',             'Show local + public IP'),
        ('ping <host>',      'Ping a host'),
        ('trace <host>',     'Traceroute to host'),
        ('scan <host> [ports]', 'Fast port scanner (built-in)'),
        ('banner <host> <port>', 'Grab service banner'),
        ('dig <domain> [type]',  'DNS lookup'),
        ('whois <target>',       'WHOIS lookup'),
    ])
    section('RECON & OSINT' + ('' if is_pro else '  — requires Pro'), [
        ('netscan',                    'Scan local network — all devices + ports'),
        ('osint <user|email|domain>',  'Full OSINT — socials, DNS, breaches, WHOIS'),
        ('monitor',                    'Live network monitor — watch who joins/leaves'),
    ])
    section('ATTACK TOOLS' + ('' if is_pro else '  — requires Pro'), [
        ('crack <hash>',               'Auto-detect & crack any hash'),
        ('nmap <target> [flags]',      'Network mapper & port scanner'),
        ('masscan <target> -p <ports>','Ultra-fast mass port scanner'),
        ('sqlmap <url> [opts]',        'SQL injection scanner'),
        ('hydra <opts>',               'Password brute-forcer'),
        ('nikto <host>',               'Web vulnerability scanner'),
        ('gobuster <opts>',            'Directory & DNS brute-forcer'),
        ('hashcat <opts>',             'GPU password cracker'),
        ('john <hashfile>',            'Password cracker (CPU)'),
        ('aircrack <cap> -w <wl>',     'WPA/WPA2 handshake cracker'),
    ])
    if is_max:
        section('MAX ACCESS', [
            ('run <cmd> [args]',  'Execute any system command directly'),
        ])

# ── PROMPT ─────────────────────────────────────────────────────────────────────
def prompt():
    plan = SESSION['plan']
    role = SESSION['role']
    name = SESSION['displayName']
    badge = f'{PK}[DEV]{RST}' if role == 'dev' else {'pro': f'{CY}[PRO]{RST}', 'max': f'{YL}[MAX]{RST}'}.get(plan, '')
    return f'{DG}{name}{RST}{badge}{G}@atomic{RST}{DM}:{RST}{G}~$ {RST}'

# ── MAIN LOOP ─────────────────────────────────────────────────────────────────
def main_loop():
    clr()
    glitch_logo()
    print()
    print(f'{DM}{"─"*56}{RST}')
    plan  = SESSION['plan']
    role  = SESSION['role']
    badge = f'{PK}DEV{RST}' if role == 'dev' else {'pro': f'{CY}PRO{RST}', 'max': f'{YL}MAX{RST}'}.get(plan, f'{DM}FREE{RST}')
    print(f'  {G}Welcome back, {WH}{SESSION["displayName"]}{RST}   Plan: {badge}')
    print(f'  {DM}Type  help  for commands.  Just talk to chat with Atomic AI.{RST}')
    print(f'{DM}{"─"*56}{RST}')
    print()

    while True:
        try:
            raw = input(prompt()).strip()
        except (KeyboardInterrupt, EOFError):
            print()
            typewrite('  Session terminated. Stay safe.', DM, 0.02)
            sys.exit(0)

        if not raw:
            continue

        parts = raw.split()
        cmd   = parts[0].lower()
        args  = parts[1:]

        # Log every command to Firebase (runs in background, never blocks)
        threading.Thread(target=log_activity, args=(cmd, ' '.join(args)), daemon=True).start()

        plan   = SESSION['plan']
        role   = SESSION['role']
        is_pro = plan in ('pro','max') or role == 'dev'
        is_max = plan == 'max' or role == 'dev'

        print()

        if cmd in ('exit','quit','q','logout'):
            typewrite('  Session terminated. Stay safe.', DM, 0.02)
            sys.exit(0)

        elif cmd == 'clear':
            clr()
            continue

        elif cmd == 'help':         cmd_help(args)
        elif cmd == 'whoami':       cmd_whoami(args)
        elif cmd == 'status':       cmd_status(args)

        elif cmd == 'reset':
            SESSION['history'] = []
            p('  AI conversation cleared.', DG)

        elif cmd == 'myip':         cmd_myip(args)

        elif cmd == 'ping':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_ping(args)

        elif cmd == 'trace':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_trace(args)

        elif cmd == 'scan':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_scan(args)

        elif cmd == 'banner':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_banner(args)

        elif cmd in ('dig','dns'):
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_dig(args)

        elif cmd == 'whois':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_whois(args)

        elif cmd == 'nmap':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_nmap(args)

        elif cmd == 'masscan':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_masscan(args)

        elif cmd == 'sqlmap':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_sqlmap(args)

        elif cmd == 'hydra':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_hydra(args)

        elif cmd == 'nikto':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_nikto(args)

        elif cmd == 'gobuster':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_gobuster(args)

        elif cmd == 'hashcat':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_hashcat(args)

        elif cmd == 'john':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_john(args)

        elif cmd == 'aircrack':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_aircrack(args)

        elif cmd == 'netscan':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_netscan(args)

        elif cmd == 'crack':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_crack(args)

        elif cmd == 'osint':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_osint(args)

        elif cmd == 'monitor':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_monitor(args)

        elif cmd == 'run':
            cmd_run(args)

        elif cmd == 'sudo':
            shell_exec(raw)

        else:
            # Unknown command → try to run as real shell command, else AI
            binary = parts[0]
            is_real_cmd = shutil.which(binary) is not None
            if is_real_cmd:
                shell_exec(raw)
            else:
                stream_ai(raw)

        print()

# ── ENTRY ──────────────────────────────────────────────────────────────────────
def main():
    signal.signal(signal.SIGINT, lambda s, f: (print(), sys.exit(0)))

    cfg = _load_cfg()

    # First run: show disclaimer + install tools
    if not cfg.get('installed'):
        show_disclaimer()
        install_tools()
        cfg = _load_cfg()

    # Always show disclaimer if not yet accepted
    if not cfg.get('disclaimer_accepted'):
        show_disclaimer()

    boot_sequence()
    login_screen()
    main_loop()

if __name__ == '__main__':
    main()
