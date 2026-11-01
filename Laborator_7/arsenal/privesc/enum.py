# -*- coding: utf-8 -*-
"""Laboratorul 7 - enumerare spre root. Generat din programul
de laborator, cu codul scris de student."""
import argparse, io, json, os

GTFO = {'cp', 'bash', 'python3', 'awk', 'find', 'vim.basic', 'nmap', 'perl', 'less', 'vim'}

#  PARTEA A - aduna si grupeaza
# ---------------------------------------------------------------------------

def citeste_linii(cale):
    """Sarcina 1. Citeste un fisier si intoarce LISTA randurilor folositoare.

    Fiecare rand se curata de spatiile de la capete. Se arunca randurile
    goale si cele care incep cu diez, fiindca sunt comentarii.

    citeste_linii("start/suid.txt")  ->  lista cu 14 randuri
    """
    lista=[]
    try:
        with open(cale, "r") as file:
            for i in file:
                i=i.strip()
                if i[0] == "#":
                    continue
                lista.append(i)
        return lista
    except FileNotFoundError:
        print("Fisierul nu a fost gasit")

def nume(cale):
    """Sarcina 2. Intoarce numele fisierului dintr-o cale.

    Numele decide daca binarul e periculos, nu toata calea.

    nume("/usr/bin/find")  ->  "find"
    """
    fisier=[]
    fisier=cale.rsplit("/", 1)
    nume_fisier=fisier[-1]
    return nume_fisier


def suid_constatari(cale):
    """Sarcina 3. Din fisierul SUID face o LISTA DE DICTIONARE.

    Fiecare cale UNICA, in ordine sortata, devine o fisa cu trei campuri:
        {"cale": ..., "nume": ..., "risc": "mare" sau "normal"}
    Riscul e "mare" daca numele se afla in multimea GTFO, altfel "normal".

    Atentie: in captura o cale apare de doua ori. Fisa ei apare o data.
    """ 
    lista_suid=[]
    lista_cale=[]
    lista_cale=set(citeste_linii(cale))
    lista_cale=sorted(lista_cale)
    for i in lista_cale:
        if nume(i) in GTFO:
            risc="mare"
        else:
            risc="normal"
        lista_suid.append({"cale": i, "nume": nume(i), "risc": risc})
    return lista_suid


def sudo_constatari(cale):
    """Sarcina 4. Din fisierul sudo face o lista de dictionare.

    Un rand are forma  utilizator : drept
    Il despachetezi intr-un tuplu de doua valori, taind la PRIMUL separator:
        user, drept = rand.split(" : ", 1)

    Fiecare rand devine:
        {"user": ..., "drept": ..., "risc": "mare" sau "normal"}
    Riscul e "mare" daca in drept apare NOPASSWD, fiindca atunci comanda
    se ruleaza fara sa se ceara parola.
    """
    sudo_usr_eval = []
    try:
        with open(cale, "r") as f:
            for i in f:
                i = i.strip()
                user, drept = i.split(":",1)
                user = user.strip()
                drept = drept.strip()
                if "NOPASSWD" in drept:
                    risc = "mare"
                else:
                    risc = "normal"
                sudo_usr_eval.append({
                    "user": user,
                    "drept": drept,
                    "risc": risc
                    })
    except FileNotFoundError:
        print("Fisierul nu a fost gasit")
    return sudo_usr_eval



def cron_constatari(cale):
    """Sarcina 5. Din crontab face o lista de dictionare.

    Un rand de crontab are cinci campuri de timp, apoi utilizatorul si
    comanda. Desparti randul in campuri cu split(), iar:
        campul 5 (al saselea) este utilizatorul
        tot ce urmeaza, lipit la loc cu spatii, este comanda

    Fiecare rand devine:  {"user": ..., "comanda": ...}
    """
    line = []
    crontab_list = []
    try:
        with open(cale, "r") as f:
            for i in f:
                if "#" in i:
                    continue
                line = i.split()
                crontab_list.append({
                    "user": line[5],
                    "comanda": " ".join(line[6:])
                    })
    except FileNotFoundError:
        print("Fisierul nu a fost gasit")
    return crontab_list

def enumereaza(dosar):
    """Sarcina 6. Aduna toate constatarile intr-un singur DICTIONAR.

    Primeste calea folderului cu capturi si intoarce un dictionar cu o
    cheie pe categorie, iar valoarea este lista de constatari:

        {"suid": [...], "sudo": [...], "cron": [...]}

    Pentru a lipi calea unui fisier de folder, foloseste os.path.join.
    """
    dict_constatari={}
    try:
        dict_constatari["suid"] = suid_constatari(os.path.join(dosar, "suid.txt"))
        dict_constatari["sudo"] = sudo_constatari(os.path.join(dosar, "sudo.txt"))
        dict_constatari["cron"] = cron_constatari(os.path.join(dosar, "crontab.txt"))
    except FileNotFoundError:
        print("Fisierul nu a fost gasit")
    return dict_constatari


def utilizatori_implicati(raport):
    """Sarcina 7. Intoarce MULTIMEA utilizatorilor care apar in raport.

    Sunt utilizatorii din constatarile sudo REUNITI cu cei din cron.
    Reuniunea a doua multimi se face cu operatorul  |  si arunca dublurile.

    Primeste dictionarul intors de enumereaza.
    """
    user_list = {}
    user_sudo = set()
    user_cron = set()
    try:
        for i in raport["sudo"]:
            user_sudo.add(i["user"])
        for i in raport["cron"]:
            user_cron.add(i["user"])
        user_list = user_sudo | user_cron
    except FileNotFoundError:
        print("Fisierul nu a fost gasit")
    return user_list


# ---------------------------------------------------------------------------
#  PARTEA B - ce e nou fata de un sistem curat
# ---------------------------------------------------------------------------

def cai(fisier):
    """Sarcina 8. Intoarce MULTIMEA cailor dintr-un fisier.

    Foloseste citeste_linii, pe care ai scris-o deja la sarcina 1.
    O multime arunca singura dublurile, de aceea aici iese 13, nu 14.
    """
    paths_set = set(citeste_linii(fisier))
    return paths_set


def suid_noi(acum, baza):
    """Sarcina 9. Ce e in acum, dar nu si in baza.

    Amandoua sunt multimi de cai. Rezultatul este tot o multime: fisierele
    SUID aparute fata de sistemul curat.

    Se face cu UN SINGUR operator, nu cu doua bucle una in alta.
    """
    return acum - baza


def risc_pe_nume(multime_cai):
    """Sarcina 10. Fisa nume -> risc, ca DICTIONAR.

    Pentru fiecare cale din multimea primita, cheia este numele fisierului,
    iar valoarea este "mare" daca numele se afla in GTFO, altfel "normal".

    Se scrie pe un singur rand, cu dict comprehension.
    """
    return {nume(c): ("mare" if nume(c) in GTFO else "normal") for c in multime_cai}


def periculoase_noi(noi):
    """Sarcina 11. Lista cailor noi care sunt periculoase, sortata.

    Din multimea primita pastrezi doar caile al caror nume e in GTFO si le
    intorci ca lista, in ordine sortata.
    """
    cai_noi = noi
    cai_in_GTFO = []
    for i in cai_noi:
        if nume(i) in GTFO:
            cai_in_GTFO.append(i)
    return sorted(cai_in_GTFO)



# ===========================================================================
#
#   Sub randul urmator incepe programul care te verifica.
#   Nu e nevoie sa intelegi codul de mai jos si nu il modifica.
#
# ===========================================================================
#  


def main():
    p = argparse.ArgumentParser()
    p.add_argument("capturi")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    raport = enumereaza(a.capturi)
    if a.json:
        print(json.dumps(raport, indent=2, ensure_ascii=False))
        return
    for categorie, lista in raport.items():
        mari = [c for c in lista if c.get("risc") == "mare"]
        print("%s: %d gasite, %d cu risc mare" % (categorie, len(lista), len(mari)))
    useri = utilizatori_implicati(raport)
    print("utilizatori implicati:", ", ".join(sorted(useri)))
    with io.open("enum.json", "w", encoding="utf-8") as fis:
        json.dump(raport, fis, indent=2, ensure_ascii=False)
    print("Raport salvat in enum.json")


if __name__ == "__main__":
    main()
