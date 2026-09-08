# Zdroje a fact-check

Podľa tvojich pravidiel pre AI Tools obsah: hype môže byť v hooku, fakty musia ostať presné.
Toto je čiara medzi tým, čo je overené, a tým, čo je marketing projektu.

Stav k **8. 9. 2026**, zdroj: oficiálne README a docs repozitára `diegosouzapw/OmniRoute`.

---

## Overené — toto povedať môžeš

| Tvrdenie | Zdroj |
| --- | --- |
| Open-source, licencia MIT | README repozitára |
| Beží lokálne na `localhost:20128`, dashboard + `/v1` API | README, Quick Start |
| Inštalácia `npm install -g omniroute`, potom `omniroute` | README, Quick Start |
| Funguje bez API kľúča hneď po inštalácii (keyless free providery v `auto`) | README |
| OpenAI-kompatibilné API, plus Anthropic a Gemini rozhrania | README |
| Automatický fallback cez 4 vrstvy: predplatné → API → lacné → free | README |
| Kompresia tokenov (RTK + Caveman) | README, docs/compression |
| Podporuje Claude Code, Codex, Cursor, Cline, Kilo, Continue, Aider, Goose, OpenCode a ďalšie | docs/reference/CLI-TOOLS.md |
| Beží na npm, Dockeri, Electron desktope, ARM, Androide cez Termux, ako PWA | README |
| Kľúče šifrované lokálne AES-256-GCM, telemetria defaultne vypnutá | README |
| Vyžaduje Node.js `>=22.22.2 <23` alebo `>=24.0.0 <27` | README, Tech Stack |
| Claude Code potrebuje `ANTHROPIC_BASE_URL` **bez** `/v1` | docs/guides/CLAUDE-CODE-CONFIGURATION.md |
| Kiro AI ako free provider: free Claude, ~50 kreditov mesačne na účet | README, Quick Start |
| Docker image má default heap 1024 MB, na coding agentov treba viac | README, Docker sekcia |
| Rotácia na 400/401 cez `OMNIROUTE_ROTATE_ON_400=true` | docs/guides/TROUBLESHOOTING.md |

---

## Čísla projektu — cituj ich ako čísla projektu, nie ako svoje meranie

Toto sú údaje, ktoré o sebe uvádza samotný projekt. Sú konkrétne a doložené metodikou, ale **nie sú nezávisle overené** a projekt sám píše, že sa menia oboma smermi:

- **352 registrovaných providerov**, z toho **154 s `hasFree: true`** metadátami
- **~1,51 miliardy free tokenov mesačne** — vypočítané z 20 pool-ov s publikovaným kladným mesačným rozpočtom, deduplikované cez zdieľané pooly
- **až ~2,13 miliardy** v prvom mesiaci, keď sa započítajú signup kredity
- **455 katalogizovaných free-tier záznamov** v 40 opakujúcich sa pooloch
- **19 routing stratégií**
- **úspora tokenov 15–95 %** na vhodných workloadoch, priemer uvádzaný ~89 %
- **35 podporovaných CLI/agent nástrojov**

Ako to povedať vo videu správne:
> „Projekt uvádza vyše 350 providerov a zhruba jeden a pol miliardy free tokenov mesačne — je to ich vlastný výpočet, majú k tomu publikovanú metodiku a sami píšu, že sa to mesiac po mesiaci mení."

Ako to **nepovedať**:
> ~~„Máš jeden a pol miliardy tokenov zadarmo každý mesiac."~~ — to je ich najlepší scenár, nie tvoja garancia divákovi.

---

## Čo netvrdiť vôbec

- ❌ „Zadarmo navždy" — free tiery providerov sa rušia aj pridávajú.
- ❌ „Nahradí ti to platený Claude/ChatGPT" — free modely nie sú tie isté modely.
- ❌ „Je to bezpečné pre firemné dáta" — nie je, prompty idú cez cudzích providerov.
- ❌ Vlastné percentá úspor, ktoré si nezmeral.
- ❌ Prezentovať to ako svoj projekt alebo svoj objav. Autor je `diegosouzapw`, povedz to.
- ❌ „Nič sa neloguje" — OmniRoute netelemetruje, ale čo robia providery, za to neručíš.

---

## Vec, ktorú väčšina influencerov v tomto reelse zamlčí

Free tier = **tvoje prompty idú cez servery tretích strán**, a nie každá garantuje, že ich nepoužije na tréning. Katalóg projektu sám označuje 15 providerov ako rizikových z hľadiska podmienok, aby si sa vedel rozhodnúť.

Povedz to. Je to jedna veta, stojí ťa nulovú konverziu a robí presne ten rozdiel medzi „chalan čo recykluje AI novinky" a niekým, koho beriem vážne — čo je presne pozícia, ktorú si chceš držať.

---

## Ako si to overiť sám pred natáčaním

```bash
npm view omniroute version        # aktuálna verzia
node --version                    # tvoja verzia Node
```

Potom `omniroute` → `http://localhost:20128/dashboard/free-tiers` → screenshot živých kvót.
**Screenshot z vlastného dashboardu je najsilnejší proof, aký k tomuto videu vieš mať.** Silnejší než akékoľvek číslo z README.
