"""
Endpoint
--------
    GET /country={country_name}

Auto-download behaviour
-----------------------
On startup, the server checks if `data/all_data.txt` exists locally.
If not, it streams the file from REMOTE_URL (one-time ~184MB download)
and caches it locally.  Subsequent runs use the local copy.

This way the GitHub repo stays small (~3 MB), but the bot can still
serve all 1.5M V1 records.
"""

from __future__ import annotations

import os
import random
import sys
import threading
from collections import defaultdict
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, HTTPException, Query

REMOTE_URL = "https://github.com/Xirrod/Address_Faker/releases/download/V1/all_data.txt"


ALLOWED_COUNTRIES = {
    "Australia",
    "India",
    "France",
    "United Kingdom",
    "Canada",
    "USA",
    "Germany",
}
HERE = Path(__file__).resolve().parent
V1_FILE = HERE / "data" / "all_data.txt"
V2_FILE = HERE / "v2_real_addresses.txt"

FIELDS = ("country", "full_name", "address", "phone", "postal_code", "email")

app = FastAPI(
    title="Random Person Data API",
    description="Serves random fake-but-format-valid person records by country. "
                "Round-robin between real OSM addresses and synthetic-but-real-street records. "
                "Limited to: Australia, India, France, UK, Canada, USA, Germany.",
    version="3.1.0",
)

COUNTRY_ALIASES = {
    "uk": "United Kingdom",
    "britain": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "us": "USA",
    "united states": "USA",
    "united states of america": "USA",
    "america": "USA",
    "de": "Germany",
    "deutschland": "Germany",
    "deutschland": "Germany",
    "fr": "France",
    "in": "India",
    "ca": "Canada",
    "au": "Australia",
}



def download_v1_file(target: Path = V1_FILE, url: str = REMOTE_URL) -> bool:
   
    if target.exists():
        size_mb = target.stat().st_size / (1024 * 1024)
        print(f"[+] V1 file already present locally: {target} ({size_mb:.1f} MB)")
        return True

    if not url:
        print(f"[!] V1 file missing at {target} and REMOTE_URL is empty - cannot download")
        return False

    # Make sure parent directory exists
    target.parent.mkdir(parents=True, exist_ok=True)

    print(f"[+] V1 file not found locally. Downloading from:")
    print(f"    {url}")
    print(f"    This is a one-time download (~184 MB). The file will be cached at:")
    print(f"    {target}")
    print(f"    Subsequent runs will use the local copy (no re-download).")
    print()

    try:
        
        with requests.get(url, stream=True, timeout=600,
                          headers={"User-Agent": "RandomDataValidator/3.1"}) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            if total_size > 0:
                print(f"    File size: {total_size / (1024 * 1024):.1f} MB")
            else:
                print(f"    File size: unknown (server didn't send Content-Length)")
            downloaded = 0
            last_pct = -1
            with target.open("wb") as fh:
                for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1 MB chunks
                    if chunk:
                        fh.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            pct = int(100 * downloaded / total_size)
                            # Print every 10%
                            if pct >= last_pct + 10:
                                last_pct = pct - (pct % 10)
                                print(f"    {last_pct:>3}%  "
                                      f"({downloaded / (1024 * 1024):>6.1f} MB / "
                                      f"{total_size / (1024 * 1024):.1f} MB)")
                        else:
                            # No content-length, just show MB downloaded every 10 MB
                            if downloaded % (10 * 1024 * 1024) < 1024 * 1024:
                                print(f"    {downloaded / (1024 * 1024):>6.1f} MB downloaded")
        size_mb = target.stat().st_size / (1024 * 1024)
        print(f"[+] Download complete! Cached at: {target} ({size_mb:.1f} MB)")
        return True
    except Exception as e:
        print(f"[!] Download failed: {e}")
        # Clean up partial file
        if target.exists():
            try:
                target.unlink()
            except Exception:
                pass
        return False



class DataStore:
    
    def __init__(self, v1_path: Path, v2_path: Path):
        self.v1_path = v1_path
        self.v2_path = v2_path
        self.lock = threading.Lock()

        # country -> list[str] of records currently being served
        self.v2_pools: dict[str, list[str]] = {}
        self.v1_pools: dict[str, list[str]] = {}

        # country -> (start_line, end_line) index for V1 file (1-indexed)
        self.v1_index: dict[str, tuple[int, int]] = {}

        # country -> bool  has v2 pool been exhausted at least once?
        self.v2_exhausted_once: dict[str, bool] = {}
        # country -> bool  has v1 pool been exhausted at least once?
        self.v1_exhausted_once: dict[str, bool] = {}

        # country -> "v1" or "v2" - which to serve next
        self.next_source: dict[str, str] = {}

        # country -> dict of counters (v1_served, v2_served, total_served)
        self.served_count: dict[str, dict[str, int]] = defaultdict(
            lambda: {"v1": 0, "v2": 0, "total": 0}
        )

    
    def _load_v2(self) -> None:
        if not self.v2_path.exists():
            print(f"[!] V2 file not found: {self.v2_path}")
            return
        per_country: dict[str, list[str]] = defaultdict(list)
        with self.v2_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line or line.startswith("#"):
                    continue
                country = line.split("|", 1)[0]
                if country in ALLOWED_COUNTRIES:
                    per_country[country].append(line)
        total_before_dedupe = 0
        total_after_dedupe = 0
        for c in ALLOWED_COUNTRIES:
            recs = per_country.get(c, [])
            total_before_dedupe += len(recs)
            seen_addrs: set[str] = set()
            unique_recs: list[str] = []
            for r in recs:
                parts = r.split("|")
                if len(parts) >= 3:
                    addr_key = parts[2]
                    if addr_key in seen_addrs:
                        continue
                    seen_addrs.add(addr_key)
                    unique_recs.append(r)
            random.shuffle(unique_recs)
            self.v2_pools[c] = unique_recs
            self.v2_exhausted_once[c] = False
            self.next_source[c] = "v1"  # start with v1, alternate thereafter
            total_after_dedupe += len(unique_recs)
        if total_before_dedupe != total_after_dedupe:
            print(f"[+] V2 dedupe: {total_before_dedupe:,} -> {total_after_dedupe:,} records "
                  f"(removed {total_before_dedupe - total_after_dedupe} duplicates)")
        print(f"[+] V2 loaded: {total_after_dedupe:,} real-OSM records across {len(self.v2_pools)} countries")

    
    def _build_v1_index(self) -> None:
        if not self.v1_path.exists():
            print(f"[!] V1 file not found: {self.v1_path}")
            return
        country_starts: dict[str, int] = {}
        last_country: Optional[str] = None
        line_no = 0
        with self.v1_path.open("r", encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, 1):
                line = line.rstrip("\n")
                if not line or line.startswith("#"):
                    continue
                country = line.split("|", 1)[0]
                if country not in ALLOWED_COUNTRIES:
                    continue
                if country != last_country:
                    country_starts[country] = line_no
                    if last_country is not None and last_country in ALLOWED_COUNTRIES:
                        self.v1_index[last_country] = (country_starts[last_country], line_no - 1)
                    last_country = country
        if last_country is not None and last_country in ALLOWED_COUNTRIES and last_country not in self.v1_index:
            self.v1_index[last_country] = (country_starts[last_country], line_no)
        total = sum(e - s + 1 for s, e in self.v1_index.values())
        print(f"[+] V1 indexed: {self.v1_path}")
        print(f"[+] V1 records available for the 7 countries: {total:,}")

   
    def _ensure_v1_pool(self, country: str) -> bool:
        if country in self.v1_pools:
            return True
        if country not in self.v1_index:
            return False
        start, end = self.v1_index[country]
        recs: list[str] = []
        with self.v1_path.open("r", encoding="utf-8") as fh:
            for i, line in enumerate(fh, 1):
                if i < start:
                    continue
                if i > end:
                    break
                line = line.rstrip("\n")
                if not line or line.startswith("#"):
                    continue
                recs.append(line)
        random.shuffle(recs)
        self.v1_pools[country] = recs
        self.v1_exhausted_once[country] = False
        return True

   
    def init(self) -> None:
        # Load V2 (always local, small file)
        self._load_v2()

        # Ensure V1 file exists locally - download from REMOTE_URL if missing
        if not self.v1_path.exists():
            print(f"[+] V1 file ({self.v1_path.name}) not found locally - auto-downloading from REMOTE_URL")
            ok = download_v1_file(self.v1_path, REMOTE_URL)
            if not ok:
                print(f"[!] Failed to download V1 file. The API will only serve V2 records.")
                # Still proceed - V2 alone can serve requests
        else:
            size_mb = self.v1_path.stat().st_size / (1024 * 1024)
            print(f"[+] V1 file present locally: {self.v1_path} ({size_mb:.1f} MB)")

        # Build V1 index (line ranges per country)
        if self.v1_path.exists():
            self._build_v1_index()

        print(f"[+] Allowlist: {sorted(ALLOWED_COUNTRIES)}")
        print(f"[+] V2 pools ready: {sum(len(v) for v in self.v2_pools.values()):,} real-OSM records")
        if self.v1_index:
            print(f"[+] V1 indexed (lazy-load on first request): {self.v1_path}")
        print(f"[+] Serving strategy: round-robin V1 <-> V2 (alternating per request)")

    # -----------------------------------------------------------------
    # Public: get one record for a country (round-robin)
    # -----------------------------------------------------------------
    def get_random(self, country: str) -> Optional[dict]:
      
        key = self._resolve_country(country)
        if key is None:
            return None

        with self.lock:
            self.served_count[key]["total"] += 1

            # Pick the source for this request
            preferred = self.next_source.get(key, "v1")
            # Flip for the NEXT request
            self.next_source[key] = "v2" if preferred == "v1" else "v1"
            fallback = "v2" if preferred == "v1" else "v1"

            record = self._pop_from(key, preferred) or self._pop_from(key, fallback)
            if record is None:
               
                self._refill_v1(key)
                self._refill_v2(key)
                record = self._pop_from(key, preferred) or self._pop_from(key, fallback)
            if record is None:
                return None

            
            source_tag = "v2_real_osm" if record[0] == "v2" else "v1_synthetic"
            self.served_count[key][record[0]] += 1
            return self._parse(record[1], source=source_tag)

    def _pop_from(self, country: str, source: str) -> Optional[tuple[str, str]]:
       
        if source == "v2":
            pool = self.v2_pools.get(country, [])
            if pool:
                rec = pool.pop()
                if not pool:
                    self.v2_exhausted_once[country] = True
                return ("v2", rec)
        else:  # v1
            self._ensure_v1_pool(country)
            pool = self.v1_pools.get(country, [])
            if pool:
                rec = pool.pop()
                if not pool:
                    self.v1_exhausted_once[country] = True
                    del self.v1_pools[country]
                return ("v1", rec)
        return None

    def _refill_v1(self, country: str) -> None:
        """Re-shuffle V1 pool from disk (starts a new rotation cycle for V1)."""
        if country in self.v1_pools:
            del self.v1_pools[country]
        self._ensure_v1_pool(country)

    def _refill_v2(self, country: str) -> None:
        """Re-shuffle V2 pool from disk (starts a new rotation cycle for V2)."""
        if not self.v2_path.exists():
            return
        per_country: list[str] = []
        with self.v2_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line or line.startswith("#"):
                    continue
                c = line.split("|", 1)[0]
                if c == country:
                    per_country.append(line)
        seen: set[str] = set()
        unique: list[str] = []
        for r in per_country:
            addr = r.split("|")[2] if len(r.split("|")) >= 3 else r
            if addr in seen:
                continue
            seen.add(addr)
            unique.append(r)
        random.shuffle(unique)
        self.v2_pools[country] = unique

    # -----------------------------------------------------------------
    # Country name resolution (case-insensitive + aliases)
    # -----------------------------------------------------------------
    def _resolve_country(self, country: str) -> Optional[str]:
        country = country.strip()
        if country in ALLOWED_COUNTRIES:
            return country
        low = country.lower()
        for k in ALLOWED_COUNTRIES:
            if k.lower() == low:
                return k
        if low in COUNTRY_ALIASES:
            return COUNTRY_ALIASES[low]
        return None

    @staticmethod
    def _parse(record: str, source: str = "v1") -> dict:
        parts = record.split("|")
        if len(parts) != 6:
            parts += [""] * (6 - len(parts))
        out = dict(zip(FIELDS, parts))
        out["source"] = source
        return out

    # -----------------------------------------------------------------
    # /countries status endpoint
    # -----------------------------------------------------------------
    def status(self) -> dict:
        out = {}
        for c in sorted(ALLOWED_COUNTRIES):
            v2_size = len(self.v2_pools.get(c, []))
            v1_size = len(self.v1_pools.get(c, [])) if c in self.v1_pools else "not-loaded"
            v1_total = (self.v1_index[c][1] - self.v1_index[c][0] + 1) if c in self.v1_index else 0
            sc = self.served_count.get(c, {"v1": 0, "v2": 0, "total": 0})
            out[c] = {
                "v2_in_pool":      v2_size,
                "v1_in_pool":      v1_size,
                "v1_total":        v1_total,
                "next_source":     self.next_source.get(c, "v1"),
                "v2_exhausted":    self.v2_exhausted_once.get(c, False),
                "v1_exhausted":    self.v1_exhausted_once.get(c, False),
                "served_v1":       sc["v1"],
                "served_v2":       sc["v2"],
                "served_total":    sc["total"],
            }
        return out

store = DataStore(V1_FILE, V2_FILE)


@app.on_event("startup")
def _startup():
    store.init()


@app.get("/")
def root():
    """Service info."""
    return {
        "service": "Random Person Data API (v3.1 - round-robin + auto-download)",
        "endpoint": "/country={country_name}",
        "allowed_countries": sorted(ALLOWED_COUNTRIES),
        "data_sources": {
            "v1": {
                "path": str(V1_FILE),
                "remote_url": REMOTE_URL,
                "type": "1.5M records with real OSM street names + random house # (auto-downloaded on first run if missing)",
                "local_cached": V1_FILE.exists(),
            },
            "v2": {
                "path": str(V2_FILE),
                "type": "10,754 REAL OSM addresses - house # AND street both real (ships with the repo, ~1.1 MB)",
            },
        },
        "serving_strategy": "round-robin: V1 <-> V2 alternating per request. "
                            "Falls through to the other pool when next-up is exhausted.",
        "usage_examples": [
            "/country=USA",
            "/country=Australia",
            "/country=India",
            "/country=Germany",
            "/country=France",
            "/country=UK",
            "/country=Canada",
        ],
        "aliases_supported": list(COUNTRY_ALIASES.keys())[:15],
    }


@app.get("/country={country_name}")
def get_person(country_name: str):
   
    rec = store.get_random(country_name)
    if rec is None:
        raise HTTPException(
            status_code=404,
            detail=f"Country {country_name!r} not available. "
                   f"This API only serves: {sorted(ALLOWED_COUNTRIES)}. "
                   f"Try /country=USA or /country=Germany."
        )
    return rec


@app.get("/random")
def random_any(
    country: Optional[str] = Query(None, description="Optional country filter (must be in allowlist)"),
):

    if country:
        rec = store.get_random(country)
        if rec is None:
            raise HTTPException(
                status_code=404,
                detail=f"Country {country!r} not available. "
                       f"Allowed: {sorted(ALLOWED_COUNTRIES)}",
            )
        return rec
    key = random.choice(sorted(ALLOWED_COUNTRIES))
    rec = store.get_random(key)
    if rec is None:
        raise HTTPException(status_code=503, detail="No data loaded")
    return rec


@app.get("/countries")
def list_countries():
    """Per-country pool status (only allowed countries are shown)."""
    return store.status()


@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "v2_loaded": bool(store.v2_pools),
        "v1_indexed": bool(store.v1_index),
        "v1_local_cached": V1_FILE.exists(),
        "remote_url": REMOTE_URL,
        "strategy": "round-robin",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
