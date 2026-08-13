from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/generate_apollo_ghidra_chunks.py"
SPEC = importlib.util.spec_from_file_location("generate_apollo_ghidra_chunks", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
chunks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(chunks)


class ApolloGhidraChunkTests(unittest.TestCase):
    def test_authenticated_stock_image(self) -> None:
        chunks.authenticate_firmware(
            ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
        )

    def test_default_boundaries_tile_application_exactly(self) -> None:
        boundaries = chunks.chunk_boundaries()
        self.assertEqual(len(boundaries), 65)
        self.assertEqual(boundaries[0], chunks.APPLICATION_START)
        self.assertEqual(boundaries[-1], chunks.APPLICATION_END)
        sizes = [right - left for left, right in zip(boundaries, boundaries[1:])]
        self.assertEqual(sum(sizes), chunks.APPLICATION_END - chunks.APPLICATION_START)
        self.assertTrue(all(size > 0 and size % 2 == 0 for size in sizes))
        self.assertLessEqual(max(sizes) - min(sizes), 2)

    def test_manifest_has_64_data_rows_and_exact_file_offsets(self) -> None:
        rows = [
            line.split("\t")
            for line in chunks.render_manifest().splitlines()
            if line and not line.startswith("#")
        ]
        self.assertEqual(len(rows), 64)
        self.assertEqual(rows[0], [
            "apollo-00", "0x00438000", "0x0044570C", "0x00000020", "0x0000D72C"
        ])
        self.assertEqual(rows[-1][2], "0x00794324")
        self.assertEqual(int(rows[-1][4], 16), chunks.EXPECTED_FIRMWARE_SIZE)

    def test_function_balancing_tiles_range_and_distributes_entries(self) -> None:
        entries = [chunks.APPLICATION_START + index * 2 for index in range(640)]
        boundaries = chunks.balanced_boundaries(entries)
        self.assertEqual(len(boundaries), 65)
        self.assertEqual(boundaries[0], chunks.APPLICATION_START)
        self.assertEqual(boundaries[-1], chunks.APPLICATION_END)
        counts = [
            sum(start <= entry < end for entry in entries)
            for start, end in zip(boundaries, boundaries[1:])
        ]
        self.assertEqual(sum(counts), 640)
        self.assertLessEqual(max(counts) - min(counts), 1)


if __name__ == "__main__":
    unittest.main()
