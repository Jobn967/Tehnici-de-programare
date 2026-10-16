from pathlib import Path
from PIL import Image


def ascunde_mesaj(cale_imagine, mesaj, iesire="stego.png"):
    img = Image.open(cale_imagine).convert("RGB")
    pixeli = list(img.getdata())

    date = mesaj.encode("utf-8") + b"\x00"
    biti = "".join(f"{octet:08b}" for octet in date)

    if len(biti) > len(pixeli) * 3:
        raise ValueError("Mesajul este prea mare pentru această imagine.")

    pixeli_noi = []
    index_bit = 0

    for pixel in pixeli:
        canale = list(pixel)
        for i in range(3):
            if index_bit < len(biti):
                canale[i] = (canale[i] & ~1) | int(biti[index_bit])
                index_bit += 1
        pixeli_noi.append(tuple(canale))

    img.putdata(pixeli_noi)
    img.save(iesire, "PNG")
    print("Mesajul a fost ascuns în", iesire)


def dezvaluie_mesaj(cale_imagine="stego.png"):
    img = Image.open(cale_imagine).convert("RGB")
    biti = []

    for r, g, b in img.getdata():
        biti.extend((str(r & 1), str(g & 1), str(b & 1)))

    rezultat = bytearray()
    for start in range(0, len(biti) - 7, 8):
        octet = int("".join(biti[start:start + 8]), 2)
        if octet == 0:
            break
        rezultat.append(octet)

    return rezultat.decode("utf-8", errors="replace")


if __name__ == "__main__":
    sursa = Path("probe/foto.jpg")
    if not sursa.exists():
        print("Lipsește probe/foto.jpg. Rulează mai întâi probe/pregateste.py.")
    else:
        ascunde_mesaj(sursa, "FLAG{ascuns_in_pixeli}")
        print("Mesaj dezvăluit:", dezvaluie_mesaj("stego.png"))
