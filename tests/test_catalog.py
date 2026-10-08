import copy
import json
import tempfile
import unittest
from pathlib import Path

from validate_catalog import read_catalog, validate

ROOT = Path(__file__).resolve().parents[1]

class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = read_catalog(ROOT / "catalog.json")

    def available(self):
        self.catalog["pilotPackages"] = [{
            "regionID": "CN-AH-HN", "name": "淮南市试点", "coverage": "city-bbox", "status": "available",
            "version": "huainan-20261003-v1", "asset": "CN-AH-HN.vmap",
            "downloadURL": "https://github.com/12668426/VELO-Maps/releases/download/huainan-20261003-v1/CN-AH-HN.vmap",
            "bytes": 20129324, "sha256": "a" * 64, "contentChecksum": "b" * 64,
            "osmTimestamp": "2026-10-03T20:20:50Z", "sourceURL": "https://download.geofabrik.de/asia/china/anhui.html",
            "sourceSHA256": "c" * 64, "license": "ODbL-1.0",
            "boundsWGS84": {"minLon": 116.35, "maxLon": 117.21, "minLat": 31.90, "maxLat": 33.01}}]
        return self.catalog["pilotPackages"][0]

    def test_current_catalog(self):
        validate(self.catalog)

    def test_valid_pilot(self):
        self.available()
        validate(self.catalog)

    def test_preparing_has_no_fake_download(self):
        self.catalog["provinces"][0]["bytes"] = 1
        with self.assertRaises(ValueError): validate(self.catalog)

    def test_missing_province_and_duplicate(self):
        for change in (lambda c: c["provinces"].pop(), lambda c: c["provinces"].append(copy.deepcopy(c["provinces"][0]))):
            c = copy.deepcopy(self.catalog)
            change(c)
            with self.assertRaises(ValueError): validate(c)

    def test_available_requires_real_metadata(self):
        self.catalog["provinces"][0]["status"] = "available"
        with self.assertRaises(ValueError): validate(self.catalog)

    def test_city_cannot_be_province(self):
        item = self.available()
        item["coverage"] = "province"
        with self.assertRaises(ValueError): validate(self.catalog)

    def test_urls_and_path_injection(self):
        item = self.available()
        for value in ("http://github.com/a", "https://evil.test/a", "https://github.com/12668426/VELO/releases/download/v1/a.vmap", item["downloadURL"] + "?token=x"):
            item["downloadURL"] = value
            with self.assertRaises(ValueError): validate(self.catalog)
        item["version"] = "../main"
        with self.assertRaises(ValueError): validate(self.catalog)

    def test_invalid_hash_and_size(self):
        for key, values in (("sha256", ("", "ABC", "A" * 64)), ("bytes", (0, -1, True, 2 * 1024**3))):
            for value in values:
                self.available()[key] = value
                with self.assertRaises(ValueError): validate(self.catalog)

    def test_asset_identity(self):
        self.available()["asset"] = "CN-AH.vmap"
        with self.assertRaises(ValueError): validate(self.catalog)

    def test_schema_repository_and_bounds(self):
        for key, value in (("schemaVersion", 2), ("schemaVersion", True), ("repository", "other/repo")):
            c = copy.deepcopy(self.catalog)
            c[key] = value
            with self.assertRaises(ValueError): validate(c)
        self.available()["boundsWGS84"]["maxLat"] = 100
        with self.assertRaises(ValueError): validate(self.catalog)

    def test_duplicate_keys_and_size_limit(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "test.json"
            path.write_text('{"schemaVersion":1,"schemaVersion":2}')
            with self.assertRaises(ValueError): read_catalog(path)
            path.write_bytes(b" " * (256 * 1024 + 1))
            with self.assertRaises(ValueError): read_catalog(path)

    def test_timestamp_and_license(self):
        for key, value in (("osmTimestamp", "no timestamp"), ("osmTimestamp", "2026-10-03T21:20:50+01:00"), ("license", "proprietary")):
            self.available()[key] = value
            with self.assertRaises(ValueError): validate(self.catalog)

if __name__ == "__main__":
    unittest.main()
