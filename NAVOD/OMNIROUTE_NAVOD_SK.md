# Ako kódiť s AI zadarmo cez OmniRoute

Presný postup, ktorý ti rozbehne Claude Code, Cursor, Codex alebo Cline na free modeloch — bez platenej karty.
Čistý čas: ~10 minút.

---

## Čo to vlastne je

OmniRoute je **lokálna brána** medzi tvojím AI nástrojom a poskytovateľmi modelov.

Bežne to funguje takto: Claude Code → Anthropic → tvoja karta.
S OmniRoute to funguje takto: Claude Code → OmniRoute (beží u teba na počítači) → 350+ poskytovateľov, z toho vyše 90 s free tierom.

Tri veci, ktoré ti to reálne dá:

1. **Jeden endpoint namiesto desiatich kľúčov.** Všetky nástroje mieria na jednu adresu.
2. **Automatický fallback.** Keď ti jeden provider vyhodí rate limit, request ide na ďalší. Nepadneš uprostred práce.
3. **Kompresia tokenov.** Skracuje prompty a výstupy nástrojov, takže na free limity narazíš neskôr.

Je to open-source (MIT), beží u teba lokálne, kľúče sa šifrujú na disku a telemetria je defaultne vypnutá.

> **Buď v obraze:** free tier neznamená, že modely bežia zadarmo z dobroty srdca. Znamená to, že OmniRoute vie využiť free kvóty desiatok providerov naraz. Kvóty sa menia — dnes ti provider dá milión tokenov, o mesiac free tier zruší. Preto je v dashboarde stránka so živým stavom.

---

## Čo potrebuješ pred štartom

- **Node.js 24.x LTS** (podporované je `22.22.2+` alebo `24.x`–`26.x`).
  Over si to: `node --version`
  Ak máš staršiu verziu, dashboard ti spadne na bielu stránku — je to najčastejší problém pri inštalácii.
- Terminál. Na Windowse odporúčam PowerShell alebo WSL.
- Voľný port `20128`.

---

## Krok 1 — Inštalácia

```bash
npm install -g omniroute
omniroute
```

Server nabehne a dashboard máš na **http://localhost:20128**, API na **http://localhost:20128/v1**.

Ak ti npm počas inštalácie vypíše kopu žltých warningov (`ERESOLVE`, `peer`, `deprecated`) — **ignoruj ich**. Sú to zastarané peer-dependency rozsahy v cudzích balíkoch. Inštalácia prešla, ak vidíš `added N packages`.

---

## Krok 2 — Over, že to žije (bez akéhokoľvek kľúča)

Toto je časť, ktorá ľudí prekvapí: čerstvá inštalácia odpovedá aj bez registrácie a bez API kľúča, lebo pár keyless free providerov je predpojených v `auto` combe.

```bash
curl http://localhost:20128/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Ahoj, funguješ?"}]}'
```

Keď ti príde odpoveď, brána beží.

---

## Krok 3 — Pripoj si free providera

Bez kľúča ti bežia len tie najzákladnejšie free modely. Na reálne kódenie chceš pripojiť aspoň jedného poriadneho.

Dashboard → **Providers** → vyber si a pripoj:

| Provider | Čo z toho máš |
| --- | --- |
| **Kiro AI** | Free Claude modely, ~50 kreditov mesačne na účet |
| **OpenCode Free** | Bez prihlásenia, bez tokenového stropu |
| **Cerebras** | 1M tokenov denne, veľmi rýchle |
| **Z.AI GLM** | GLM-4.7 / 4.5-Flash zadarmo |
| **Qoder AI** | Qwen3-Max, Kimi-K2 |
| **NVIDIA NIM** | ~40 requestov za minútu zadarmo |
| **Cloudflare AI** | 50+ modelov, 10K neurónov denne |

Odporúčanie: pripoj **aspoň tri**. V tom je celý point — keď prvý vyčerpáš, fallback ťa prepne na druhý a ty si to ani nevšimneš.

Živý stav kvót (koľko ti ešte zostáva) nájdeš na `http://localhost:20128/dashboard/free-tiers`.

---

## Krok 4 — Vytiahni si API kľúč

Dashboard → **Endpoints** → skopíruj kľúč.

Vyzerá takto: `sk-xxxxxxxxxxxxxxxx-xxxxxxxxx`

Tento kľúč je **tvoj lokálny** kľúč do OmniRoute, nie kľúč od providera. Nikam ho neposielaj.

---

## Krok 5 — Napoj svoj nástroj

### Claude Code (najrýchlejšia cesta)

```bash
omniroute setup-claude
```

Tento príkaz si sám načíta zoznam živých modelov a zapíše konfig. Potom stačí:

```bash
omniroute run claude
```

alebo `omniroute launch` — spustí Claude Code s injektnutými premennými a nič ti neprepíše.

**Ručne**, ak to chceš mať pod kontrolou — vytvor `~/.claude/settings.json`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:20128",
    "ANTHROPIC_AUTH_TOKEN": "sk-tvoj-omniroute-kluc",
    "CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY": "1"
  }
}
```

Dva detaily, na ktorých ľudia zamrznú:

- Pri `ANTHROPIC_BASE_URL` **nedávaj `/v1` na koniec.** Claude Code si `/v1/messages` dolepí sám. Ostatné nástroje `/v1` naopak chcú.
- Premenné sa čítajú **iba pri štarte**. Po zmene musíš Claude Code reštartovať.

Test: `claude "povedz ahoj"`

### Codex CLI

```bash
omniroute setup-codex
```

Alebo ručne do `~/.codex/config.toml`:

```toml
model_provider = "omniroute"

[model_providers.omniroute]
name                 = "OmniRoute"
base_url             = "http://localhost:20128/v1"
env_key              = "OMNIROUTE_API_KEY"
requires_openai_auth = false
```

a `export OMNIROUTE_API_KEY="sk-tvoj-omniroute-kluc"`

### Cursor, Cline, Kilo, Continue, Aider, Goose, OpenCode

Rovnaká logika, každý má svoj setup príkaz:

```bash
omniroute setup-cursor      omniroute setup-cline       omniroute setup-kilo
omniroute setup-continue    omniroute setup-opencode    omniroute setup-aider
omniroute setup-goose       omniroute setup-qwen        omniroute setup-roo
```

Alebo cez dashboard: **CLI Code** → klikni na nástroj → **Apply Config**.

### Hocijaký iný OpenAI-kompatibilný nástroj

```
Base URL: http://localhost:20128/v1
API Key:  sk-tvoj-omniroute-kluc
Model:    auto
```

### VS Code / Copilot Chat

Nainštaluj rozšírenie **OmniCopilot**, nasmeruj ho na `localhost:20128` a modely ti naskočia priamo do natívneho model pickera v Copilot Chate.

---

## Krok 6 — Finálna kontrola

```bash
curl http://localhost:20128/v1/models -H "Authorization: Bearer sk-tvoj-omniroute-kluc"
```

Vypíše ti to zoznam modelov, ktoré máš cez pripojených providerov k dispozícii. Ak tam sú, si hotový.

---

## Ako si vybrať model

- **`auto`** — nechaj to na router. Sám vyberá podľa dostupnosti, ceny a zdravia providera a padá cez 4 vrstvy: predplatné → API kľúč → lacné → free.
- **`auto/fast`** — keď ti ide o rýchlosť.
- **`provider/model`** (napr. `glm/glm-5.2`) — keď presne vieš, čo chceš.

Ak `auto` vyberie iného providera, než si čakal, **nie je to chyba** — to je presne jeho práca.

---

## Keď niečo nejde

| Vidím toto | Čo s tým |
| --- | --- |
| Biela stránka / crash pri logine | Zlá verzia Node.js. `nvm install 24 && nvm use 24`, potom `npm install -g omniroute` znova. |
| „Can't connect" | OmniRoute nebeží. Spusti `omniroute`. |
| `429 Too Many Requests` | Free kvóta providera je vyčerpaná. Počkaj minútu, alebo pripoj ďalšieho providera. |
| `401 Unauthorized` | Zlý kľúč. Skopíruj ho znova z Dashboard → Endpoints. |
| `502` | Provider je dole. Použi `model: "auto"` a prepne ťa. |
| Náhodné 429/400/401 pri agentoch | Zapni rotáciu (nižšie). |
| `Cannot find module 'better-sqlite3'` | npm v11 preskočil build. `npm approve-scripts better-sqlite3 && npm install` |
| Antivírus karanténuje `README.md` | Známy false positive Avast/AVG. |

**Rotácia pri agentoch** — najsilnejší jeden prepínač, ak ti padajú automatizácie na free provideroch. Nastav v prostredí, kde beží OmniRoute, a reštartuj:

```bash
export OMNIROUTE_ROTATE_ON_400=true
export OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=4
export OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=5000
```

Prvý z nich spraví z tvrdej chyby tichý retry na zdravého providera.

---

## Kde beží ešte

| Kde | Ako |
| --- | --- |
| npm (globálne) | `npm install -g omniroute` |
| Docker | `docker run -d --name omniroute -p 127.0.0.1:20128:20128 -v omniroute-data:/app/data diegosouzapw/omniroute:latest` |
| Android / Termux | `pkg install nodejs && npx -y omniroute` |
| Raspberry Pi, ARM | natívne `arm64` |
| Desktop appka | Electron build, Windows / macOS / Linux |

Pri Dockeri pozor na jednu vec: image má default heap `1024 MB`, čo stačí na dashboard a chat, ale **nie na coding agentov**. Na jedného agenta daj `-e OMNIROUTE_MEMORY_MB=8192 --memory=10g`, inak ti proces spadne na `FATAL ERROR` pri dlhých kontextoch.

---

## Bezpečnosť — prečítaj si to, aj keď preskakuješ

Čo je v poriadku:
- Kľúče sa šifrujú lokálne (AES-256-GCM), prompty idú priamo na vybraného providera, telemetria je defaultne vypnutá.

Čo si musíš uvedomiť:
- **Free tier znamená, že tvoje prompty idú cez cudzie servery.** Free providerov je vyše deväťdesiat a každý má vlastné podmienky — nie všetci garantujú, že tvoje dáta nepoužijú na tréning.
- Na hobby projekty, učenie a vlastné veci: super.
- **Firemný kód, klientske dáta, osobné údaje, prístupy — cez free tier neposielaj.** Na to si nechaj platený model alebo lokálny.
- Samotný katalóg OmniRoute označuje pätnásť providerov ako rizikových z hľadiska podmienok, aby si sa vedel rozhodnúť. Pozri sa na to skôr, než tam pustíš prácu pre klienta.

---

## Odkazy

- Web: https://omniroute.online/
- GitHub: https://github.com/diegosouzapw/OmniRoute
- Setup guide: https://github.com/diegosouzapw/OmniRoute/blob/main/docs/guides/SETUP_GUIDE.md
- Claude Code konfigurácia: https://github.com/diegosouzapw/OmniRoute/blob/main/docs/guides/CLAUDE-CODE-CONFIGURATION.md
- Free tiers a metodika výpočtu: https://github.com/diegosouzapw/OmniRoute/blob/main/docs/reference/FREE_TIERS.md
- Riešenie problémov: https://github.com/diegosouzapw/OmniRoute/blob/main/docs/guides/TROUBLESHOOTING.md

---

*Návod píšem podľa oficiálnej dokumentácie projektu k septembru 2026. Free tiery sa menia oboma smermi — aktuálny stav si vždy over na `/dashboard/free-tiers`.*
