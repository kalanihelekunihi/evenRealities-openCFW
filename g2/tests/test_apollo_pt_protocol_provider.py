# SPDX-License-Identifier: MIT
"""Software-only admission tests for the in-place Apollo PT provider."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components" / "apollo_main" / "pt_protocol"
OFFICIAL = ROOT / "blobs" / "official" / "g2-2.2.6.10" / \
    "ota_s200_firmware_ota.bin"
SPEC = importlib.util.spec_from_file_location(
    "open_cfw_pt_protocol_provider_test", COMPONENT / "build_component.py")
assert SPEC is not None and SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)
CORE_SPEC = importlib.util.spec_from_file_location(
    "open_cfw_core_provider_profile_test",
    ROOT / "components/apollo_main/core_overlay/build_component.py")
assert CORE_SPEC is not None and CORE_SPEC.loader is not None
CORE_BUILDER = importlib.util.module_from_spec(CORE_SPEC)
CORE_SPEC.loader.exec_module(CORE_BUILDER)
CORE_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
CONFIG = json.loads(CORE_CONFIG.read_text(encoding="utf-8"))
OFFICIAL_EXPECTED = {
    "size": int(CONFIG["base"]["size"]),
    "sha256": CONFIG["base"]["sha256"],
}


class ApolloPtProtocolProviderTest(unittest.TestCase):
    def build(self, base: Path, output: Path, **arguments):
        arguments.setdefault("ingress_authentication_base_path", OFFICIAL)
        arguments.setdefault(
            "ingress_authentication_base_expected", OFFICIAL_EXPECTED)
        return BUILDER.build(
            base_path=base, output_dir=output, clang="/usr/bin/clang",
            **arguments)

    def test_complete_provider_is_source_routed_and_in_place(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-pt-provider-test-") as name:
            output = Path(name)
            report = self.build(OFFICIAL, output)
            component = (output / "ota_s200_firmware_ota.bin").read_bytes()
        base = OFFICIAL.read_bytes()
        placement = report["placement"]
        self.assertEqual(placement["capacity"], 35524)
        self.assertEqual(placement["writable_bytes"], 0)
        self.assertEqual(placement["loadable_size"] + placement["padding_size"],
                         placement["capacity"])
        self.assertEqual(len(report["source_provider_routes"]), 40)
        self.assertEqual(report["patch_sites"], [])
        self.assertEqual(len(report["ingress_sites"]), 3)
        for ingress in report["ingress_sites"]:
            self.assertNotIn("expected_hex", ingress)
            offset = ingress["runtime_address"] - BUILDER.RUN_BASE
            donor_instruction = base[offset:offset + 4]
            self.assertEqual(ingress["authenticated_size"], 4)
            self.assertEqual(
                ingress["authenticated_sha256"],
                hashlib.sha256(donor_instruction).hexdigest(),
            )
            self.assertEqual(component[offset:offset + 4], donor_instruction)
            self.assertEqual(
                BUILDER._decode_thumb_bl(
                    ingress["runtime_address"], donor_instruction),
                ingress["target_address"],
            )
        sections = placement["sections"]
        self.assertEqual(sections[".pt_legacy_entry"]["runtime_address"],
                         0x0056F4A0)
        self.assertEqual(sections[".pt_legacy_postprocess"]["runtime_address"],
                         0x0056F92C)
        interval_start = BUILDER.INTERVAL_START - BUILDER.RUN_BASE
        interval_end = BUILDER.INTERVAL_END - BUILDER.RUN_BASE
        self.assertNotEqual(component[interval_start:interval_end],
                            base[interval_start:interval_end])
        occupied = set()
        for section in sections.values():
            start = section["runtime_address"] - BUILDER.INTERVAL_START
            occupied.update(range(start, start + section["size"]))
        interval = component[interval_start:interval_end]
        self.assertTrue(all(value == 0xFF for index, value in enumerate(interval)
                            if index not in occupied))
        for route in report["source_provider_routes"]:
            self.assertLessEqual(BUILDER.INTERVAL_START,
                                 route["target_runtime_address"])
            self.assertLess(route["target_runtime_address"], BUILDER.INTERVAL_END)
            self.assertEqual(route["target_thumb_pointer"],
                             route["target_runtime_address"] | 1)

    def test_tampered_interval_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-pt-tamper-") as name:
            temporary = Path(name)
            payload = bytearray(OFFICIAL.read_bytes())
            payload[BUILDER.INTERVAL_START - BUILDER.RUN_BASE] ^= 1
            struct.pack_into("<I", payload, 4,
                             zlib.crc32(payload[8:]) & 0xFFFFFFFF)
            base = temporary / "tampered.bin"
            base.write_bytes(payload)
            with self.assertRaisesRegex(BUILDER.BuildError,
                                        "stock interval changed"):
                self.build(base, temporary / "output")

    def test_tampered_physical_ingress_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-pt-ingress-") as name:
            temporary = Path(name)
            payload = bytearray(OFFICIAL.read_bytes())
            payload[0x00538716 - BUILDER.RUN_BASE] ^= 1
            struct.pack_into("<I", payload, 4,
                             zlib.crc32(payload[8:]) & 0xFFFFFFFF)
            base = temporary / "tampered.bin"
            base.write_bytes(payload)
            expected = {"size": len(payload),
                        "sha256": hashlib.sha256(payload).hexdigest()}
            with self.assertRaisesRegex(BUILDER.BuildError,
                                        "working ingress differs"):
                self.build(base, temporary / "output", base_expected=expected)

    @staticmethod
    def route_receipt(profile: str = "apple-clang") -> dict:
        stage_expected = (
            CONFIG["core_stage_expected"] if profile == "apple-clang" else
            CONFIG["toolchain_profiles"][profile]["core_stage_expected"]
        )
        return {
            "mode": "source_overlay_relocation",
            "profile": profile,
            "function": "open_cfw_box_uart_handle",
            "strict_relocation_contract": True,
            "profile_route_active": True,
            "stage_overlay": {
                "size": stage_expected["overlay_size"],
                "sha256": stage_expected["overlay_sha256"],
            },
            "leaf": dict(BUILDER.SOURCE_UART_LEAF_EXPECTED),
            "relocations": [
                {
                    "symbol": symbol,
                    "type": kind,
                    "target_address": target,
                    "offset": offset,
                    "type_id": type_id,
                }
                for symbol, kind, target, offset, type_id
                in BUILDER.SOURCE_UART_ROUTE_REQUIREMENTS
            ],
        }

    def test_routed_uart_ingress_uses_authenticated_donor_and_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-pt-routed-") as name:
            temporary = Path(name)
            payload = bytearray(OFFICIAL.read_bytes())
            thumb_nop_pair = struct.pack("<HH", 0xBF00, 0xBF00)
            for address, _target, route in BUILDER.LEGACY_INGRESS:
                if route == "source_uart_relocation":
                    offset = address - BUILDER.RUN_BASE
                    payload[offset:offset + 4] = thumb_nop_pair
            struct.pack_into(
                "<I", payload, 4, zlib.crc32(payload[8:]) & 0xFFFFFFFF)
            working = temporary / "routed.bin"
            working.write_bytes(payload)
            report = self.build(
                working, temporary / "output",
                base_expected={
                    "size": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                },
                source_uart_routed=True,
                source_uart_route_receipt=self.route_receipt(),
            )
        self.assertEqual(
            report["source_uart_route_receipt"]["mode"],
            "source_overlay_relocation",
        )
        self.assertEqual(
            sum(site["route"] == "source_uart_relocation"
                for site in report["ingress_sites"]),
            2,
        )

    def test_routed_uart_ingress_requires_exact_donor_authentication(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-pt-donor-auth-") as name:
            temporary = Path(name)
            donor = bytearray(OFFICIAL.read_bytes())
            donor[0x0053A218 - BUILDER.RUN_BASE] ^= 1
            struct.pack_into(
                "<I", donor, 4, zlib.crc32(donor[8:]) & 0xFFFFFFFF)
            donor_path = temporary / "tampered-donor.bin"
            donor_path.write_bytes(donor)
            with self.assertRaisesRegex(
                    BUILDER.BuildError,
                    "PT ingress authentication base changed"):
                self.build(
                    OFFICIAL, temporary / "output",
                    ingress_authentication_base_path=donor_path,
                    source_uart_routed=True,
                    source_uart_route_receipt=self.route_receipt(),
                )

    def test_routed_uart_ingress_requires_route_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-pt-route-receipt-") as name:
            with self.assertRaisesRegex(BUILDER.BuildError,
                                        "route receipt missing"):
                self.build(OFFICIAL, Path(name), source_uart_routed=True)

    def test_route_receipt_is_bound_to_stage_leaf_and_relocations(self) -> None:
        receipt = self.route_receipt()
        receipt["relocations"][0]["offset"] += 2
        with tempfile.TemporaryDirectory(prefix="g2-pt-route-pin-") as name:
            with self.assertRaisesRegex(BUILDER.BuildError,
                                        "relocation receipt changed"):
                self.build(
                    OFFICIAL, Path(name), source_uart_routed=True,
                    source_uart_route_receipt=receipt,
                )

    def test_core_stage_route_receipt_is_profile_exact(self) -> None:
        leaf = next(
            item for item in CONFIG["relocated_leaves"]
            if item.get("function") == "open_cfw_box_uart_handle"
        )
        stage_expected = CONFIG["core_stage_expected"]
        extraction = {
            **leaf["expected"],
            "function": "open_cfw_box_uart_handle",
            "relocations": [
                {
                    "symbol": symbol, "type": kind,
                    "target_address": target, "offset": offset,
                    "type_id": type_id,
                }
                for symbol, kind, target, offset, type_id
                in CORE_BUILDER.PT_SOURCE_UART_ROUTES
            ],
        }
        pins = {
            **leaf["expected"],
            "relocations": [
                {
                    "symbol": symbol, "type": kind,
                    "target_address": target, "offset": offset,
                }
                for symbol, kind, target, offset, _type_id
                in CORE_BUILDER.PT_SOURCE_UART_ROUTES
            ],
        }
        stage_report = {
            "toolchain": {"profile": "apple-clang"},
            "overlay": {
                "size": stage_expected["overlay_size"],
                "sha256": stage_expected["overlay_sha256"],
            },
            "relocated_leaves": [{"extraction": extraction, "pins": pins}],
        }
        routed, receipt = CORE_BUILDER._verify_pt_source_uart_ingress(
            CONFIG, stage_report, "apple-clang", stage_expected)
        self.assertTrue(routed)
        self.assertEqual(receipt["leaf"], BUILDER.SOURCE_UART_LEAF_EXPECTED)
        stage_report["relocated_leaves"][0]["extraction"]["relocations"][
            0]["type_id"] += 1
        with self.assertRaisesRegex(CORE_BUILDER.BuildError,
                                    "route receipt changed"):
            CORE_BUILDER._verify_pt_source_uart_ingress(
                CONFIG, stage_report, "apple-clang", stage_expected)

    def test_linux_core_stage_receipt_uses_authenticated_direct_ingress(
            self) -> None:
        stage_expected = CONFIG["toolchain_profiles"]["linux-clang"][
            "core_stage_expected"]
        stage_report = {
            "toolchain": {"profile": "linux-clang"},
            "overlay": {
                "size": stage_expected["overlay_size"],
                "sha256": stage_expected["overlay_sha256"],
            },
            "relocated_leaves": [],
        }
        routed, receipt = CORE_BUILDER._verify_pt_source_uart_ingress(
            CONFIG, stage_report, "linux-clang", stage_expected)
        self.assertFalse(routed)
        self.assertEqual(receipt["mode"], "authenticated_donor_direct")
        self.assertFalse(receipt["profile_route_active"])
        BUILDER._validate_source_uart_route_receipt(
            receipt, profile="linux-clang", routed=False)

    def test_routed_receipt_accepts_donor_identical_working_sites(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-pt-route-identical-") as name:
            report = self.build(
                OFFICIAL, Path(name), source_uart_routed=True,
                source_uart_route_receipt=self.route_receipt(),
            )
        self.assertEqual(
            report["source_uart_route_receipt"]["mode"],
            "source_overlay_relocation",
        )

    def test_builder_has_no_raw_ingress_transcript(self) -> None:
        source = (COMPONENT / "build_component.py").read_text(encoding="utf-8")
        self.assertNotIn("bytes.fromhex", source)
        self.assertNotIn("expected_hex", source)
        with tempfile.TemporaryDirectory(prefix="g2-pt-clean-report-") as name:
            report = self.build(OFFICIAL, Path(name))
        self.assertNotIn("expected_hex", json.dumps(report, sort_keys=True))

    def test_active_profile_pin_is_fail_closed(self) -> None:
        config = json.loads(CORE_CONFIG.read_text(encoding="utf-8"))
        expected = config["post_link_providers"]["pt_protocol"]["profiles"][
            "apple-clang"]
        report = {"placement": {
            "loadable_size": expected["payload_size"],
            "payload_sha256": expected["payload_sha256"],
            "interval_sha256": expected["interval_sha256"],
        }}
        CORE_BUILDER._verify_pt_provider_profile(
            config, "apple-clang", report)
        report["placement"]["loadable_size"] += 1
        with self.assertRaisesRegex(CORE_BUILDER.BuildError,
                                    "PT protocol provider profile"):
            CORE_BUILDER._verify_pt_provider_profile(
                config, "apple-clang", report)
        with self.assertRaisesRegex(CORE_BUILDER.BuildError,
                                    "lacks profile"):
            CORE_BUILDER._verify_pt_provider_profile(
                config, "missing-profile", report)

    def test_linux_profile_is_exact_and_builds(self) -> None:
        clang = Path("/opt/homebrew/opt/llvm@22/bin/clang")
        self.assertTrue(clang.is_file(), "reviewed LLVM 22 toolchain missing")
        with tempfile.TemporaryDirectory(prefix="g2-pt-linux-provider-") as name:
            report = BUILDER.build(
                base_path=OFFICIAL, output_dir=Path(name), clang=str(clang),
                profile="linux-clang",
                ingress_authentication_base_path=OFFICIAL,
                ingress_authentication_base_expected=OFFICIAL_EXPECTED)
        config = json.loads(CORE_CONFIG.read_text(encoding="utf-8"))
        CORE_BUILDER._verify_pt_provider_profile(
            config, "linux-clang", report)

    def test_failed_final_admission_does_not_publish_stage_artifacts(self) -> None:
        config = json.loads(CORE_CONFIG.read_text(encoding="utf-8"))
        profile = config["post_link_providers"]["pt_protocol"]["profiles"][
            "apple-clang"]

        def fake_overlay_build(*, output_dir: Path, **_arguments):
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / config["overlay_artifact"]).write_bytes(b"stage-overlay")
            (output_dir / "ota_s200_firmware_ota.bin").write_bytes(
                b"stage-component")
            return {"base": {"size": 4}}

        class FakeLc3:
            @staticmethod
            def build(*, output_dir: Path, **_arguments):
                output_dir.mkdir(parents=True, exist_ok=True)
                (output_dir / "ota_s200_firmware_ota.bin").write_bytes(b"lc3")
                return {"placement": {"sections": {}}}

        class FakePt:
            @staticmethod
            def build(*, output_dir: Path, **_arguments):
                output_dir.mkdir(parents=True, exist_ok=True)
                (output_dir / "ota_s200_firmware_ota.bin").write_bytes(b"final")
                return {"placement": {
                    "loadable_size": profile["payload_size"],
                    "payload_sha256": profile["payload_sha256"],
                    "interval_sha256": profile["interval_sha256"],
                }}

        with tempfile.TemporaryDirectory(prefix="g2-core-transaction-") as name:
            output = Path(name) / "published"
            output.mkdir()
            sentinels = {
                config["overlay_artifact"]: b"published-overlay",
                "ota_s200_firmware_ota.bin": b"published-component",
                "build-report.json": b"published-report",
            }
            for relative, payload in sentinels.items():
                (output / relative).write_bytes(payload)
            with (mock.patch.object(CORE_BUILDER, "overlay_build",
                                    side_effect=fake_overlay_build),
                  mock.patch.object(CORE_BUILDER, "_load_liblc3_builder",
                                    return_value=FakeLc3),
                  mock.patch.object(CORE_BUILDER, "_load_pt_protocol_builder",
                                    return_value=FakePt),
                  mock.patch.object(
                      CORE_BUILDER, "_verify_pt_source_uart_ingress",
                      return_value=(False, {"mode": "test"}))):
                with self.assertRaisesRegex(CORE_BUILDER.BuildError,
                                            "canonical post-link"):
                    CORE_BUILDER.build(
                        root=ROOT, config_path=CORE_CONFIG,
                        output_dir=output, clang="unused")
            for relative, payload in sentinels.items():
                self.assertEqual((output / relative).read_bytes(), payload)

    def test_changed_build_inputs_do_not_publish(self) -> None:
        with tempfile.TemporaryDirectory(prefix="g2-pt-input-race-") as name:
            output = Path(name) / "published"
            output.mkdir()
            sentinels = {
                "ota_s200_firmware_ota.bin": b"old-component",
                "pt-protocol-in-place.bin": b"old-payload",
                "build-report.json": b"old-report",
            }
            for relative, payload in sentinels.items():
                (output / relative).write_bytes(payload)
            with mock.patch.object(
                    BUILDER, "_build_input_snapshot",
                    side_effect=[(("before", 1, "a" * 64),),
                                 (("after", 1, "b" * 64),)]):
                with self.assertRaisesRegex(BUILDER.BuildError,
                                            "build inputs changed"):
                    self.build(OFFICIAL, output)
            for relative, payload in sentinels.items():
                self.assertEqual((output / relative).read_bytes(), payload)

    def test_transactional_stage_directory_is_inside_repository(self) -> None:
        source = (ROOT / "components/apollo_main/core_overlay/build_component.py"
                  ).read_text(encoding="utf-8")
        self.assertIn('prefix=".tmp-open-cfw-apollo-canonical-", dir=root',
                      source)
        self.assertIn('overlay_report["artifact"] = str(overlay_path', source)
        self.assertIn('component_report["artifact"] = str(component_path',
                      source)


if __name__ == "__main__":
    unittest.main()
