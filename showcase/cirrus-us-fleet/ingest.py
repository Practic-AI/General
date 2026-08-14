#!/usr/bin/env python3
"""Download the FAA Releasable Aircraft Database and write a PII-stripped Cirrus extract.

Owner name, street, city, ZIP, county, and 'other names' are dropped and never
written to the processed file. N-numbers stay — they are painted on the airframe
and already public.

Not affiliated with Cirrus Aircraft.
"""
from __future__ import annotations

import csv
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "_raw"
UNZIPPED = RAW / "unzipped"
PROCESSED = ROOT / "data" / "processed"
FAA_ZIP_URL = "https://registry.faa.gov/database/ReleasableAircraft.zip"
USER_AGENT = "Practic-AI cirrus-us-fleet showcase (public FAA registry; PII stripped)"

# Columns we keep. Everything else in MASTER is either PII or unused.
KEEP = [
    "N-NUMBER",
    "SERIAL NUMBER",
    "MFR MDL CODE",
    "YEAR MFR",
    "TYPE REGISTRANT",
    "STATE",
    "REGION",
    "COUNTRY",
    "LAST ACTION DATE",
    "CERT ISSUE DATE",
    "TYPE AIRCRAFT",
    "TYPE ENGINE",
    "STATUS CODE",
    "FRACT OWNER",
    "AIR WORTH DATE",
]

PII_NEVER_KEEP = {
    "NAME",
    "STREET",
    "STREET2",
    "CITY",
    "ZIP CODE",
    "COUNTY",
    "OTHER NAMES(1)",
    "OTHER NAMES(2)",
    "OTHER NAMES(3)",
    "OTHER NAMES(4)",
    "OTHER NAMES(5)",
}

PRODUCTION_MODELS = {"SR20", "SR22", "SR22T", "SF50"}


def _clean(name: str | None) -> str:
    return (name or "").lstrip("\ufeff").strip()


def _row(raw: dict) -> dict:
    return {_clean(k): (v or "").strip() for k, v in raw.items() if k is not None}


def download_zip(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1_000_000:
        print(f"using cached zip ({dest.stat().st_size:,} bytes)")
        return dest
    print(f"downloading {FAA_ZIP_URL}")
    req = Request(FAA_ZIP_URL, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=180) as resp:
        dest.write_bytes(resp.read())
    print(f"wrote {dest} ({dest.stat().st_size:,} bytes)")
    return dest


def extract_zip(zpath: Path) -> Path:
    UNZIPPED.mkdir(parents=True, exist_ok=True)
    needed = ["MASTER.txt", "ACFTREF.txt"]
    if all((UNZIPPED / n).exists() for n in needed):
        print("using extracted MASTER/ACFTREF")
        return UNZIPPED
    with zipfile.ZipFile(zpath) as zf:
        for name in needed:
            zf.extract(name, UNZIPPED)
    return UNZIPPED


def cirrus_codes(acftref: Path) -> dict[str, tuple[str, str]]:
    codes: dict[str, tuple[str, str]] = {}
    with acftref.open(encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = _row(raw)
            mfr = row.get("MFR", "").upper()
            if "CIRRUS" not in mfr:
                continue
            codes[row["CODE"]] = (row.get("MFR", ""), row.get("MODEL", ""))
    return codes


def model_family(model: str) -> str:
    if model == "SF50":
        return "Vision Jet"
    if model in {"SR20", "SR22", "SR22T", "SR10", "SRT"}:
        return "SR Series"
    return "Other / experimental"


def parse_year(value: str) -> str:
    v = value.strip()
    if len(v) == 4 and v.isdigit() and 1990 <= int(v) <= 2030:
        return v
    return ""


def write_extract(master: Path, codes: dict[str, tuple[str, str]], out: Path) -> dict:
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    missing_year = 0
    fieldnames = [
        "n_number",
        "serial_number",
        "mfr_mdl_code",
        "mfr",
        "model",
        "model_family",
        "is_production_model",
        "year_mfr",
        "type_registrant",
        "state",
        "region",
        "country",
        "last_action_date",
        "cert_issue_date",
        "airworth_date",
        "type_aircraft",
        "type_engine",
        "status_code",
        "fract_owner",
    ]
    with master.open(encoding="utf-8-sig", errors="replace", newline="") as src, out.open(
        "w", encoding="utf-8", newline=""
    ) as dst:
        reader = csv.DictReader(src)
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        for raw in reader:
            row = _row(raw)
            # belt-and-suspenders: never copy PII even if KEEP is edited later
            for key in PII_NEVER_KEEP:
                row.pop(key, None)
            code = row.get("MFR MDL CODE", "")
            if code not in codes:
                continue
            mfr, model = codes[code]
            year = parse_year(row.get("YEAR MFR", ""))
            if not year:
                missing_year += 1
            writer.writerow(
                {
                    "n_number": row.get("N-NUMBER", ""),
                    "serial_number": row.get("SERIAL NUMBER", ""),
                    "mfr_mdl_code": code,
                    "mfr": mfr,
                    "model": model,
                    "model_family": model_family(model),
                    "is_production_model": "1" if model in PRODUCTION_MODELS else "0",
                    "year_mfr": year,
                    "type_registrant": row.get("TYPE REGISTRANT", ""),
                    "state": row.get("STATE", ""),
                    "region": row.get("REGION", ""),
                    "country": row.get("COUNTRY", ""),
                    "last_action_date": row.get("LAST ACTION DATE", ""),
                    "cert_issue_date": row.get("CERT ISSUE DATE", ""),
                    "airworth_date": row.get("AIR WORTH DATE", ""),
                    "type_aircraft": row.get("TYPE AIRCRAFT", ""),
                    "type_engine": row.get("TYPE ENGINE", "").strip(),
                    "status_code": row.get("STATUS CODE", ""),
                    "fract_owner": row.get("FRACT OWNER", ""),
                }
            )
            n += 1

    meta = {
        "source": FAA_ZIP_URL,
        "source_name": "FAA Releasable Aircraft Database (MASTER + ACFTREF)",
        "extracted_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cirrus_rows": n,
        "missing_year_mfr": missing_year,
        "pii_dropped": sorted(PII_NEVER_KEEP),
        "output": str(out.relative_to(ROOT)).replace("\\", "/"),
        "affiliation": "Not affiliated with Cirrus Aircraft.",
    }
    (out.parent / "snapshot_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"wrote {n:,} Cirrus rows → {out} (missing year_mfr={missing_year})")
    return meta


def main() -> None:
    zpath = download_zip(RAW / "ReleasableAircraft.zip")
    folder = extract_zip(zpath)
    codes = cirrus_codes(folder / "ACFTREF.txt")
    print(f"Cirrus make/model codes: {len(codes)}")
    write_extract(folder / "MASTER.txt", codes, PROCESSED / "cirrus_us_fleet.csv")


if __name__ == "__main__":
    main()
