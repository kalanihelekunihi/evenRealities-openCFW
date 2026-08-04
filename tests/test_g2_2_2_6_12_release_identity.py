#!/usr/bin/env python3
"""Regression tests for the G2 2.2.6.12 runtime identity relabeling."""

from __future__ import annotations

import importlib.util
import struct
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "releases" / "g2-2.2.6.12" / "build.py"
INTER_LENS_VERSION_OFFSET = 4_267_771


def load_builder():
    spec = importlib.util.spec_from_file_location("g2_2_2_6_12_builder", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def synthetic_evenota(builder) -> bytes:
    """Build the smallest package exercising the builder's pinned absolute offsets."""
    component_offset = 0x100
    payload_start = component_offset + 128
    size = max(builder.EXPECTED_MAIN_VERSION_OFFSETS) + len(builder.OLD_VERSION) + 1
    image = bytearray(size)

    struct.pack_into("<I", image, 8, 1)
    image[builder.PACKAGE_IDENTITY_OFFSET : builder.PACKAGE_IDENTITY_OFFSET + 16] = (
        builder.PACKAGE_IDENTITY_PREFIX + builder.OLD_VERSION
    )
    struct.pack_into("<IIII", image, 0x40, 0, component_offset, 0, 0)
    struct.pack_into("<I", image, component_offset + 8, size - payload_start)
    component_name = b"ota/s200_firmware_ota.bin"
    image[component_offset + 48 : component_offset + 48 + len(component_name)] = (
        component_name
    )
    for offset in builder.EXPECTED_MAIN_VERSION_OFFSETS:
        image[offset : offset + len(builder.OLD_VERSION)] = builder.OLD_VERSION
    return bytes(image)


class G2PointReleaseIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()

    def test_relabel_updates_inter_lens_version_reported_as_left_firmware(self) -> None:
        stock = synthetic_evenota(self.builder)

        release, identity = self.builder.relabel_release(stock, stock)

        end = INTER_LENS_VERSION_OFFSET + len(self.builder.NEW_VERSION)
        self.assertEqual(
            release[INTER_LENS_VERSION_OFFSET:end],
            self.builder.NEW_VERSION,
        )
        self.assertIn(INTER_LENS_VERSION_OFFSET, identity["runtime_offsets"])
        self.assertNotIn(
            INTER_LENS_VERSION_OFFSET,
            identity["preserved_vendor_offsets"],
        )


if __name__ == "__main__":
    unittest.main()
