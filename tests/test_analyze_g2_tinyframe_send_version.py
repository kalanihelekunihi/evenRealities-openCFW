#!/usr/bin/env python3
"""Guard the fail-closed G2 TinyFrame send/version recovery."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_tinyframe_send_version.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_tinyframe_send_version", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TinyFrameSendVersionRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.data = cls.analyzer._load()
        cls.report = cls.analyzer.audit(cls.data)

    def test_image_and_read_only_mode_are_pinned(self) -> None:
        self.assertEqual(
            self.report["component"], "TinyFrame post-2.3.0 vendor fork"
        )
        self.assertEqual(
            self.report["analysis_mode"],
            "read-only; no hardware or flash operation",
        )
        self.assertEqual(self.report["image"]["size"], 3_523_396)
        self.assertEqual(
            self.report["image"]["sha256"],
            "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
        )
        self.assertEqual(self.report["image"]["load_base"], 0x00437FE0)

    def test_send_closure_spans_are_complete_and_hash_pinned(self) -> None:
        spans = self.report["pinned_spans"]
        self.assertEqual(set(spans), set(self.analyzer.PINNED_SPANS))
        expected_sizes = {
            "TF_ComposeHead": 222,
            "TF_ComposeBody": 72,
            "TF_ComposeTail": 48,
            "TF_SendFrame_Begin": 106,
            "TF_SendFrame_Chunk": 132,
            "TF_SendFrame_End": 104,
            "TF_SendFrame": 60,
            "TF_Send": 16,
            "TF_Query": 14,
            "TF_Respond": 12,
            "TF_Query_Multipart": 18,
            "TF_Multipart_Payload": 8,
            "TF_Multipart_Close": 8,
        }
        for name, size in expected_sizes.items():
            with self.subTest(name=name):
                self.assertEqual(spans[name]["size"], size)
                self.assertEqual(
                    spans[name]["sha256"], self.analyzer.PINNED_SPANS[name][2]
                )

    def test_receive_facts_are_independently_reauthenticated(self) -> None:
        spans = self.report["pinned_spans"]
        self.assertEqual(spans["TF_CksumStart"]["size"], 4)
        self.assertEqual(spans["TF_CksumAdd"]["size"], 30)
        self.assertEqual(spans["TF_CksumEnd"]["size"], 4)
        self.assertEqual(spans["pars_begin_frame"]["size"], 46)
        self.assertEqual(spans["TF_AcceptChar"]["size"], 756)
        table = self.analyzer._slice(
            self.data,
            self.analyzer.CRC16_TABLE[0],
            self.analyzer.CRC16_TABLE[1],
        )
        self.assertEqual(table, self.analyzer._generated_crc_table())
        self.assertEqual(self.analyzer.crc16_arc(b"123456789"), 0xBB3D)

    def test_wire_contract_correctly_includes_sof_in_head_crc(self) -> None:
        wire = self.report["wire_contract"]
        self.assertEqual(wire["SOF"], {"enabled": True, "value": 1, "bytes": 1})
        for field in ("ID", "LEN", "TYPE"):
            self.assertEqual(wire[field], {"bytes": 2, "wire_endian": "big"})
        self.assertEqual(
            wire["HEAD_CKSUM"]["coverage"], "SOF || ID || LEN || TYPE"
        )
        self.assertEqual(wire["HEAD_CKSUM"]["algorithm"], "CRC-16/ARC")
        self.assertTrue(wire["DATA_CKSUM"]["present_only_when_len_nonzero"])
        self.assertEqual(wire["RX_payload_cap"], 0x6000)
        self.assertEqual(wire["TX_encoded_length_limit"], 0xFFFF)
        self.assertIsNone(wire["TX_explicit_payload_guard"])

    def test_reference_composer_matches_recovered_golden_frames(self) -> None:
        golden = self.report["golden_reference_frames"]
        self.assertEqual(
            golden["slave_request_id_0_type_0x1234_data_1020"],
            "0100000002123477bc1020180c",
        )
        self.assertEqual(
            golden["master_request_id_0_type_0x1234_data_1020"],
            "01800000021234b7a31020180c",
        )
        # No DATA_CKSUM follows a zero-length payload.
        self.assertEqual(
            golden["empty_response_id_0xbeef_type_0x2222"],
            "01beef00002222b046",
        )
        self.assertEqual(
            self.analyzer.crc16_arc(bytes.fromhex("01000000021234")),
            0x77BC,
        )

    def test_peer_bit_counter_and_response_policy(self) -> None:
        peer = self.report["peer_id_policy"]
        self.assertEqual(peer["peer_bit_mask"], 0x8000)
        self.assertEqual(peer["counter_mask"], 0x7FFF)
        self.assertEqual(peer["wire_request_id_period"], 0x8000)
        self.assertEqual(
            self.analyzer.resolve_request_id(0x7FFF, 0), (0x7FFF, 0x8000)
        )
        self.assertEqual(
            self.analyzer.resolve_request_id(0x8000, 0), (0x0000, 0x8001)
        )
        self.assertEqual(
            self.analyzer.resolve_request_id(0xFFFF, 1), (0xFFFF, 0x0000)
        )
        frame, frame_id, next_after = self.analyzer.compose_reference(
            frame_type=3,
            payload=b"",
            next_id=0x1234,
            peer_bit=0,
            is_response=True,
            response_id=0xF00D,
        )
        self.assertEqual(frame_id, 0xF00D)
        self.assertEqual(next_after, 0x1234)
        self.assertEqual(frame[1:3], b"\xF0\x0D")

    def test_tx_buffer_layout_lock_and_chunk_policy_are_pinned(self) -> None:
        tx = self.report["tx_configuration"]
        self.assertEqual(tx["TF_USE_MUTEX"], 0)
        self.assertEqual(tx["TF_SENDBUF_LEN"], 1024)
        self.assertIn("non-atomic soft lock", tx["lock_policy"])
        fields = tx["object_fields"]
        self.assertEqual(fields["peer_bit"], {"offset": 0x0C, "size": 1})
        self.assertEqual(fields["next_id"], {"offset": 0x0E, "size": 2})
        self.assertEqual(fields["sendbuf"], {"offset": 0x6021, "size": 1024})
        self.assertEqual(fields["tx_pos"]["offset"], 0x6424)
        self.assertEqual(fields["tx_len"]["offset"], 0x6428)
        self.assertEqual(fields["tx_cksum"]["offset"], 0x642C)
        self.assertEqual(fields["soft_lock"]["offset"], 0x642E)

    def test_direct_call_topology_separates_library_and_application(self) -> None:
        topology = self.report["direct_call_topology"]
        self.assertEqual(set(topology), set(self.analyzer.TARGETS))
        for name, expected in self.analyzer.EXPECTED_DIRECT_CALLERS.items():
            with self.subTest(name=name):
                self.assertEqual(topology[name]["direct_callers"], expected)
                self.assertEqual(topology[name]["entry"], self.analyzer.TARGETS[name])
        self.assertEqual(topology["TF_Query_Multipart"]["direct_callers"], [0x0045E76A])
        self.assertEqual(topology["TF_Multipart_Payload"]["direct_callers"], [0x0045E808])
        self.assertEqual(topology["TF_Multipart_Close"]["direct_callers"], [0x0045E858])

    def test_local_transport_and_callbacks_are_not_misclassified(self) -> None:
        local = self.report["local_boundaries"]
        write = local["TF_WriteImpl"]
        self.assertEqual(write["range"], [0x004D9522, 0x004D9530])
        self.assertIn("0x00541790", write["behavior"])
        self.assertEqual(
            write["classification"], "application transport; not upstream TinyFrame"
        )
        self.assertIn("application-owned", local["callbacks"])
        self.assertEqual(len(local["application_send_callers"]["response_builder_calls"]), 12)

    def test_official_history_interval_and_source_blobs_are_authenticated(self) -> None:
        upstream = self.report["upstream_provenance"]
        floor = upstream["source_equivalence_floor"]
        ceiling = upstream["source_equivalence_ceiling"]
        self.assertEqual(
            floor["commit"], "44ecc0686c6a6b89ec357b6ab187763089e2b2bc"
        )
        self.assertEqual(floor["tree"], "4cb10d005bc934172a62a5a2301946fc971bb66b")
        self.assertEqual(
            floor["TinyFrame.c_blob"], "771bc1d2c6ffbae6024f542e455a0c10209a5b2f"
        )
        self.assertEqual(
            ceiling["commit"], "a29167a69f052975b0e0134a73b4d31d03afa8fa"
        )
        self.assertEqual(
            ceiling["TinyFrame.c_blob"], "ac64150369dd155f26d1e47c1f5a10f92887298b"
        )
        self.assertEqual(
            upstream["formatting_successor"]["TinyFrame.h_blob"],
            "a142b4bba086f27565bd26282055c357364616b3",
        )

    def test_release_tag_is_excluded_and_exact_vendor_revision_fails_closed(self) -> None:
        version = self.report["version_recovery"]
        self.assertEqual(
            version["classification"],
            "post-2.3.0 official TinyFrame lineage with vendor patches",
        )
        self.assertIsNone(version["exact_vendor_commit_or_tree"])
        self.assertIsNone(version["exact_released_tag"])
        self.assertEqual(
            version["narrowest_official_send_source_equivalence_interval"],
            {
                "first": "44ecc0686c6a6b89ec357b6ab187763089e2b2bc",
                "last": "a29167a69f052975b0e0134a73b4d31d03afa8fa",
                "first_date": "2021-12-09T19:29:14+08:00",
                "last_date": "2021-12-09T13:33:34+01:00",
            },
        )
        self.assertIn("five-argument", version["lower_bound"])
        self.assertIn("predates TF_Listener_Timeout", version["why_release_2_3_0_is_excluded"])
        self.assertIn("cannot distinguish", version["why_interval_cannot_select_one_commit"])
        self.assertEqual(len(version["vendor_divergences"]), 4)

    def test_mit_license_and_latest_release_identity_are_pinned(self) -> None:
        upstream = self.report["upstream_provenance"]
        license_info = upstream["license"]
        self.assertEqual(license_info["spdx"], "MIT")
        self.assertEqual(
            license_info["git_blob_sha1"], "22acaabc6b85723107caae262ec537e710c19aac"
        )
        self.assertEqual(license_info["size"], 1072)
        self.assertEqual(
            license_info["sha256"],
            "eb7b9df3ca390100d31f9aac23f2d8dfe0183a63987112675fc58af9a42f6874",
        )
        release = upstream["latest_release_reference"]
        self.assertEqual(release["tag"], "2.3.0")
        self.assertEqual(release["tag_kind"], "lightweight")
        self.assertEqual(
            release["commit"], "74d6451d5076136ed05abb486bacb850ae75d1a9"
        )

    def test_invalid_reference_inputs_are_rejected(self) -> None:
        for args in (
            {"next_id": -1, "peer_bit": 0},
            {"next_id": 0x10000, "peer_bit": 0},
            {"next_id": 0, "peer_bit": 2},
        ):
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.analyzer.resolve_request_id(**args)
        with self.assertRaises(ValueError):
            self.analyzer.compose_reference(frame_type=0x10000, payload=b"")
        with self.assertRaises(ValueError):
            self.analyzer.compose_reference(frame_type=0, payload=b"x" * 0x10000)

    def test_mutated_or_truncated_images_are_rejected(self) -> None:
        for run in (
            0x004916CA,
            0x00491730,
            0x00491F84,
            0x0049215C,
            0x004D952A,
            0x006C0950,
            0x006FE474,
        ):
            with self.subTest(run=f"0x{run:08x}"):
                changed = bytearray(self.data)
                changed[run - self.analyzer.LOAD_BASE] ^= 1
                with self.assertRaises(self.analyzer.AuditError):
                    self.analyzer.audit(bytes(changed))
        with self.assertRaises(self.analyzer.AuditError):
            self.analyzer.audit(self.data[:-1])

    def test_cli_text_and_json_modes(self) -> None:
        text = subprocess.run(
            [sys.executable, str(ANALYZER)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertIn("44ecc068..a29167a6", text)
        self.assertIn("SOF || ID || LEN || TYPE", text)
        self.assertIn("exact vendor commit/tag: unresolved", text)
        parsed = json.loads(
            subprocess.run(
                [sys.executable, str(ANALYZER), "--json"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        )
        self.assertEqual(parsed["tx_configuration"]["TF_SENDBUF_LEN"], 1024)
        self.assertIsNone(parsed["version_recovery"]["exact_vendor_commit_or_tree"])


if __name__ == "__main__":
    unittest.main()
