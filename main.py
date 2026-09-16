"""

Endpoint
--------
    GET /country={country_name}

If REMOTE_URL is set, V1 is fetched from there instead of the local file.
V2 is always loaded from the local file (it's small).
"""

from __future__ import annotations

import random
import threading
from collections import defaultdict
from pathlib import Path
from typing import Optional

import requests
from fastapi import FastAPI, HTTPException, Query

REMOTE_URL = ""


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
    version="3.0.0",
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
    "fr": "France",
    "in": "India",
    "ca": "Canada",
    "au": "Australia",
}

class DataStore:
 
    def __init__(self, v1_path: Path, v2_path: Path):
        self.v1_path = v1_path
        self.v2_path = v2_path
        self.lock = threading.Lock()

       
        self.v2_pools: dict[str, list[str]] = {}
        self.v1_pools: dict[str, list[str]] = {}

       
        self.v1_index: dict[str, tuple[int, int]] = {}

        
        self.v2_exhausted_once: dict[str, bool] = {}
        
        self.v1_exhausted_once: dict[str, bool] = {}

        
        self.next_source: dict[str, str] = {}

        
        self.served_count: dict[str, dict[str, int]] = defaultdict(
            lambda: {"v1": 0, "v2": 0, "total": 0}
        )

        
        self._remote_text: Optional[str] = None
        self._remote_loaded = False

   
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

    
    def _load_remote_v1(self) -> bool:
        if self._remote_loaded:
            return True
        if not REMOTE_URL:
            return False
        try:
            r = requests.get(REMOTE_URL, timeout=60)
            r.raise_for_status()
        except Exception as e:
            print(f"[!] Failed to fetch REMOTE_URL: {e}")
            return False
        self._remote_text = r.text
        per_country: dict[str, list[str]] = defaultdict(list)
        for line in self._remote_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            country = line.split("|", 1)[0]
            if country in ALLOWED_COUNTRIES:
                per_country[country].append(line)
        for c in ALLOWED_COUNTRIES:
            recs = per_country.get(c, [])
            random.shuffle(recs)
            self.v1_pools[c] = recs
            self.v1_exhausted_once[c] = False
            self.v1_index[c] = (1, len(recs))
        self._remote_loaded = True
        total = sum(len(v) for v in self.v1_pools.values())
        print(f"[+] V1 remote loaded: {total:,} records across {len(self.v1_pools)} countries")
        return True

    
    def init(self) -> None:
        self._load_v2()
        if REMOTE_URL:
            ok = self._load_remote_v1()
            if not ok:
                print("[!] Remote URL failed, falling back to local V1 file")
                self._build_v1_index()
        else:
            self._build_v1_index()
        print(f"[+] Allowlist: {sorted(ALLOWED_COUNTRIES)}")
        print(f"[+] V2 pools ready: {sum(len(v) for v in self.v2_pools.values()):,} real-OSM records")
        if self._remote_loaded:
            print(f"[+] V1 pools ready:  {sum(len(v) for v in self.v1_pools.values()):,} records (from REMOTE_URL)")
        elif self.v1_index:
            print(f"[+] V1 indexed (lazy-load on first request): {self.v1_path}")
        print(f"[+] Serving strategy: round-robin V1 <-> V2 (alternating per request)")
        
        
    def get_random(self, country: str) -> Optional[dict]:
        """Round-robin serve: alternate between V1 and V2 per request.
        Falls through to the other pool when next-up is empty."""
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

            # Track which source actually served (could be different from preferred
            # if we fell through)
            source_tag = "v2_real_osm" if record[0] == "v2" else "v1_synthetic"
            self.served_count[key][record[0]] += 1
            return self._parse(record[1], source=source_tag)

    def _pop_from(self, country: str, source: str) -> Optional[tuple[str, str]]:
        """Try to pop one record from the named pool.
        Returns (source, record_string) or None if empty."""
        if source == "v2":
            pool = self.v2_pools.get(country, [])
            if pool:
                rec = pool.pop()
                if not pool:
                    self.v2_exhausted_once[country] = True
                return ("v2", rec)
        else:  # v1
            if not self._remote_loaded:
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
        # Drop any existing (probably empty) V1 pool, then re-load
        if country in self.v1_pools:
            del self.v1_pools[country]
        self._ensure_v1_pool(country)

    def _refill_v2(self, country: str) -> None:
        """Re-shuffle V2 pool from disk (starts a new rotation cycle for V2)."""
        # Reload V2 file (small) for this country
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
        # Dedupe
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


# =====================================================================
# Startup
# =====================================================================
store = DataStore(V1_FILE, V2_FILE)


@app.on_event("startup")
def _startup():
    store.init()


# =====================================================================
# Routes
# =====================================================================
@app.get("/")
def root():
    """Service info."""
    return {
        "service": "Random Person Data API (v3.0 - round-robin)",
        "endpoint": "/country={country_name}",
        "allowed_countries": sorted(ALLOWED_COUNTRIES),
        "data_sources": {
            "v1": {
                "path": str(V1_FILE),
                "remote_url": REMOTE_URL or "(local file used)",
                "type": "real OSM street names + random house # (1.5M records)",
            },
            "v2": {
                "path": str(V2_FILE),
                "type": "REAL OSM addresses - house # AND street both real (10,754 records)",
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
    """Return one random person record for the given country.

    Limited to: Australia, India, France, United Kingdom, Canada, USA, Germany.

    Round-robin: alternates between V1 (synthetic, real streets) and
    V2 (real OSM addresses) per request.  Falls through to the other
    pool when next-up is exhausted.
    """
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
    """Return one random person.  If `country` is omitted, picks one of
    the 7 allowed countries at random."""
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
        "remote_used": bool(store._remote_loaded),
        "strategy": "round-robin",
    }


# =====================================================================
# Run as a script
# =====================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
