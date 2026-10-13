import requests
import time
from requests.exceptions import HTTPError

SITES = [
    # Pagini obișnuite (Părțile 2, 3 și 4)
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    # Pagini care eșuează
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    # Anteturi de securitate (Partea 5)
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    # Răspunde aleatoriu cu 200 sau 500 (Partea 6)
    "https://httpbin.org/status/200,500",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]
TIMEOUT=10


def build_url(host, path):
    """Returnează o adresă completă, de exemplu https://example.com/login."""
    if path[0] != "/":
        r=f"https://{host}/{path}"
    else:
        r=f"https://{host}{path}"
    return r


def is_https(url):
    """Returnează True dacă adresa începe cu https://, altfel False."""
    if "https://" in url:
        return True
    else:
        return False


def show_response(url):
    """Trimite un GET la url și afișează statusul și Content-Type."""
    r=requests.get(url, timeout=TIMEOUT)
    print("Status: ",r.status_code)
    print("Content-Type: ",r.headers["Content-Type"])


def check_site(url):
    """Returnează un dicționar cu: status, content_type, length, server."""
    dictreturn={}
    try:
        r=requests.get(url, timeout=5)
        
        dictreturn={"status": r.status_code, "content_type": r.headers["Content-Type"], "length": len(r.content), "server": r.headers["Server"]}
    except requests.HTTPError as e:
        dictreturn={"status": "None", "error": e}
        return dictreturn


def scan_sites():
    """Verifică toate site-urile din SITES, afișează-le pe cele care merg și un rezumat."""
    countEsuate=0
    countReusite=0
    for url in SITES:
        try:
            r=requests.get(url, timeout=5)
            name=url
            status=r.status_code
            length=len(r.content)
            if status>=200 and status <300:
                print(name, " -> ", status,", ", length, " octeți\n")
                countReusite+=1

        except HTTPError as e:
            countEsuate+=1
    print("\n")
    print(f"Reușite: {countReusite} | Eșuate: {countEsuate}")

def check_headers(url):
    """Returnează un dicționar cu: present, missing, score."""
    dictSecurity={"present": [], "missing": [], "score": 0}
    counterScore=0
    for header in SECURITY_HEADERS:
        try:
            r=requests.get(url, timeout=5)
            if r.headers[header] is not None:
                dictSecurity["present"].append(header)
                counterScore+=1
            else:
                dictSecurity["missing"].append(header)
            time.sleep(1)
        except HTTPError:
            print()
    dictSecurity["score"]=counterScore*25
    return dictSecurity


def retry_check(url, attempts=3):
    """Încearcă de cel mult `attempts` ori; returnează un dicționar cu: status, attempts."""
    pass
