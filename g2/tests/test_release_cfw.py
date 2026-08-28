from __future__ import annotations

import hashlib
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock


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
        release, report = release_cfw.transform_test_only_synthetic(source)
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
        first, first_report = release_cfw.transform_test_only_synthetic(source)
        second, second_report = release_cfw.transform_test_only_synthetic(source)
        self.assertEqual(first, second)
        self.assertEqual(first_report, second_report)

    def test_transform_rejects_wrong_package_version(self) -> None:
        source = bytearray(self.package())
        source[0x30:0x40] = b"s200_v2.2.6.1\0"
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "input version"):
            release_cfw.transform_test_only_synthetic(bytes(source))

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
            release_cfw.transform_test_only_synthetic(bytes(source))

    def test_transform_rejects_corrupt_component_crc(self) -> None:
        source = bytearray(self.package())
        source[-1] ^= 1
        with self.assertRaisesRegex(open_cfw.OpenCFWError, "CRC-32C"):
            release_cfw.transform_test_only_synthetic(bytes(source))

    @staticmethod
    def canonical_context(root: Path) -> tuple[bytes, Path, Path]:
        manifest_path = root / "manifests/g2-2.2.6.10-core-source.json"
        receipt_path = root / "build/source/build-report.json"
        payloads = {
            "codec": b"codec",
            "ble_em9305": b"em9305",
            "touch": b"touch",
            "case": b"case",
            "apollo_bootloader": b"bootloader",
            "apollo_main": make_main(),
        }
        metadata = (
            ("codec", 1, 4, "firmware/codec.bin", "official_blob"),
            ("ble_em9305", 2, 5, "firmware/ble_em9305.bin", "official_blob"),
            ("touch", 3, 3, "firmware/touch.bin", "official_blob"),
            ("case", 4, 6, "firmware/box.bin", "official_blob"),
            ("apollo_bootloader", 5, 1, "ota/s200_bootloader.bin", "source_build"),
            ("apollo_main", 6, 0, release_cfw.MAIN_FILENAME, "source_build"),
        )
        components = []
        for name, entry_id, type_id, filename, kind in metadata:
            payload = payloads[name]
            components.append(
                {
                    "name": name,
                    "entry_id": entry_id,
                    "type_id": type_id,
                    "storage_type": 3,
                    "package_filename": filename,
                    "provider": {
                        "kind": kind,
                        "path": f"providers/{name}.bin",
                        "size": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest(),
                    },
                }
            )
        manifest = {
            "schema_version": 1,
            "target": "Even Realities G2",
            "package": {
                "format": "EVENOTA",
                "build_date": "2026-08-23",
                "build_time": "16:00:00",
                "version": release_cfw.SOURCE_PACKAGE_VERSION,
                "output_name": "canonical-source.evenota.bin",
            },
            "components": components,
        }
        image, _ = open_cfw.assemble_evenota(manifest, payloads)
        manifest["package"]["expected_size"] = len(image)
        manifest["package"]["expected_sha256"] = hashlib.sha256(image).hexdigest()
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        parsed = release_cfw._parse_entries(image)
        receipt = {
            "schema_version": 1,
            "target": manifest["target"],
            "manifest": "manifests/g2-2.2.6.10-core-source.json",
            "manifest_sha256": open_cfw.effective_manifest_sha256(manifest),
            "manifest_sources": open_cfw.manifest_source_ledger(manifest_path),
            "toolchain_profile": "apple-clang",
            "provider_mode": "official_blob+source_build",
            "providers": [
                {
                    "component": component["name"],
                    "kind": component["provider"]["kind"],
                    "path": component["provider"]["path"],
                    "size": len(payloads[component["name"]]),
                    "sha256": hashlib.sha256(
                        payloads[component["name"]]
                    ).hexdigest(),
                }
                for component in components
            ],
            "package": {
                "artifact": "package/canonical-source.evenota.bin",
                "size": len(image),
                "sha256": hashlib.sha256(image).hexdigest(),
                "reference_sha256": hashlib.sha256(image).hexdigest(),
                "byte_identical_to_reference": True,
            },
            "entries": [release_cfw._receipt_entry(entry) for entry in parsed],
            "placed_region_count": 1,
            "unresolved_region_count": 0,
            "container_region_count": 0,
        }
        receipt_path.parent.mkdir(parents=True)
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        package_path = receipt_path.parent / "package/canonical-source.evenota.bin"
        package_path.parent.mkdir(parents=True)
        package_path.write_bytes(image)
        return image, manifest_path, receipt_path

    @staticmethod
    def verified_generation(receipt: Path):
        value = json.loads(receipt.read_text(encoding="utf-8"))
        return mock.patch.object(
            open_cfw, "verify_artifacts_with_lock_held", return_value=value
        )

    def test_production_transform_accepts_only_bound_six_entry_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-release-source-") as temporary:
            root = Path(temporary)
            source, manifest, receipt = self.canonical_context(root)
            with mock.patch.multiple(
                release_cfw,
                ROOT=root,
                CANONICAL_SOURCE_MANIFEST=manifest,
                CANONICAL_SOURCE_BUILD_REPORT=receipt,
            ), self.verified_generation(receipt):
                released, report = release_cfw.transform(
                    source,
                    source_manifest_path=manifest,
                    source_build_report_path=receipt,
                    toolchain_profile="apple-clang",
                )
            self.assertEqual(len(released), len(source))
            self.assertEqual(
                report["canonical_source"]["package_sha256"],
                hashlib.sha256(source).hexdigest(),
            )

    def test_production_transform_rejects_generic_same_version_package(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-release-source-") as temporary:
            root = Path(temporary)
            _, manifest, receipt = self.canonical_context(root)
            with mock.patch.multiple(
                release_cfw,
                ROOT=root,
                CANONICAL_SOURCE_MANIFEST=manifest,
                CANONICAL_SOURCE_BUILD_REPORT=receipt,
            ), self.verified_generation(receipt):
                with self.assertRaisesRegex(
                    open_cfw.OpenCFWError,
                    "exact six G2 components|entry count",
                ):
                    release_cfw.transform(
                        self.package(),
                        source_manifest_path=manifest,
                        source_build_report_path=receipt,
                        toolchain_profile="apple-clang",
                    )

    def test_production_transform_rejects_stale_build_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-release-source-") as temporary:
            root = Path(temporary)
            source, manifest, receipt = self.canonical_context(root)
            value = json.loads(receipt.read_text(encoding="utf-8"))
            value["package"]["sha256"] = "0" * 64
            receipt.write_text(json.dumps(value), encoding="utf-8")
            with mock.patch.multiple(
                release_cfw,
                ROOT=root,
                CANONICAL_SOURCE_MANIFEST=manifest,
                CANONICAL_SOURCE_BUILD_REPORT=receipt,
            ), self.verified_generation(receipt):
                with self.assertRaisesRegex(
                    open_cfw.OpenCFWError,
                    "build receipt does not authenticate",
                ):
                    release_cfw.transform(
                        source,
                        source_manifest_path=manifest,
                        source_build_report_path=receipt,
                        toolchain_profile="apple-clang",
                    )

    def test_production_transform_reads_receipt_referenced_package(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-release-source-") as temporary:
            root = Path(temporary)
            source, manifest, receipt = self.canonical_context(root)
            package = receipt.parent / "package/canonical-source.evenota.bin"
            changed = bytearray(package.read_bytes())
            changed[-1] ^= 1
            package.write_bytes(changed)
            with mock.patch.multiple(
                release_cfw,
                ROOT=root,
                CANONICAL_SOURCE_MANIFEST=manifest,
                CANONICAL_SOURCE_BUILD_REPORT=receipt,
            ), self.verified_generation(receipt):
                with self.assertRaisesRegex(
                    open_cfw.OpenCFWError,
                    "differs from the package referenced",
                ):
                    release_cfw.transform(
                        source,
                        source_manifest_path=manifest,
                        source_build_report_path=receipt,
                        toolchain_profile="apple-clang",
                    )

    def test_production_transform_requires_verified_artifact_generation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-release-source-") as temporary:
            root = Path(temporary)
            source, manifest, receipt = self.canonical_context(root)
            with mock.patch.multiple(
                release_cfw,
                ROOT=root,
                CANONICAL_SOURCE_MANIFEST=manifest,
                CANONICAL_SOURCE_BUILD_REPORT=receipt,
            ), mock.patch.object(
                open_cfw, "verify_artifacts_with_lock_held", return_value={}
            ):
                with self.assertRaisesRegex(
                    open_cfw.OpenCFWError,
                    "not the verified generation receipt",
                ):
                    release_cfw.transform(
                        source,
                        source_manifest_path=manifest,
                        source_build_report_path=receipt,
                        toolchain_profile="apple-clang",
                    )

    def test_production_transform_rejects_symlinked_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-release-source-") as temporary:
            root = Path(temporary)
            source, manifest, receipt = self.canonical_context(root)
            linked_receipt = receipt.with_name("linked-build-report.json")
            linked_receipt.symlink_to(receipt.name)
            with mock.patch.multiple(
                release_cfw,
                ROOT=root,
                CANONICAL_SOURCE_MANIFEST=manifest,
                CANONICAL_SOURCE_BUILD_REPORT=linked_receipt,
            ):
                with self.assertRaisesRegex(
                    open_cfw.OpenCFWError,
                    "regular non-symlink file",
                ):
                    release_cfw.transform(
                        source,
                        source_manifest_path=manifest,
                        source_build_report_path=linked_receipt,
                        toolchain_profile="apple-clang",
                    )

    def test_atomic_write_replaces_symlink_without_following_it(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-release-output-") as temporary:
            root = Path(temporary)
            protected = root / "protected.bin"
            destination = root / "release.bin"
            protected.write_bytes(b"preserve")
            destination.symlink_to(protected.name)
            release_cfw._atomic_write(destination, b"release")
            self.assertEqual(protected.read_bytes(), b"preserve")
            self.assertFalse(destination.is_symlink())
            self.assertEqual(destination.read_bytes(), b"release")

    def test_cli_destinations_reject_input_and_source_generation_aliases(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-release-paths-") as temporary:
            root = Path(temporary)
            source_build = root / "build/source"
            source_build.mkdir(parents=True)
            input_path = source_build / "package/source.bin"
            input_path.parent.mkdir()
            input_path.write_bytes(b"source")
            receipt = source_build / "build-report.json"
            receipt.write_text("{}", encoding="utf-8")
            manifest = root / "manifests/source.json"
            manifest.parent.mkdir()
            manifest.write_text("{}", encoding="utf-8")
            with mock.patch.multiple(
                release_cfw,
                CANONICAL_SOURCE_MANIFEST=manifest,
                CANONICAL_SOURCE_BUILD_REPORT=receipt,
            ):
                with self.assertRaisesRegex(
                    open_cfw.OpenCFWError, "protected input"
                ):
                    release_cfw._validate_cli_destinations(
                        input_path, input_path, None
                    )
                with self.assertRaisesRegex(
                    open_cfw.OpenCFWError, "canonical source build"
                ):
                    release_cfw._validate_cli_destinations(
                        input_path, root / "release.bin", source_build / "new.json"
                    )
                with self.assertRaisesRegex(
                    open_cfw.OpenCFWError, "must be distinct"
                ):
                    release_cfw._validate_cli_destinations(
                        input_path, root / "release.bin", root / "release.bin"
                    )

    def test_public_release_entrypoint_is_blocked_without_binary_authority(self) -> None:
        with self.assertRaisesRegex(
            open_cfw.OpenCFWError,
            "redistribution authority is unresolved",
        ):
            release_cfw.assert_redistribution_authorized()


if __name__ == "__main__":
    unittest.main()
