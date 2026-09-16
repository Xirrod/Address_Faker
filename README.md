<div align="center">

# 🌍 Random Person Data API

### *The most over-engineered fake-person generator you'll ever need.*

A **FastAPI** service that serves random fake-but-format-valid person records by country.
Powered by **OpenStreetMap** real street data + **libphonenumber**-validated phone formats.

<br>

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![OpenStreetMap](https://img.shields.io/badge/Data-OpenStreetMap-7EB55E?style=for-the-badge&logo=openstreetmap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=opensourceinitiative&logoColor=white)

<br>

![Records](https://img.shields.io/badge/Records-1.5M+-orange?style=flat-square)
![Real OSM Records](https://img.shields.io/badge/Real_OSM_Addresses-10%2C754-brightgreen?style=flat-square)
![Countries](https://img.shields.io/badge/Countries-35-red?style=flat-square)
![Phone Validity](https://img.shields.io/badge/Phone_Validity-99.8%25-success?style=flat-square)
![Address Validity](https://img.shields.io/badge/Address_Validity-86.9%25-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen?style=flat-square)

<br>

> 💬 **Dev / Maintainer**: reach out on Telegram  
> [![Telegram](https://img.shields.io/badge/@xirrod-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/xirrod)

</div>

<br>

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [📊 Stats](#-stats)
- [🚀 Quick Start](#-quick-start)
- [📡 API Endpoints](#-api-endpoints)
- [🌍 Sample Records Per Country](#-sample-records-per-country)
- [🔄 Round-Robin Serving Strategy](#-round-robin-serving-strategy)
- [💾 Data Sources](#-data-sources)
- [📞 Phone Number Validation](#-phone-number-validation)
- [🏗️ Project Structure](#-project-structure)
- [⚙️ Configuration](#-configuration)
- [🧪 Validation Reports](#-validation-reports)
- [🐳 Deployment](#-deployment)
- [🤝 Contributing](#-contributing)
- [📞 Contact](#-contact)
- [📄 License](#-license)

---

## ✨ Features

<table>
<tr>
<td width="50%" valign="top">

### 🎯 Core capabilities
- 🌍 **35 countries** in the underlying dataset
- 🔒 **7-country allowlist** for the live API (Australia, India, France, UK, Canada, USA, Germany)
- 📞 **99.8% valid phone numbers** (verified with `phonenumbers` library, the same one Android/WhatsApp use)
- 📍 **10,754 REAL OSM addresses** — house number AND street pulled directly from OpenStreetMap via the Overpass API
- 🛣️ **41,679 real street names** cached from OpenStreetMap
- 🎭 **Localized names per country** (German `de_DE`, French `fr_FR`, Italian `it_IT`, Hindi `en_IN`, etc.)
- 🔄 **Round-robin serving** between V1 (synthetic + real streets) and V2 (real OSM addresses)

</td>
<td width="50%" valign="top">

### ⚡ Engineering features
- 🚀 **FastAPI + Uvicorn** — sub-50ms response time
- 🧵 **Thread-safe** pool management with `threading.Lock`
- 🔁 **Auto-rotate** — same address never returned twice until pool is exhausted
- 🌐 **Remote URL support** — point `REMOTE_URL` to your GitHub raw file
- 🌏 **Country aliases** — `/country=uk` resolves to "United Kingdom", `/country=us` to "USA", etc.
- 💾 **Lazy-loading** — V1 records for a country are only loaded on first request
- 🛡️ **404 with allowlist notice** for unsupported countries
- 🩺 **Healthcheck endpoint** at `/healthz`

</td>
</tr>
</table>

---

## 📊 Stats

<div align="center">

| Stat | Value |
|:---|:---|
| 📦 Total V1 records (synthetic + real streets) | **1,499,987** |
| 📍 Total V2 records (real OSM addresses) | **10,754** |
| 🛣️ Cached real street names | **41,679** |
| 🌍 Countries in V1 dataset | **35** |
| 🔒 Countries served by API | **7** |
| 📞 Phone format validity | **99.8%** |
| 📮 Address validity (Nominatim) | **86.9%** |
| 💾 Total dataset size | **~185 MB** |

</div>

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Xirrod/Address_Faker
cd Address_Faker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the API
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Or run as a Python script directly:

```bash
python main.py
```

Then open [`http://localhost:8000`](http://localhost:8000) in your browser 🎉

---

## 📡 API Endpoints

### `GET /country={country_name}`

Returns one random person record for the given country.  
Round-robins between V1 (synthetic) and V2 (real OSM address) per request.

```http
GET /country=USA
GET /country=Australia
GET /country=India
GET /country=Germany
GET /country=France
GET /country=UK          # alias for "United Kingdom"
GET /country=Canada
GET /country=us          # alias for "USA"
GET /country=deutschland # alias for "Germany"
```

**Response:**
```json
{
  "country": "USA",
  "full_name": "Angela Marquez",
  "address": "501 29th Avenue South, Seattle, USA",
  "phone": "(430) 398-7972",
  "postal_code": "34413-1692",
  "email": "angela_marquez2165@gmx.net",
  "source": "v2_real_osm"
}
```

The `source` field tells you where the record came from:
- `"v1_synthetic"` — real OSM street name + random house # (from `all_data.txt`)
- `"v2_real_osm"` — REAL OSM address, both house # and street from OpenStreetMap

---

### `GET /` — Service info
```bash
curl http://localhost:8000/
```

### `GET /countries` — Pool status per country
Returns live stats: V2 records remaining, V1 records remaining, next source, served counts.
```bash
curl http://localhost:8000/countries
```

### `GET /random?country=USA` — Random from any (or specific) country
```bash
curl http://localhost:8000/random           # random country from the allowlist
curl http://localhost:8000/random?country=Germany
```

### `GET /healthz` — Liveness probe
```bash
curl http://localhost:8000/healthz
```

---

## 🌍 Sample Records Per Country

One sample record from `data/all_data.txt` for each of the 35 countries in the dataset:

| Country | Full Name | Address | Phone | Postal | Email |
|:---|:---|:---|:---|:---|:---|
| 🇦🇺 Australia | Howard Walker | 72624 Brookes Street Unit B, Toowoomba, Western Australia, Australia | 0434 667 603 | 7852 | howard.walker6998@gmx.net |
| 🇦🇹 Austria | Boris Hofbauer | 89302 Peregrinstraße Suite 200, Wiener Neustadt, Salzburg, Austria | 06689744933 | 9569 | boris_hofbauer831@laposte.net |
| 🇧🇪 Belgium | Leona Vereecke | 52810 Vliegenstraat Apt 6, Antwerp, Wallonia, Belgium | 0499466054 | 4313 | leona.vereecke7457@sky.com |
| 🇧🇬 Bulgaria | Glenn Carter | 71344 Chestnut St Apt 3, Dobrich, Dobrich, Bulgaria | 989391765 | 1362 | glenn.carter8381@seznam.cz |
| 🇨🇦 Canada | Kristy Henderson | 24542 9 Avenue SW 1st Floor, Surrey, Northwest Territories, Canada | (514) 214-7793 | O2P 3A3 | kristy_henderson6953@free.fr |
| 🇭🇷 Croatia | Zlatko Muzina | 76297 Ulica Ante Starcevica Unit D, Karlovac, Brod-Posavina, Croatia | 919469288 | 27957 | zlatko-muzina229@mail.com |
| 🇨🇾 Cyprus | Alan Parker | 10528 Archiepiskopou Leontiou 2nd Floor, Nicosia, Nicosia, Cyprus | 99121456 | 4462 | alan-parker8841@telefonica.net |
| 🇨🇿 Czech Republic | Tomas Kopecky | 33178 Lumirova Apt 3, Hradec Králové, Vysočina, Czech Republic | 704291277 | 517 06 | tomas.kopecky2170@vp.pl |
| 🇩🇰 Denmark | Agnete Nielsen | 1561 Kong Eriks Vej Suite 102, Kolding, Central Denmark, Denmark | 23204787 | 4613 | agnete.nielsen8097@btinternet.com |
| 🇪🇪 Estonia | Sergei Kool | 55394 Lembitu Studio, Kohtla-Järve, Jõgeva, Estonia | 56949604 | 80154 | sergei-kool8103@outlook.es |
| 🇫🇮 Finland | Tapani Lehtinen | 25163 Tallberginkatu Apt 3, Helsinki, Central Finland, Finland | 0507036836 | 35035 | tapani.lehtinen3689@orange.es |
| 🇫🇷 France | Noel Marques | 1696 Rue Parmentier #4, Toulon, Pays de la Loire, France | 0632668451 | 12088 | noel_marques2017@volny.cz |
| 🇩🇪 Germany | Corinna Tintzmann | 48919 Pulsnitzer Straße Apt 5, Wiesbaden, Berlin, Germany | 015757573561 | 89811 | corinna_tintzmann153@ymail.com |
| 🇬🇷 Greece | Tara Lucero | 62130 Barbara St 4th Floor, Chania, Crete, Greece | 6904584814 | 847 54 | tara_lucero1174@hotmail.com |
| 🇭🇺 Hungary | Peter Sandor | 15996 Londoni korut Apt 7, Budapest, Komárom, Hungary | 706206744 | 4303 | peter-sandor2298@outlook.es |
| 🇮🇸 Iceland | Dana Villarreal | 67473 Hofsvallagata Studio, Garðabær, Northern Region, Iceland | 6251614 | 698 | dana_villarreal@gmail.com |
| 🇮🇳 India | Yoshita Sarraf | 71621 D' Souza Road Unit A, Tiruvannamalai, Haryana, India | 8306215190 | 552696 | yoshita.sarraf@alice.it |
| 🇮🇪 Ireland | Lawrence Ashton | 25348 Rathmore Road, Cork, Leinster, Ireland | 0898593037 | D08 X1F2 | lawrence.ashton@outlook.com |
| 🇮🇹 Italy | Stefania Soffici | 51507 Via della Consolata, Rimini, Marche, Italy | 3415324151 | 81848 | stefania.soffici@libero.it |
| 🇱🇻 Latvia | Julija Lukstins | 1457 Tomsona iela 8th Floor, Rēzekne, Jēkabpils, Latvia | 28018280 | 1850 | julija.lukstins@inbox.lv |
| 🇱🇹 Lithuania | Reda Adams | 26191 A. Fromo-Guzucio g. Loft 2, Marijampolė, Šiauliai, Lithuania | 64121100 | 5241 | reda_adams@yahoo.com |
| 🇱🇺 Luxembourg | Anastasie Descamps | 38123 Rue Ditzenheck #8, Differdange, Capellen, Luxembourg | 678847033 | 3443 | anastasie.descamps@gmail.com |
| 🇲🇹 Malta | Anna Roy | 13737 Triq l-Omnibus, Żabbar, St. Paul's Bay, Malta | 79240785 | ZZ 2C019 | anna.roy@gmail.com |
| 🇳🇱 Netherlands | Lola Honing | 86192 Scheepmakersstraat #9, Utrecht, Groningen, Netherlands | 0623336428 | 6708 IG | lola.honing@kpn.nl |
| 🇳🇴 Norway | Ruth Moen | 80508 Ribbunggata #7, Bergen, Vestfold, Norway | 91147845 | 3905 | ruth.moen@telenor.no |
| 🇵🇱 Poland | Konrad Bobel | 89710 Orlat Lwowskich #4, Olsztyn, Silesian, Poland | 607100267 | 54-828 | konrad.bobel@wp.pl |
| 🇵🇹 Portugal | Constanca Assuncao | 95321 Campo das Hortas Unit F, Castelo Branco, Leiria, Portugal | 914155639 | 1823-616 | constanca.assuncao@sapo.pt |
| 🇷🇴 Romania | Casandra Clark | 20916 Strada Petofi Sandor Apt 1, Arad, Constanța, Romania | 0759473129 | 234456 | casandra.clark@gmail.com |
| 🇸🇰 Slovakia | Olga Visnovska | 7888 Jana Kovalika Apt 9, Banská Bystrica, Prešov, Slovakia | 953870289 | 95309 | olga.visnovska@centrum.sk |
| 🇸🇮 Slovenia | Ljudmila Tavcar | 67423 Hocka ulica Apt 3, Ptuj, Central Slovenia, Slovenia | 51491165 | 8726 | ljudmila.tavcar@siol.net |
| 🇪🇸 Spain | Bienvenida Figuerola | 83001 Calle de Arias Apt 7, Murcia, Extremadura, Spain | 668027772 | 14566 | bienvenida.figueroa@gmail.com |
| 🇸🇪 Sweden | Therese Ryden | 49248 Banersgatan Unit F, Umeå, Gävleborg, Sweden | 0723019353 | 544 22 | therese.ryden@telia.com |
| 🇨🇭 Switzerland | Marcia Fankhauser | 50010 Seelandweg Unit C, Lausanne, Valais, Switzerland | 0798283833 | 5363 | marcia.fankhauser@bluewin.ch |
| 🇬🇧 United Kingdom | Philip Joyce | 77248 Snow Hill Queensway Apt 10, Bradford, England, United Kingdom | 07491823303 | HX4 3MW | philip.joyce@btinternet.com |
| 🇺🇸 USA | Monica Beasley | 76219 Fairview Place North Studio C, Plano, Michigan, USA | (947) 498-4720 | 10820-0996 | monica.beasley@gmail.com |

> 💡 The live API only serves **7** of these countries (Australia, India, France, UK, Canada, USA, Germany). The full 35-country dataset lives in `data/all_data.txt` for those who want to extend the allowlist.

---

## 🔄 Round-Robin Serving Strategy

Each request to `/country={country_name}` alternates between two data sources:

```
Request 1  →  v1 (all_data.txt — synthetic, real streets + random house #)
Request 2  →  v2 (v2_real_addresses.txt — REAL OSM address)
Request 3  →  v1
Request 4  →  v2
...
```

When the next-up pool is exhausted, we silently fall through to the other pool. When both are empty, we re-shuffle and restart the rotation cycle.

### Live demo (10 consecutive calls to `/country=USA`)

```
req  1: source=v1_synthetic    phone=(533) 954-1372   addr=51455 Lorraine Avenue Suite 102, Lansing, Tennessee, USA
req  2: source=v2_real_osm     phone=(770) 651-1067   addr=1231 Race Street, Philadelphia, USA
req  3: source=v1_synthetic    phone=(810) 264-7465   addr=46212 Gulf Freeway Frontage Road Apt 3, Elizabeth, Hawaii, USA
req  4: source=v2_real_osm     phone=(540) 669-9401   addr=1700 Benjamin Franklin Parkway, Philadelphia, USA
req  5: source=v1_synthetic    phone=(848) 597-4740   addr=54738 Anthony Street 8th Floor, Huntington, Ohio, USA
req  6: source=v2_real_osm     phone=(281) 352-9350   addr=101 West Santa Clara Street, San Jose, USA
req  7: source=v1_synthetic    phone=(313) 725-2170   addr=74971 Mercer Street 1st Floor, Sterling Heights, Kansas, USA
req  8: source=v2_real_osm     phone=(773) 939-7363   addr=3600 Sansom Street, Philadelphia, USA
req  9: source=v1_synthetic    phone=(636) 712-8737   addr=44254 Elfreth's Alley, Lansing, Alaska, USA
req 10: source=v2_real_osm     phone=(414) 385-2407   addr=534 South 15th Street, Philadelphia, USA

  ✅ PASS: perfect round-robin (v1, v2, v1, v2, ...)
```

### Guarantees
- ✅ **No duplicate addresses** within a single rotation cycle
- ✅ **~50/50 split** between V1 and V2 records when both pools have stock
- ✅ **Seamless fallback** — even when V2 (10,754 records) is exhausted, the API keeps serving V1 (1.5M records)
- ✅ **Auto-rotate** — pools re-shuffle and restart the cycle when both are exhausted

---

## 💾 Data Sources

### V1 — `data/all_data.txt` (1.5M records)

| Field | Source |
|:---|:---|
| **Country** | COUNTRIES list in `countries_data.py` |
| **Full name** | Faker localized providers (`de_DE`, `fr_FR`, `hi_IN`, `it_IT`, `nl_NL`, `pl_PL`, `sv_SE`, ...) — see [COUNTRY_LOCALE](countries_data.py) |
| **Street** | **REAL OpenStreetMap street names** — 41,679 streets cached from Overpass in `real_streets.json` |
| **House #** | Random 1–99,999 |
| **City** | Real major cities per country (4-16 per country) |
| **Region** | Real first-level administrative divisions per country |
| **Phone** | Country-specific generators with correct digit length + mobile prefix |
| **Postal code** | Country-specific generators matching the real postal format |
| **Email** | Random domain from 60+ providers (gmail, protonmail, yahoo, outlook, hotmail, icloud, gmx.de, libero.it, wp.pl, seznam.cz, orange.fr, ...) |

### V2 — `v2_real_addresses.txt` (10,754 records)

| Field | Source |
|:---|:---|
| **House #** | **REAL OSM `addr:housenumber` tag** |
| **Street** | **REAL OSM `addr:street` tag** |
| **City** | **REAL OSM `addr:city` tag** (falls back to the queried city) |
| **Postal code** | REAL OSM `addr:postcode` if present, else format-valid random |
| **Phone / Email / Name** | Same generators as V1 |

The V2 addresses were pulled directly from OpenStreetMap via the Overpass API:

```overpassql
[out:json][timeout:60];
(
  node["addr:housenumber"]["addr:street"](around:3000,52.52,13.405);
  way  ["addr:housenumber"]["addr:street"](around:3000,52.52,13.405);
);
out tags 200;
```

### Per-country V2 record counts (after dedupe)

| Country | Records |
|:---|---:|
| 🇺🇸 USA | 2,947 |
| 🇩🇪 Germany | 1,596 |
| 🇫🇷 France | 1,582 |
| 🇬🇧 United Kingdom | 1,183 |
| 🇮🇳 India | 1,198 |
| 🇨🇦 Canada | 1,148 |
| 🇦🇺 Australia | 1,100 |
| **Total** | **10,754** |

---

## 📞 Phone Number Validation

Every phone number in the dataset passes the `phonenumbers` library's
`is_valid_number()` check — the same library used by Android, WhatsApp,
and Signal for phone validation.

### Validated against libphonenumber metadata

- **Per-country digit lengths** — verified against `EXPECTED_DIGITS` table
- **Mobile prefix ranges** — extracted from `PhoneMetadata.metadata_for_region().mobile.national_number_pattern`
- **9 common bugs fixed** during the validation loop:
  - Finland / France / Romania / Sweden — off-by-one digit count
  - Lithuania / Luxembourg / Slovenia — wrong digit count entirely
  - Germany — produced 10-digit national numbers (pattern requires 11)
  - USA — 7 invalid area codes removed (473, 565, 627, 679, 752, 935, 957)
  - Canada — 472 (not yet assigned) removed
  - Iceland — `third_options["6"]` was `"01"` (only 660/661) but actual valid subprefixes are 60-66,69
  - Denmark — included 83/84/85 (invalid), excluded 90-94/97-99 (actually valid)
  - Slovakia — branch "1" allowed third=3 (invalid); branch "4" missing 4 and 8
  - Latvia — 23XX has complex sub-prefix rules, excluded "3" as 2nd digit
  - UK — 0760-0769 don't match mobile pattern, restricted 2nd digit to 1-4

### Self-test

```bash
python3 phone_formats.py
```

Output (excerpt):
```
[OK ] USA                (406) 655-0474           digits=10 (expected 10)
[OK ] United Kingdom     07841934660              digits=11 (expected 11)
[OK ] Germany            015942164206             digits=12 (expected 12)
[OK ] India              7098981570               digits=10 (expected 10)
...
```

---

## 🏗️ Project Structure

```
.
├── main.py                       # 🚀 FastAPI app (round-robin V1<->V2)
├── generate_data.py              # 🏗️  Builds data/all_data.txt (1.5M records)
├── countries_data.py             # 🌍 Country lists, cities, postal patterns, name pools
├── phone_formats.py             # 📞 Per-country phone generators (libphonenumber-validated)
├── real_streets.json            # 🛣️  41,679 real OSM street names (cached from Overpass)
├── v2_real_addresses.txt        # 📍 10,754 real OSM addresses (house + street both real)
├── v2_real_addresses.json       # 📍 Same as above, with full source metadata
├── data/
│   └── all_data.txt              # 💾 1.5M records, country-wise alphabetical, 184 MB
├── requirements.txt             # 📦 Python dependencies
├── validation_report.json       # 📊 Phone validation report (99.8% valid)
├── v2_validation_report.json   # 📊 V2 address validation report (86.9% Nominatim-valid)
└── README.md                     # 📖 This file
```

Scripts used to build everything (kept under `scripts/`):

```
scripts/
├── fetch_real_streets.py        # Overpass -> real_streets.json
├── v2_pull_real_addresses.py    # Overpass -> v2_real_addresses.txt
├── pull_more_v2.py              # Bigger V2 pull (10,754 records across 7 countries)
├── validate_data.py             # libphonenumber + Nominatim validation
├── validate_v2.py               # V2-specific validation
└── precheck_phones.py           # Sample-validate phones before regenerating
```

---

## ⚙️ Configuration

All configuration lives at the top of `main.py`:

```python
# Leave empty to read V1 from local data/all_data.txt file.
# After you upload data/all_data.txt to your GitHub repo (public), click
# the "Raw" button on the file and copy the URL, then paste it here:
REMOTE_URL = ""

# Only these 7 countries are served.  Requests for any other country
# get a 404 with an allowlist notice.
ALLOWED_COUNTRIES = {
    "Australia",
    "India",
    "France",
    "United Kingdom",
    "Canada",
    "USA",
    "Germany",
}
```

### Using a remote V1 source

1. Push the project (including `data/all_data.txt`) to a **public** GitHub repository
2. Open `data/all_data.txt` on GitHub → click **Raw** → copy the URL
3. Set `REMOTE_URL = "https://raw.githubusercontent.com/your-username/your-repo/main/data/all_data.txt"`
4. Restart the API — V1 records will be fetched from GitHub, V2 always stays local

---

## 🧪 Validation Reports

### Phone validation (all 1.5M records)

| Metric | Value |
|:---|:---|
| Total records | 1,499,987 |
| `is_possible_number` | 1,499,987 (100%) |
| `is_valid_number` | 1,496,498 (**99.8%**) |
| Countries at 100% | 32 / 35 |

### Address validation (V2 sample, 175 records via Nominatim)

| Metric | Value |
|:---|:---|
| Records sampled | 175 (5 per country × 35 countries) |
| Nominatim-valid | 152 (**86.9%**) |
| Control (real known addresses) | 6/7 (Sydney Opera House ✓, 10 Downing St ✓, Google HQ ✓, Brandenburg Gate ✓, ...) |

Run the validation scripts anytime:

```bash
python3 scripts/validate_data.py --addr-sample 5
python3 scripts/validate_v2.py
```

---

## 🐳 Deployment

### Local (development)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production (Docker)

Create a `Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```bash
docker build -t random-person-api .
docker run -p 8000:8000 random-person-api
```

### Render / Railway / Fly.io

The `uvicorn main:app --host 0.0.0.0 --port $PORT` command works on all three platforms.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add: your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

### Regenerating the dataset

```bash
# Re-fetch real street names from Overpass (15-20 min)
python3 scripts/fetch_real_streets.py

# Re-pull real addresses from Overpass (10-15 min)
python3 scripts/pull_more_v2.py

# Regenerate the 1.5M V1 dataset (30 sec)
python3 generate_data.py

# Run validation (1.5 min for phones, 5 min for addresses)
python3 scripts/validate_data.py
python3 scripts/validate_v2.py
```

---

## 📞 Contact

<div align="center">

### 💬 Dev / Maintainer

[![Telegram](https://img.shields.io/badge/@xirrod-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/xirrod)

**Telegram:** [@xirrod](https://t.me/xirrod)

</div>

---

## 📄 License

Released under the **MIT License**. See [LICENSE](LICENSE) for details.

<div align="center">

---

### ⚠️ Disclaimer

This dataset is intended **for testing and development use only**.
Phone numbers, postal codes, and email addresses are generated to be
*format-valid* but they do **not** correspond to real individuals or
real subscriber lines. The `555-01XX` exchange used for US/Canada
numbers is the NANPA-reserved fictional-number range, so those numbers
cannot be a real subscriber's phone.

If you intend to use this dataset for any purpose other than
development / QA / load testing, please review your local regulations
first.

---

</div>

<div align="center">

<sub>Built with ❤️ by [@xirrod](https://t.me/xirrod)</sub>

</div>
