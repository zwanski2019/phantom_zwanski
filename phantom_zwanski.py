import streamlit as st
import urllib.parse
import json
import re
import socket
import base64
import time
import importlib.util
from datetime import datetime
from collections import defaultdict

# Optional imports — graceful fallback
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import mmh3
    HAS_MMH3 = True
except ImportError:
    HAS_MMH3 = False

HAS_DNS = importlib.util.find_spec("dns.resolver") is not None

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="PHANTOM // ZWANSKI",
    page_icon="👁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Bebas+Neue&family=Rajdhani:wght@400;600;700&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

html,body,[data-testid="stApp"]{
    background:#03000a !important;
    color:#b388ff !important;
    font-family:'JetBrains Mono',monospace !important;
}

[data-testid="stApp"]::before{
    content:'';position:fixed;inset:0;
    background:
        radial-gradient(ellipse 80% 50% at 50% -10%,rgba(103,58,183,0.15) 0%,transparent 60%),
        radial-gradient(ellipse 40% 40% at 100% 100%,rgba(0,188,212,0.05) 0%,transparent 60%),
        repeating-linear-gradient(0deg,transparent,transparent 60px,rgba(103,58,183,0.03) 60px,rgba(103,58,183,0.03) 61px),
        repeating-linear-gradient(90deg,transparent,transparent 60px,rgba(103,58,183,0.02) 60px,rgba(103,58,183,0.02) 61px);
    pointer-events:none;z-index:0;
}

#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important}
[data-testid="stMain"],[data-testid="block-container"]{padding:0!important;max-width:100%!important}

/* HEADER */
.ph-header{
    background:linear-gradient(135deg,#0a0015 0%,#120020 60%,#0a0015 100%);
    border-bottom:1px solid rgba(103,58,183,0.5);
    padding:2rem 3rem 1.5rem;
    position:relative;overflow:hidden;
}
.ph-header::after{
    content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
    background:linear-gradient(90deg,transparent,#7c4dff,#00e5ff,#7c4dff,transparent);
    animation:scanline 3s linear infinite;
}
@keyframes scanline{0%{transform:scaleX(0) translateX(-100%)}100%{transform:scaleX(1) translateX(100%)}}
@keyframes flicker{0%,100%{opacity:1}92%{opacity:1}93%{opacity:0.7}94%{opacity:1}97%{opacity:0.9}}
@keyframes glow-pulse{0%,100%{text-shadow:0 0 20px rgba(124,77,255,0.8),0 0 40px rgba(124,77,255,0.4)}50%{text-shadow:0 0 30px rgba(124,77,255,1),0 0 60px rgba(124,77,255,0.6),0 0 100px rgba(0,229,255,0.3)}}

.ph-title{
    font-family:'Bebas Neue',sans-serif;
    font-size:3.5rem;color:#7c4dff;
    letter-spacing:0.2em;
    animation:glow-pulse 3s ease-in-out infinite,flicker 8s infinite;
}
.ph-subtitle{
    font-family:'Rajdhani',sans-serif;font-size:0.85rem;
    color:#00e5ff;letter-spacing:0.4em;margin-top:0.2rem;opacity:0.8;
}
.ph-warn{
    display:inline-block;margin-top:0.5rem;
    font-size:0.6rem;color:#ff1744;letter-spacing:0.25em;
    border:1px solid rgba(255,23,68,0.5);padding:0.2rem 0.8rem;
    background:rgba(255,23,68,0.05);
}

/* INPUTS */
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{
    background:#08001a !important;
    border:1px solid rgba(124,77,255,0.4) !important;
    border-radius:0 !important;color:#e1bee7 !important;
    font-family:'JetBrains Mono',monospace !important;
    font-size:0.9rem !important;caret-color:#7c4dff !important;
}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{
    box-shadow:0 0 20px rgba(124,77,255,0.25) !important;
    border-color:#7c4dff !important;
}
[data-testid="stTextInput"] label,[data-testid="stTextArea"] label{
    color:#9c27b0 !important;font-family:'JetBrains Mono',monospace !important;
    font-size:0.7rem !important;letter-spacing:0.25em !important;
}

/* BUTTONS */
[data-testid="stButton"] button{
    background:linear-gradient(135deg,rgba(124,77,255,0.1),rgba(0,229,255,0.05)) !important;
    border:1px solid rgba(124,77,255,0.6) !important;
    color:#b388ff !important;font-family:'Rajdhani',sans-serif !important;
    font-size:0.85rem !important;font-weight:700 !important;
    letter-spacing:0.2em !important;border-radius:0 !important;
    padding:0.6rem 1.5rem !important;transition:all 0.2s !important;
    text-transform:uppercase !important;
}
[data-testid="stButton"] button:hover{
    background:linear-gradient(135deg,rgba(124,77,255,0.25),rgba(0,229,255,0.1)) !important;
    box-shadow:0 0 25px rgba(124,77,255,0.4),0 0 5px rgba(0,229,255,0.2) !important;
    color:#fff !important;border-color:#7c4dff !important;
}

/* TABS */
[data-testid="stTabs"] [role="tablist"]{background:#08001a !important;border-bottom:1px solid rgba(124,77,255,0.2) !important;gap:0 !important}
[data-testid="stTabs"] [role="tab"]{font-family:'JetBrains Mono',monospace !important;font-size:0.7rem !important;letter-spacing:0.12em !important;color:#9c27b0 !important;border-radius:0 !important;padding:0.5rem 1rem !important;border-right:1px solid rgba(124,77,255,0.1) !important}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:rgba(124,77,255,0.1) !important;color:#b388ff !important;border-bottom:2px solid #7c4dff !important}

/* MULTISELECT */
[data-testid="stMultiSelect"]>div{background:#08001a !important;border:1px solid rgba(124,77,255,0.4) !important;border-radius:0 !important}
[data-testid="stMultiSelect"] span[data-baseweb="tag"]{background:rgba(124,77,255,0.2) !important;border-radius:0 !important}

/* SELECT */
[data-testid="stSelectbox"]>div>div{background:#08001a !important;border:1px solid rgba(124,77,255,0.4) !important;border-radius:0 !important;color:#b388ff !important}

/* DOWNLOAD */
[data-testid="stDownloadButton"] button{background:rgba(0,229,255,0.05) !important;border:1px solid rgba(0,229,255,0.4) !important;color:#00e5ff !important;font-family:'Rajdhani',sans-serif !important;font-size:0.75rem !important;letter-spacing:0.2em !important;border-radius:0 !important}

/* EXPANDER */
[data-testid="stExpander"]{background:#08001a !important;border:1px solid rgba(124,77,255,0.2) !important;border-radius:0 !important}
[data-testid="stExpander"] summary{color:#9c27b0 !important;font-family:'JetBrains Mono',monospace !important;font-size:0.75rem !important}

/* CHECKBOX */
[data-testid="stCheckbox"] label{color:#9c27b0 !important;font-family:'JetBrains Mono',monospace !important;font-size:0.75rem !important}

/* PROGRESS */
[data-testid="stProgress"]>div>div{background:linear-gradient(90deg,#7c4dff,#00e5ff) !important}

/* METRIC */
[data-testid="stMetric"] [data-testid="stMetricValue"]{color:#7c4dff !important;font-family:'Bebas Neue',sans-serif !important;font-size:2rem !important}
[data-testid="stMetric"] [data-testid="stMetricLabel"]{color:#9c27b0 !important;font-size:0.6rem !important;letter-spacing:0.2em !important}

/* ALERT/INFO */
[data-testid="stAlert"]{background:rgba(124,77,255,0.06) !important;border:1px solid rgba(124,77,255,0.3) !important;border-radius:0 !important;color:#b388ff !important}

/* CUSTOM COMPONENTS */
.module-header{
    display:flex;align-items:center;gap:1rem;
    background:linear-gradient(90deg,rgba(124,77,255,0.15) 0%,transparent 100%);
    border-left:3px solid #7c4dff;
    padding:0.7rem 1rem;margin:1.5rem 0 0.8rem;
    font-family:'Rajdhani',sans-serif;font-size:0.8rem;
    letter-spacing:0.3em;color:#b388ff;text-transform:uppercase;
}
.module-badge{
    display:inline-block;background:rgba(0,229,255,0.1);
    border:1px solid rgba(0,229,255,0.4);color:#00e5ff;
    font-size:0.55rem;letter-spacing:0.2em;padding:0.1rem 0.5rem;
}
.dork-card{
    background:#06001a;
    border:1px solid rgba(124,77,255,0.15);
    border-left:2px solid #7c4dff;
    padding:0.7rem 1rem 0.7rem 0.9rem;
    margin:0.3rem 0;position:relative;
    transition:all 0.15s;
}
.dork-card:hover{
    border-color:rgba(124,77,255,0.5);
    background:#08001f;
    box-shadow:0 0 15px rgba(124,77,255,0.1);
}
.dork-label{font-size:0.6rem;color:#7c4dff;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:0.25rem;opacity:0.8}
.dork-query{font-family:'JetBrains Mono',monospace;font-size:0.82rem;color:#e1bee7;word-break:break-all;line-height:1.5}
.dork-link{font-size:0.6rem;letter-spacing:0.1em;margin-top:0.35rem;display:inline-block}
.dork-link a{color:#00e5ff;text-decoration:none}
.dork-link a:hover{text-shadow:0 0 8px rgba(0,229,255,0.6)}

.engine-pill{
    position:absolute;top:0.5rem;right:0.7rem;
    font-size:0.5rem;letter-spacing:0.15em;padding:0.12rem 0.45rem;
    border:1px solid;text-transform:uppercase;
}
.ep-google{color:#4285f4;border-color:#4285f4;background:rgba(66,133,244,0.08)}
.ep-github{color:#e040fb;border-color:#e040fb;background:rgba(224,64,251,0.08)}
.ep-shodan{color:#ff6d00;border-color:#ff6d00;background:rgba(255,109,0,0.08)}
.ep-censys{color:#00bcd4;border-color:#00bcd4;background:rgba(0,188,212,0.08)}
.ep-fofa{color:#ff4081;border-color:#ff4081;background:rgba(255,64,129,0.08)}
.ep-zoomeye{color:#69f0ae;border-color:#69f0ae;background:rgba(105,240,174,0.08)}
.ep-wayback{color:#ffd600;border-color:#ffd600;background:rgba(255,214,0,0.08)}
.ep-leak{color:#ff5252;border-color:#ff5252;background:rgba(255,82,82,0.08)}
.ep-linkedin{color:#0288d1;border-color:#0288d1;background:rgba(2,136,209,0.08)}
.ep-dehashed{color:#ff6e40;border-color:#ff6e40;background:rgba(255,110,64,0.08)}
.ep-nuclei{color:#76ff03;border-color:#76ff03;background:rgba(118,255,3,0.08)}
.ep-cloud{color:#40c4ff;border-color:#40c4ff;background:rgba(64,196,255,0.08)}
.ep-email{color:#ea80fc;border-color:#ea80fc;background:rgba(234,128,252,0.08)}
.ep-recon{color:#b388ff;border-color:#b388ff;background:rgba(179,136,255,0.08)}

/* LIVE MODULE CARDS */
.live-card{
    background:#06001a;border:1px solid rgba(0,229,255,0.2);
    border-top:2px solid #00e5ff;padding:1rem 1.2rem;margin:0.5rem 0;
}
.live-card-title{font-family:'Rajdhani',sans-serif;font-size:0.75rem;letter-spacing:0.25em;color:#00e5ff;margin-bottom:0.5rem}
.live-item{font-size:0.78rem;color:#b388ff;padding:0.2rem 0;border-bottom:1px solid rgba(124,77,255,0.08)}
.live-item:last-child{border-bottom:none}
.live-badge{display:inline-block;font-size:0.55rem;padding:0.1rem 0.4rem;border:1px solid;margin-left:0.5rem;vertical-align:middle}

/* STATS */
.stat-row{
    display:flex;gap:1.5rem;
    background:#06001a;border:1px solid rgba(124,77,255,0.15);
    padding:1rem 1.5rem;margin:1rem 0;flex-wrap:wrap;
}
.stat-block{display:flex;flex-direction:column;min-width:80px}
.stat-val{font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:#7c4dff;line-height:1}
.stat-lbl{font-size:0.55rem;color:#9c27b0;letter-spacing:0.2em;text-transform:uppercase;margin-top:0.2rem;opacity:0.7}

/* TARGET STRIP */
.target-strip{
    background:rgba(124,77,255,0.05);
    border:1px solid rgba(124,77,255,0.25);
    padding:0.8rem 1.5rem;margin:1rem 0;
    display:flex;align-items:center;gap:1rem;flex-wrap:wrap;
}
.t-chip{
    background:rgba(124,77,255,0.1);border:1px solid rgba(124,77,255,0.4);
    color:#b388ff;font-size:0.65rem;letter-spacing:0.12em;padding:0.2rem 0.7rem;
}
.t-chip-cyan{
    background:rgba(0,229,255,0.08);border:1px solid rgba(0,229,255,0.35);
    color:#00e5ff;font-size:0.65rem;letter-spacing:0.12em;padding:0.2rem 0.7rem;
}

/* PASSWORD SCREEN */
.pw-wrap{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:60vh;padding:3rem}
.pw-box{border:1px solid rgba(124,77,255,0.4);background:rgba(124,77,255,0.04);padding:3rem;width:100%;max-width:440px;text-align:center;box-shadow:0 0 60px rgba(124,77,255,0.08),inset 0 0 40px rgba(124,77,255,0.02)}
.pw-title{font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:#7c4dff;letter-spacing:0.4em;margin-bottom:1rem}
.pw-eye{font-size:3.5rem;filter:drop-shadow(0 0 15px rgba(124,77,255,0.7));animation:glow-pulse 3s infinite}

/* FOOTER */
.ph-footer{
    background:#03000a;border-top:1px solid rgba(124,77,255,0.15);
    padding:1.5rem 3rem;margin-top:4rem;
    display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;
}
.footer-brand{font-family:'Bebas Neue',sans-serif;font-size:1.1rem;color:#7c4dff;letter-spacing:0.3em}
.footer-warn{font-size:0.58rem;color:#ff1744;letter-spacing:0.15em;text-align:center;border:1px solid rgba(255,23,68,0.25);padding:0.4rem 1.2rem;text-transform:uppercase;background:rgba(255,23,68,0.03)}
.footer-right{font-size:0.6rem;color:#9c27b0;letter-spacing:0.12em;text-align:right;opacity:0.7}
.footer-right a{color:#b388ff;text-decoration:none}

::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:#03000a}
::-webkit-scrollbar-thumb{background:rgba(124,77,255,0.3)}
::-webkit-scrollbar-thumb:hover{background:#7c4dff}
hr{border-color:rgba(124,77,255,0.15) !important}
code{background:#08001a !important;color:#b388ff !important;border:1px solid rgba(124,77,255,0.2) !important;border-radius:0 !important;font-family:'JetBrains Mono',monospace !important}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# UTILS
# ══════════════════════════════════════════════════════════════
def parse_target(url: str) -> dict:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    p = urllib.parse.urlparse(url)
    hostname = (p.netloc or p.path).split(":")[0]
    clean = hostname.lstrip("www.")
    parts = clean.split(".")
    tld = ".".join(parts[-2:]) if len(parts) >= 2 else clean
    root = parts[-2] if len(parts) >= 2 else clean
    subdomain = ".".join(parts[:-2]) if len(parts) > 2 else ""
    return {
        "raw": url, "hostname": hostname, "clean": clean,
        "tld": tld, "root": root, "subdomain": subdomain,
        "scheme": p.scheme,
        "org_variants": _org_variants(root)
    }

def _org_variants(root: str) -> list:
    """Generate org name permutations for bucket/cloud hunting."""
    r = root.lower()
    return list(set([
        r, r.replace("-", ""), r.replace("-", "_"),
        f"{r}-prod", f"{r}-dev", f"{r}-staging", f"{r}-test",
        f"{r}-backup", f"{r}-assets", f"{r}-media", f"{r}-static",
        f"{r}-data", f"{r}-files", f"{r}-storage", f"{r}-logs",
        f"{r}-archive", f"{r}-cdn", f"{r}-api", f"{r}-internal",
        f"{r}-private", f"{r}-public", f"{r}-uploads", f"{r}-export",
        f"{r}-import", f"{r}-reports", f"{r}-docs", f"{r}-dump",
    ]))

def safe_get(url, timeout=6, headers=None):
    if not HAS_REQUESTS:
        return None
    try:
        h = {"User-Agent": "Mozilla/5.0 (Security Research) zwanski-recon/2.0"}
        if headers:
            h.update(headers)
        return requests.get(url, timeout=timeout, headers=h, verify=False)
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════
# LIVE MODULE: CRT.SH
# ══════════════════════════════════════════════════════════════
def live_crtsh(tld: str) -> list:
    r = safe_get(f"https://crt.sh/?q=%.{tld}&output=json")
    if not r:
        return []
    try:
        data = r.json()
        names = set()
        for entry in data:
            for n in entry.get("name_value", "").split("\n"):
                n = n.strip().lstrip("*.")
                if tld in n and "*" not in n:
                    names.add(n.lower())
        return sorted(names)
    except Exception:
        return []


# ══════════════════════════════════════════════════════════════
# LIVE MODULE: WAYBACK CDX PARAMETER MINER
# ══════════════════════════════════════════════════════════════
def live_wayback_params(tld: str) -> dict:
    url = f"https://web.archive.org/cdx/search/cdx?url=*.{tld}&output=json&fl=original&collapse=urlkey&matchType=domain&limit=2000"
    r = safe_get(url, timeout=15)
    if not r:
        return {"params": [], "endpoints": [], "extensions": [], "raw_count": 0}
    try:
        lines = r.json()
        params = set()
        endpoints = set()
        extensions = set()
        for row in lines[1:]:
            try:
                raw = row[0]
                p = urllib.parse.urlparse(raw)
                qs = urllib.parse.parse_qs(p.query)
                for k in qs:
                    params.add(k)
                path = p.path
                if path and path != "/":
                    parts = path.strip("/").split("/")
                    if len(parts) >= 2:
                        endpoints.add("/" + "/".join(parts[:3]))
                ext = path.split(".")[-1] if "." in path.split("/")[-1] else ""
                if ext and len(ext) <= 4 and ext.isalpha():
                    extensions.add(ext.lower())
            except Exception:
                pass
        return {
            "params": sorted(params)[:80],
            "endpoints": sorted(endpoints)[:60],
            "extensions": sorted(extensions),
            "raw_count": len(lines) - 1
        }
    except Exception:
        return {"params": [], "endpoints": [], "extensions": [], "raw_count": 0}


# ══════════════════════════════════════════════════════════════
# LIVE MODULE: DNS INTELLIGENCE
# ══════════════════════════════════════════════════════════════
def live_dns_intel(domain: str) -> dict:
    result = {}
    if not HAS_REQUESTS:
        return result
    # Use Google DoH
    def doh(name, rtype):
        try:
            r = safe_get(
                f"https://dns.google/resolve?name={name}&type={rtype}",
                headers={"Accept": "application/dns-json"}
            )
            if r and r.status_code == 200:
                return r.json().get("Answer", [])
        except Exception:
            pass
        return []

    for rtype in ["TXT", "MX", "NS", "A", "AAAA", "CNAME"]:
        ans = doh(domain, rtype)
        if ans:
            result[rtype] = [a.get("data", "") for a in ans]

    # SPF analysis
    txt = result.get("TXT", [])
    spf = [t for t in txt if "v=spf1" in t]
    if spf:
        result["SPF"] = spf
        # Extract cloud providers from SPF
        providers = []
        spf_str = " ".join(spf)
        if "google.com" in spf_str or "googlemail.com" in spf_str:
            providers.append("Google Workspace")
        if "sendgrid.net" in spf_str:
            providers.append("SendGrid")
        if "mailchimp" in spf_str or "mandrill" in spf_str:
            providers.append("Mailchimp")
        if "amazonaws.com" in spf_str:
            providers.append("AWS SES")
        if "office365" in spf_str or "outlook.com" in spf_str:
            providers.append("Microsoft 365")
        if "zendesk" in spf_str:
            providers.append("Zendesk")
        if providers:
            result["EMAIL_PROVIDERS"] = providers

    dmarc = doh(f"_dmarc.{domain}", "TXT")
    if dmarc:
        result["DMARC"] = [a.get("data", "") for a in dmarc]

    return result


# ══════════════════════════════════════════════════════════════
# LIVE MODULE: FAVICON HASH (SHODAN)
# ══════════════════════════════════════════════════════════════
def live_favicon_hash(target_url: str, hostname: str) -> dict:
    """Fetch favicon, compute mmh3 hash for Shodan search."""
    paths = ["/favicon.ico", "/favicon.png", "/apple-touch-icon.png"]
    results = {}
    for path in paths:
        r = safe_get(f"{target_url}{path}", timeout=5)
        if r and r.status_code == 200 and r.content:
            b64 = base64.encodebytes(r.content).decode()
            if HAS_MMH3:
                h = mmh3.hash(b64)
                results[path] = {
                    "hash": h,
                    "shodan_dork": f'http.favicon.hash:{h}',
                    "fofa_dork": f'icon_hash="{h}"',
                    "link_shodan": f"https://www.shodan.io/search?query=http.favicon.hash%3A{h}",
                    "link_fofa": f"https://fofa.info/result?qbase64={base64.b64encode(f'icon_hash=\"{h}\"'.encode()).decode()}"
                }
            else:
                results[path] = {"hash": "install mmh3", "shodan_dork": "pip install mmh3 required"}
    return results


# ══════════════════════════════════════════════════════════════
# LIVE MODULE: ASN / IP RANGE
# ══════════════════════════════════════════════════════════════
def live_asn_intel(hostname: str) -> dict:
    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        return {}
    r = safe_get(f"https://ipinfo.io/{ip}/json")
    if not r:
        return {"ip": ip}
    try:
        data = r.json()
        return {
            "ip": ip,
            "org": data.get("org", ""),
            "asn": data.get("org", "").split()[0] if data.get("org") else "",
            "asn_name": " ".join(data.get("org", "").split()[1:]) if data.get("org") else "",
            "country": data.get("country", ""),
            "city": data.get("city", ""),
            "cidr": data.get("ip", ""),
            "hostname_rdns": data.get("hostname", ""),
            "abuse": data.get("abuse", {}).get("email", ""),
        }
    except Exception:
        return {"ip": ip}


# ══════════════════════════════════════════════════════════════
# LIVE MODULE: JS ENDPOINT EXTRACTION
# ══════════════════════════════════════════════════════════════
def live_js_endpoints(target_url: str) -> list:
    """Fetch main page, find JS files, extract endpoints."""
    r = safe_get(target_url, timeout=8)
    if not r:
        return []
    js_urls = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', r.text)
    endpoints = set()
    regex_ep = re.compile(r'["\`](\/[a-zA-Z0-9_\-\/\.]{3,80})["\`]')
    regex_param = re.compile(r'(?:fetch|axios|xhr|http)\s*\(?\s*["`\']([^"`\']{5,120})["`\']')
    for js_path in js_urls[:8]:
        if not js_path.startswith("http"):
            js_path = target_url.rstrip("/") + "/" + js_path.lstrip("/")
        jr = safe_get(js_path, timeout=5)
        if jr and jr.status_code == 200:
            for m in regex_ep.findall(jr.text):
                if any(x in m for x in ["/api/", "/v1/", "/v2/", "/user", "/admin", "/auth", "/token", "/data"]):
                    endpoints.add(m)
            for m in regex_param.findall(jr.text):
                if m.startswith("/") or m.startswith("http"):
                    endpoints.add(m[:100])
    return sorted(endpoints)[:40]


# ══════════════════════════════════════════════════════════════
# DORK GENERATOR — ELITE
# ══════════════════════════════════════════════════════════════
def generate_dorks(t: dict, tech: list, kw_raw: str,
                   wayback_data: dict, subdomains: list,
                   dns_data: dict, asn_data: dict, js_endpoints: list) -> list:
    d = t["tld"]
    h = t["hostname"]
    r = t["root"]
    variants = t["org_variants"]
    kw = [k.strip() for k in kw_raw.split(",") if k.strip()]
    dorks = []

    def add(engine, cat, label, query, link=None):
        eng_links = {
            "Google": f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}",
            "GitHub": f"https://github.com/search?q={urllib.parse.quote_plus(query)}&type=code",
            "Shodan": f"https://www.shodan.io/search?query={urllib.parse.quote_plus(query)}",
            "Censys": f"https://search.censys.io/search?resource=hosts&q={urllib.parse.quote_plus(query)}",
            "FOFA": f"https://fofa.info/result?qbase64={base64.b64encode(query.encode()).decode()}",
            "ZoomEye": f"https://www.zoomeye.org/searchResult?q={urllib.parse.quote_plus(query)}",
            "Wayback": f"https://web.archive.org/web/*/{query}",
            "Leak": f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}",
            "LinkedIn": f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}",
            "DeHashed": f"https://dehashed.com/search?query={urllib.parse.quote_plus(query)}",
            "Email": f"https://hunter.io/domain-search?domain={d}",
            "Cloud": None,
            "Nuclei": None,
            "Recon": None,
        }
        dorks.append({
            "engine": engine, "cat": cat, "label": label, "query": query,
            "link": link or eng_links.get(engine)
        })

    # ══ GOOGLE: ULTRA-TARGETED FILE EXPOSURE ════════════════
    C = "File & Config Exposure"
    add("Google", C, ".env with secrets", f'site:{d} ext:env "DB_PASSWORD" OR "APP_SECRET" OR "JWT_SECRET" OR "REDIS_PASSWORD"')
    add("Google", C, "Laravel .env", f'site:{d} ext:env "APP_KEY=base64" OR "DB_CONNECTION=mysql"')
    add("Google", C, "Django settings", f'site:{d} ext:py inurl:settings "SECRET_KEY" OR "DATABASES" OR "ALLOWED_HOSTS"')
    add("Google", C, "Spring boot props", f'site:{d} ext:properties OR ext:yml "spring.datasource.password" OR "spring.security"')
    add("Google", C, "PHP localconf", f'site:{d} filename:LocalConfiguration.php "password" OR "database"')
    add("Google", C, "wp-config", f'site:{d} filename:wp-config.php "DB_PASSWORD" OR "DB_HOST"')
    add("Google", C, "Source maps", f'site:{d} ext:js.map OR ext:css.map "sources" "mappings"')
    add("Google", C, "Git objects", f'site:{d} inurl:/.git/objects OR inurl:/.git/COMMIT_EDITMSG OR inurl:/.git/config')
    add("Google", C, "SVN/Mercurial", f'site:{d} inurl:/.svn/entries OR inurl:/.hg/store')
    add("Google", C, "Docker secrets", f'site:{d} filename:docker-compose.yml "MYSQL_ROOT_PASSWORD" OR "POSTGRES_PASSWORD"')
    add("Google", C, "Kubernetes secrets", f'site:{d} filename:*.yaml "kind: Secret" "data:" OR "stringData:"')
    add("Google", C, "SSH keys", f'site:{d} ext:pem OR ext:key "BEGIN RSA PRIVATE KEY" OR "BEGIN OPENSSH PRIVATE KEY"')
    add("Google", C, "AWS credentials", f'site:{d} ext:conf OR ext:cfg "aws_access_key_id" OR "aws_secret_access_key"')
    add("Google", C, "GCP service account", f'site:{d} ext:json "type":"service_account" "private_key_id"')
    add("Google", C, "Azure app creds", f'site:{d} "client_secret" "tenant_id" "client_id" ext:json OR ext:env')
    add("Google", C, "JDBC conn strings", f'site:{d} "jdbc:mysql://" OR "jdbc:postgresql://" ext:xml OR ext:properties')

    # ══ GOOGLE: SURGICAL ADMIN/AUTH ══════════════════════════
    C = "Admin & Auth Panels"
    add("Google", C, "F5 TMUI (CVE-2020-5902)", f'site:{d} inurl:/tmui/login.jsp OR inurl:/tmui/util/login.jsp')
    add("Google", C, "Citrix Netscaler", f'site:{d} inurl:/vpn/index.html OR intitle:"Citrix Gateway"')
    add("Google", C, "Pulse Secure VPN", f'site:{d} inurl:/dana-na/auth/url_default/welcome.cgi')
    add("Google", C, "GlobalProtect VPN", f'site:{d} inurl:/global-protect/login.esp OR intitle:"GlobalProtect"')
    add("Google", C, "Fortinet SSL-VPN", f'site:{d} inurl:/remote/login OR intitle:"FortiGate" "SSL VPN"')
    add("Google", C, "Keycloak admin", f'site:{d} inurl:/auth/admin OR inurl:/realms/master/protocol/openid-connect')
    add("Google", C, "CAS SSO exposed", f'site:{d} inurl:/cas/login OR inurl:/cas/serviceValidate')
    add("Google", C, "Shibboleth IdP", f'site:{d} inurl:/idp/profile OR inurl:/idp/shibboleth')
    add("Google", C, "ADFS login", f'site:{d} inurl:/adfs/ls OR inurl:/adfs/oauth2/authorize')
    add("Google", C, "Grafana anon", f'site:{d} inurl:/grafana OR inurl:3000 intitle:"Grafana" -"Login"')
    add("Google", C, "Kibana open", f'site:{d} inurl:5601 OR inurl:/app/kibana intitle:"Kibana"')
    add("Google", C, "Elasticsearch open", f'site:{d} inurl:9200/_cat OR inurl:9200/_nodes intitle:"200 OK"')
    add("Google", C, "Kubernetes dashboard", f'site:{d} inurl:/api/v1/namespaces OR intitle:"Kubernetes Dashboard"')
    add("Google", C, "Consul UI", f'site:{d} inurl:/ui/dc1 OR inurl:/v1/kv intitle:"Consul"')
    add("Google", C, "Vault UI", f'site:{d} inurl:/ui/vault OR inurl:8200/v1 intitle:"Vault"')

    # ══ GOOGLE: API ATTACK SURFACE ═══════════════════════════
    C = "API Attack Surface"
    add("Google", C, "GraphQL introspection", f'site:{d} inurl:/graphql OR inurl:/graphiql OR inurl:/api/graphql "query IntrospectionQuery"')
    add("Google", C, "REST explorers", f'site:{d} inurl:/api/explorer OR inurl:/api/console OR inurl:/api/browser')
    add("Google", C, "Postman workspaces", f'"api.{d}" OR "{d}/api" site:postman.com OR site:getpostman.com')
    add("Google", C, "OpenAPI 3.0 exposed", f'site:{d} inurl:/openapi.json OR inurl:/openapi.yaml OR inurl:/api/openapi.json')
    add("Google", C, "WSDL/SOAP", f'site:{d} inurl:?wsdl OR inurl:service.wsdl OR ext:wsdl')
    add("Google", C, "gRPC reflection", f'site:{d} inurl:/grpc.reflection OR inurl:grpc intitle:"gRPC"')
    add("Google", C, "Strapi CMS API", f'site:{d} inurl:/admin/auth/local OR inurl:/api/content-types')
    add("Google", C, "Directus API", f'site:{d} inurl:/directus OR inurl:8055 intitle:"Directus"')
    add("Google", C, "Hasura GraphQL", f'site:{d} inurl:/hasura OR inurl:8080/v1/graphql')
    add("Google", C, "IDOR pattern: ID param", f'site:{d} inurl:?id= OR inurl:?user_id= OR inurl:?account_id= OR inurl:?order_id=')
    add("Google", C, "IDOR: UUID in URL", f'site:{d} inurl:/[0-9a-f]{{8}}-[0-9a-f]{{4}} OR inurl:/profile/ OR inurl:/account/')
    add("Google", C, "Mass assignment clue", f'site:{d} inurl:?role= OR inurl:?admin= OR inurl:?is_admin= OR inurl:?privilege=')

    # ══ GOOGLE: VULN INDICATORS ══════════════════════════════
    C = "Vulnerability Indicators"
    add("Google", C, "SQL error strings", f'site:{d} "You have an error in your SQL syntax" OR "mysql_fetch_array" OR "Unclosed quotation mark"')
    add("Google", C, "LFI indicator", f'site:{d} inurl:?page= OR inurl:?file= OR inurl:?path= OR inurl:?include= "Warning: include"')
    add("Google", C, "Open redirect", f'site:{d} inurl:?redirect= OR inurl:?url= OR inurl:?return= OR inurl:?next= OR inurl:?goto=')
    add("Google", C, "SSRF-prone params", f'site:{d} inurl:?url= OR inurl:?uri= OR inurl:?endpoint= OR inurl:?webhook= OR inurl:?callback=')
    add("Google", C, "XXE/XML injection", f'site:{d} inurl:?xml= OR inurl:?data= ext:xml "<!DOCTYPE" OR "SYSTEM"')
    add("Google", C, "Reflected XSS clue", f'site:{d} inurl:?q= OR inurl:?search= OR inurl:?query= OR inurl:?s= "alert" OR "<script"')
    add("Google", C, "Insecure deserialization", f'site:{d} ext:java OR ext:py "pickle.loads" OR "ObjectInputStream" OR "unserialize("')
    add("Google", C, "Debug endpoints", f'site:{d} inurl:/debug OR inurl:/trace OR inurl:?debug=1 OR inurl:?test=1 "DEBUG"')
    add("Google", C, "Exposed .DS_Store", f'site:{d} inurl:.DS_Store "Bud1" OR filetype:DS_Store')
    add("Google", C, "PHP info exposed", f'site:{d} inurl:phpinfo.php OR intitle:"phpinfo()" "PHP Version"')
    add("Google", C, "Server-status exposed", f'site:{d} inurl:/server-status OR inurl:/server-info intitle:"Apache Status"')
    add("Google", C, "Internal IP in page", f'site:{d} "10.0." OR "192.168." OR "172.16." "internal server" OR "backend" OR "upstream"')

    # ══ GOOGLE: CLOUD & STORAGE ═══════════════════════════════
    C = "Cloud Storage Exposure"
    for v in variants[:8]:
        add("Google", C, f"S3 bucket: {v}", f'site:s3.amazonaws.com "{v}"', f"https://www.google.com/search?q=site:s3.amazonaws.com+%22{v}%22")
        add("Cloud", C, f"S3 direct: {v}", f"https://{v}.s3.amazonaws.com", f"https://{v}.s3.amazonaws.com")
        add("Cloud", C, f"Azure blob: {v}", f"https://{v}.blob.core.windows.net", f"https://{v}.blob.core.windows.net")
        add("Cloud", C, f"GCP bucket: {v}", f"https://storage.googleapis.com/{v}", f"https://storage.googleapis.com/{v}")
    add("Google", C, "Generic S3 search", f'site:s3.amazonaws.com "{r}" OR "{d}"')
    add("Google", C, "Azure blobs", f'site:blob.core.windows.net "{r}"')
    add("Google", C, "GCP buckets", f'site:storage.googleapis.com "{r}"')
    add("Google", C, "Firebase exposed", f'site:firebaseio.com "{r}" OR "{d}" ".json"')
    add("Google", C, "DigitalOcean Spaces", f'site:digitaloceanspaces.com "{r}"')

    # ══ GOOGLE: SENSITIVE DOCS (ADVANCED) ════════════════════
    C = "Sensitive Documents"
    add("Google", C, "Security audit reports", f'site:{d} ext:pdf "pentest" OR "penetration test" OR "security assessment" OR "vulnerability report"')
    add("Google", C, "Architecture diagrams", f'site:{d} ext:pdf OR ext:pptx "architecture" OR "infrastructure" OR "network diagram"')
    add("Google", C, "Employee data", f'site:{d} ext:xlsx OR ext:csv "nom" OR "prénom" OR "salaire" OR "email" OR "matricule"')
    add("Google", C, "Financial data", f'site:{d} ext:pdf OR ext:xlsx "budget" OR "facture" OR "comptabilité" OR "trésorerie"')
    add("Google", C, "HR documents", f'site:{d} ext:pdf "contrat de travail" OR "fiche de paie" OR "ressources humaines" filetype:pdf')
    add("Google", C, "Medical records clue", f'site:{d} ext:pdf "dossier médical" OR "patient" OR "diagnostic" OR "traitement" "confidentiel"')
    add("Google", C, "API credentials in docs", f'site:{d} ext:pdf OR ext:docx "Bearer" OR "API key" OR "Authorization:" OR "token:"')
    add("Google", C, "Meeting minutes", f'site:{d} ext:pdf OR ext:docx "procès-verbal" OR "compte rendu" OR "réunion" "confidentiel"')

    # ══ GOOGLE: TECH-SPECIFIC CVE-MAPPED ═════════════════════
    C = "CVE-Mapped Tech Dorks"
    for tc in tech:
        tl = tc.lower()
        if "typo3" in tl:
            add("Google", C, "TYPO3 install tool (CVE)", f'site:{d} inurl:/typo3/install.php OR inurl:/typo3/index.php?install')
            add("Google", C, "TYPO3 debug (miscfg)", f'site:{d} "TYPO3 Exception" "Uncaught TYPO3 Exception"')
            add("Google", C, "TYPO3 DB exposed", f'site:{d} inurl:typo3conf/LocalConfiguration.php OR filename:LocalConfiguration.php')
            add("Shodan", C, "TYPO3 instances", f'http.title:"TYPO3" ssl:"{d}"')
        if "forgerock" in tl or "openam" in tl:
            add("Google", C, "ForgeRock user list", f'site:{d} inurl:/json/users?_queryFilter=true OR inurl:/json/realms/root/users')
            add("Google", C, "OpenAM CVE-2021-35464", f'site:{d} inurl:/openam/oauth2/authorize OR inurl:/openam/json/authenticate')
            add("Google", C, "AM password reset", f'site:{d} inurl:/json/realms/root/users/?_action=forgotPassword')
        if "thelia" in tl:
            add("Google", C, "Thelia admin path", f'site:{d} inurl:/admin/login OR inurl:/admin/index OR inurl:thelia/admin')
            add("Google", C, "Thelia customer dump", f'site:{d} inurl:/api/customer OR inurl:/api/order filetype:json')
        if "f5" in tl or "big" in tl:
            add("Google", C, "F5 CVE-2020-5902 TMUI", f'site:{d} inurl:/tmui/login.jsp OR inurl:/tmui/util/login.jsp')
            add("Shodan", C, "F5 BIG-IP exposed", f'ssl:"{d}" product:"BIG-IP" http.status:200')
            add("Google", C, "F5 iControl REST", f'site:{d} inurl:/mgmt/tm/ OR inurl:/mgmt/shared/')
        if "horizon" in tl or "vdi" in tl:
            add("Google", C, "Horizon broker XML", f'site:{d} inurl:/broker/xml OR inurl:/broker/public/api/')
            add("Google", C, "Horizon Connection Svr", f'site:{d} inurl:/admin-ui OR inurl:/portal intitle:"Horizon"')
        if "keycloak" in tl:
            add("Google", C, "Keycloak realm brute", f'site:{d} inurl:/auth/realms/ inurl:openid-configuration')
            add("Google", C, "Keycloak admin console", f'site:{d} inurl:/auth/admin/master/console OR intitle:"Keycloak Administration"')
            add("Google", C, "OIDC token endpoint", f'site:{d} inurl:/protocol/openid-connect/token')
        if "drupal" in tl:
            add("Google", C, "Drupal JSONAPI user enum", f'site:{d} inurl:/jsonapi/user/user OR inurl:/jsonapi/node/article')
            add("Google", C, "Drupalgeddon (CVE-2018-7600)", f'site:{d} inurl:/?q=user/password OR inurl:/user/register')
        if "wordpress" in tl:
            add("Google", C, "WP REST user enum", f'site:{d} inurl:/wp-json/wp/v2/users OR inurl:/wp-json/wp/v2/posts')
            add("Google", C, "WP xmlrpc brute target", f'site:{d} inurl:xmlrpc.php "XML-RPC server"')
            add("Google", C, "WP debug log", f'site:{d} inurl:/wp-content/debug.log')
        if "exchange" in tl or "owa" in tl:
            add("Google", C, "OWA login CVE target", f'site:{d} inurl:/owa/auth.owa OR inurl:/EWS/Exchange.asmx')
            add("Google", C, "Exchange autodiscover", f'site:{d} inurl:/autodiscover/autodiscover.xml OR inurl:/autodiscover/autodiscover.json')
            add("Google", C, "ProxyLogon indicator", f'site:{d} inurl:/ecp/default.aspx OR inurl:/ecp/DDI/DDIService')

    # ══ GITHUB: ULTRA ═════════════════════════════════════════
    C = "GitHub Intelligence"
    add("GitHub", C, "Org code search", f'org:{r} NOT is:fork', f"https://github.com/search?q=org%3A{r}&type=code")
    add("GitHub", C, "API tokens in code", f'"{d}" (ghp_ OR gho_ OR ghu_ OR ghs_ OR ghr_)')
    add("GitHub", C, "AWS keys in commits", f'"{d}" AKIA OR ASIA OR ABIA OR ACCA "secret"')
    add("GitHub", C, "JWT secrets", f'"{d}" jwt_secret OR JWT_SECRET OR "secret_key" lang:python OR lang:javascript')
    add("GitHub", C, "DB credentials", f'"{d}" (mysql:// OR postgresql:// OR mongodb://) password')
    add("GitHub", C, "Internal API endpoints", f'"{d}" ("http://10." OR "http://192.168." OR "http://172.") api')
    add("GitHub", C, "Source maps + secrets", f'"{d}" filename:*.js.map "sourcesContent"')
    add("GitHub", C, "Terraform state files", f'"{d}" filename:terraform.tfstate "sensitive"')
    add("GitHub", C, "Helm chart secrets", f'"{d}" filename:values.yaml "password:" OR "secret:"')
    add("GitHub", C, "Ansible vault", f'"{d}" filename:*.yml "$ANSIBLE_VAULT" OR "ansible_become_pass"')
    add("GitHub", C, "CI/CD env leaks", f'"{d}" filename:.travis.yml OR filename:.circleci/config.yml "password" OR "token"')
    add("GitHub", C, "Leaked .env files", f'"{d}" filename:.env "APP_KEY" OR "DB_PASSWORD" OR "SECRET_KEY"')
    add("GitHub", C, "Mobile app secrets", f'"{d}" filename:*.swift OR filename:*.kt "apiKey" OR "baseUrl" OR "endpoint"')
    add("GitHub", C, "Gist dump search", f'"{d}" site:gist.github.com password OR token OR secret', f"https://gist.github.com/search?q={urllib.parse.quote(d)}")

    # ══ SHODAN: PRO ═══════════════════════════════════════════
    C = "Shodan Intelligence"
    add("Shodan", C, "All SSL hosts", f'ssl:"{d}"')
    add("Shodan", C, "Non-standard ports", f'ssl:"{d}" port:8080,8443,8888,9090,9200,5601,3000,4848,8161')
    add("Shodan", C, "Default credential pages", f'ssl:"{d}" http.title:"login" OR http.title:"admin" OR http.title:"dashboard"')
    add("Shodan", C, "Open Elasticsearch", f'ssl:"{d}" product:"Elasticsearch" port:9200')
    add("Shodan", C, "Exposed Redis", f'ssl:"{d}" product:"Redis" port:6379')
    add("Shodan", C, "MongoDB exposed", f'ssl:"{d}" product:"MongoDB" port:27017')
    add("Shodan", C, "RDP open", f'ssl:"{d}" port:3389 product:"Remote Desktop Protocol"')
    add("Shodan", C, "Exposed Kubernetes API", f'ssl:"{d}" port:6443 product:"Kubernetes"')
    add("Shodan", C, "Jenkins unauth", f'ssl:"{d}" http.title:"Dashboard [Jenkins]" -"log in"')
    add("Shodan", C, "Swagger exposed", f'ssl:"{d}" http.title:"Swagger UI"')
    add("Shodan", C, "Grafana no auth", f'ssl:"{d}" http.title:"Grafana" -login')
    add("Shodan", C, "Portainer", f'ssl:"{d}" http.title:"Portainer"')
    add("Shodan", C, "Exposed .git", f'ssl:"{d}" http.title:"Index of /.git"')
    add("Shodan", C, "ASN range scan", f'net:{asn_data.get("ip","0.0.0.0")}/24' if asn_data.get("ip") else f'org:"{r}"')
    add("Shodan", C, "Org search", f'org:"{asn_data.get("asn_name", r)}"' if asn_data.get("asn_name") else f'org:"{r}"')

    # ══ FOFA: ELITE ═══════════════════════════════════════════
    C = "FOFA Intelligence"
    add("FOFA", C, "Domain all assets", f'domain="{d}"', f"https://fofa.info/result?qbase64={base64.b64encode(f'domain=\"{d}\"'.encode()).decode()}")
    add("FOFA", C, "SSL cert search", f'cert="{d}"', f"https://fofa.info/result?qbase64={base64.b64encode(f'cert=\"{d}\"'.encode()).decode()}")
    add("FOFA", C, "Login panels", f'domain="{d}" && title="login" || title="admin"', f"https://fofa.info/result?qbase64={base64.b64encode(f'domain=\"{d}\" && (title=\"login\" || title=\"admin\")'.encode()).decode()}")
    add("FOFA", C, "Open admin panels", f'domain="{d}" && title="dashboard" && status_code="200"', f"https://fofa.info/result?qbase64={base64.b64encode(f'domain=\"{d}\" && title=\"dashboard\" && status_code=\"200\"'.encode()).decode()}")
    add("FOFA", C, "Database ports", f'domain="{d}" && (port="3306" || port="5432" || port="27017" || port="6379")', f"https://fofa.info/result?qbase64={base64.b64encode(f'domain=\"{d}\" && (port=\"3306\" || port=\"5432\" || port=\"27017\" || port=\"6379\")'.encode()).decode()}")
    add("FOFA", C, "Non-std services", f'domain="{d}" && (port="8080" || port="8443" || port="9090" || port="4848")', f"https://fofa.info/result?qbase64={base64.b64encode(f'domain=\"{d}\" && (port=\"8080\" || port=\"8443\")'.encode()).decode()}")
    add("FOFA", C, "IP range sweep", f'ip="{asn_data.get("ip","")}/24" && status_code="200"' if asn_data.get("ip") else f'domain="{d}" && status_code="200"', "https://fofa.info/")

    # ══ ZOOMEYE ═══════════════════════════════════════════════
    C = "ZoomEye Intelligence"
    add("ZoomEye", C, "Site search", f'site:{d}', f"https://www.zoomeye.org/searchResult?q={urllib.parse.quote_plus(f'site:{d}')}")
    add("ZoomEye", C, "Hostname", f'hostname:"{d}"', f"https://www.zoomeye.org/searchResult?q={urllib.parse.quote_plus(f'hostname:\"{d}\"')}")
    add("ZoomEye", C, "SSL cert", f'ssl:"{d}"', f"https://www.zoomeye.org/searchResult?q={urllib.parse.quote_plus(f'ssl:\"{d}\"')}")
    add("ZoomEye", C, "Admin panels", f'hostname:"{d}" title:"admin" OR title:"login"', f"https://www.zoomeye.org/searchResult?q={urllib.parse.quote_plus(f'hostname:\"{d}\" title:\"admin\"')}")
    add("ZoomEye", C, "App:Elasticsearch", f'hostname:"{d}" app:Elasticsearch', f"https://www.zoomeye.org/searchResult?q={urllib.parse.quote_plus(f'hostname:\"{d}\" app:Elasticsearch')}")

    # ══ CENSYS: SURGICAL ══════════════════════════════════════
    C = "Censys Intelligence"
    add("Censys", C, "All hosts", f'parsed.names: {d}')
    add("Censys", C, "Self-signed certs", f'parsed.names: {d} AND tags.raw: "self-signed"')
    add("Censys", C, "Deprecated ciphers", f'parsed.names: {d} AND tags.raw: "deprecated-cipher"')
    add("Censys", C, "Non-standard ports", f'parsed.names: {d} AND services.port: {{8080, 8443, 9200, 5601, 6379, 27017}}')
    add("Censys", C, "Expired certificates", f'parsed.names: {d} AND tags.raw: "expired"')
    add("Censys", C, "HTTP-only services", f'parsed.names: {d} AND services.service_name: HTTP AND NOT services.service_name: HTTPS')

    # ══ WAYBACK: PARAMETER MINING ════════════════════════════
    C = "Wayback Parameter Mining"
    add("Wayback", C, "All historical URLs", f'{h}/*', f'https://web.archive.org/web/*/{h}/*')
    add("Wayback", C, "CDX full dump", f'CDX API for *.{d}', f'https://web.archive.org/cdx/search/cdx?url=*.{d}&output=text&fl=original&collapse=urlkey&matchType=domain&limit=5000')
    add("Wayback", C, "Historical APIs", f'{h}/api/*', f'https://web.archive.org/web/*/{h}/api/*')
    add("Wayback", C, "Old admin paths", f'{h}/admin*', f'https://web.archive.org/web/*/{h}/admin*')
    add("Wayback", C, "Deleted env/config", f'{h}/*.env OR {h}/*.config', f'https://web.archive.org/web/*/{h}/*.env')
    add("Wayback", C, "Old Swagger docs", f'{h}/swagger*', f'https://web.archive.org/web/*/{h}/swagger*')

    if wayback_data.get("params"):
        for param in wayback_data["params"][:12]:
            add("Google", C, f"Mined param: {param}", f'site:{d} inurl:"?{param}=" OR inurl:"&{param}="')
    if wayback_data.get("endpoints"):
        for ep in wayback_data["endpoints"][:10]:
            add("Wayback", C, f"Historic endpoint: {ep}", f'{h}{ep}', f'https://web.archive.org/web/*/{h}{ep}')
    if wayback_data.get("extensions"):
        rare = [e for e in wayback_data["extensions"] if e in ["env","bak","old","sql","log","conf","key","pem","dump"]]
        for ext in rare:
            add("Google", C, f"Exposed .{ext} (mined)", f'site:{d} ext:{ext}')

    # ══ LEAK SITES: ELITE ═════════════════════════════════════
    C = "Credential Leaks"
    add("DeHashed", C, "Domain email leak", d, f"https://dehashed.com/search?query={d}")
    add("DeHashed", C, "Org name leak", r, f"https://dehashed.com/search?query={r}")
    add("Leak", C, "Pastebin credential dump", f'site:pastebin.com "{d}" password OR credential OR dump OR leak')
    add("Leak", C, "Gist secrets", f'site:gist.github.com "{d}" password OR token OR key OR secret')
    add("Leak", C, "Publicly indexed breaches", f'"{d}" filetype:txt OR filetype:csv "password" site:archive.org OR site:mega.nz')
    add("Leak", C, "HaveIBeenPwned check", d, "https://haveibeenpwned.com/DomainSearch")
    add("Leak", C, "IntelX search", d, f"https://intelx.io/?s={d}")
    add("Leak", C, "Leakix scan", d, f"https://leakix.net/domain/{d}")

    # ══ EMAIL OSINT ═══════════════════════════════════════════
    C = "Email & People OSINT"
    add("Email", C, "Hunter.io domain", d, f"https://hunter.io/domain-search?domain={d}")
    add("Email", C, "Phonebook.cz", d, f"https://phonebook.cz/?q={d}")
    add("Email", C, "LinkedIn employees", f'site:linkedin.com/in "{r}"', f"https://www.google.com/search?q=site:linkedin.com/in+%22{r}%22")
    add("Email", C, "Security team", f'site:linkedin.com "{r}" "CISO" OR "security engineer" OR "information security"', f"https://www.google.com/search?q=site:linkedin.com+%22{r}%22+CISO")
    add("Email", C, "Dev team stack reveal", f'site:linkedin.com "{r}" "' + '" OR "'.join([t.split("/")[0] for t in tech[:4]]) + '"' if tech else f'site:linkedin.com "{r}" developer', None)
    if dns_data.get("EMAIL_PROVIDERS"):
        for prov in dns_data["EMAIL_PROVIDERS"]:
            add("Email", C, f"Provider: {prov}", f'site:{d} "@{d}" filetype:txt OR filetype:csv', None)

    # ══ JS ENDPOINT DORKS ════════════════════════════════════
    C = "JS-Mined Endpoints"
    if js_endpoints:
        for ep in js_endpoints[:15]:
            clean_ep = ep.strip("/").split("?")[0]
            if clean_ep:
                add("Google", C, f"JS endpoint: /{clean_ep[:40]}", f'site:{d} inurl:/{clean_ep.split("/")[0] if "/" in clean_ep else clean_ep}')
                add("Wayback", C, f"Historic: {ep[:50]}", f'{h}{ep}', f'https://web.archive.org/web/*/{h}{ep}')

    # ══ SUBDOMAINS FROM LIVE RECON ════════════════════════════
    C = "Subdomain Intelligence"
    if subdomains:
        add("Google", C, "All subdomains (crt.sh)", f'site:*.{d} -www', f"https://crt.sh/?q=%.{d}")
        interesting_subs = [s for s in subdomains if any(x in s for x in [
            "admin", "dev", "staging", "test", "api", "internal", "intranet",
            "vpn", "remote", "mail", "owa", "exchange", "git", "jenkins",
            "backup", "monitor", "grafana", "kibana", "elastic", "docker",
            "k8s", "portainer", "vault", "consul", "db", "database", "sql"
        ])]
        for sub in interesting_subs[:20]:
            add("Google", C, f"Interesting sub: {sub}", f'site:{sub}', f"https://www.google.com/search?q=site:{sub}")
            add("Shodan", C, f"Shodan: {sub}", f'hostname:"{sub}"', f"https://www.shodan.io/search?query=hostname%3A%22{sub}%22")

    # ══ NUCLEI PLAYBOOK ═══════════════════════════════════════
    C = "Nuclei Attack Playbook"
    add("Nuclei", C, "Full vulnerability scan", f'nuclei -u https://{h} -t cves/ -t exposures/ -t misconfiguration/ -t default-logins/ -severity medium,high,critical -rl 3 -timeout 15 -H "X-BugBounty: zwanski"')
    add("Nuclei", C, "Tech fingerprint", f'nuclei -u https://{h} -t technologies/ -rl 5')
    add("Nuclei", C, "Exposed panels", f'nuclei -u https://{h} -t exposed-panels/ -t exposed-services/ -rl 5')
    add("Nuclei", C, "Subdomain takeover", f'echo "{chr(10).join(subdomains[:10]) if subdomains else h}" | nuclei -t takeovers/ -rl 3')
    add("Nuclei", C, "CORS misconfig", f'nuclei -u https://{h} -t misconfiguration/cors-misconfiguration.yaml')
    add("Nuclei", C, "JWT attack", f'nuclei -u https://{h} -t misconfiguration/jwt-*')
    add("Nuclei", C, "Fuzzing mode", f'nuclei -u https://{h} -t fuzzing/ -rl 2 -timeout 20 -interactsh-url https://interact.sh')

    # ══ RECON AUTOMATION ══════════════════════════════════════
    C = "Recon Automation Commands"
    add("Recon", C, "Subfinder full", f'subfinder -d {d} -all -recursive -o subs_{r}.txt')
    add("Recon", C, "HTTPX probe", f'cat subs_{r}.txt | httpx -title -tech-detect -status-code -follow-redirects -H "X-BugBounty: zwanski" -o live_{r}.txt')
    add("Recon", C, "GAU parameter harvest", f'echo {h} | gau --subs | grep "=" | uro | qsreplace "FUZZ" | tee params_{r}.txt')
    add("Recon", C, "FFuF directory brute", f'ffuf -u https://{h}/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -mc 200,301,302,403 -t 5 -H "X-BugBounty: zwanski"')
    add("Recon", C, "Dalfox XSS scan", f'cat params_{r}.txt | dalfox pipe --skip-bav --deep-domxss')
    add("Recon", C, "SQLMap on params", f'sqlmap -m params_{r}.txt --batch --level=2 --risk=1 --random-agent -H "X-BugBounty: zwanski"')
    add("Recon", C, "TruffleHog secrets", f'trufflehog github --org={r} --token=$GITHUB_TOKEN')
    add("Recon", C, "Arjun param discover", f'arjun -u https://{h}/api/ --stable -oJ params_arjun_{r}.json')
    add("Recon", C, "LinkFinder JS", f'python3 linkfinder.py -i https://{h} -d -o cli')
    add("Recon", C, "Waybackurls harvest", f'echo {d} | waybackurls | grep -E "\\.(env|bak|sql|log|conf|key|pem)$" | sort -u')

    # ══ CUSTOM KEYWORDS ═══════════════════════════════════════
    if kw:
        C = "Custom Intelligence"
        for k in kw:
            add("Google", C, "Keyword in site", f'site:{d} "{k}"')
            add("Google", C, "Keyword in URL", f'site:{d} inurl:{k}')
            add("Google", C, "Keyword in file", f'site:{d} "{k}" ext:pdf OR ext:xlsx OR ext:docx OR ext:sql')
            add("GitHub", C, f"GitHub: {k}", f'"{k}" "{d}"')
            add("Shodan", C, f"Shodan: {k}", f'ssl:"{d}" "{k}"')

    return dorks


# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="ph-header">
    <div class="ph-title">👁 PHANTOM</div>
    <div class="ph-subtitle">ELITE OSINT & DORK INTELLIGENCE ENGINE // ZWANSKI SECURITY</div>
    <div class="ph-warn">⚠ AUTHORIZED SECURITY RESEARCH ONLY — PRIVATE — DO NOT REDISTRIBUTE</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# AUTH GATE
# ══════════════════════════════════════════════════════════════
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown('<div class="pw-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="pw-box"><div class="pw-eye">👁</div><div class="pw-title">AUTHENTICATION REQUIRED</div></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        pw = st.text_input("ACCESS CODE", type="password", placeholder="••••••••", key="pw")
        if st.button("⚡ AUTHENTICATE", use_container_width=True):
            if pw == "zwanski":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("⛔ ACCESS DENIED")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙ PHANTOM CONFIG")
    st.markdown("---")
    tech_opts = [
        "TYPO3", "ForgeRock/OpenAM", "Thelia", "F5/BIG-IP",
        "Horizon/VDI", "Keycloak", "Drupal", "WordPress",
        "Exchange/OWA", "MobileIron/Ivanti", "OwnCloud/Nextcloud",
        "Jenkins", "GitLab", "Kubernetes", "Elasticsearch",
        "Spring Boot", "Laravel", "Django", "Strapi", "Directus"
    ]
    tech = st.multiselect("KNOWN TECH STACK", tech_opts, [])
    kw_raw = st.text_input("EXTRA KEYWORDS", placeholder="kumo, geneveid, kumo-api...")
    st.markdown("---")
    run_live = st.checkbox("⚡ Live Recon Modules", value=True, help="crt.sh, Wayback CDX, DNS, ASN, JS extraction")
    run_favicon = st.checkbox("🎯 Favicon Hash (Shodan)", value=False, help="Requires mmh3: pip install mmh3")
    show_links = st.checkbox("🔗 Show clickable links", value=True)
    st.markdown("---")
    if st.button("🔒 LOGOUT", use_container_width=True):
        st.session_state.auth = False
        st.rerun()
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.55rem;color:rgba(124,77,255,0.4);letter-spacing:0.1em'>requests: {'✓' if HAS_REQUESTS else '✗'}<br>mmh3: {'✓' if HAS_MMH3 else '✗'}<br>dns: {'✓' if HAS_DNS else '✗'}</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
st.markdown("<div style='padding:1.5rem 3rem 3rem'>", unsafe_allow_html=True)

c_in, c_btn = st.columns([5, 1])
with c_in:
    target_input = st.text_input("TARGET", placeholder="https://target.ge.ch  or  target.ge.ch", key="target")
with c_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    go = st.button("👁 SCAN", use_container_width=True)

if go and target_input:
    t = parse_target(target_input)

    st.markdown(f"""
    <div class="target-strip">
        <span style='color:rgba(124,77,255,0.5);font-size:0.65rem;letter-spacing:0.2em'>TARGET</span>
        <span class="t-chip">🌐 {t['hostname']}</span>
        <span class="t-chip">📍 {t['tld']}</span>
        <span class="t-chip">🔑 {t['root']}</span>
        {"<span class='t-chip-cyan'>📂 " + t['subdomain'] + "</span>" if t['subdomain'] else ""}
        <span style='margin-left:auto;font-size:0.6rem;color:rgba(124,77,255,0.5)'>{datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ UTC")}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── LIVE RECON MODULES ────────────────────────────────────
    subdomains, wayback_data, dns_data, asn_data, js_endpoints, favicon_data = [], {}, {}, {}, [], {}

    if run_live and HAS_REQUESTS:
        prog = st.progress(0, text="⚡ Initializing live recon...")

        with st.spinner(""):
            prog.progress(10, "🌐 crt.sh subdomain harvest...")
            subdomains = live_crtsh(t["tld"])

            prog.progress(30, "🕰️ Wayback CDX parameter mining...")
            wayback_data = live_wayback_params(t["tld"])

            prog.progress(50, "🔍 DNS intelligence...")
            dns_data = live_dns_intel(t["clean"])

            prog.progress(65, "🌊 ASN / IP intel...")
            asn_data = live_asn_intel(t["hostname"])

            prog.progress(80, "🔗 JS endpoint extraction...")
            js_endpoints = live_js_endpoints(t["raw"])

            if run_favicon:
                prog.progress(90, "🎯 Favicon hash calculation...")
                favicon_data = live_favicon_hash(t["raw"], t["hostname"])

            prog.progress(100, "✅ Live recon complete!")
            time.sleep(0.5)
            prog.empty()

        # ── DISPLAY LIVE RESULTS ──────────────────────────────
        live_tabs = st.tabs(["🌐 SUBDOMAINS", "🕰️ WAYBACK", "🔍 DNS", "🌊 ASN", "🔗 JS", "🎯 FAVICON"])

        with live_tabs[0]:
            st.markdown(f'<div class="module-header">CRT.SH LIVE HARVEST <span class="module-badge">{len(subdomains)} FOUND</span></div>', unsafe_allow_html=True)
            if subdomains:
                interesting = [s for s in subdomains if any(x in s for x in ["admin","dev","stag","test","api","internal","vpn","mail","git","backup","monitor","db","sql","intranet","secret","private","mgmt"])]
                if interesting:
                    st.markdown(f"**🚨 INTERESTING SUBDOMAINS ({len(interesting)}):**")
                    for s in interesting:
                        st.markdown(f'<div class="live-item">⚡ {s} <span class="live-badge" style="color:#ff1744;border-color:#ff1744">HIGH VALUE</span></div>', unsafe_allow_html=True)
                st.markdown(f"**ALL ({len(subdomains)}):**")
                cols = st.columns(3)
                for i, s in enumerate(subdomains):
                    cols[i % 3].code(s)

                # Export
                st.download_button("📥 EXPORT SUBDOMAINS",
                    "\n".join(subdomains),
                    file_name=f"subdomains_{t['root']}.txt",
                    mime="text/plain")
            else:
                st.info("No subdomains found or crt.sh unreachable.")

        with live_tabs[1]:
            st.markdown(f'<div class="module-header">WAYBACK CDX INTELLIGENCE <span class="module-badge">{wayback_data.get("raw_count",0)} URLS ANALYZED</span></div>', unsafe_allow_html=True)
            if wayback_data:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**🔑 MINED PARAMS ({len(wayback_data.get('params',[]))})**")
                    for p in wayback_data.get("params", [])[:30]:
                        st.code(p)
                with c2:
                    st.markdown(f"**📂 HISTORIC ENDPOINTS ({len(wayback_data.get('endpoints',[]))})**")
                    for e in wayback_data.get("endpoints", [])[:30]:
                        st.code(e)
                with c3:
                    st.markdown("**📄 FILE EXTENSIONS**")
                    for e in wayback_data.get("extensions", []):
                        color = "#ff1744" if e in ["env","bak","sql","log","key","pem"] else "#b388ff"
                        st.markdown(f'<div class="live-item" style="color:{color}">.{e}</div>', unsafe_allow_html=True)
            else:
                st.info("Wayback CDX returned no data.")

        with live_tabs[2]:
            st.markdown('<div class="module-header">DNS INTELLIGENCE</div>', unsafe_allow_html=True)
            if dns_data:
                for rtype, vals in dns_data.items():
                    st.markdown(f"**{rtype}:**")
                    for v in vals:
                        st.code(v)
            else:
                st.info("DNS query failed.")

        with live_tabs[3]:
            st.markdown('<div class="module-header">ASN / IP INTELLIGENCE</div>', unsafe_allow_html=True)
            if asn_data:
                for k, v in asn_data.items():
                    if v:
                        st.markdown(f"**{k}:** `{v}`")
            else:
                st.info("ASN lookup failed.")

        with live_tabs[4]:
            st.markdown(f'<div class="module-header">JS ENDPOINT EXTRACTION <span class="module-badge">{len(js_endpoints)} FOUND</span></div>', unsafe_allow_html=True)
            if js_endpoints:
                for ep in js_endpoints:
                    st.code(ep)
            else:
                st.info("No JS endpoints extracted.")

        with live_tabs[5]:
            st.markdown('<div class="module-header">FAVICON HASH (SHODAN/FOFA)</div>', unsafe_allow_html=True)
            if favicon_data:
                for path, info in favicon_data.items():
                    st.markdown(f"**{path}**")
                    st.code(info.get("shodan_dork",""))
                    if info.get("link_shodan"):
                        st.markdown(f"[▶ Open in Shodan]({info['link_shodan']})")
                    if info.get("fofa_dork"):
                        st.code(info.get("fofa_dork",""))
                        st.markdown(f"[▶ Open in FOFA]({info.get('link_fofa','')})")
            elif not run_favicon:
                st.info("Enable favicon hash in sidebar config.")
            else:
                st.info("No favicons found or target unreachable.")

        st.markdown("---")

    # ── GENERATE DORKS ────────────────────────────────────────
    with st.spinner("⚡ Generating elite dork matrix..."):
        dorks = generate_dorks(t, tech, kw_raw, wayback_data, subdomains, dns_data, asn_data, js_endpoints)

    # Stats
    by_engine = defaultdict(list)
    by_cat = defaultdict(list)
    for dk in dorks:
        by_engine[dk["engine"]].append(dk)
        by_cat[dk["cat"]].append(dk)

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-block"><div class="stat-val">{len(dorks)}</div><div class="stat-lbl">Total Dorks</div></div>
        <div class="stat-block"><div class="stat-val">{len(by_engine)}</div><div class="stat-lbl">Engines</div></div>
        <div class="stat-block"><div class="stat-val">{len(by_cat)}</div><div class="stat-lbl">Categories</div></div>
        <div class="stat-block"><div class="stat-val">{len(subdomains)}</div><div class="stat-lbl">Subdomains</div></div>
        <div class="stat-block"><div class="stat-val">{len(wayback_data.get('params',[]))}</div><div class="stat-lbl">Mined Params</div></div>
        <div class="stat-block"><div class="stat-val">{len(js_endpoints)}</div><div class="stat-lbl">JS Endpoints</div></div>
        <div class="stat-block"><div class="stat-val">{len(t['org_variants'])}</div><div class="stat-lbl">Bucket Variants</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Exports
    ec1, ec2, ec3, ec4 = st.columns(4)
    all_txt = "\n".join([f"[{dk['engine']}][{dk['cat']}] {dk['label']}\n{dk['query']}\n" for dk in dorks])
    all_json = json.dumps([{"engine": dk["engine"], "cat": dk["cat"], "label": dk["label"], "query": dk["query"], "link": dk["link"]} for dk in dorks], indent=2)
    google_txt = "\n".join([dk["query"] for dk in dorks if dk["engine"] == "Google"])
    recon_txt = "\n".join([dk["query"] for dk in dorks if dk["engine"] in ["Nuclei", "Recon"]])
    with ec1:
        st.download_button("📥 ALL (TXT)", all_txt, f"phantom_{t['root']}_all.txt", "text/plain", use_container_width=True)
    with ec2:
        st.download_button("📥 ALL (JSON)", all_json, f"phantom_{t['root']}_all.json", "application/json", use_container_width=True)
    with ec3:
        st.download_button("📥 GOOGLE ONLY", google_txt, f"phantom_{t['root']}_google.txt", "text/plain", use_container_width=True)
    with ec4:
        st.download_button("📥 COMMANDS", recon_txt, f"phantom_{t['root']}_commands.txt", "text/plain", use_container_width=True)

    # ── DORK TABS ─────────────────────────────────────────────
    engine_list = ["ALL"] + sorted(by_engine.keys())
    tabs = st.tabs(engine_list)

    badge_cls = {
        "Google": "ep-google", "GitHub": "ep-github", "Shodan": "ep-shodan",
        "Censys": "ep-censys", "FOFA": "ep-fofa", "ZoomEye": "ep-zoomeye",
        "Wayback": "ep-wayback", "Leak": "ep-leak", "LinkedIn": "ep-linkedin",
        "DeHashed": "ep-dehashed", "Nuclei": "ep-nuclei", "Cloud": "ep-cloud",
        "Email": "ep-email", "Recon": "ep-recon",
    }
    icons = {
        "Google": "🔍", "GitHub": "🐙", "Shodan": "🌊", "Censys": "🔭",
        "FOFA": "🔴", "ZoomEye": "🔵", "Wayback": "🕰️", "Leak": "💧",
        "LinkedIn": "💼", "DeHashed": "⚠️", "Nuclei": "⚛️",
        "Cloud": "☁️", "Email": "📧", "Recon": "🛠️",
    }

    for tab_i, tab in enumerate(tabs):
        with tab:
            sel = engine_list[tab_i]
            filtered = dorks if sel == "ALL" else [dk for dk in dorks if dk["engine"] == sel]
            grp = defaultdict(list)
            for dk in filtered:
                grp[dk["cat"]].append(dk)
            for cat_name, cat_dorks in grp.items():
                st.markdown(f'<div class="module-header">{cat_name} <span class="module-badge">{len(cat_dorks)}</span></div>', unsafe_allow_html=True)
                for dk in cat_dorks:
                    bc = badge_cls.get(dk["engine"], "ep-google")
                    icon = icons.get(dk["engine"], "🔍")
                    link_html = ""
                    if show_links and dk.get("link"):
                        link_html = f'<div class="dork-link"><a href="{dk["link"]}" target="_blank">▶ OPEN → {dk["engine"].upper()}</a></div>'
                    st.markdown(f"""
                    <div class="dork-card">
                        <span class="engine-pill {bc}">{icon} {dk['engine']}</span>
                        <div class="dork-label">{dk['label']}</div>
                        <div class="dork-query">{dk['query']}</div>
                        {link_html}
                    </div>
                    """, unsafe_allow_html=True)

elif go and not target_input:
    st.warning("⚠ INPUT A TARGET FIRST")
else:
    st.markdown("""
    <div style='text-align:center;padding:5rem 2rem;opacity:0.3'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:5rem;color:#7c4dff;line-height:1'>👁</div>
        <div style='font-family:Rajdhani,sans-serif;font-size:1rem;color:#b388ff;letter-spacing:0.4em;margin-top:1rem'>INPUT TARGET → EXECUTE</div>
        <div style='font-size:0.65rem;color:#9c27b0;letter-spacing:0.2em;margin-top:0.5rem'>
            Google · GitHub · Shodan · FOFA · ZoomEye · Censys · Wayback · DeHashed · Nuclei · Cloud
        </div>
        <div style='font-size:0.6rem;color:#7c4dff;letter-spacing:0.15em;margin-top:0.3rem;opacity:0.6'>
            + LIVE: crt.sh · CDX Parameter Mining · DNS Intel · ASN · JS Extraction · Favicon Hash
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="ph-footer">
    <div>
        <div class="footer-brand">👁 PHANTOM</div>
        <div style='font-size:0.55rem;color:rgba(124,77,255,0.4);letter-spacing:0.1em;margin-top:0.2rem'>ELITE OSINT FRAMEWORK v3.0</div>
    </div>
    <div class="footer-warn">
        ⚠ THIS TOOL IS FOR AUTHORIZED SECURITY RESEARCH ONLY<br>
        DO NOT USE AGAINST TARGETS WITHOUT EXPLICIT WRITTEN PERMISSION<br>
        UNAUTHORIZED USE IS A CRIMINAL OFFENCE
    </div>
    <div class="footer-right">
        Built by <a href="https://zwanski.bio" target="_blank">zwanski</a><br>
        HackerOne · Bugcrowd · Bug Bounty Switzerland<br>
        <span style='opacity:0.4;font-size:0.5rem'>© 2026 ZWANSKI — ALL RIGHTS RESERVED</span>
    </div>
</div>
""", unsafe_allow_html=True)
