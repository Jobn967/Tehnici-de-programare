import re
import zipfile
from fractions import Fraction
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def tip_real(cale):
    with open(cale, "rb") as f:
        cap = f.read(8)

    if cap.startswith(b"%PDF"):
        return "pdf"
    if cap.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if cap.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if cap.startswith(b"PK\x03\x04"):
        return "zip/docx"
    return "necunoscut (" + cap.hex() + ")"


def extrage_strings(cale, minim=4):
    date = Path(cale).read_bytes()
    return [m.decode("ascii", errors="ignore")
            for m in re.findall(rb"[ -~]{" + str(minim).encode() + rb",}", date)]


def valoare_numar(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        try:
            return float(v.numerator) / float(v.denominator)
        except AttributeError:
            return float(Fraction(v))


def coordonate_zecimale(coord, ref):
    grade, minute, secunde = [valoare_numar(x) for x in coord]
    rezultat = grade + minute / 60 + secunde / 3600
    if ref in ("S", "W"):
        rezultat *= -1
    return rezultat


def citeste_exif(cale):
    img = Image.open(cale)
    exif = img.getexif()
    print("Metadate EXIF:")
    for tag_id, valoare in exif.items():
        nume = TAGS.get(tag_id, tag_id)
        print(f"{nume} = {valoare}")

    gps = exif.get_ifd(34853) if 34853 in exif else {}
    if not gps:
        print("Nu au fost găsite coordonate GPS.")
        return

    gps_citibil = {GPSTAGS.get(k, k): v for k, v in gps.items()}
    print("GPS:")
    for nume, valoare in gps_citibil.items():
        print(f"{nume} = {valoare}")

    lat = gps_citibil.get("GPSLatitude")
    lat_ref = gps_citibil.get("GPSLatitudeRef")
    lon = gps_citibil.get("GPSLongitude")
    lon_ref = gps_citibil.get("GPSLongitudeRef")

    if lat and lat_ref and lon and lon_ref:
        print("Latitudine zecimală:", coordonate_zecimale(lat, lat_ref))
        print("Longitudine zecimală:", coordonate_zecimale(lon, lon_ref))


def extrage_zip(cale, destinatie="gasit.zip"):
    date = Path(cale).read_bytes()
    i = date.find(b"PK\x03\x04")
    if i == -1:
        print("Nu a fost găsită semnătura ZIP.")
        return None

    Path(destinatie).write_bytes(date[i:])
    print("Arhivă extrasă de la octetul", i, "în", destinatie)

    try:
        with zipfile.ZipFile(destinatie) as arhiva:
            print("Fișiere în arhivă:", arhiva.namelist())
            arhiva.extractall("arhiva_extrasa")
            print("Conținut extras în directorul arhiva_extrasa/")
    except zipfile.BadZipFile:
        print("Datele găsite încep cu semnătura ZIP, dar arhiva nu este validă.")
    return destinatie


if __name__ == "__main__":
    for cale in ("probe/foto.jpg", "probe/ascuns.png"):
        if Path(cale).exists():
            print(f"\n{cale}: {tip_real(cale)}")

    if Path("probe/ascuns.png").exists():
        print("\nȘiruri imprimabile din ascuns.png:")
        for sir in extrage_strings("probe/ascuns.png"):
            print(sir)

    if Path("probe/foto.jpg").exists():
        print("\nAnaliza EXIF:")
        citeste_exif("probe/foto.jpg")

    if Path("probe/ascuns.png").exists():
        print("\nExtragere arhivă:")
        extrage_zip("probe/ascuns.png")
