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
![Real OSM Records](https://img.shields.io/badge/Real_OSM_Addresses-10%2C598-brightgreen?style=flat-square)
![Countries](https://img.shields.io/badge/Countries-7_served_(35_in_dataset)-red?style=flat-square)
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
- [🌍 Sample Records Per Country](#-sample-records-per-country)
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
- 🌍 **35 countries** in the underlying dataset
- 🔒 **7-country allowlist** for the live API (Australia, India, France, UK, Canada, USA, Germany)
- 📞 **99.8% valid phone numbers** (verified with `phonenumbers` library, the same one Android/WhatsApp use)
- 📍 **10,598 REAL OSM addresses** — house number AND street pulled directly from OpenStreetMap via the Overpass API
- 🛣️ **41,679 real street names** cached from OpenStreetMap
- 🎭 **Localized names per country** (German `de_DE`, French `fr_FR`, Italian `it_IT`, Hindi `en_IN`, etc.)
- 🔄 **Round-robin serving** between V1 (synthetic + real streets) and V2 (real OSM addresses)

</td>
<td width="50%" valign="top">

### ⚡ Engineering features
- 🚀 **FastAPI + Uvicorn** — sub-50ms response time
- 🧵 **Thread-safe** pool management with `threading.Lock`
- 🔁 **Auto-rotate** — same address never returned twice until pool is exhausted
- 📦 **Tiny repo (~3 MB)** — the 184 MB V1 file auto-downloads from GitHub Releases on first run
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
| 📍 Total V2 records (real OSM addresses) | **10,598** |
| 🌍 Countries in V1 dataset | **35** |
| 🔒 Countries served by API | **7** |
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

**Response (V1 — synthetic + real street):**
```json
{
  "country": "USA",
  "full_name": "Jessica Carr",
  "address": "19385 Branch Street #3, Bayamon, Kentucky, USA",
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

## 🌍 Sample Records Per Country

One sample record from `data/all_data.txt` for each of the 35 countries in the underlying dataset:

| Country | Full Name | Address | Phone | Postal | Email |
|:---|:---|:---|:---|:---|:---|
| 🇦🇺 Australia | Howard Walker | 72624 Brookes Street Unit B, Toowoomba, WA | 0434 667 603 | 7852 | howard.walker6998@gmx.net |
| 🇦🇹 Austria | Boris Hofbauer | 89302 Peregrinstraße Suite 200, Wiener Neustadt | 06689744933 | 9569 | boris_hofbauer831@laposte.net |
| 🇧🇪 Belgium | Leona Vereecke | 52810 Vliegenstraat Apt 6, Antwerp | 0499466054 | 4313 | leona.vereecke7457@sky.com |
| 🇧🇬 Bulgaria | Glenn Carter | 71344 Chestnut St Apt 3, Dobrich | 989391765 | 1362 | glenn.carter8381@seznam.cz |
| 🇨🇦 Canada | Kristy Henderson | 24542 9 Avenue SW 1st Floor, Surrey | (514) 214-7793 | O2P 3A3 | kristy_henderson6953@free.fr |
| 🇭🇷 Croatia | Zlatko Muzina | 76297 Ulica Ante Starcevica, Karlovac | 919469288 | 27957 | zlatko-muzina229@mail.com |
| 🇨🇾 Cyprus | Alan Parker | 10528 Archiepiskopou Leontiou, Nicosia | 99121456 | 4462 | alan-parker8841@telefonica.net |
| 🇨🇿 Czech Republic | Tomas Kopecky | 33178 Lumirova Apt 3, Hradec Králové | 704291277 | 517 06 | tomas.kopecky2170@vp.pl |
| 🇩🇰 Denmark | Agnete Nielsen | 1561 Kong Eriks Vej Suite 102, Kolding | 23204787 | 4613 | agnete.nielsen8097@btinternet.com |
| 🇪🇪 Estonia | Sergei Kool | 55394 Lembitu Studio, Kohtla-Järve | 56949604 | 80154 | sergei-kool8103@outlook.es |
| 🇫🇮 Finland | Tapani Lehtinen | 25163 Tallberginkatu Apt 3, Helsinki | 0507036836 | 35035 | tapani.lehtinen3689@orange.es |
| 🇫🇷 France | Noel Marques | 1696 Rue Parmentier #4, Toulon | 0632668451 | 12088 | noel_marques2017@volny.cz |
| 🇩🇪 Germany | Corinna Tintzmann | 48919 Pulsnitzer Straße Apt 5, Wiesbaden | 015757573561 | 89811 | corinna_tintzmann153@ymail.com |
| 🇬🇷 Greece | Tara Lucero | 62130 Barbara St 4th Floor, Chania | 6904584814 | 847 54 | tara_lucero1174@hotmail.com |
| 🇭🇺 Hungary | Peter Sandor | 15996 Londoni korut Apt 7, Budapest | 706206744 | 4303 | peter-sandor2298@outlook.es |
| 🇮🇸 Iceland | Dana Villarreal | 67473 Hofsvallagata Studio, Garðabær | 6251614 | 698 | dana_villarreal@gmail.com |
| 🇮🇳 India | Yoshita Sarraf | 71621 D' Souza Road Unit A, Tiruvannamalai | 8306215190 | 552696 | yoshita.sarraf@alice.it |
| 🇮🇪 Ireland | Lawrence Ashton | 25348 Rathmore Road, Cork | 0898593037 | D08 X1F2 | lawrence.ashton@outlook.com |
| 🇮🇹 Italy | Stefania Soffici | 51507 Via della Consolata, Rimini | 3415324151 | 81848 | stefania.soffici@libero.it |
| 🇱🇻 Latvia | Julija Lukstins | 1457 Tomsona iela 8th Floor, Rēzekne | 28018280 | 1850 | julija.lukstins@inbox.lv |
| 🇱🇹 Lithuania | Reda Adams | 26191 A. Fromo-Guzucio g. Loft 2, Marijampolė | 64121100 | 5241 | reda_adams@yahoo.com |
| 🇱🇺 Luxembourg | Anastasie Descamps | 38123 Rue Ditzenheck #8, Differdange | 678847033 | 3443 | anastasie.descamps@gmail.com |
| 🇲🇹 Malta | Anna Roy | 13737 Triq l-Omnibus, Żabbar | 79240785 | ZZ 2C019 | anna.roy@gmail.com |
| 🇳🇱 Netherlands | Lola Honing | 86192 Scheepmakersstraat #9, Utrecht | 0623336428 | 6708 IG | lola.honing@kpn.nl |
| 🇳🇴 Norway | Ruth Moen | 80508 Ribbunggata #7, Bergen | 91147845 | 3905 | ruth.moen@telenor.no |
| 🇵🇱 Poland | Konrad Bobel | 89710 Orlat Lwowskich #4, Olsztyn | 607100267 | 54-828 | konrad.bobel@wp.pl |
| 🇵🇹 Portugal | Constanca Assuncao | 95321 Campo das Hortas, Castelo Branco | 914155639 | 1823-616 | constanca.assuncao@sapo.pt |
| 🇷🇴 Romania | Casandra Clark | 20916 Strada Petofi Sandor Apt 1, Arad | 0759473129 | 234456 | casandra.clark@gmail.com |
| 🇸🇰 Slovakia | Olga Visnovska | 7888 Jana Kovalika Apt 9, Banská Bystrica | 953870289 | 95309 | olga.visnovska@centrum.sk |
| 🇸🇮 Slovenia | Ljudmila Tavcar | 67423 Hocka ulica Apt 3, Ptuj | 51491165 | 8726 | ljudmila.tavcar@siol.net |
| 🇪🇸 Spain | Bienvenida Figuerola | 83001 Calle de Arias Apt 7, Murcia | 668027772 | 14566 | bienvenida.figueroa@gmail.com |
| 🇸🇪 Sweden | Therese Ryden | 49248 Banersgatan Unit F, Umeå | 0723019353 | 544 22 | therese.ryden@telia.com |
| 🇨🇭 Switzerland | Marcia Fankhauser | 50010 Seelandweg Unit C, Lausanne | 0798283833 | 5363 | marcia.fankhauser@bluewin.ch |
| 🇬🇧 United Kingdom | Philip Joyce | 77248 Snow Hill Queensway Apt 10, Bradford | 07491823303 | HX4 3MW | philip.joyce@btinternet.com |
| 🇺🇸 USA | Monica Beasley | 76219 Fairview Place North Studio C, Plano | (947) 498-4720 | 10820-0996 | monica.beasley@gmail.com |

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
- ✅ **Seamless fallback** — even when V2 (10,598 records) is exhausted, the API keeps serving V1 (1.5M records)
- ✅ **Auto-rotate** — pools re-shuffle and restart the cycle when both are exhausted

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
     30% (  55.0 MB / 183.1 MB)
    ...
[+] Download complete! Cached at: data/all_data.txt (183.1 MB)
```

If the download fails (network issues, wrong URL), the API still starts and serves V2 records only.

### V2 — `v2_real_addresses.txt` (10,598 records, ~1.1 MB) — **ships with the repo**

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
| 🇺🇸 USA | ~2,791 |
| 🇩🇪 Germany | ~1,440 |
| 🇫🇷 France | ~1,425 |
| 🇬🇧 United Kingdom | ~1,065 |
| 🇮🇳 India | ~1,080 |
| 🇨🇦 Canada | ~1,030 |
| 🇦🇺 Australia | ~990 |
| **Total** | **10,598** |

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
├── main.py                       # 🚀 FastAPI app (round-robin V1<->V2, auto-download V1)
├── v2_real_addresses.txt          # 📍 10,598 real OSM addresses (ships with repo, ~1.1 MB)
├── requirements.txt              # 📦 Python dependencies
├── .gitignore                    # 🚫 Excludes data/all_data.txt + Python caches
├── LICENSE                       # 📄 MIT License
├── data/                         # 📁 Auto-created on first run
│   └── all_data.txt              # 💾 184 MB V1 dataset (auto-downloaded from GitHub Releases, NOT in repo)
└── README.md                     # 📖 This file
```

**Total repo size pushed to GitHub: ~1.3 MB** (just `main.py`, `v2_real_addresses.txt`, `requirements.txt`, `LICENSE`, `README.md`, `.gitignore`).

The 184 MB `data/all_data.txt` is hosted on GitHub Releases and auto-downloaded on first run.

---

## ⚙️ Configuration

All configuration lives at the top of `main.py`:

```python
# URL of the all_data.txt file (hosted on GitHub Releases because it's
# too big - 184 MB - for the regular GitHub repo).
REMOTE_URL = "https://github.com/xirrod/Address_Facker/releases/latest/download/all_data.txt"

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

### To extend the country allowlist

Edit `ALLOWED_COUNTRIES` to add more countries from the V1 dataset:

```python
ALLOWED_COUNTRIES = {
    "Australia", "India", "France", "United Kingdom",
    "Canada", "USA", "Germany",
    "Spain", "Italy", "Netherlands",  # <-- add new countries here
}
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

The `v2_real_addresses.txt` file ships with the repo (~1.1 MB). To refresh it with new OSM data:

1. Use the Overpass API to pull fresh `addr:housenumber` + `addr:street` tags
2. Replace `v2_real_addresses.txt` with the new data
3. Commit and push

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
