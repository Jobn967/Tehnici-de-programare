import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote


DIRECTOR = Path(__file__).resolve().parent
FISA = DIRECTOR / "fisa.json"


def ghici_strat(s):
    """Recunoaște forma probabilă a unei codări."""
    if re.search(r"%[0-9a-fA-F]{2}", s):
        return "url"

    if s and len(s) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", s):
        return "hex"

    if s and re.fullmatch(r"[A-Za-z0-9+/]*={0,2}", s):
        try:
            base64.b64decode(s, validate=True)
            if len(s) % 4 == 0:
                return "base64"
        except (ValueError, base64.binascii.Error):
            pass

    return "necunoscut"


def desfa(s):
    """Întoarce (numele_stratului, octeții_decodați)."""
    strat = ghici_strat(s)

    try:
        if strat == "base64":
            return strat, base64.b64decode(s, validate=True)
        if strat == "hex":
            return strat, bytes.fromhex(s)
        if strat == "url":
            return strat, unquote(s).encode("utf-8")
    except (ValueError, base64.binascii.Error):
        pass

    return "necunoscut", s.encode("utf-8")


def citibil(b):
    """True dacă octeții reprezintă caractere ASCII imprimabile."""
    return all(32 <= c < 127 for c in b)


def decodeaza_straturi(val, maxim=8):
    """Desface succesiv codările și păstrează pașii efectuați."""
    pasi = []
    curent = val

    for _ in range(maxim):
        if isinstance(curent, bytes):
            try:
                curent = curent.decode("utf-8")
            except UnicodeDecodeError:
                break

        strat, rezultat = desfa(curent)
        if strat == "necunoscut":
            break

        pasi.append({"strat": strat, "rezultat_hex": rezultat.hex()})

        try:
            text = rezultat.decode("utf-8")
        except UnicodeDecodeError:
            if citibil(rezultat):
                text = rezultat.decode("latin1")
            else:
                break

        if ghici_strat(text) != "necunoscut":
            curent = text
            continue

        if citibil(rezultat):
            return text, pasi
        break

    return curent.decode("utf-8", errors="replace") if isinstance(curent, bytes) else curent, pasi


def sparge_xor(cale):
    """Încearcă toate cheile XOR de un octet și întoarce rezultatele imprimabile."""
    date = Path(cale).read_bytes()
    rezultate = []

    for cheie in range(256):
        clar = bytes(octet ^ cheie for octet in date)
        if clar and citibil(clar):
            rezultate.append((cheie, clar.decode("ascii")))

    return rezultate


def algoritm_hash(tinta):
    """Alege algoritmul uzual în funcție de lungimea hash-ului."""
    return {32: "md5", 40: "sha1", 64: "sha256"}.get(len(tinta))


def sparge_hash(cale_hash, cale_wordlist):
    tinta = Path(cale_hash).read_text(encoding="utf-8").splitlines()[0].strip()
    algoritm = algoritm_hash(tinta)

    if algoritm is None:
        raise ValueError("Lungimea hash-ului nu corespunde MD5, SHA-1 sau SHA-256.")

    with open(cale_wordlist, encoding="latin1") as f:
        for cuv in f:
            cuv = cuv.rstrip("\r\n")
            calculat = hashlib.new(algoritm, cuv.encode()).hexdigest()
            if calculat.lower() == tinta.lower():
                return algoritm, cuv

    return algoritm, None


def salveaza_fisa(strat, rezultat, sursa):
    date = {
        "sursa": sursa,
        "strat": strat,
        "rezultat": rezultat,
    }
    FISA.write_text(json.dumps(date, ensure_ascii=False, indent=4), encoding="utf-8")
    return date


def main():
    parser = argparse.ArgumentParser(
        description="Decoder pentru URL, hex, Base64, XOR și hash-uri uzuale."
    )
    parser.add_argument("intrare", help="Șirul de analizat sau calea către fișier")
    parser.add_argument("--fisier", action="store_true", help="Intrarea este o cale de fișier")
    parser.add_argument("--xor", action="store_true", help="Încearcă toate cheile XOR de un octet")
    parser.add_argument("--hash", action="store_true", help="Intrarea este fișierul cu hash")
    parser.add_argument("--wordlist", default="probe/wordlist.txt", help="Calea către wordlist")
    args = parser.parse_args()

    if args.xor:
        for cheie, text in sparge_xor(args.intrare):
            print(f"Cheie XOR: {cheie} | Text: {text}")
        return

    if args.hash:
        algoritm, parola = sparge_hash(args.intrare, args.wordlist)
        print("Algoritm:", algoritm)
        print("Parolă găsită:" if parola is not None else "Parola nu a fost găsită:", parola or "")
        return

    if args.fisier:
        cale = Path(args.intrare)
        continut = cale.read_bytes()
        try:
            valoare = continut.decode("utf-8").strip()
        except UnicodeDecodeError:
            valoare = continut.hex()
    else:
        valoare = args.intrare

    rezultat, pasi = decodeaza_straturi(valoare)
    strat_initial = pasi[0]["strat"] if pasi else ghici_strat(valoare)
    salveaza_fisa(strat_initial, rezultat, args.intrare)

    print("Strat inițial:", strat_initial)
    print("Rezultat:", rezultat)
    print("Fișa a fost salvată în:", FISA)


if __name__ == "__main__":
    main()
