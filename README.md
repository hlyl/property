# Italian Property Tracker

Et Python-baseret system til at spore og gennemgå italienske ejendomme fra immobiliare.it.

## Oversigt

Dette projekt giver et komplet system til:
- Automatisk scraping af ejendomsdata fra immobiliare.it
- Lagring af ejendomme i en SQLite database
- Interaktiv web-grænseflade til gennemgang af ejendomme
- Kortvisning med clickbare markers
- Automatisk oversættelse fra italiensk til dansk
- Beregning af afstande til kyst og vand
- POI (Points of Interest) tælling omkring ejendomme

## Funktioner

### 🏠 Ejendomsscraping
- Automatisk indsamling af ejendomsdata fra immobiliare.it
- Håndtering af prisfald og nye annoncer
- Sporring af hvornår ejendomme først blev observeret
- Markering af solgte ejendomme

### 🗺️ Interaktiv kortvisning
- Folium-baseret kort med clickbare ejendomsmarkører
- Farvekodning baseret på pris:
  - 🟢 Grøn: <€50k
  - 🔵 Blå: €50-75k
  - 🟠 Orange: €75-100k
  - 🔴 Rød: >€100k
- Clickbare links direkte til ejendomsannoncen
- Auto-selektion af ejendomme ved klik på marker

### 📊 Review-system
- Tre-status review system:
  - **To Review** (🤔 Perhaps): Skal gennemgås
  - **Interested** (✅ Yes): Interessant ejendom
  - **Rejected** (❌ No): Afvist ejendom
- Hurtige review-knapper på kortside
- Filtrering efter review-status

### 🌍 Geospatial funktioner
- Beregning af afstand til nærmeste kystlinje
- Beregning af afstand til nærmeste vandområde
- Lazy-loading af geodata for optimal ydeevne
- UTM-projektion for præcise afstandsberegninger

### 🔍 POI-tælling
- Tælling af nærliggende Points of Interest:
  - Barer og cafeer
  - Butikker og supermarkeder
  - Bagerier
  - Restauranter
- To implementationer:
  - **Overpass API** (gratis, anbefalet)
  - **Google Places API** (koster penge, fallback)

### 🌐 Oversættelse
- Automatisk oversættelse af beskrivelser fra italiensk til dansk
- To implementationer:
  - **deep-translator** (gratis, anbefalet)
  - **googletrans** (udfaset, ustabil)

## Installation

### Forudsætninger
- Python 3.12 eller nyere
- uv (Python package installer)

### Opsætning

1. Klon repository:
```bash
git clone <repository-url>
cd property
```

2. Installer dependencies med uv:
```bash
uv sync
```

3. Migrer database (tilføj manglende kolonner):
```bash
uv run python utils/migrate_add_province_city.py --prod
```

4. Konfigurer miljøvariabler (valgfrit):
```bash
cp .env.example .env
# Rediger .env efter behov
```

## Konfiguration

### Miljøvariabler (.env)

```bash
# Feature Flags (Omkostningsreduktion)
USE_GOOGLE_PLACES=false      # true = Google Places API (koster $)
USE_GOOGLE_TRANSLATE=false   # true = googletrans (udfaset)

# Database Configuration
DB_SELECTOR=production       # production, test
DATABASE_PATH=database.db
TEST_DATABASE_PATH=test.db

# Application Settings
PRODUCTION=true
LOG_FILE=logging.txt
LOG_LEVEL=DEBUG

# POI Search Configuration
POI_SEARCH_RADIUS=2000       # Søgeradius i meter
POI_SEARCH_PROVIDER=overpass # overpass (gratis) eller google

# Translation Configuration
TRANSLATION_SOURCE_LANG=it   # Kildesprog
TRANSLATION_TARGET_LANG=da   # Målsprog
```

### Google API Keys (valgfrit)
Hvis du vil bruge Google-tjenester:
```bash
GOOGLE_API_KEY=din_api_nøgle_her
USE_GOOGLE_PLACES=true
USE_GOOGLE_TRANSLATE=true
```

**Bemærk:** Google-tjenester koster penge. De gratis alternativer anbefales.

## Brug

### 1. Scrape ejendomme

Kør main.py for at scrape nye ejendomme:

```bash
uv run python main.py
```

Dette vil:
- Hente nye ejendomme fra immobiliare.it
- Gemme dem i databasen
- Oversætte beskrivelser til dansk
- Beregne afstande til kyst og vand
- Tælle nærliggende POI'er (hvis aktiveret)

### 2. Start web-interface

Start Streamlit-appen:

```bash
uv run streamlit run ui/app.py
```

Åbn browser på `http://localhost:8501`

### 3. Se ejendomme på kort

Naviger til **Hyperlink** siden:
- Se alle ejendomme på et interaktivt kort
- Klik på markers for at se detaljer
- Klik "Open Property" for at åbne ejendomsannoncen
- Brug review-knapperne til at klassificere ejendomme

### 4. Tjek database-status

Kør check_db.py for at se review-statistikker:

```bash
uv run python check_db.py
```

## Projektstruktur

```
property/
├── property_tracker/          # Hovedpakke
│   ├── config/               # Konfiguration
│   │   └── settings.py       # Miljøvariabler og konstanter
│   ├── models/               # Database-modeller
│   │   └── property.py       # Property SQLModel
│   ├── services/             # Forretningslogik
│   │   ├── poi.py           # POI-tælling (Overpass/Google)
│   │   ├── review.py        # Review-system
│   │   └── translation.py   # Oversættelse (deep-translator/googletrans)
│   └── utils/               # Hjælpefunktioner
│       └── distance.py      # Afstandsberegninger
├── ui/                       # Streamlit web-interface
│   ├── app.py               # Hovedside
│   ├── components/          # Genbrugelige komponenter
│   │   └── review_buttons.py
│   └── pages/               # Undersider
│       └── 03_Hyperlink.py  # Kortvisning med review
├── data/                     # Geodata
│   └── boundaries/
│       ├── ITA_coastline.json    # Italiensk kystlinje
│       └── ITA_water_lines.json  # Italienske vandområder
├── tests/                    # Test suite
│   ├── unit/                # Enhedstests
│   └── integration/         # Integrationstests
├── utils/                    # Utility scripts
│   └── migrate_add_province_city.py  # Database-migration
├── main.py                   # Scraping-script
├── dao.py                    # Database access object
├── check_db.py              # Database-status script
└── pyproject.toml           # Projekt-metadata og dependencies

```

## Udvikling

### Kørsel af tests

Kør hele test suite:
```bash
uv run pytest -v
```

Kør kun enhedstests:
```bash
uv run pytest tests/unit -v
```

Kør med coverage:
```bash
uv run pytest --cov=property_tracker --cov-report=html
```

### Code Quality

Kør linting:
```bash
uv run ruff check .
```

Kør formatting:
```bash
uv run ruff format .
```

Kør type checking:
```bash
uv run mypy dao.py calcdist.py property_tracker/
```

### Pre-commit checks

Før commit, kør:
```bash
uv run ruff format .
uv run ruff check . --fix
uv run mypy dao.py calcdist.py
uv run pytest
```

## CI/CD

GitHub Actions kører automatisk:
- ✅ Ruff linting
- ✅ Ruff formatting check
- ✅ MyPy type checking
- ✅ Pytest test suite

Se `.github/workflows/` for konfiguration.

## Database Schema

### Property Table

Hovedtabel med ejendomsdata:

| Kolonne | Type | Beskrivelse |
|---------|------|-------------|
| id | BigInteger | Primær nøgle (immobiliare.it ID) |
| region | String | Region/område |
| province | String | Provins |
| city | String | By |
| caption | String | Overskrift |
| category | String | Kategori (fx "Residenziale") |
| description | Text | Italiensk beskrivelse |
| description_dk | Text | Dansk oversættelse |
| price | Integer | Pris i EUR |
| price_m | Integer | Pris per m² |
| price_drop | String | Original pris hvis nedsat |
| rooms | Integer | Antal værelser |
| bathrooms | Integer | Antal badeværelser |
| surface | String | Areal (fx "100 m²") |
| floor | String | Etage |
| latitude | Float | Breddegrad |
| longitude | Float | Længdegrad |
| dist_coast | Float | Afstand til kyst (km) |
| dist_water | Float | Afstand til vand (km) |
| pub_count | Integer | Antal barer/cafeer inden for 2km |
| shopping_count | Integer | Antal butikker inden for 2km |
| baker_count | Integer | Antal bagerier inden for 2km |
| food_count | Integer | Antal restauranter inden for 2km |
| review_status | String | Review-status (To Review/Interested/Rejected) |
| observed | String | Dato først observeret |
| sold | Integer | 1 hvis solgt, 0 ellers |

## Performance

### Lazy Loading
Geodata (8.7MB) loaderes lazy for at undgå import-overhead:
- Kystlinjedata: ~714KB (loades ved første brug)
- Vandområdedata: ~8MB (loades ved første brug)

### Caching
- Distance calculator bruger singleton pattern
- Spatial tree indexing for hurtig POI-søgning
- Session state i Streamlit for UI-performance

## Fejlfinding

### Common Issues

**Problem:** Tests fejler med "json_mock_file.json not found"
- **Løsning:** Dette er forventet - legacy tests skippes automatisk

**Problem:** Overpass API rate limiting
- **Løsning:** POI-tælling er disabled som standard. Aktiver kun når nødvendigt.

**Problem:** Import errors
- **Løsning:** Kør `uv sync` for at installere alle dependencies

**Problem:** Database fejl
- **Løsning:** Kør migration: `uv run python utils/migrate_add_province_city.py --prod`

## Bidrag

1. Fork repository
2. Opret feature branch: `git checkout -b feature/mit-feature`
3. Commit ændringer: `git commit -am 'Tilføj nyt feature'`
4. Push til branch: `git push origin feature/mit-feature`
5. Opret Pull Request

## Licens

[Indsæt licensinformation her]

## Kontakt

[Indsæt kontaktinformation her]

## Acknowledgments

- immobiliare.it for ejendomsdata
- OpenStreetMap for geodata via Overpass API
- Alle open-source libraries brugt i dette projekt
