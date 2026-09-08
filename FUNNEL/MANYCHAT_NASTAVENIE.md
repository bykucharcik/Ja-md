# ManyChat — ako to naklikať

Cieľ: komentár pod reelom → automatická DM s návodom → kvalifikácia → CTA.
Čas na nastavenie: ~20 minút, robíš to raz a potom už len meníš keyword na každé video.

---

## Predpoklady

- Instagram **Professional účet** (Business alebo Creator) — @kuchar.ai
- Prepojený s Facebook stránkou
- ManyChat účet s pripojeným Instagramom (Settings → Instagram → Connect)
- V ManyChate zapnuté **Instagram → Comment Reply** povolenia

Free plán ManyChatu na toto stačí. Automation, ktorú potrebuješ, je v základe.

---

## Krok 1 — Nové Automation

**Automation → New Automation → Start from scratch**
Názov: `IG — OMNIROUTE — free AI coding`

---

## Krok 2 — Trigger

**Trigger → Instagram → User comments on your post or reel**

- **Post:** vyber konkrétny reel (nie „any post" — chceš vedieť, ktoré video generuje leady)
- **Keyword:** `ZADARMO`
- **Match type:** `contains` (nie exact — ľudia píšu preklepy a emoji)
- Pridaj varianty: `zadarmo`, `ZADARMO!`, `omniroute`, `AI`

⚠️ Nedávaj keyword, ktorý sa bežne vyskytuje v normálnych komentároch, inak ti bude automat strieľať na každého.

---

## Krok 3 — Verejná odpoveď na komentár

**Action → Reply to comment**

Text: `Poslal som ti to do správ 📩`

Zapni **randomizáciu odpovedí** (ManyChat: viac variantov v jednom bloku) — Instagram nemá rád, keď máš pod videom 200× rovnaký komentár. Pridaj aspoň 4 varianty:

- `Poslal som ti to do správ 📩`
- `Máš to v DM ✅`
- `Poslané, pozri si správy`
- `V DM to máš 👌`

---

## Krok 4 — Prvá DM (opt-in, BEZ linku)

**Action → Send Instagram Message**

Text zo súboru `MANYCHAT_DM_SEKVENCIA.md`, sekcia 2.

Pridaj **Quick reply tlačidlá:**
- `Áno, pošli` → pokračuje na Krok 5
- `Čo to je?` → vetva s vysvetlením, potom späť na Krok 5

Prečo bez linku: Instagram obmedzuje dosah správam s linkom od účtu, s ktorým používateľ ešte neinteragoval. Keď klikne na tlačidlo, interakcia existuje a link už prejde.

---

## Krok 5 — Druhá DM (dodanie návodu)

**Action → Send Instagram Message**

Text zo sekcie 3. Sem už ide link na návod aj oficiálne linky projektu.

**Tag:** `omniroute-lead` — takto si vieš neskôr vyfiltrovať všetkých, čo si vypýtali návod.

---

## Krok 6 — Delay + druhé CTA

**Action → Smart Delay → 90 minút**
→ **Send Instagram Message** — text zo sekcie 4 (varianta A alebo B).

Prečo 90 minút a nie hneď: keď pošleš ponuku v tej istej sekunde ako hodnotu, je jasné, že hodnota bola len návnada.

---

## Krok 7 — Follow-upy

**Smart Delay 24 hodín** → podmienka `Neodpísal` → správa zo sekcie 5.
**Smart Delay 4 dni** → podmienka `Neodpísal` → správa zo sekcie 6.

Podmienku nastav cez **Condition → Last Interaction** alebo cez tag, ktorý pridáš pri odpovedi.

---

## Krok 8 — Kvalifikácia (nepovinné, ale toto robí peniaze)

Do vetvy po CTA daj otázku s tlačidlami:

> Nech viem, čo ti sem posielať — máš rozbehnutý biznis/e-shop, alebo sa učíš pre seba?

- `Mám biznis` → tag `b2b-lead` → ďalšia otázka na obrat a najväčší manuálny žrút času → ponuka callu
- `Učím sa` → tag `b2c-lead` → waitlist na kurz

Toto je presne tvoj kvalifikačný postup: pain → fit → call.

---

## Krok 9 — Test pred publikovaním

1. **Preview** v ManyChate — prejdi celý flow.
2. Z **druhého Instagram účtu** napíš komentár s keywordom pod reel. Automat musí zabrať do pár sekúnd.
3. Over, že linky sú klikateľné a otvárajú sa v Instagram prehliadači (nie všetky doménky sa správajú rovnako).
4. Skontroluj text na mobile — dlhé správy sa v IG DM krátia na „viac".

---

## Čo sledovať po spustení

| Metrika | Kde | Čo znamená |
| --- | --- | --- |
| Počet triggerov | ManyChat → Automation stats | Koľko ľudí reálne komentovalo keyword |
| Open rate prvej DM | ManyChat | Pod 80 % = zlá prvá veta |
| Klik na návod | ManyChat link clicks | Pod 40 % = správa je dlhá alebo nedôveryhodná |
| Odpovede vlastnými slovami | ručne | Toto sú tvoje reálne leady |
| Konverzia na CTA2 | podľa linku | Sem patrí drvivá väčšina tvojej pozornosti |

---

## Bežné chyby

- **Keyword je príliš generický** → automat strieľa na náhodné komentáre.
- **Link v prvej správe** → nižší doručovací dosah.
- **Nikdy nevypneš automatiku** → človek napíše reálnu otázku a dostane robotickú odpoveď. Zabije to dôveru okamžite.
- **Rovnaký keyword na všetkých videách** → nevieš, ktoré video ti reálne robí leady.
- **Žiadny follow-up** → 60–70 % ľudí návod otvorí, nedokončí a už sa nevráti.
