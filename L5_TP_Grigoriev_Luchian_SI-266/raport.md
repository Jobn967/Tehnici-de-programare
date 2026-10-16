# Raport – Laboratorul 5: Forensics

## Lucrarea A – Decoder universal

### A1–A4. Codări și straturi
Am verificat diferența dintre text și octeți, apoi am implementat recunoașterea și decodarea straturilor URL, hexadecimal și Base64. Programul încearcă să desfacă succesiv straturile până obține text imprimabil.

- Mesajul final decodat: FLAG{straturi_de_encoding}
- Stratul folosit: base64

### A5. XOR
Programul a încercat cheile de un octet de la 0 la 255 și a afișat rezultatele ASCII imprimabile.

- Cheia XOR găsită: 128
- Textul clar: Un singur octet tine tot secretul... gaseste-l! FLAG{xor_un_octet}

### A6. Hash
Algoritmul a fost estimat după lungimea hash-ului: MD5 (32), SHA-1 (40) sau SHA-256 (64) caractere hexazecimale.

- Algoritm: md5
- Parola găsită în wordlist: password

## Lucrarea B – Analiza fișierelor

### B1. Semnături
- `foto.jpg`: jpeg
- `ascuns.png`: png

### B2. Șiruri imprimabile
Din `ascuns.png` au fost extrase șirurile ASCII imprimabile. Indiciul găsit: FLAG{ascuns_prin_carving}.

### B3. EXIF și GPS
- Metadate importante: Model = iPhone 13
DateTime = 2026:09:14 10:30:00
GPSInfo = 98
Make = Apple
GPS:
GPSLatitudeRef = N
GPSLatitude = (47.0, 1.0, 0.0)
GPSLongitudeRef = E
GPSLongitude = (28.0, 51.0, 27.0)
- Latitudine zecimală: 47.016666666666666
- Longitudine zecimală: 28.8575

### B4. Arhiva ascunsă
Arhiva ZIP a fost căutată după semnătura `PK\x03\x04` și salvată în `gasit.zip`.

- Poziția semnăturii: 782
- Fișierele și mesajul din arhivă: FLAG{ascuns_prin_carving}

### B5–B6. Steganografie LSB
Mesajul a fost ascuns în biții cei mai puțin semnificativi ai canalelor RGB și salvat în PNG pentru a nu pierde biții la recomprimare.

- Mesaj ascuns și apoi dezvăluit: FLAG{ascuns_in_pixeli}
- Fișier rezultat: `stego.png`

## Concluzie
Exercițiile au demonstrat cum pot fi recunoscute codările, cum poate fi recuperat un text XOR sau o parolă dintr-un dicționar și cum pot fi identificate metadatele și datele ascunse în fișiere.
