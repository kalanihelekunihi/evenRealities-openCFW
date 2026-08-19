#!/usr/bin/env python3
"""Fail-closed tests for the one-use BLE source transition."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


R1 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R1 / "tools"))

from package_r1_ble_transition import (  # noqa: E402
    RETAIL_BOOT_START,
    RECOVERED_LF_CLOCK_CONFIG,
    TRANSITION_BYTES_MAX,
    linked_load_size,
    validate_transition,
)


class TransitionTests(unittest.TestCase):
    def test_transition_source_preserves_proven_boot_entry_order(self) -> None:
        source = (
            R1
            / "research/bootloader-reconstruction/firmware-project/src/r1_transition_main.c"
        ).read_text(encoding="utf-8")
        main = source[source.index("int main(void)") :]
        self.assertLess(
            main.index("nrf_bootloader_mbr_addrs_populate()"),
            main.index("staged_source_image(&source)"),
        )
        self.assertIn("nrf_dfu_settings_reinit();", source)
        self.assertNotIn("nrf_dfu_settings_init(false)", source)
        self.assertLess(
            source.index("copy_page(0u, source)"),
            source.index("crc32_compute((const uint8_t *)0u"),
        )

    def test_recovered_ring_lf_clock_is_pinned(self) -> None:
        config = (
            R1
            / "research/bootloader-reconstruction/firmware-project/config/r1_recovered_config.h"
        ).read_text(encoding="utf-8")
        for define in (
            "#define NRF_SDH_CLOCK_LF_SRC 0",
            "#define NRF_SDH_CLOCK_LF_RC_CTIV 16",
            "#define NRF_SDH_CLOCK_LF_RC_TEMP_CTIV 2",
            "#define NRF_SDH_CLOCK_LF_ACCURACY 1",
        ):
            self.assertIn(define, config)

    def test_transition_validation_pins_vector_and_owner_key(self) -> None:
        key = bytes(range(64))
        image = bytearray(b"\xff" * TRANSITION_BYTES_MAX)
        image[0:4] = (0x20040000).to_bytes(4, "little")
        image[4:8] = (RETAIL_BOOT_START + 0x101).to_bytes(4, "little")
        image[0x100:0x140] = key
        image[0x180:0x184] = RECOVERED_LF_CLOCK_CONFIG
        validate_transition(bytes(image), key)
        image[0x200:0x240] = key
        with self.assertRaisesRegex(ValueError, "exactly one owner trust anchor"):
            validate_transition(bytes(image), key)

    def test_linked_load_size_uses_text_plus_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            size_tool = root / "size"
            size_tool.write_text(
                "#!/bin/sh\nprintf 'text data bss dec hex filename\\n24144 184 21976 46304 b4e0 image\\n'\n",
                encoding="utf-8",
            )
            size_tool.chmod(0o755)
            self.assertEqual(linked_load_size(size_tool, root / "image"), 24328)


if __name__ == "__main__":
    unittest.main()
