import streamlit as st
import urllib.parse
from datetime import datetime
import json
import re

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="DORK ENGINE // ZWANSKI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stApp"] {
    background: #050508 !important;
    color: #c8ffc8 !important;
    font-family: 'Share Tech Mono', monospace !important;
}

[data-testid="stApp"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,255,65,0.015) 2px, rgba(0,255,65,0.015) 4px),
        repeating-linear-gradient(90deg, transparent, transparent 80px, rgba(0,255,65,0.008) 80px, rgba(0,255,65,0.008) 81px);
    pointer-events: none;
    z-index: 0;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }

[data-testid="stMain"], [data-testid="block-container"] {
    padding: 0 !important;
    max-width: 100% !important;
}

/* HEADER */
.dork-header {
    background: linear-gradient(135deg, #000a00 0%, #001a00 50%, #000a00 100%);
    border-bottom: 2px solid #00ff41;
    padding: 2rem 3rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.dork-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -10%;
    width: 120%;
    height: 200%;
    background: radial-gradient(ellipse at center, rgba(0,255,65,0.06) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:0.5} 50%{opacity:1} }

.header-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: #00ff41;
    text-shadow: 0 0 20px rgba(0,255,65,0.8), 0 0 40px rgba(0,255,65,0.4);
    letter-spacing: 0.15em;
    position: relative;
    z-index: 1;
}
.header-sub {
    font-family: 'Exo 2', sans-serif;
    font-size: 0.85rem;
    color: #4dff4d;
    letter-spacing: 0.3em;
    margin-top: 0.3rem;
    position: relative;
    z-index: 1;
    opacity: 0.8;
}
.header-warning {
    font-size: 0.7rem;
    color: #ff6b35;
    letter-spacing: 0.2em;
    margin-top: 0.5rem;
    position: relative;
    z-index: 1;
    border: 1px solid #ff6b35;
    display: inline-block;
    padding: 0.2rem 0.8rem;
    text-transform: uppercase;
}

/* PASSWORD SCREEN */
.pw-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    padding: 3rem;
}
.pw-box {
    border: 1px solid #00ff41;
    background: rgba(0,255,65,0.03);
    padding: 3rem;
    width: 100%;
    max-width: 420px;
    text-align: center;
    box-shadow: 0 0 40px rgba(0,255,65,0.1), inset 0 0 40px rgba(0,255,65,0.02);
}
.pw-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem;
    color: #00ff41;
    letter-spacing: 0.3em;
    margin-bottom: 1.5rem;
}
.pw-lock {
    font-size: 3rem;
    margin-bottom: 1rem;
    filter: drop-shadow(0 0 10px rgba(0,255,65,0.6));
}

/* INPUT STYLING */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #000a00 !important;
    border: 1px solid #00ff41 !important;
    border-radius: 0 !important;
    color: #00ff41 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.95rem !important;
    caret-color: #00ff41 !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    box-shadow: 0 0 15px rgba(0,255,65,0.3) !important;
    border-color: #4dff4d !important;
}
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label {
    color: #4dff4d !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.2em !important;
}

/* BUTTONS */
[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid #00ff41 !important;
    color: #00ff41 !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.2em !important;
    border-radius: 0 !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
    text-transform: uppercase !important;
}
[data-testid="stButton"] button:hover {
    background: rgba(0,255,65,0.1) !important;
    box-shadow: 0 0 20px rgba(0,255,65,0.3) !important;
    color: #ffffff !important;
}

/* CATEGORY CARDS */
.cat-header {
    background: linear-gradient(90deg, rgba(0,255,65,0.12) 0%, transparent 100%);
    border-left: 3px solid #00ff41;
    padding: 0.6rem 1rem;
    margin: 1.5rem 0 0.8rem;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.75rem;
    letter-spacing: 0.25em;
    color: #00ff41;
    text-transform: uppercase;
}
.cat-badge {
    display: inline-block;
    background: rgba(0,255,65,0.15);
    border: 1px solid #00ff41;
    color: #00ff41;
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    padding: 0.1rem 0.5rem;
    margin-left: 0.8rem;
    vertical-align: middle;
}

/* DORK CARDS */
.dork-card {
    background: #000d00;
    border: 1px solid #1a4d1a;
    border-left: 3px solid #00ff41;
    padding: 0.8rem 1rem;
    margin: 0.4rem 0;
    position: relative;
    transition: all 0.2s;
    cursor: pointer;
}
.dork-card:hover {
    border-color: #00ff41;
    background: #001200;
    box-shadow: 0 0 15px rgba(0,255,65,0.1);
}
.dork-label {
    font-size: 0.65rem;
    color: #4dff4d;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
    opacity: 0.7;
}
.dork-query {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #c8ffc8;
    word-break: break-all;
    line-height: 1.5;
}
.dork-engine-badge {
    position: absolute;
    top: 0.5rem;
    right: 0.8rem;
    font-size: 0.55rem;
    letter-spacing: 0.15em;
    padding: 0.15rem 0.5rem;
    border: 1px solid;
    text-transform: uppercase;
}
.badge-google { color: #4285f4; border-color: #4285f4; background: rgba(66,133,244,0.08); }
.badge-github { color: #e040fb; border-color: #e040fb; background: rgba(224,64,251,0.08); }
.badge-shodan { color: #ff6b35; border-color: #ff6b35; background: rgba(255,107,53,0.08); }
.badge-censys { color: #00bcd4; border-color: #00bcd4; background: rgba(0,188,212,0.08); }
.badge-wayback { color: #ffd600; border-color: #ffd600; background: rgba(255,214,0,0.08); }
.badge-paste { color: #ff5252; border-color: #ff5252; background: rgba(255,82,82,0.08); }
.badge-linkedin { color: #0288d1; border-color: #0288d1; background: rgba(2,136,209,0.08); }
.badge-nuclei { color: #76ff03; border-color: #76ff03; background: rgba(118,255,3,0.08); }

/* STATS BAR */
.stats-bar {
    display: flex;
    gap: 2rem;
    padding: 1rem 3rem;
    background: #000a00;
    border-bottom: 1px solid #1a4d1a;
    flex-wrap: wrap;
}
.stat-item {
    display: flex;
    flex-direction: column;
}
.stat-val {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.4rem;
    color: #00ff41;
    font-weight: 700;
    text-shadow: 0 0 10px rgba(0,255,65,0.5);
}
.stat-label {
    font-size: 0.6rem;
    color: #4dff4d;
    letter-spacing: 0.2em;
    opacity: 0.7;
    text-transform: uppercase;
}

/* MAIN CONTENT AREA */
.main-content {
    padding: 1.5rem 3rem 3rem;
}

/* TARGET DISPLAY */
.target-display {
    background: rgba(0,255,65,0.05);
    border: 1px solid #00ff41;
    padding: 1rem 1.5rem;
    margin: 1rem 0 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.target-pill {
    background: rgba(0,255,65,0.12);
    border: 1px solid #00ff41;
    color: #00ff41;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    padding: 0.2rem 0.7rem;
    text-transform: uppercase;
}

/* SECTION TABS */
[data-testid="stTabs"] [role="tablist"] {
    background: #000a00 !important;
    border-bottom: 1px solid #1a4d1a !important;
    gap: 0 !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.15em !important;
    color: #4dff4d !important;
    border-radius: 0 !important;
    padding: 0.6rem 1.2rem !important;
    border: none !important;
    border-right: 1px solid #1a4d1a !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: rgba(0,255,65,0.1) !important;
    color: #00ff41 !important;
    border-bottom: 2px solid #00ff41 !important;
}

/* SELECT BOX */
[data-testid="stSelectbox"] select,
[data-testid="stSelectbox"] > div > div {
    background: #000a00 !important;
    border: 1px solid #00ff41 !important;
    border-radius: 0 !important;
    color: #00ff41 !important;
    font-family: 'Share Tech Mono', monospace !important;
}

/* MULTISELECT */
[data-testid="stMultiSelect"] > div {
    background: #000a00 !important;
    border: 1px solid #00ff41 !important;
    border-radius: 0 !important;
}

/* DOWNLOAD BUTTON */
[data-testid="stDownloadButton"] button {
    background: rgba(0,255,65,0.08) !important;
    border: 1px solid #00ff41 !important;
    color: #00ff41 !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.2em !important;
    border-radius: 0 !important;
}

/* EXPANDER */
[data-testid="stExpander"] {
    background: #000a00 !important;
    border: 1px solid #1a4d1a !important;
    border-radius: 0 !important;
}
[data-testid="stExpander"] summary {
    color: #4dff4d !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* DIVIDER */
hr { border-color: #1a4d1a !important; }

/* ALERT */
[data-testid="stAlert"] {
    background: rgba(255,107,53,0.08) !important;
    border: 1px solid #ff6b35 !important;
    border-radius: 0 !important;
    color: #ff6b35 !important;
}

/* FOOTER */
.dork-footer {
    background: #000500;
    border-top: 1px solid #1a4d1a;
    padding: 1.5rem 3rem;
    margin-top: 3rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}
.footer-left {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.65rem;
    color: #00ff41;
    letter-spacing: 0.2em;
}
.footer-center {
    font-size: 0.6rem;
    color: #ff6b35;
    letter-spacing: 0.15em;
    text-align: center;
    border: 1px solid rgba(255,107,53,0.3);
    padding: 0.3rem 1rem;
    text-transform: uppercase;
}
.footer-right {
    font-size: 0.6rem;
    color: #4dff4d;
    letter-spacing: 0.15em;
    opacity: 0.6;
    text-align: right;
}

/* CHECKBOX */
[data-testid="stCheckbox"] label {
    color: #4dff4d !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* CODE BLOCK */
code {
    background: #000a00 !important;
    color: #00ff41 !important;
    border: 1px solid #1a4d1a !important;
    font-family: 'Share Tech Mono', monospace !important;
    padding: 0.1rem 0.4rem !important;
    border-radius: 0 !important;
}

/* SCROLLBAR */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #000500; }
::-webkit-scrollbar-thumb { background: #1a4d1a; }
::-webkit-scrollbar-thumb:hover { background: #00ff41; }
</style>
""", unsafe_allow_html=True)


# ── HELPER: PARSE TARGET ──────────────────────────────────────
def parse_target(url: str) -> dict:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urllib.parse.urlparse(url)
    hostname = parsed.netloc or parsed.path
    hostname = hostname.split(":")[0].lstrip("www.")
    parts = hostname.split(".")
    if len(parts) >= 2:
        tld = ".".join(parts[-2:])
        subdomain = ".".join(parts[:-2]) if len(parts) > 2 else ""
        root = parts[-2]
    else:
        tld = hostname
        subdomain = ""
        root = hostname
    return {
        "raw": url,
        "hostname": hostname,
        "tld": tld,
        "root": root,
        "subdomain": subdomain,
        "scheme": parsed.scheme,
        "quoted": urllib.parse.quote(hostname),
    }


# ── DORK ENGINE ───────────────────────────────────────────────
def generate_dorks(t: dict, tech_stack: list, extra_keywords: str) -> list:
    d = t["tld"]
    h = t["hostname"]
    r = t["root"]
    kw = [k.strip() for k in extra_keywords.split(",") if k.strip()]
    dorks = []

    def add(engine, category, label, query, link=None):
        base_links = {
            "Google": f"https://www.google.com/search?q={urllib.parse.quote(query)}",
            "GitHub": f"https://github.com/search?q={urllib.parse.quote(query)}&type=code",
            "Shodan": f"https://www.shodan.io/search?query={urllib.parse.quote(query)}",
            "Censys": f"https://search.censys.io/search?resource=hosts&q={urllib.parse.quote(query)}",
            "Wayback": f"https://web.archive.org/web/*/{query}",
            "Pastebin": f"https://www.google.com/search?q=site:pastebin.com+{urllib.parse.quote(query)}",
            "LinkedIn": f"https://www.google.com/search?q=site:linkedin.com+{urllib.parse.quote(query)}",
            "Nuclei": None,
        }
        dorks.append({
            "engine": engine,
            "category": category,
            "label": label,
            "query": query,
            "link": link or base_links.get(engine, "#")
        })

    # ══ GOOGLE — SENSITIVE FILES ══════════════════════════════
    cat = "Sensitive Files & Configs"
    add("Google", cat, "ENV files", f'site:{d} ext:env "DB_PASSWORD" OR "APP_KEY" OR "SECRET"')
    add("Google", cat, "Config dumps", f'site:{d} ext:xml OR ext:conf OR ext:cfg inurl:config')
    add("Google", cat, "YAML secrets", f'site:{d} ext:yml OR ext:yaml "password:" OR "secret:" OR "token:"')
    add("Google", cat, "PHP config leak", f'site:{d} ext:php inurl:config OR inurl:settings "define(" "password"')
    add("Google", cat, "Backup files", f'site:{d} ext:bak OR ext:old OR ext:backup OR ext:swp')
    add("Google", cat, "Log files exposed", f'site:{d} ext:log "Exception" OR "Error" OR "password"')
    add("Google", cat, "SQL dumps", f'site:{d} ext:sql "INSERT INTO" OR "CREATE TABLE" OR "DROP TABLE"')
    add("Google", cat, "Private keys", f'site:{d} ext:pem OR ext:key OR ext:ppk "PRIVATE KEY"')
    add("Google", cat, "JSON credentials", f'site:{d} ext:json "password" OR "api_key" OR "access_token"')
    add("Google", cat, "Git config exposed", f'site:{d} inurl:.git/config "url ="')

    # ══ GOOGLE — AUTH & ADMIN ═════════════════════════════════
    cat = "Auth & Admin Panels"
    add("Google", cat, "Login panels", f'site:{d} inurl:login OR inurl:signin OR inurl:auth inurl:admin')
    add("Google", cat, "Admin dashboards", f'site:{d} inurl:admin OR inurl:backend OR inurl:dashboard OR inurl:manager')
    add("Google", cat, "phpMyAdmin", f'site:{d} inurl:phpmyadmin OR inurl:pma "phpMyAdmin"')
    add("Google", cat, "Webmail panels", f'site:{d} inurl:owa OR inurl:webmail OR inurl:roundcube OR inurl:squirrel')
    add("Google", cat, "Grafana/Kibana", f'site:{d} inurl:grafana OR inurl:kibana OR inurl:elastic')
    add("Google", cat, "Exposed Kubernetes", f'site:{d} inurl:kubernetes OR inurl:k8s OR inurl:api/v1/pods')
    add("Google", cat, "Jenkins CI", f'site:{d} inurl:jenkins "Dashboard [Jenkins]" OR intitle:"Dashboard [Jenkins]"')
    add("Google", cat, "GitLab instance", f'site:{d} inurl:gitlab "GitLab" inurl:users OR inurl:admin')
    add("Google", cat, "Portainer Docker", f'site:{d} inurl:portainer OR intitle:"Portainer"')
    add("Google", cat, "Default creds page", f'site:{d} intitle:"Please change your password" OR intitle:"Default password"')

    # ══ GOOGLE — API & DOCS ═══════════════════════════════════
    cat = "API Exposure & Docs"
    add("Google", cat, "Swagger UI", f'site:{d} inurl:swagger OR inurl:api-docs OR inurl:openapi "swagger-ui"')
    add("Google", cat, "GraphQL endpoint", f'site:{d} inurl:graphql OR inurl:graphiql')
    add("Google", cat, "REST API docs", f'site:{d} inurl:api/v1 OR inurl:api/v2 OR inurl:rest/api')
    add("Google", cat, "Postman collections", f'site:{d} ext:json "postman_collection" OR "info":{{"name"')
    add("Google", cat, "WSDL exposed", f'site:{d} ext:wsdl OR inurl:?wsdl OR inurl:?WSDL')
    add("Google", cat, "OpenID/.well-known", f'site:{d} inurl:/.well-known/openid-configuration')
    add("Google", cat, "JWKS endpoint", f'site:{d} inurl:/.well-known/jwks OR inurl:jwks.json')
    add("Google", cat, "OAuth token leak", f'site:{d} inurl:oauth OR inurl:authorize "client_id" "redirect_uri"')

    # ══ GOOGLE — ERROR & DEBUG ════════════════════════════════
    cat = "Error & Debug Leaks"
    add("Google", cat, "Stack traces", f'site:{d} "Exception in thread" OR "Traceback (most recent call" OR "at java.lang"')
    add("Google", cat, "PHP errors", f'site:{d} "Warning: " "on line" OR "Fatal error:" "in /" OR "Parse error:"')
    add("Google", cat, "DB errors", f'site:{d} "ORA-" OR "MySQL server version" OR "PostgreSQL ERROR" OR "SQLSTATE"')
    add("Google", cat, "ASP.NET errors", f'site:{d} "Server Error in" "Application" OR "Runtime Error" "ASP.NET"')
    add("Google", cat, "Debug mode active", f'site:{d} intitle:"DEBUG" "debug=true" OR "APP_DEBUG" OR "django.conf"')
    add("Google", cat, "Internal IP leaked", f'site:{d} "192.168." OR "10.0." OR "172.16." "internal" OR "server"')
    add("Google", cat, "Path traversal sign", f'site:{d} "root:x:0:0" OR "bin/bash" OR "/etc/passwd"')

    # ══ GOOGLE — SENSITIVE DOCS ════════════════════════════════
    cat = "Sensitive Documents"
    add("Google", cat, "Internal PDFs", f'site:{d} ext:pdf inurl:internal OR inurl:confidentiel OR inurl:prive OR inurl:secret')
    add("Google", cat, "Excel with data", f'site:{d} ext:xlsx OR ext:xls "password" OR "confidentiel" OR inurl:staff')
    add("Google", cat, "Word docs", f'site:{d} ext:docx OR ext:doc inurl:internal OR "ne pas diffuser"')
    add("Google", cat, "Contract docs", f'site:{d} ext:pdf "contrat" OR "convention" OR "accord" OR "confidential"')
    add("Google", cat, "HR / employee data", f'site:{d} ext:csv OR ext:xlsx "nom" OR "prenom" OR "email" OR "salaire"')
    add("Google", cat, "Audit reports", f'site:{d} ext:pdf "audit" OR "pentest" OR "vulnerability" OR "sécurité"')

    # ══ GOOGLE — NETWORK & INFRA ══════════════════════════════
    cat = "Network & Infrastructure"
    add("Google", cat, "VPN login pages", f'site:{d} inurl:vpn OR inurl:remote OR inurl:citrix OR inurl:pulse "login"')
    add("Google", cat, "Network devices", f'site:{d} intitle:"RouterOS" OR intitle:"Cisco" OR intitle:"Fortinet" OR intitle:"pfSense"')
    add("Google", cat, "Camera feeds", f'site:{d} inurl:view/index.shtml OR inurl:axis-cgi OR intitle:"Live View / - AXIS"')
    add("Google", cat, "SNMP exposed", f'site:{d} "public" inurl:snmp OR intitle:"SNMP"')
    add("Google", cat, "RDP exposed", f'site:{d} intitle:"Remote Desktop Web Connection" OR inurl:rdweb')
    add("Google", cat, "BigIP F5 panel", f'site:{d} inurl:/tmui/login.jsp OR intitle:"BIG-IP" "F5"')
    add("Google", cat, "Proxy mgmt panel", f'site:{d} inurl:proxy OR inurl:squid OR intitle:"Squid Analysis"')

    # ══ GOOGLE — SUBDOMAINS & DIRS ════════════════════════════
    cat = "Subdomain & Directory Intel"
    add("Google", cat, "All subdomains", f'site:*.{d} -www')
    add("Google", cat, "Dev/staging env", f'site:{d} inurl:dev OR inurl:staging OR inurl:test OR inurl:preprod OR inurl:rec OR inurl:uat')
    add("Google", cat, "Backup dirs", f'site:{d} intitle:"Index of" "backup" OR "old" OR "archive"')
    add("Google", cat, "Open dir listing", f'site:{d} intitle:"Index of /" "Parent Directory"')
    add("Google", cat, "Exposed uploads", f'site:{d} intitle:"Index of" inurl:upload OR inurl:uploads OR inurl:files')
    add("Google", cat, "Exposed .git", f'site:{d} inurl:.git "HEAD" OR inurl:.svn OR inurl:.hg')
    add("Google", cat, "Temp files", f'site:{d} ext:tmp OR ext:temp OR ext:cache inurl:/{r}/')

    # ══ GOOGLE — TECH-SPECIFIC ════════════════════════════════
    cat = "Tech-Stack Specific"
    for tech in tech_stack:
        t_low = tech.lower()
        if "typo3" in t_low:
            add("Google", cat, "TYPO3 exceptions", f'site:{d} "TYPO3 Exception" OR "TYPO3_CONF_VARS" OR "TypoScript parser"')
            add("Google", cat, "TYPO3 install tool", f'site:{d} inurl:typo3/install OR inurl:typo3conf/LocalConfiguration.php')
            add("Google", cat, "TYPO3 debug output", f'site:{d} "TYPO3 CMS" "An exception occurred" filetype:html')
        if "forgerock" in t_low or "openam" in t_low:
            add("Google", cat, "ForgeRock user enum", f'site:{d} inurl:/json/users OR inurl:/json/realms OR inurl:/json/groups')
            add("Google", cat, "OpenAM server info", f'site:{d} inurl:serverinfo "cookieName" OR "zeroPageLogin"')
        if "thelia" in t_low:
            add("Google", cat, "Thelia admin", f'site:{d} inurl:admin/login OR inurl:thelia/admin')
            add("Google", cat, "Thelia customer data", f'site:{d} inurl:/order/ OR inurl:/customer/ OR inurl:/invoice/ inurl:thelia')
        if "f5" in t_low or "big-ip" in t_low:
            add("Google", cat, "F5 BIG-IP TMUI", f'site:{d} inurl:/tmui/ OR inurl:/hsqlui/ OR "BIG-IP logout"')
        if "horizon" in t_low or "vdi" in t_low:
            add("Google", cat, "VMware Horizon broker", f'site:{d} inurl:broker OR inurl:portal "Horizon" inurl:xml OR inurl:api')
        if "keycloak" in t_low:
            add("Google", cat, "Keycloak realms", f'site:{d} inurl:/auth/realms OR inurl:/realms inurl:openid-configuration')
        if "drupal" in t_low:
            add("Google", cat, "Drupal JSONAPI", f'site:{d} inurl:jsonapi OR inurl:node.json OR inurl:/user/login "Drupal"')
            add("Google", cat, "Drupal update.php", f'site:{d} inurl:update.php OR inurl:install.php "Drupal"')
        if "wordpress" in t_low:
            add("Google", cat, "WP user enum", f'site:{d} inurl:wp-json/wp/v2/users')
            add("Google", cat, "WP plugins exposed", f'site:{d} inurl:wp-content/plugins OR inurl:wp-includes ext:php')
        if "exchange" in t_low or "owa" in t_low:
            add("Google", cat, "OWA login", f'site:{d} inurl:/owa/auth/logon.aspx OR inurl:owa "Outlook Web App"')
            add("Google", cat, "Exchange autodiscover", f'site:{d} inurl:autodiscover/autodiscover.xml')
        if "mobileiron" in t_low or "ivanti" in t_low:
            add("Google", cat, "MobileIron admin", f'site:{d} inurl:mics OR inurl:mobileiron "MobileIron" inurl:admin')
        if "owncloud" in t_low or "nextcloud" in t_low:
            add("Google", cat, "OwnCloud admin", f'site:{d} inurl:owncloud OR inurl:nextcloud inurl:login OR inurl:admin')
            add("Google", cat, "Shared files", f'site:{d} inurl:/s/ "ownCloud" OR "Nextcloud" "public share"')

    # ══ GOOGLE — EXTRA KEYWORDS ═══════════════════════════════
    if kw:
        cat = "Custom Keyword Dorks"
        for k in kw:
            add("Google", cat, f"Keyword: {k}", f'site:{d} "{k}"')
            add("Google", cat, f"File: {k}", f'site:{d} ext:pdf OR ext:docx OR ext:xlsx "{k}"')
            add("Google", cat, f"URL: {k}", f'site:{d} inurl:{k}')

    # ══ GITHUB ════════════════════════════════════════════════
    cat = "GitHub Secrets"
    add("GitHub", cat, "Hardcoded passwords", f'"{d}" password OR passwd OR secret OR credential')
    add("GitHub", cat, "API keys", f'"{d}" api_key OR apikey OR api_secret OR access_token OR bearer')
    add("GitHub", cat, "DB connection strings", f'"{d}" connectionString OR db_password OR DATABASE_URL OR mongodb://')
    add("GitHub", cat, "Private keys", f'"{d}" "BEGIN RSA PRIVATE KEY" OR "BEGIN PRIVATE KEY" OR "BEGIN EC PRIVATE KEY"')
    add("GitHub", cat, "JWT secrets", f'"{d}" jwt_secret OR JWT_SECRET OR jwt_key OR SECRET_KEY')
    add("GitHub", cat, "Internal URLs", f'"{h}" internalurl OR internal_api OR intranet OR ".internal"')
    add("GitHub", cat, "Config files", f'"{d}" filename:LocalConfiguration.php OR filename:.env OR filename:config.yml')
    add("GitHub", cat, "Exposed tokens", f'"{d}" ghp_ OR xox OR sk- OR pk- OR AIza OR AKIA')
    add("GitHub", cat, "SMTP credentials", f'"{d}" smtp_password OR MAIL_PASSWORD OR "smtp://"')
    add("GitHub", cat, "Docker secrets", f'"{d}" filename:docker-compose.yml OR filename:Dockerfile "password" OR "secret"')
    add("GitHub", cat, "Infrastructure code", f'"{d}" filename:*.tf OR filename:*.tfvars "password" OR "token"')
    add("GitHub", cat, "CI/CD secrets", f'"{d}" filename:.travis.yml OR filename:.gitlab-ci.yml OR filename:Jenkinsfile')
    add("GitHub", cat, "Org-specific search", f'org:{r} password OR secret OR token OR key')

    # ══ SHODAN ════════════════════════════════════════════════
    cat = "Shodan Intelligence"
    add("Shodan", cat, "SSL cert hostname", f'ssl:"{d}"')
    add("Shodan", cat, "Admin panels up", f'ssl:"{d}" http.title:"admin" port:443,8443,8080')
    add("Shodan", cat, "F5 BIG-IP", f'ssl:"{d}" product:"BIG-IP"')
    add("Shodan", cat, "Default titles", f'ssl:"{d}" http.title:"login" OR http.title:"admin" OR http.title:"dashboard"')
    add("Shodan", cat, "Open Elastic", f'ssl:"{d}" product:"Elasticsearch" port:9200')
    add("Shodan", cat, "Open MongoDB", f'ssl:"{d}" product:"MongoDB" port:27017')
    add("Shodan", cat, "RDP exposed", f'ssl:"{d}" port:3389 product:"Remote Desktop"')
    add("Shodan", cat, "Jenkins CI", f'ssl:"{d}" http.title:"Dashboard [Jenkins]"')
    add("Shodan", cat, "Tomcat exposed", f'ssl:"{d}" product:"Apache Tomcat" http.title:"Apache Tomcat"')
    add("Shodan", cat, "Swagger UI", f'ssl:"{d}" http.title:"Swagger UI"')
    add("Shodan", cat, "Grafana", f'ssl:"{d}" http.title:"Grafana"')
    add("Shodan", cat, "GitLab", f'ssl:"{d}" http.title:"GitLab"')
    add("Shodan", cat, "200 status + 8443", f'ssl:"{d}" http.status:200 port:8443')
    add("Shodan", cat, "Self-signed certs", f'ssl.cert.issuer.cn:"{r}" ssl.cert.subject.cn:"{r}"')

    # ══ CENSYS ════════════════════════════════════════════════
    cat = "Censys Intelligence"
    add("Censys", cat, "All hosts by domain", f'parsed.names: {d}')
    add("Censys", cat, "Self-signed certs", f'parsed.names: {d} AND tags.raw: "self-signed"')
    add("Censys", cat, "HTTP services", f'parsed.names: {d} AND services.service_name: HTTP')
    add("Censys", cat, "Open non-std ports", f'parsed.names: {d} AND services.port: {{8080, 8443, 8888, 9090, 9200}}')
    add("Censys", cat, "Expired certs", f'parsed.names: {d} AND tags.raw: "expired"')
    add("Censys", cat, "Weak cipher", f'parsed.names: {d} AND tags.raw: "deprecated-cipher"')

    # ══ WAYBACK MACHINE ═══════════════════════════════════════
    cat = "Wayback Machine"
    add("Wayback", cat, "All snapshots", f'{h}/*',
        f'https://web.archive.org/web/*/{h}/*')
    add("Wayback", cat, "Old API endpoints", f'{h}/api/*',
        f'https://web.archive.org/web/*/{h}/api/*')
    add("Wayback", cat, "Old swagger/docs", f'{h}/swagger*',
        f'https://web.archive.org/web/*/{h}/swagger*')
    add("Wayback", cat, "Old admin panels", f'{h}/admin/*',
        f'https://web.archive.org/web/*/{h}/admin*')
    add("Wayback", cat, "Old config files", f'{h}/*.env',
        f'https://web.archive.org/web/*/{h}/*.env')
    add("Wayback", cat, "CDX API full list", f'CDX API: {h}',
        f'https://web.archive.org/cdx/search/cdx?url=*.{d}&output=text&fl=original&collapse=urlkey&matchType=domain')

    # ══ PASTEBIN / LEAK SITES ═════════════════════════════════
    cat = "Leak Sites & Pastebins"
    add("Pastebin", cat, "Pastebin leaks", f'site:pastebin.com "{d}"',
        f'https://www.google.com/search?q=site:pastebin.com+"{d}"')
    add("Pastebin", cat, "Hastebin", f'site:hastebin.com "{d}"',
        f'https://www.google.com/search?q=site:hastebin.com+"{d}"')
    add("Pastebin", cat, "PrivateBin", f'site:privatebin.net "{d}"',
        f'https://www.google.com/search?q=site:privatebin.net+"{d}"')
    add("Pastebin", cat, "Gist credentials", f'site:gist.github.com "{d}" password OR secret OR token',
        f'https://github.com/search?q=site%3Agist.github.com+"{d}"+password&type=code')
    add("Pastebin", cat, "BreachForums mention", f'"{d}" site:breachforums.is OR site:raidforums.com',
        f'https://www.google.com/search?q="{d}"+site:breachforums.is')
    add("Pastebin", cat, "Google: general paste", f'"{d}" credentials OR dump OR breach OR leaked',
        f'https://www.google.com/search?q="{d}"+credentials+OR+dump+OR+breach+OR+leaked')

    # ══ LINKEDIN OSINT ════════════════════════════════════════
    cat = "LinkedIn OSINT"
    add("LinkedIn", cat, "Devs with stack info", f'site:linkedin.com "{r}" developer OR engineer OR IT',
        f'https://www.google.com/search?q=site:linkedin.com+"{r}"+developer+OR+engineer+OR+IT')
    add("LinkedIn", cat, "Tech stack from devs", f'site:linkedin.com "{r}" TYPO3 OR ForgeRock OR Thelia OR F5',
        f'https://www.google.com/search?q=site:linkedin.com+"{r}"+TYPO3+OR+ForgeRock+OR+Thelia+OR+F5')
    add("LinkedIn", cat, "Security team", f'site:linkedin.com "{r}" "information security" OR "cybersecurity" OR CISO',
        f'https://www.google.com/search?q=site:linkedin.com+"{r}"+information+security+OR+cybersecurity')
    add("LinkedIn", cat, "IT admins", f'site:linkedin.com "{r}" "system administrator" OR "network engineer" OR "IT manager"',
        f'https://www.google.com/search?q=site:linkedin.com+"{r}"+"system+administrator"+OR+"network+engineer"')

    # ══ NUCLEI TEMPLATE HINTS ════════════════════════════════
    cat = "Nuclei Template Hints"
    add("Nuclei", cat, "Run default templates", f'nuclei -u https://{h} -t technologies/ -t exposures/ -t misconfiguration/',
        None)
    add("Nuclei", cat, "CVE scan", f'nuclei -u https://{h} -t cves/ -severity medium,high,critical',
        None)
    add("Nuclei", cat, "Exposed panels", f'nuclei -u https://{h} -t exposed-panels/ -t default-logins/',
        None)
    add("Nuclei", cat, "Fuzzing mode", f'nuclei -u https://{h} -t fuzzing/ -rl 3 -timeout 10',
        None)
    add("Nuclei", cat, "Takeover check", f'nuclei -l subdomains.txt -t takeovers/ -rl 5',
        None)

    return dorks


# ══════════════════════════════════════════════════════════════
# RENDER HEADER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="dork-header">
    <div class="header-title">⚡ DORK ENGINE</div>
    <div class="header-sub">ELITE RECONNAISSANCE FRAMEWORK // ZWANSKI SECURITY</div>
    <div class="header-warning">⚠ AUTHORIZED SECURITY RESEARCH ONLY — PRIVATE USE</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PASSWORD GATE
# ══════════════════════════════════════════════════════════════
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="pw-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="pw-box">
        <div class="pw-lock">🔒</div>
        <div class="pw-title">AUTHENTICATION REQUIRED</div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pw = st.text_input("ACCESS CODE", type="password", placeholder="enter access code...", key="pw_input")
        if st.button("⚡ AUTHENTICATE", use_container_width=True):
            if pw == "zwanski":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("⛔ ACCESS DENIED — INVALID CREDENTIALS")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="dork-footer">
        <div class="footer-left">DORK ENGINE // ZWANSKI</div>
        <div class="footer-center">⚠ THIS TOOL IS FOR AUTHORIZED SECURITY RESEARCH ONLY<br>UNAUTHORIZED USE IS STRICTLY PROHIBITED</div>
        <div class="footer-right">Built by zwanski<br>zwanski.bio</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ── SIDEBAR CONFIG ────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙ CONFIG")
    st.markdown("---")
    tech_options = [
        "TYPO3", "ForgeRock/OpenAM", "Thelia", "F5/BIG-IP",
        "Horizon/VDI", "Keycloak", "Drupal", "WordPress",
        "Exchange/OWA", "MobileIron/Ivanti", "OwnCloud/Nextcloud",
        "Jenkins", "GitLab", "Kubernetes", "Elasticsearch"
    ]
    tech_stack = st.multiselect(
        "KNOWN TECH STACK",
        options=tech_options,
        default=[],
        help="Select known technologies for targeted dorks"
    )
    extra_kw = st.text_input(
        "EXTRA KEYWORDS (comma-separated)",
        placeholder="kumo, geneveid, intranet..."
    )
    st.markdown("---")
    show_links = st.checkbox("Show clickable links", value=True)
    group_by_engine = st.checkbox("Group by engine", value=False)
    st.markdown("---")
    if st.button("🔒 LOGOUT", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ── TARGET INPUT ──────────────────────────────────────────────
col_in, col_btn = st.columns([5, 1])
with col_in:
    target_input = st.text_input(
        "TARGET URL OR DOMAIN",
        placeholder="https://target.example.com  OR  example.com",
        key="target_url"
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    generate = st.button("⚡ GENERATE", use_container_width=True)

# ── GENERATE ──────────────────────────────────────────────────
if generate and target_input:
    t = parse_target(target_input)
    dorks = generate_dorks(t, tech_stack, extra_kw)

    # Stats
    engines = list(set(dk["engine"] for dk in dorks))
    cats = list(set(dk["category"] for dk in dorks))

    st.markdown(f"""
    <div class="target-display">
        <span style="color:#4dff4d;font-size:0.7rem;letter-spacing:0.2em">TARGET</span>
        <span class="target-pill">🌐 {t['hostname']}</span>
        <span class="target-pill">📍 TLD: {t['tld']}</span>
        <span class="target-pill">🔑 ROOT: {t['root']}</span>
        {"<span class='target-pill'>📂 SUB: " + t['subdomain'] + "</span>" if t['subdomain'] else ""}
        <span style="margin-left:auto;font-size:0.65rem;color:#4dff4d;opacity:0.6">{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item"><div class="stat-val">{len(dorks)}</div><div class="stat-label">Total Dorks</div></div>
        <div class="stat-item"><div class="stat-val">{len(engines)}</div><div class="stat-label">Engines</div></div>
        <div class="stat-item"><div class="stat-val">{len(cats)}</div><div class="stat-label">Categories</div></div>
        <div class="stat-item"><div class="stat-val">{len(tech_stack)}</div><div class="stat-label">Tech Detected</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── EXPORT BUTTONS ────────────────────────────────────────
    ecol1, ecol2, ecol3 = st.columns(3)
    all_text = "\n".join([
        f"[{dk['engine']}][{dk['category']}] {dk['label']}\n{dk['query']}\n"
        for dk in dorks
    ])
    all_json = json.dumps([{
        "engine": dk["engine"],
        "category": dk["category"],
        "label": dk["label"],
        "query": dk["query"],
        "link": dk["link"]
    } for dk in dorks], indent=2)

    with ecol1:
        st.download_button("📥 EXPORT TXT", all_text,
            file_name=f"dorks_{t['root']}_{datetime.utcnow().strftime('%Y%m%d%H%M')}.txt",
            mime="text/plain", use_container_width=True)
    with ecol2:
        st.download_button("📥 EXPORT JSON", all_json,
            file_name=f"dorks_{t['root']}_{datetime.utcnow().strftime('%Y%m%d%H%M')}.json",
            mime="application/json", use_container_width=True)
    with ecol3:
        google_only = "\n".join([dk["query"] for dk in dorks if dk["engine"] == "Google"])
        st.download_button("📥 GOOGLE ONLY", google_only,
            file_name=f"google_dorks_{t['root']}.txt",
            mime="text/plain", use_container_width=True)

    # ── RENDER DORKS ──────────────────────────────────────────
    engine_tabs = ["ALL"] + sorted(set(dk["engine"] for dk in dorks))
    tabs = st.tabs(engine_tabs)

    for tab_idx, tab in enumerate(tabs):
        with tab:
            selected_engine = engine_tabs[tab_idx]
            filtered = dorks if selected_engine == "ALL" else [dk for dk in dorks if dk["engine"] == selected_engine]

            # Group by category
            by_cat = {}
            for dk in filtered:
                by_cat.setdefault(dk["category"], []).append(dk)

            for cat_name, cat_dorks in by_cat.items():
                badge_class = {
                    "Google": "badge-google", "GitHub": "badge-github",
                    "Shodan": "badge-shodan", "Censys": "badge-censys",
                    "Wayback": "badge-wayback", "Pastebin": "badge-paste",
                    "LinkedIn": "badge-linkedin", "Nuclei": "badge-nuclei"
                }
                engine_icons = {
                    "Google": "🔍", "GitHub": "🐙", "Shodan": "🌊",
                    "Censys": "🔭", "Wayback": "🕰️", "Pastebin": "📋",
                    "LinkedIn": "💼", "Nuclei": "⚛️"
                }
                st.markdown(f"""
                <div class="cat-header">{cat_name}
                    <span class="cat-badge">{len(cat_dorks)} DORKS</span>
                </div>
                """, unsafe_allow_html=True)

                for dk in cat_dorks:
                    bc = badge_class.get(dk["engine"], "badge-google")
                    icon = engine_icons.get(dk["engine"], "🔍")
                    link_html = f'<a href="{dk["link"]}" target="_blank" style="color:#00ff41;font-size:0.65rem;letter-spacing:0.1em;text-decoration:none;margin-top:0.4rem;display:inline-block">▶ OPEN IN {dk["engine"].upper()}</a>' if show_links and dk["link"] else ""

                    st.markdown(f"""
                    <div class="dork-card">
                        <span class="dork-engine-badge {bc}">{icon} {dk['engine']}</span>
                        <div class="dork-label">{dk['label']}</div>
                        <div class="dork-query">{dk['query']}</div>
                        {link_html}
                    </div>
                    """, unsafe_allow_html=True)

elif generate and not target_input:
    st.warning("⚠ INPUT A TARGET URL OR DOMAIN FIRST")

else:
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;opacity:0.4">
        <div style="font-family:'Orbitron',sans-serif;font-size:3rem;color:#00ff41;margin-bottom:1rem">⚡</div>
        <div style="font-family:'Orbitron',sans-serif;font-size:0.9rem;color:#4dff4d;letter-spacing:0.3em">
            INPUT TARGET → GENERATE → HUNT
        </div>
        <div style="font-size:0.7rem;color:#4dff4d;letter-spacing:0.15em;margin-top:0.5rem;opacity:0.6">
            Google · GitHub · Shodan · Censys · Wayback · LinkedIn · Nuclei
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="dork-footer">
    <div class="footer-left">
        ⚡ DORK ENGINE v2.0<br>
        <span style="opacity:0.5;font-size:0.55rem">ZWANSKI SECURITY RESEARCH FRAMEWORK</span>
    </div>
    <div class="footer-center">
        ⚠ THIS TOOL IS FOR AUTHORIZED SECURITY RESEARCH ONLY<br>
        DO NOT USE AGAINST TARGETS YOU DO NOT HAVE PERMISSION TO TEST<br>
        <span style="color:#ffd600">© 2026 ZWANSKI — ALL RIGHTS RESERVED</span>
    </div>
    <div class="footer-right">
        Built by <a href="https://zwanski.bio" target="_blank" style="color:#00ff41;text-decoration:none">zwanski</a><br>
        HackerOne · Bugcrowd · Bug Bounty Switzerland<br>
        <span style="opacity:0.4;font-size:0.5rem">zwanski.bio</span>
    </div>
</div>
""", unsafe_allow_html=True)
