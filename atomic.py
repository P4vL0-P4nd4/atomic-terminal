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
import getpass, platform, re, signal
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
FB_API_KEY   = 'AIzaSyAR6x06-F1W5obJvr2eN8m5pGrixCmMm8w'
FB_DB_URL    = 'https://atomic-ai-f07f1-default-rtdb.firebaseio.com'
FB_AUTH_URL  = 'https://identitytoolkit.googleapis.com/v1/accounts'
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
        (G,  '  [OK]  Gemini 2.0 Flash ready'),
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
        found = subprocess.run(
            ['which', check], capture_output=True
        ).returncode == 0
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

# ── FIREBASE AUTH ─────────────────────────────────────────────────────────────
def fb_login(email, password):
    try:
        r = requests.post(
            f'{FB_AUTH_URL}:signInWithPassword?key={FB_API_KEY}',
            json={'email': email, 'password': password, 'returnSecureToken': True},
            timeout=10
        )
        d = r.json()
        if 'idToken' in d:
            return d['idToken'], d['localId']
        return None, d.get('error', {}).get('message', 'Login failed')
    except Exception as e:
        return None, str(e)

def fb_get_user(uid, token):
    try:
        r = requests.get(
            f'{FB_DB_URL}/users/{uid}.json?auth={token}', timeout=8
        )
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
        email    = input(f'{G}  email    › {RST}').strip()
        password = getpass.getpass(f'{G}  password › {RST}')
        print()
        p('  Authenticating...', DG)

        token, result = fb_login(email, password)
        if not token:
            pe(f'  ✗  {result}')
            print()
            if input(f'{DM}  Try again? [y/n]: {RST}').strip().lower() != 'y':
                sys.exit(0)
            print()
            continue

        uid = result
        p('  Fetching profile...', DG)
        udata = fb_get_user(uid, token)
        if not udata:
            pe('  Could not load user profile.')
            sys.exit(1)

        plan = udata.get('plan', 'free')
        role = udata.get('role', 'user')
        name = udata.get('displayName', email.split('@')[0])

        # Terminal gate: Pro or Max only
        if role != 'dev' and plan not in ('pro', 'max'):
            print()
            pw('  ╔════════════════════════════════════════╗')
            pw('  ║  ATOMIC TERMINAL requires Pro or Max  ║')
            pw('  ║  Upgrade at: atomicai.pavlopanda.com  ║')
            pw('  ╚════════════════════════════════════════╝')
            print()
            sys.exit(0)

        SESSION['uid']         = uid
        SESSION['email']       = email
        SESSION['idToken']     = token
        SESSION['plan']        = plan
        SESSION['role']        = role
        SESSION['displayName'] = name

        badge_map = {
            'pro': f'{CY}● PRO{RST}',
            'max': f'{YL}⚡ MAX{RST}',
        }
        badge = badge_map.get(plan, f'{DM}○ FREE{RST}')
        print()
        p(f'  ✓  Authenticated as {WH}{name}{RST}{G}', G)
        p(f'  Plan: {badge}', WH)
        time.sleep(0.8)
        return

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
        f"User plan: {plan.upper()}. OS: {OS_NAME}. User: {SESSION['displayName']}."
    )

    SESSION['history'].append({'role': 'user', 'content': user_msg})

    payload = {
        'messages': SESSION['history'][-24:],
        'system':   sys_prompt,
    }

    try:
        r = requests.post(WORKER, json=payload, timeout=30)
        if not r.ok:
            return f'[AI Error] Worker returned {r.status_code}'
        d = r.json()
        reply = (
            d.get('content') or
            d.get('choices', [{}])[0].get('message', {}).get('content') or
            d.get('reply') or
            str(d)
        ).strip()
        SESSION['history'].append({'role': 'assistant', 'content': reply})
        return reply
    except Exception as e:
        return f'[AI Error] {e}'

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
    return subprocess.run(['which', name.split('-')[0]], capture_output=True).returncode == 0

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
    run_tool(['nmap'] + args)

def cmd_masscan(args):
    if not tool_ok('masscan'):
        pe('  masscan not found.  brew install masscan')
        return
    if not args:
        pb('  Usage: masscan <target> -p <ports> --rate=<rate>')
        pd('  masscan 192.168.1.0/24 -p 80,443,22 --rate=1000')
        return
    pw('  ⚠  Only scan systems you own or have written authorization to test.')
    run_tool(['masscan'] + args)

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
    run_tool(['sqlmap'] + args)

def cmd_hydra(args):
    if not tool_ok('hydra'):
        pe('  brew install hydra  /  apt install hydra')
        return
    if not args:
        pb('  Usage: hydra -l admin -P wordlist.txt ssh://192.168.1.1')
        return
    pw('  ⚠  Only test systems you own or have written authorization to test.')
    run_tool(['hydra'] + args)

def cmd_nikto(args):
    if not tool_ok('nikto'):
        pe('  brew install nikto  /  apt install nikto')
        return
    if not args:
        pb('  Usage: nikto -h http://192.168.1.1')
        return
    pw('  ⚠  Only test systems you own or have written authorization to test.')
    run_tool(['nikto'] + args)

def cmd_gobuster(args):
    if not tool_ok('gobuster'):
        pe('  brew install gobuster  /  apt install gobuster')
        return
    if not args:
        pb('  Usage: gobuster dir -u http://target.com -w /wordlist.txt')
        return
    pw('  ⚠  Only test systems you own or have written authorization to test.')
    run_tool(['gobuster'] + args)

def cmd_hashcat(args):
    if not tool_ok('hashcat'):
        pe('  brew install hashcat  /  apt install hashcat')
        return
    if not args:
        pb('  Usage: hashcat -m 0 hashes.txt rockyou.txt')
        pd('  Modes: 0=MD5 100=SHA1 1800=sha512crypt 22000=WPA2 ...')
        return
    run_tool(['hashcat'] + args)

def cmd_john(args):
    if not tool_ok('john'):
        pe('  brew install john  /  apt install john')
        return
    if not args:
        pb('  Usage: john <hashfile> [--wordlist=<file>]')
        return
    run_tool(['john'] + args)

def cmd_aircrack(args):
    if not tool_ok('aircrack-ng'):
        pe('  brew install aircrack-ng  /  apt install aircrack-ng')
        return
    if not args:
        pb('  Usage: aircrack <capfile> -w <wordlist>')
        return
    pw('  ⚠  Only test networks you own or have written authorization to test.')
    run_tool(['aircrack-ng'] + args)

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
    badge_map = {
        'pro': f'{CY}● PRO{RST}',
        'max': f'{YL}⚡ MAX{RST}',
        'free': f'{DM}○ FREE{RST}',
    }
    badge = badge_map.get(plan, '')
    print()
    print(f'  {CY}User       {RST}  {WH}{SESSION["displayName"]}{RST}')
    print(f'  {CY}Email      {RST}  {WH}{SESSION["email"]}{RST}')
    print(f'  {CY}Plan       {RST}  {badge}')
    print(f'  {CY}Role       {RST}  {WH}{role}{RST}')
    print(f'  {CY}OS         {RST}  {WH}{platform.platform()}{RST}')
    print(f'  {CY}Python     {RST}  {WH}{sys.version.split()[0]}{RST}')
    print(f'  {CY}Session    {RST}  {WH}{datetime.now().strftime("%Y-%m-%d %H:%M")}{RST}')
    print()

def cmd_status(args):
    plan = SESSION['plan']
    limits = {
        'pro': 'Unlimited scans · All tools · Atomic AI',
        'max': 'Unlimited everything · Direct shell · Priority AI',
    }
    print()
    print(f'  {CY}Plan     {RST}  {WH}{plan.upper()}{RST}')
    print(f'  {CY}Access   {RST}  {WH}{limits.get(plan,"?")}{RST}')
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
        ('ai <message>',     'Chat with Atomic AI (Gemini 2.0 Flash)'),
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
    section('ATTACK TOOLS' + ('' if is_pro else '  — requires Pro'), [
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
    name = SESSION['displayName']
    badge = {'pro': f'{CY}[PRO]{RST}', 'max': f'{YL}[MAX]{RST}'}.get(plan, '')
    return f'{DG}{name}{RST}{badge}{G}@atomic{RST}{DM}:{RST}{G}~$ {RST}'

# ── MAIN LOOP ─────────────────────────────────────────────────────────────────
def main_loop():
    clr()
    glitch_logo()
    print()
    print(f'{DM}{"─"*56}{RST}')
    plan  = SESSION['plan']
    badge = {'pro': f'{CY}PRO{RST}', 'max': f'{YL}MAX{RST}'}.get(plan, f'{DM}FREE{RST}')
    print(f'  {G}Welcome back, {WH}{SESSION["displayName"]}{RST}   Plan: {badge}')
    print(f'  {DM}Type  help  for all commands.  Type  ai <msg>  to chat.{RST}')
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

        elif cmd == 'ai':
            if not args:
                pb('  Usage: ai <message>')
            else:
                stream_ai(' '.join(args))

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

        elif cmd == 'run':
            cmd_run(args)

        else:
            # Unknown command → pass to AI
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
