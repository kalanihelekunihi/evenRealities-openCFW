from __future__ import annotations

import hashlib
import struct
import sys
import unittest
import zlib
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OPENCFW_ROOT / "tools"))

import open_cfw  # noqa: E402
import release_cfw  # noqa: E402


def make_main() -> bytes:
    size = max(release_cfw.RUNTIME_VERSION_FIELDS.values()) + 0x100
    main = bytearray(size)
    struct.pack_into("<I", main, 0, 0x04000000 | size)
    struct.pack_into("<I", main, 0x10, 0xCB)
    struct.pack_into("<I", main, 0x14, open_cfw.MAIN_RUN_BASE)
    struct.pack_into("<I", main, 0x20, 0x20010000)
    struct.pack_into("<I", main, 0x24, open_cfw.MAIN_RUN_BASE + 0x21)
    for offset in release_cfw.RUNTIME_VERSION_FIELDS.values():
        main[offset:offset + len(release_cfw.SOURCE_RUNTIME_FIELD)] = (
            release_cfw.SOURCE_RUNTIME_FIELD
        )
    struct.pack_into("<I", main, 4, zlib.crc32(main[8:]) & 0xFFFFFFFF)
    return bytes(main)


class ReleaseCFWTests(unittest.TestCase):
    @staticmethod
    def package() -> bytes:
        main = make_main()
        component = {
            "name": "apollo_main",
            "entry_id": 6,
            "type_id": 0,
            "storage_type": 1,
            "package_filename": release_cfw.MAIN_FILENAME,
        }
        manifest = {
            "package": {
                "build_date": "2026-08-23",
                "build_time": "16:00:00",
                "version": release_cfw.SOURCE_PACKAGE_VERSION,
            },
            "components": [component],
        }
        image, _ = open_cfw.assemble_evenota(manifest, {"apollo_main": main})
        return image

    def test_transform_updates_both_live_versions_and_all_checksums(self) -> None:
        source = self.package()
        release, report = release_cfw.transform(source)
        self.assertEqual(len(release), len(source))
        self.assertEqual(
            release[0x30:0x40],
            b"s200_v2.2.6.0".ljust(16, b"\0"),
        )
        entries = release_cfw._parse_entries(release)
        main = entries[0]
        payload = release[main.payload_offset:main.payload_offset + main.payload_size]
        for offset in release_cfw.RUNTIME_VERSION_FIELDS.values():
            self.assertEqual(
                payload[offset:offset + len(release_cfw.RELEASE_RUNTIME_FIELD)],
                release_cfw.RELEASE_RUNTIME_FIELD,
            )
        open_cfw.validate_apollo_main(payload)
        self.assertEqual(report["release"]["sha256"], hashlib.sha256(release).hexdigest())

    def test_transform_is_deterministic(self) -> None:
        source = self.package()
        first, first_report = release_cfw.transform(source)
        second, second_report = release_cfw.transform(source)
        self.assertEqual(first, second)
        self.assertEqual(first_report, second_report)

    def test_transform_rejects_wrong_package_version(self) -> None:
        source = bytearray(self.package())
        source[0x30:0x40] = b"s200_v2.2.6.1\0"
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "input version"):
            release_cfw.transform(bytes(source))

    def test_transform_rejects_shifted_runtime_field(self) -> None:
        source = bytearray(self.package())
        entry = release_cfw._parse_entries(bytes(source))[0]
        offset = entry.payload_offset + release_cfw.RUNTIME_VERSION_FIELDS["settings"]
        source[offset] ^= 1
        payload = source[entry.payload_offset:entry.payload_offset + entry.payload_size]
        nested_crc = zlib.crc32(payload[8:]) & 0xFFFFFFFF
        struct.pack_into("<I", source, entry.payload_offset + 4, nested_crc)
        payload = source[entry.payload_offset:entry.payload_offset + entry.payload_size]
        component_crc = open_cfw.crc32c_msb(payload)
        struct.pack_into("<I", source, entry.toc_offset + 12, component_crc)
        struct.pack_into("<I", source, entry.body_offset + 12, component_crc)
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "settings version field"):
            release_cfw.transform(bytes(source))

    def test_transform_rejects_corrupt_component_crc(self) -> None:
        source = bytearray(self.package())
        source[-1] ^= 1
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "CRC-32C"):
            release_cfw.transform(bytes(source))


if __name__ == "__main__":
    unittest.main()
