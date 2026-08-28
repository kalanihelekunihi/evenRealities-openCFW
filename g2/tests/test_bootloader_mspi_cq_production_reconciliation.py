from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
BUILDER = ROOT / "components/bootloader/core_overlay/build_component.py"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

ROUTES = (
    ("open_cfw_bootloader_mspi_cq_init_423f28", 0x00423F28, 0x00423F54,
     "8e2e5409620c3c1b334d8c3ede2ea19b20a31471e40a0c8b0c88f6550a7e9b05",
     "GPL-3.0-or-later"),
    ("open_cfw_bootloader_mspi_cq_term_423f54", 0x00423F54, 0x00423F8E,
     "07a7e8e54305fbecb7f891cd4e843881b73a33186ba1750b147e0647d0041807",
     "GPL-3.0-or-later"),
    ("open_cfw_bootloader_mspi_cq_enable_423f8e", 0x00423F8E, 0x00423FAC,
     "b846c512f60e83e86f69d04322eb6ce0d5936f143ad86475967c6be67545ab65",
     "GPL-3.0-or-later"),
    ("open_cfw_bootloader_mspi_cq_disable_423fac", 0x00423FAC, 0x00423FB8,
     "8c21c4878a3125546a7201b39610d661f69d8da7e1cae81d3eb223fdf919fb0a",
     "GPL-3.0-or-later"),
    ("open_cfw_bootloader_mspi_cq_pause_423fb8", 0x00423FB8, 0x0042403E,
     "ff20411c8e4283f16d82cb8373e95004d648e4c03d151ba89bf43ff7d58a2794",
     "BSD-3-Clause"),
    ("open_cfw_bootloader_mspi_program_dma_42403e", 0x0042403E, 0x004240AA,
     "d075d73aba138735bc9229bcf8672cb6a1c2fadec21985d2159043534ad130e1",
     "BSD-3-Clause"),
    ("open_cfw_bootloader_mspi_sched_hiprio_4240aa", 0x004240AA, 0x00424120,
     "dfbd51c61eba1ea51418a1faeaaa99df5aebb0ea900ed157a0c3a55a7b28d144",
     "BSD-3-Clause"),
)


class BootloaderMspiCqProductionReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="open-cfw-cq-production-")
        subprocess.run(
            [sys.executable, str(BUILDER), "--output-dir", cls.tmp.name],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        cls.report = json.loads(
            (Path(cls.tmp.name) / "build-report.json").read_text(encoding="utf-8")
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_routes_are_contiguous_and_exact_stock(self) -> None:
        image = OFFICIAL.read_bytes()
        self.assertEqual(ROUTES[0][1], 0x00423F28)
        self.assertEqual(ROUTES[-1][2], 0x00424120)
        for left, right in zip(ROUTES, ROUTES[1:]):
            self.assertEqual(left[2], right[1])
        for _name, start, end, expected_hash, _license in ROUTES:
            body = image[start - 0x00410000:end - 0x00410000]
            self.assertEqual(len(body), end - start)
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected_hash)

    def test_overlay_pins_source_license_evidence_and_linked_bytes(self) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaves = {row["function"]: row for row in config["in_place_leaves"]}
        built = {row["extraction"]["function"]: row
                 for row in self.report["in_place_leaves"]}
        for name, start, end, expected_hash, expected_license in ROUTES:
            configured = leaves[name]
            self.assertEqual(configured["runtime_address"], start)
            self.assertEqual(configured["expected"], {
                "size": end - start,
                "sha256": expected_hash,
                "unrelocated_sha256": configured["expected"]["unrelocated_sha256"],
            })
            self.assertEqual(configured["stock"], {
                "size": end - start, "sha256": expected_hash,
            })
            self.assertEqual(configured["source"]["license"], expected_license)
            evidence = ROOT / configured["source"]["evidence"]
            self.assertTrue(evidence.is_file(), evidence)
            source = ROOT / configured["source"]["path"]
            self.assertEqual(source.stat().st_size, configured["source"]["size"])
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),
                             configured["source"]["sha256"])
            self.assertEqual(built[name]["extraction"]["sha256"], expected_hash)
            self.assertEqual(built[name]["placement"]["stock_sha256"], expected_hash)

    def test_manifest_frontier_and_component_accounting_are_exact(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        regions = manifest["component_overrides"]["apollo_bootloader"]["regions"]
        selected = [row for row in regions
                    if 0x00423F28 <= row["target_address"] < 0x00426506]
        self.assertEqual(
            [(row["target_address"], row["size"], row["address_status"])
             for row in selected[:7]],
            [(0x00423F28, 44, "source_compiled"),
             (0x00423F54, 58, "source_compiled"),
             (0x00423F8E, 30, "source_compiled"),
             (0x00423FAC, 12, "source_compiled"),
             (0x00423FB8, 134, "source_compiled"),
             (0x0042403E, 108, "source_compiled"),
             (0x004240AA, 118, "source_compiled")],
        )
        self.assertEqual(
            (selected[7]["target_address"], selected[7]["size"],
             selected[7]["address_status"]),
            (0x00424120, 9190, "official_blob"),
        )
        self.assertEqual(self.report["component"]["source_owned_bytes"], 25869)
        self.assertEqual(self.report["component"]["opaque_base_bytes"], 121427)
        residual = OFFICIAL.read_bytes()[0x14120:0x16506]
        self.assertEqual(hashlib.sha256(residual).hexdigest(),
                         "fc2983e5f8dc3fff4bb4c1df407539aba19244b55b7f5c92fb68e1d196274bdb")

    def test_upstream_snapshot_preserves_bsd_license_and_provider_abi(self) -> None:
        provenance = json.loads((
            ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json"
        ).read_text(encoding="utf-8"))
        self.assertEqual(provenance["license"], "BSD-3-Clause")
        self.assertEqual(provenance["upstream"]["selected_commit"],
                         "5efc0228528a8adce5eae0d226fac85d2551eb3b")
        header = (ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/"
                  "am_hal_cmdq.h").read_text(encoding="utf-8")
        for symbol in ("am_hal_cmdq_term", "am_hal_cmdq_enable",
                       "am_hal_cmdq_disable"):
            self.assertIn(symbol, header)


if __name__ == "__main__":
    unittest.main()
