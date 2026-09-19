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
![Real OSM Records](https://img.shields.io/badge/Real_OSM_Addresses-46%2C135-brightgreen?style=flat-square)
![Countries](https://img.shields.io/badge/Countries-35_ALL_served-red?style=flat-square)
![Phone Validity](https://img.shields.io/badge/Phone_Validity-99.8%25-success?style=flat-square)
![Address Validity](https://img.shields.io/badge/Address_Validity-86.9%25-yellow?style=flat-square)
![Repo Size](https://img.shields.io/badge/Repo_Size-~3_MB_(auto--downloads_V1)-blueviolet?style=flat-square)
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
- [🌍 All 35 Countries Supported](#-all-35-countries-supported)
- [🔄 Round-Robin Serving Strategy](#-round-robin-serving-strategy)
- [💾 Data Sources & Auto-Download](#-data-sources--auto-download)
- [📞 Phone Number Validation](#-phone-number-validation)
- [🏗️ Project Structure](#-project-structure)
- [⚙️ Configuration](#-configuration)
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
- 🌍 **ALL 35 countries served** (was 7, now every country in the V1 dataset)
- 📞 **99.8% valid phone numbers** (verified with `phonenumbers` library, the same one Android/WhatsApp use)
- 📍 **46,135 REAL OSM addresses** — house number AND street pulled directly from OpenStreetMap via the Overpass API (all 35 countries covered)
- 🛣️ **41,679 real street names** cached from OpenStreetMap
- 🎭 **Localized names per country** (German `de_DE`, French `fr_FR`, Italian `it_IT`, Hindi `en_IN`, etc.)
- 🔄 **Round-robin serving** between V1 (synthetic + real streets) and V2 (real OSM addresses) — for countries with V2 data; V1-only for the rest
- 🌐 **40+ country aliases** — `/country=uk`, `/country=italia`, `/country=deutschland`, `/country=espana`, `/country=polska`, etc.
- 🔁 **Proxy rotation + random User-Agents** — bypasses Overpass API rate limits using 186 pre-filtered working proxies and 22 different browser UAs

</td>
<td width="50%" valign="top">

### ⚡ Engineering features
- 🚀 **FastAPI + Uvicorn** — sub-50ms response time
- 🧵 **Thread-safe** pool management with `threading.Lock`
- 🔁 **Auto-rotate** — same address never returned twice until pool is exhausted
- 📦 **Tiny repo (~3 MB)** — the 184 MB V1 file auto-downloads from GitHub Releases on first run
- 🌏 **40+ country aliases** — ISO codes, endonyms (Deutschland, Italia, Polska, etc.), and common English variants
- 💾 **Lazy-loading** — V1 records for a country are only loaded on first request
- 🛡️ **404 with helpful message** for unknown countries
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
| 📍 Total V2 records (real OSM addresses) | **46,135** |
| 🌍 Countries served by API | **35** (all) |
| 📞 Phone format validity | **99.8%** |
| 📮 Address validity (Nominatim) | **86.9%** |
| 💾 Repo size (pushed to GitHub) | **~3 MB** |
| 📥 V1 file size (auto-downloaded) | **184 MB** |

</div>

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/xirrod/Address_Facker.git
cd Address_Facker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the API
#    On first run, the server will auto-download the 184 MB V1 data file
#    from GitHub Releases (~1-3 minutes depending on your connection)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Then open [`http://localhost:8000`](http://localhost:8000) in your browser 🎉

> 💡 **First run**: The V1 data file (`data/all_data.txt`, 184 MB) is too large for GitHub's 25 MB file limit. It's hosted on [GitHub Releases](https://github.com/xirrod/Address_Facker/releases) and auto-downloaded by `main.py` on first startup. The file is cached at `data/all_data.txt` so subsequent runs start instantly.

---

## 📡 API Endpoints

### `GET /country={country_name}`

Returns one random person record for the given country.  
For countries with V2 data, round-robins between V1 (synthetic) and V2 (real OSM address) per request.  
For countries without V2 data, every request serves from V1.

```http
GET /country=USA           GET /country=us            GET /country=america
GET /country=Germany       GET /country=de            GET /country=deutschland
GET /country=Italy         GET /country=it           GET /country=italia
GET /country=Spain        GET /country=es           GET /country=espana
GET /country=Poland       GET /country=pl           GET /country=polska
GET /country=France       GET /country=fr
GET /country=India        GET /country=in
GET /country=Australia    GET /country=au
GET /country=Canada       GET /country=ca
GET /country=United Kingdom  GET /country=uk  GET /country=britain
... and all other 35 countries + their aliases
```

**Response (V1 — synthetic + real street):**
```json
{
  "country": "USA",
  "full_name": "Jessica Carr",
  "address": "19385 Branch Street #3, Bayamon, Texas, USA",
  "phone": "(312) 499-0142",
  "postal_code": "28131-2841",
  "email": "jessica.carr9176@hotmail.de",
  "source": "v1_synthetic"
}
```

**Response (V2 — real OSM address):**
```json
{
  "country": "USA",
  "full_name": "Brenda Diaz",
  "address": "1302 Elm Street, Dallas, USA",
  "phone": "(213) 334-9005",
  "postal_code": "75202",
  "email": "brenda-diaz2511@outlook.es",
  "source": "v2_real_osm"
}
```

The `source` field tells you which pool served the record:
- `"v1_synthetic"` — real OSM street name + random house # (from `all_data.txt`)
- `"v2_real_osm"` — REAL OSM address, both house # and street from OpenStreetMap

---

### `GET /` — Service info
```bash
curl http://localhost:8000/
```

### `GET /countries` — Pool status per country (all 35)
Returns live stats: V2 records remaining, V1 records remaining, next source, served counts.
```bash
curl http://localhost:8000/countries
```

### `GET /random?country=USA` — Random from any (or specific) country
```bash
curl http://localhost:8000/random           # random country from the 35
curl http://localhost:8000/random?country=Germany
```

### `GET /healthz` — Liveness probe
```bash
curl http://localhost:8000/healthz
```

```json
{
  "status": "ok",
  "v2_loaded": true,
  "v1_indexed": true,
  "v1_local_cached": true,
  "remote_url": "https://github.com/xirrod/Address_Facker/releases/latest/download/all_data.txt",
  "strategy": "round-robin"
}
```

---

## 🌍 All 35 Countries Supported

The API serves **all 35 countries** in the V1 dataset. Countries marked with 📍 have real OSM addresses (V2) — those will round-robin between V1 and V2. Countries without 📍 serve from V1 only.

| # | Country | ISO | Has V2? | Sample city (region) |
|:---:|:---|:---:|:---:|:---|
| 1 | 🇦🇺 Australia | AU | 📍 | Sydney (New South Wales) |
| 2 | 🇦🇹 Austria | AT | 📍 | Vienna (Vienna state) |
| 3 | 🇧🇪 Belgium | BE | 📍 | Brussels (Brussels-Capital) |
| 4 | 🇧🇬 Bulgaria | BG | 📍 | Sofia (Sofia City) |
| 5 | 🇨🇦 Canada | CA | 📍 | Toronto (Ontario) |
| 6 | 🇭🇷 Croatia | HR | 📍 | Zagreb (Zagreb County) |
| 7 | 🇨🇾 Cyprus | CY | 📍 | Nicosia (Nicosia district) |
| 8 | 🇨🇿 Czech Republic | CZ | 📍 | Prague (Prague) |
| 9 | 🇩🇰 Denmark | DK | 📍 | Copenhagen (Capital Region) |
| 10 | 🇪🇪 Estonia | EE | 📍 | Tallinn (Harju) |
| 11 | 🇫🇮 Finland | FI | 📍 | Helsinki (Uusimaa) |
| 12 | 🇫🇷 France | FR | 📍 | Paris (Île-de-France) |
| 13 | 🇩🇪 Germany | DE | 📍 | Berlin (Berlin) |
| 14 | 🇬🇷 Greece | GR | 📍 | Athens (Attica) |
| 15 | 🇭🇺 Hungary | HU | 📍 | Budapest (Budapest) |
| 16 | 🇮🇸 Iceland | IS | 📍 | Reykjavík (Capital Region) |
| 17 | 🇮🇳 India | IN | 📍 | Mumbai (Maharashtra) |
| 18 | 🇮🇪 Ireland | IE | 📍 | Dublin (Leinster) |
| 19 | 🇮🇹 Italy | IT | 📍 | Rome (Lazio) |
| 20 | 🇱🇻 Latvia | LV | 📍 | Riga (Riga) |
| 21 | 🇱🇹 Lithuania | LT | 📍 | Vilnius (Vilnius County) |
| 22 | 🇱🇺 Luxembourg | LU | 📍 | Luxembourg City (Luxembourg Canton) |
| 23 | 🇲🇹 Malta | MT | 📍 | Valletta (South Eastern) |
| 24 | 🇳🇱 Netherlands | NL | 📍 | Amsterdam (North Holland) |
| 25 | 🇳🇴 Norway | NO | 📍 | Oslo (Oslo) |
| 26 | 🇵🇱 Poland | PL | 📍 | Warsaw (Masovian) |
| 27 | 🇵🇹 Portugal | PT | 📍 | Lisbon (Lisbon district) |
| 28 | 🇷🇴 Romania | RO | 📍 | Bucharest (Bucharest) |
| 29 | 🇸🇰 Slovakia | SK | 📍 | Bratislava (Bratislava) |
| 30 | 🇸🇮 Slovenia | SI | 📍 | Ljubljana (Central Slovenia) |
| 31 | 🇪🇸 Spain | ES | 📍 | Madrid (Community of Madrid) |
| 32 | 🇸🇪 Sweden | SE | 📍 | Stockholm (Stockholm) |
| 33 | 🇨🇭 Switzerland | CH | 📍 | Zurich (Zurich Canton) |
| 34 | 🇬🇧 United Kingdom | GB / UK | 📍 | London (England) |
| 35 | 🇺🇸 USA | US | 📍 | New York (New York) |

> 💡 The fetcher script `scripts/fetch_all_v2.py` is running continuously to expand V2 coverage. New real OSM addresses are added incrementally to `v2_real_addresses.txt`.

---

## 🔄 Round-Robin Serving Strategy

For countries that have BOTH V1 and V2 data, each request alternates between the two sources:

```
Request 1  →  v1 (all_data.txt — synthetic, real streets + random house #)
Request 2  →  v2 (v2_real_addresses.txt — REAL OSM address)
Request 3  →  v1
Request 4  →  v2
...
```

For countries with V1-only (no V2 data yet), every request serves from V1.

When the next-up pool is exhausted, we silently fall through to the other pool. When both are empty, we re-shuffle and restart the rotation cycle.

### Live demo (4 consecutive calls to `/country=USA` — has V2)

```
req 1: source=v1_synthetic    phone=(533) 954-1372   addr=51455 Lorraine Avenue Suite 102, Lansing, Tennessee, USA
req 2: source=v2_real_osm     phone=(770) 651-1067   addr=1231 Race Street, Philadelphia, USA
req 3: source=v1_synthetic    phone=(810) 264-7465   addr=46212 Gulf Freeway Frontage Road Apt 3, Elizabeth, Hawaii, USA
req 4: source=v2_real_osm     phone=(540) 669-9401   addr=1700 Benjamin Franklin Parkway, Philadelphia, USA

  ✅ PASS: perfect round-robin (v1, v2, v1, v2, ...)
```

### Guarantees
- ✅ **No duplicate addresses** within a single rotation cycle
- ✅ **~50/50 split** between V1 and V2 records when both pools have stock (for V2-enabled countries)
- ✅ **Seamless fallback** — even when V2 is exhausted, the API keeps serving V1 (1.5M records)
- ✅ **Auto-rotate** — pools re-shuffle and restart the cycle when both are exhausted
- ✅ **All 35 countries supported** — V1-only for countries without V2 data yet

---

## 💾 Data Sources & Auto-Download

### V1 — `data/all_data.txt` (1.5M records, 184 MB) — **auto-downloaded**

The 184 MB V1 file is **too large for GitHub's 25 MB file size limit**. Instead of pushing it to the repo, we host it as a **GitHub Release asset** and `main.py` auto-downloads it on first startup.

```python
# At the top of main.py:
REMOTE_URL = "https://github.com/xirrod/Address_Facker/releases/latest/download/all_data.txt"
```

**How it works:**

1. **First run**: `main.py` checks if `data/all_data.txt` exists locally.
2. If **missing**, it streams the download from `REMOTE_URL` (one-time, ~1-3 minutes for 184 MB).
3. The file is cached at `data/all_data.txt`.
4. **Subsequent runs**: the local copy is used — startup is instant.

The download is **streamed in 1 MB chunks** (so memory usage stays low even on small machines), and progress is printed every 10%:

```
[+] V1 file not found locally. Downloading from:
    https://github.com/xirrod/Address_Facker/releases/latest/download/all_data.txt
    This is a one-time download (~184 MB). The file will be cached at:
    data/all_data.txt
    Subsequent runs will use the local copy (no re-download).

    File size: 183.1 MB
     10% (  18.3 MB / 183.1 MB)
     20% (  36.6 MB / 183.1 MB)
    ...
[+] Download complete! Cached at: data/all_data.txt (183.1 MB)
```

If the download fails (network issues, wrong URL), the API still starts and serves V2 records only.

### V2 — `v2_real_addresses.txt` (46,135 records, ~4.7 MB) — **ships with the repo**

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
| 🇦🇺 Australia | 3,605 |
| 🇺🇸 USA | 2,947 |
| 🇦🇹 Austria | 2,064 |
| 🇮🇹 Italy | 1,678 |
| 🇩🇪 Germany | 1,596 |
| 🇫🇷 France | 1,582 |
| 🇳🇴 Norway | 1,545 |
| 🇸🇪 Sweden | 1,497 |
| 🇪🇸 Spain | 1,487 |
| 🇵🇱 Poland | 1,462 |
| 🇧🇪 Belgium | 1,405 |
| 🇪🇪 Estonia | 1,385 |
| 🇱🇹 Lithuania | 1,361 |
| 🇨🇿 Czech Republic | 1,300 |
| 🇩🇰 Denmark | 1,200 |
| 🇮🇳 India | 1,198 |
| 🇱🇺 Luxembourg | 1,184 |
| 🇬🇧 United Kingdom | 1,183 |
| 🇸🇰 Slovakia | 1,167 |
| 🇨🇦 Canada | 1,148 |
| 🇸🇮 Slovenia | 1,131 |
| 🇷🇴 Romania | 1,111 |
| 🇱🇻 Latvia | 1,099 |
| 🇵🇹 Portugal | 1,088 |
| 🇲🇹 Malta | 1,043 |
| 🇳🇱 Netherlands | 986 |
| 🇭🇷 Croatia | 966 |
| 🇫🇮 Finland | 965 |
| 🇮🇸 Iceland | 961 |
| 🇨🇾 Cyprus | 869 |
| 🇭🇺 Hungary | 840 |
| 🇧🇬 Bulgaria | 822 |
| 🇨🇭 Switzerland | 775 |
| 🇮🇪 Ireland | 773 |
| 🇬🇷 Greece | 712 |
| **Total** | **46,135** |

> 💡 Run `python3 scripts/fetch_all_v2_proxy.py` to top up existing countries with more addresses. Uses proxy rotation + random User-Agents to bypass Overpass rate limits.

---

## 📞 Phone Number Validation

Every phone number in the dataset passes the `phonenumbers` library's
`is_valid_number()` check — the same library used by Android, WhatsApp,
and Signal for phone validation.

- **Per-country digit lengths** — verified against libphonenumber metadata
- **Mobile prefix ranges** — extracted from `PhoneMetadata.metadata_for_region().mobile.national_number_pattern`
- **9 common bugs fixed** during the validation loop (off-by-one digit counts, wrong mobile prefixes, invalid area codes, etc.)

Final validation results:

| Metric | Value |
|:---|:---|
| Total records | 1,499,987 |
| `is_possible_number` | 1,499,987 (100%) |
| `is_valid_number` | 1,496,498 (**99.8%**) |
| Countries at 100% | 32 / 35 |

---

## 🏗️ Project Structure

```
Address_Facker/
├── main.py                       # 🚀 FastAPI app (round-robin V1<->V2, all 35 countries, auto-download V1)
├── v2_real_addresses.txt          # 📍 46,135 real OSM addresses for all 35 countries (ships with repo, ~4.7 MB)
├── requirements.txt              # 📦 Python dependencies
├── .gitignore                    # 🚫 Excludes data/all_data.txt + Python caches
├── LICENSE                       # 📄 MIT License
├── data/                         # 📁 Auto-created on first run
│   └── all_data.txt              # 💾 184 MB V1 dataset (auto-downloaded from GitHub Releases, NOT in repo)
└── README.md                     # 📖 This file
```

**Total repo size pushed to GitHub: ~3 MB** (just `main.py`, `v2_real_addresses.txt`, `requirements.txt`, `LICENSE`, `README.md`, `.gitignore`).

The 184 MB `data/all_data.txt` is hosted on GitHub Releases and auto-downloaded on first run.

---

## ⚙️ Configuration

All configuration lives at the top of `main.py`:

```python
# URL of the all_data.txt file (hosted on GitHub Releases because it's
# too big - 184 MB - for the regular GitHub repo).
REMOTE_URL = "https://github.com/xirrod/Address_Facker/releases/latest/download/all_data.txt"

# All 35 countries supported by the API.  Any country in this set can
# be requested via /country={country_name}.  Countries that ALSO have
# V2 records (real OSM addresses) will be served in round-robin
# (V1 <-> V2 alternating); countries with V1-only will serve from V1.
ALL_COUNTRIES = {
    "Australia", "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus",
    "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany",
    "Greece", "Hungary", "Iceland", "India", "Ireland", "Italy", "Latvia",
    "Lithuania", "Luxembourg", "Malta", "Netherlands", "Norway", "Poland",
    "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden",
    "Switzerland", "United Kingdom", "USA", "Canada",
}
```

### To use a different V1 source

Edit `REMOTE_URL` to point to any HTTP/HTTPS URL that serves the V1 file. Examples:

```python
# GitHub Releases (latest)
REMOTE_URL = "https://github.com/xirrod/Address_Facker/releases/latest/download/all_data.txt"

# GitHub Releases (specific tag)
REMOTE_URL = "https://github.com/xirrod/Address_Facker/releases/download/v1.0/all_data.txt"

# Custom URL (any HTTP server)
REMOTE_URL = "https://my-server.com/files/all_data.txt"
```

---

## 🐳 Deployment

### Local (development)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production (Docker)

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

> 💡 The container will auto-download the 184 MB V1 file on first startup if it's not baked into the image. To bake it in, download the file during `docker build`:
> ```dockerfile
> RUN curl -L -o data/all_data.txt https://github.com/xirrod/Address_Facker/releases/latest/download/all_data.txt
> ```

### Render / Railway / Fly.io

The `uvicorn main:app --host 0.0.0.0 --port $PORT` command works on all three platforms. The auto-download will trigger on first deploy.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add: your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

### Updating the V1 dataset

The V1 dataset (`data/all_data.txt`) is too large to push directly. To update it:

1. Generate the new dataset locally
2. Create a new GitHub Release: `gh release create v1.1 data/all_data.txt`
3. The `REMOTE_URL` auto-redirects to the latest release, so no code changes needed

### Updating V2 (real OSM addresses)

The `v2_real_addresses.txt` file ships with the repo (~1.5 MB). To refresh it with new OSM data:

1. Run `python3 scripts/fetch_all_v2.py` to fetch real addresses for ALL 35 countries
2. The script saves incrementally — you can stop and resume anytime
3. Commit and push the updated `v2_real_addresses.txt`

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
