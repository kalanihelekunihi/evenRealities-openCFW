# SPDX-License-Identifier: MIT
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("firmware_cut", HERE / "firmware_cut.py")
fc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fc)


class FirmwareCutTest(unittest.TestCase):
    def test_all_manifests_cover_and_name_known_blockers(self):
        valid = fc.blocker_ids()
        for manifest in fc.load_manifests():
            fc.check_manifest(manifest, valid)

    def test_gap_is_rejected(self):
        m = {"payload": "x", "size": 8, "regions": [
            {"label": "a", "start": "0x0", "end": "0x4", "state": "retained", "blockers": ["OPEN-PENDING"]},
            {"label": "b", "start": "0x5", "end": "0x8", "state": "retained", "blockers": ["OPEN-PENDING"]}]}
        with self.assertRaises(fc.CutError):
            fc.check_manifest(m, fc.blocker_ids())

    def test_retained_without_blocker_is_rejected(self):
        m = {"payload": "x", "size": 4, "regions": [
            {"label": "a", "start": "0x0", "end": "0x4", "state": "retained", "blockers": []}]}
        with self.assertRaises(fc.CutError):
            fc.check_manifest(m, fc.blocker_ids())

    def test_unknown_blocker_is_rejected(self):
        m = {"payload": "x", "size": 4, "regions": [
            {"label": "a", "start": "0x0", "end": "0x4", "state": "retained", "blockers": ["NOPE"]}]}
        with self.assertRaises(fc.CutError):
            fc.check_manifest(m, fc.blocker_ids())

    def test_reassembly_is_byte_identical_when_payloads_present(self):
        manifests = [m for m in fc.load_manifests() if (fc.REPO / m["official"]).is_file()]
        if not manifests:
            self.skipTest("official payloads not present")
        for manifest in manifests:
            self.assertEqual(fc.sha256(fc.assemble(manifest, None)), manifest["sha256"])

    def test_source_region_must_match_stock(self):
        manifest = next((m for m in fc.load_manifests() if m["payload"] == "g2-touch"), None)
        if manifest is None or not (fc.REPO / manifest["official"]).is_file():
            self.skipTest("touch payload not present")
        stock = fc.official_bytes(manifest)
        first = dict(manifest["regions"][0], state="source")
        first.pop("blockers", None)
        edited = dict(manifest, regions=[first] + manifest["regions"][1:])
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / manifest["payload"]
            out.mkdir()
            end = int(first["end"], 16)
            (out / f"{first['label']}.bin").write_bytes(stock[:end])
            self.assertEqual(fc.assemble(edited, Path(tmp)), stock)
            (out / f"{first['label']}.bin").write_bytes(b"\0" * end)
            with self.assertRaises(fc.CutError):
                fc.assemble(edited, Path(tmp))


if __name__ == "__main__":
    unittest.main()
