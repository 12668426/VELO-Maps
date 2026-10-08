"""Public metadata validation. Never authenticates or installs a map package."""
import argparse
import datetime
import json
import re
from pathlib import Path

REPOSITORY = "12668426/VELO-Maps"
PROVINCES = set("BJ TJ HE SX NM LN JL HL SH JS ZJ AH FJ JX SD HA HB HN GD GX HI CQ SC GZ YN XZ SN GS QH NX XJ HK MO TW".split())
BASE = {"regionID", "name", "coverage", "status"}
DOWNLOAD = {"version", "asset", "downloadURL", "bytes", "sha256", "contentChecksum",
            "osmTimestamp", "sourceURL", "sourceSHA256", "license", "boundsWGS84"}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate(catalog):
    require(isinstance(catalog, dict), "catalog must be an object")
    require(set(catalog) == {"schemaVersion", "repository", "updatedAt", "provinces", "pilotPackages"}, "unknown/missing catalog fields")
    require(type(catalog["schemaVersion"]) is int and catalog["schemaVersion"] == 1, "unsupported schema")
    require(catalog["repository"] == REPOSITORY, "wrong repository")
    require(isinstance(catalog["updatedAt"], str), "invalid date")
    datetime.date.fromisoformat(catalog["updatedAt"])
    seen = set()
    for group, coverage in (("provinces", "province"), ("pilotPackages", "city-bbox")):
        items = catalog[group]
        require(isinstance(items, list) and len(items) <= 100, "invalid catalogue group")
        for item in items:
            require(isinstance(item, dict), "entry must be an object")
            require(BASE <= set(item), "missing identity fields")
            rid = item["regionID"]
            require(isinstance(rid, str) and re.fullmatch(r"CN-[A-Z]{2}(?:-[A-Z0-9]{1,12})?", rid), "invalid region ID")
            require(rid not in seen, "duplicate region ID")
            seen.add(rid)
            require(isinstance(item["name"], str) and 0 < len(item["name"]) <= 100, "invalid name")
            require(item["coverage"] == coverage, "group/coverage mismatch")
            if group == "provinces":
                require(rid[3:] in PROVINCES, "unknown province")
            else:
                require(len(rid.split("-")) == 3 and rid.split("-")[1] in PROVINCES, "invalid city pilot")
            require(item["status"] in ("preparing", "available"), "unknown status")
            if item["status"] == "preparing":
                require(set(item) == BASE, "unpublished package must not advertise a download")
                continue
            require(set(item) == BASE | DOWNLOAD, "available package needs exact download fields")
            tag = item["version"]
            require(isinstance(tag, str) and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}", tag), "invalid tag")
            require(item["asset"] == rid + ".vmap", "asset/region mismatch")
            expected = f"https://github.com/{REPOSITORY}/releases/download/{tag}/{rid}.vmap"
            require(item["downloadURL"] == expected, "unsafe or inconsistent download URL")
            require(type(item["bytes"]) is int and 0 < item["bytes"] < 2 * 1024**3, "invalid asset bytes")
            for key in ("sha256", "contentChecksum", "sourceSHA256"):
                require(isinstance(item[key], str) and re.fullmatch(r"[0-9a-f]{64}", item[key]), "invalid " + key)
            require(isinstance(item["osmTimestamp"], str), "invalid source timestamp")
            timestamp = datetime.datetime.fromisoformat(item["osmTimestamp"].replace("Z", "+00:00"))
            require(timestamp.utcoffset() == datetime.timedelta(0), "source timestamp must be UTC")
            require(isinstance(item["sourceURL"], str) and re.fullmatch(r"https://download\.geofabrik\.de/[a-z0-9/_-]+\.html", item["sourceURL"]), "unsafe source URL")
            require(item["license"] == "ODbL-1.0", "missing data license")
            bounds = item["boundsWGS84"]
            require(isinstance(bounds, dict) and set(bounds) == {"minLon", "maxLon", "minLat", "maxLat"}, "invalid bounds")
            require(all(type(value) in (int, float) for value in bounds.values()), "invalid bound values")
            require(-180 <= bounds["minLon"] < bounds["maxLon"] <= 180 and -90 <= bounds["minLat"] < bounds["maxLat"] <= 90, "bounds out of range")
    require({item["regionID"][3:] for item in catalog["provinces"]} == PROVINCES, "expected all 34 province-level entries")

def read_catalog(path):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    require(path.stat().st_size <= 256 * 1024, "catalog exceeds 256 KiB")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args()
    try:
        validate(read_catalog(args.catalog))
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(1, f"INVALID: {error}\n")
    print("VALID: 34 province-level entries; download identity/metadata checked (not package content)")
