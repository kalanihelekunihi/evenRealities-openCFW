"""Fail-closed admission tests for the Apollo LC3 service-audio adapter."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER_PATH = ROOT / "tools/analyze_g2_liblc3_service_audio_adapter.py"
SPEC = importlib.util.spec_from_file_location(
    "analyze_g2_liblc3_service_audio_adapter", ANALYZER_PATH)
assert SPEC is not None and SPEC.loader is not None
ANALYZER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYZER)


class Liblc3ServiceAudioAdapterAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = ANALYZER.run_audit()
        cls.admission = json.loads(
            ANALYZER.ADMISSION.read_text(encoding="utf-8"))

    def test_authenticated_stock_abi_and_context_geometry(self) -> None:
        evidence = self.report["evidence"]
        self.assertEqual(evidence["stock_functions"], {
            "pcm_width_mapper": {
                "start": 0x0057A900,
                "bytes": 38,
                "sha256": "5bbff3fde30dd7e091d8d496ab401b1036e0dc5f158c071b57a0404ed0ace8f0",
            },
            "lazy_setup": {
                "start": 0x0057A926,
                "bytes": 26,
                "sha256": "043e57c0075b4e4c1043d93fe1c9cb7fb3abe91ba6ed24af5160a198f7eb3851",
            },
            "encode_mono": {
                "start": 0x0057A940,
                "bytes": 568,
                "sha256": "a21f5d12546cd8b00b113b5234e004ca2d6c7deccd2040c3c1d019e81cc5d594",
            },
        })
        contexts = evidence["stock_contexts"]
        self.assertEqual(contexts["count"], 4)
        self.assertEqual(contexts["slot_bytes"], 2628)
        self.assertEqual(contexts["header_bytes"], 28)
        self.assertEqual(contexts["encoder_storage_bytes"], 2600)
        self.assertEqual(contexts["field_offsets"], {
            "pcm_format": 0,
            "frame_us": 4,
            "sample_rate_hz": 8,
            "channels_or_stride": 12,
            "channel_offset": 16,
            "bitrate_bps": 20,
            "encoder": 24,
            "storage": 28,
        })

    def test_owned_state_geometry_fits_all_four_exact_stock_slots(self) -> None:
        abi = self.report["abi"]
        self.assertEqual(abi["adapter_state_arm32_bytes"], 2628)
        self.assertEqual(abi["adapter_state_alignment"], 4)
        self.assertEqual(abi["storage_offset_arm32"], 28)
        self.assertEqual(abi["minimum_encoder_capacity_bytes"], 2596)
        self.assertEqual(abi["per_context_delta_bytes"], 0)
        self.assertEqual(abi["four_context_delta_bytes"], 0)
        placement = self.report["stock_slot_placement"]
        self.assertEqual(placement["total_state_bytes"], 10512)
        self.assertEqual(placement["extra_writable_bytes_required"], 0)
        self.assertEqual(
            [row["encoder_prefix_bytes"] for row in placement["contexts"]],
            [0, 4, 0, 4])
        self.assertEqual(
            [row["encoder_capacity_bytes"] for row in placement["contexts"]],
            [2600, 2596, 2600, 2596])
        routing = self.report["routing"]
        self.assertTrue(routing["software_boundary_implemented"])
        self.assertTrue(routing["stock_contexts_fit_adapter_state"])
        self.assertTrue(routing["stock_slot_placement_proven"])
        self.assertFalse(routing["direct_stock_abi_compatible"])
        self.assertFalse(routing["service_audio_routed"])

    def test_both_target_profiles_are_byte_reproducible_and_closed(self) -> None:
        profiles = self.report["target"]["profiles"]
        self.assertEqual(set(profiles), {"apple-clang", "linux-clang"})
        for name, profile in profiles.items():
            with self.subTest(profile=name):
                adapter = profile["adapter_object"]
                self.assertEqual(adapter["data_size"], 0)
                self.assertEqual(adapter["rodata_size"], 18)
                self.assertEqual(set(adapter["undefined_provider_entries"]),
                                 ANALYZER.PROVIDER_IMPORTS)
                self.assertEqual(adapter["relocations"]["count"], 28)
                retained = profile["retained_encoder_link"]
                self.assertEqual(set(retained["undefined_runtime_imports"]),
                                 ANALYZER.RUNTIME_IMPORTS)
                self.assertEqual(set(retained["defined_adapter_entries"]),
                                 set(ANALYZER.ADAPTER_ROOTS))

    def test_behavior_contract_covers_errors_ownership_and_lifetime(self) -> None:
        behavior = self.report["behavior"]
        self.assertEqual(behavior["pcm_width_bytes"], [2, 4, 3, 4])
        self.assertEqual(behavior["minimum_encoded_frame_bytes"], 20)
        self.assertTrue(behavior["interleaved_frame_multiple_required"])
        self.assertTrue(behavior["selected_channel_offset_and_stride_preserved"])
        self.assertTrue(behavior["owner_token_required_for_encode_and_close"])
        self.assertTrue(behavior["provider_failure_invalidates_lifetime"])
        self.assertTrue(behavior["partial_output_bytes_reported_on_provider_failure"])
        self.assertTrue(
            behavior["plan_query_rederives_without_encoder_reinitialization"])
        self.assertFalse(self.report["hardware_operations"])

    def test_hostile_stock_slot_overflow_alignment_and_overlap_fail_closed(
            self) -> None:
        contexts = self.report["evidence"]["stock_contexts"]
        base = {
            "addresses": contexts["addresses"],
            "slot_bytes": 2628,
            "state_bytes": 2628,
            "storage_offset": 28,
            "storage_bytes": 2600,
        }
        mutations = []
        wrong_count = dict(base)
        wrong_count["addresses"] = base["addresses"][:-1]
        mutations.append(wrong_count)
        misaligned = copy.deepcopy(base)
        misaligned["addresses"][1] += 2
        mutations.append(misaligned)
        overlap = copy.deepcopy(base)
        overlap["addresses"][1] -= 4
        mutations.append(overlap)
        overflow = dict(base)
        overflow["addresses"] = [
            0xFFFFD6F4, 0xFFFFE138, 0xFFFFEB7C, 0xFFFFF5C0]
        mutations.append(overflow)
        wrong_size = dict(base)
        wrong_size["state_bytes"] = 2629
        mutations.append(wrong_size)
        wrong_storage = dict(base)
        wrong_storage["storage_offset"] = 32
        mutations.append(wrong_storage)
        for index, mutation in enumerate(mutations):
            with self.subTest(case=index):
                with self.assertRaises(ANALYZER.AdmissionError):
                    ANALYZER.validate_stock_slot_layout(**mutation)

    def test_hostile_manifest_or_report_drift_is_rejected(self) -> None:
        mutations = []
        wrong_source = copy.deepcopy(self.admission)
        wrong_source["expected"]["source"]["implementation"]["sha256"] = "0" * 64
        mutations.append(wrong_source)
        wrong_state = copy.deepcopy(self.admission)
        wrong_state["expected"]["abi"]["adapter_state_arm32_bytes"] = 2712
        mutations.append(wrong_state)
        wrong_imports = copy.deepcopy(self.admission)
        wrong_imports["expected"]["runtime_import_allowlist"].append("malloc")
        mutations.append(wrong_imports)
        routed = copy.deepcopy(self.admission)
        routed["expected"]["routing"]["service_audio_routed"] = True
        mutations.append(routed)

        with tempfile.TemporaryDirectory(
                prefix="opencfw-lc3-service-hostile-") as directory:
            for index, admission in enumerate(mutations):
                with self.subTest(mutation=index):
                    path = Path(directory) / f"admission-{index}.json"
                    path.write_text(json.dumps(admission), encoding="utf-8")
                    with self.assertRaises(ANALYZER.AdmissionError):
                        ANALYZER.validate_admission(path, self.report)


if __name__ == "__main__":
    unittest.main()
