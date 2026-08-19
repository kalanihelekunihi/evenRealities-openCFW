import importlib.util
import contextlib
import io
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "analyze_r1_hci_capture.py"
SPEC = importlib.util.spec_from_file_location("analyze_r1_hci_capture", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def pklg_record(packet_type, payload, seconds=1_700_000_000, microseconds=123_456):
    body = struct.pack(">II", seconds, microseconds) + bytes([packet_type]) + payload
    return struct.pack(">I", len(body)) + body


def hci_event(code, params):
    return bytes([code, len(params)]) + params


def acl_packet(handle, att, pb_flag=2):
    l2cap = struct.pack("<HH", len(att), 0x0004) + att
    return struct.pack("<HH", handle | (pb_flag << 12), len(l2cap)) + l2cap


def synthetic_capture():
    handle = 0x000B
    enhanced_complete = (
        bytes([0x0A, 0x00]) + struct.pack("<H", handle) + bytes([0x00, 0x01]) +
        bytes.fromhex("010203040506") + bytes(6) + bytes(6) +
        struct.pack("<HHH", 24, 0, 400) + bytes([0])
    )
    data_length = bytes([0x07]) + struct.pack("<HHHHH", handle, 251, 2120, 251, 2120)
    phy_update = bytes([0x0C, 0x00]) + struct.pack("<H", handle) + bytes([1, 1])
    encryption = bytes([0x00]) + struct.pack("<H", handle) + bytes([1])
    completed = bytes([1]) + struct.pack("<HH", handle, 42)
    status_value = bytes.fromhex("005C2C5C6364016400400000010C00EA3B")

    records = [
        pklg_record(MODULE.PKT_HCI_EVENT, hci_event(0x3E, enhanced_complete)),
        pklg_record(MODULE.PKT_HCI_EVENT, hci_event(0x08, encryption)),
        pklg_record(MODULE.PKT_HCI_EVENT, hci_event(0x3E, data_length)),
        pklg_record(MODULE.PKT_HCI_EVENT, hci_event(0x3E, phy_update)),
        pklg_record(MODULE.PKT_SENT_ACL_DATA,
                    acl_packet(handle, bytes([0x02]) + struct.pack("<H", 247))),
        pklg_record(MODULE.PKT_RECV_ACL_DATA,
                    acl_packet(handle, bytes([0x03]) + struct.pack("<H", 247))),
        pklg_record(MODULE.PKT_SENT_ACL_DATA,
                    acl_packet(handle, bytes([0x52]) + struct.pack("<H", 0x0015) + status_value)),
        pklg_record(MODULE.PKT_RECV_ACL_DATA,
                    acl_packet(handle, bytes([0x1B]) + struct.pack("<H", 0x0017) + bytes(19))),
        pklg_record(MODULE.PKT_SENT_ACL_DATA,
                    acl_packet(handle, bytes([0x16]) + struct.pack("<HH", 0x0015, 0) + b"x")),
        pklg_record(MODULE.PKT_RECV_ACL_DATA,
                    acl_packet(handle, bytes([0x01, 0x16]) + struct.pack("<H", 0x0015) + bytes([0x06]))),
        pklg_record(MODULE.PKT_HCI_EVENT, hci_event(0x13, completed)),
    ]
    return b"".join(records)


class AnalyzeR1HCICaptureTests(unittest.TestCase):
    def test_complete_capture_closes_all_supported_gates(self):
        capture = synthetic_capture()
        report = MODULE.analyze_capture(capture)
        gates = MODULE.evaluate_gates(
            report, channel2_write_handle=0x0015,
            channel2_notify_handle=0x0017)
        self.assertTrue(all(gates.values()), gates)
        self.assertEqual(report["byte_order"], "big")
        self.assertEqual(report["record_count"], 11)
        self.assertNotIn("010203040506", json.dumps(report))
        connection = report["connections"][0]
        self.assertEqual(connection["connection_complete"]["interval_ms"], 30.0)
        self.assertEqual(connection["effective_att_mtu"], 247)
        self.assertEqual(connection["completed_packets"], 42)
        self.assertEqual(connection["queued_write_errors"][0]["error_code"], 0x06)

    def test_note_only_capture_is_explicitly_not_hci_evidence(self):
        capture = pklg_record(MODULE.PKT_NOTE, b"Disconnected from OS X Device" + bytes(32))
        report = MODULE.analyze_capture(capture)
        gates = MODULE.evaluate_gates(report)
        self.assertEqual(report["record_type_counts"], {"note": 1})
        self.assertFalse(any(gates.values()))

    def test_l2cap_continuation_reassembles_att(self):
        handle = 7
        att = bytes([0x02]) + struct.pack("<H", 247)
        l2cap = struct.pack("<HH", len(att), 0x0004) + att
        first = l2cap[:5]
        second = l2cap[5:]
        first_acl = struct.pack("<HH", handle | (2 << 12), len(first)) + first
        second_acl = struct.pack("<HH", handle | (1 << 12), len(second)) + second
        capture = (
            pklg_record(MODULE.PKT_SENT_ACL_DATA, first_acl) +
            pklg_record(MODULE.PKT_SENT_ACL_DATA, second_acl)
        )
        report = MODULE.analyze_capture(capture)
        self.assertEqual(report["connections"][0]["mtu_requests"], [247])

    def test_incomplete_l2cap_reassembly_is_rejected(self):
        handle = 7
        first = struct.pack("<HH", 10, 0x0004) + b"x"
        acl = struct.pack("<HH", handle | (2 << 12), len(first)) + first
        with self.assertRaisesRegex(MODULE.CaptureError, "incomplete L2CAP"):
            MODULE.analyze_capture(pklg_record(MODULE.PKT_SENT_ACL_DATA, acl))

    def test_truncated_and_unknown_packetlogger_records_are_rejected(self):
        valid = pklg_record(MODULE.PKT_NOTE, b"ok")
        with self.assertRaisesRegex(MODULE.CaptureError, "truncated PacketLogger record"):
            MODULE.parse_packetlogger(valid[:-1])
        unknown = pklg_record(0x77, b"no")
        with self.assertRaisesRegex(MODULE.CaptureError, "unknown PacketLogger"):
            MODULE.parse_packetlogger(unknown)

    def test_cli_hash_and_required_evidence_fail_closed(self):
        capture = synthetic_capture()
        digest = MODULE.hashlib.sha256(capture).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "trace.pklg"
            output_path = Path(directory) / "trace.json"
            input_path.write_bytes(capture)
            result = MODULE.main([
                str(input_path), "--expect-sha256", digest,
                "--channel2-write-handle", "0x15",
                "--channel2-notify-handle", "0x17",
                "--require", "hci", "--require", "mtu",
                "--require", "data-length", "--require", "phy",
                "--require", "encryption", "--require", "completed-packets",
                "--require", "queued-write-rejection",
                "--require", "channel2-traffic", "--output", str(output_path),
            ])
            self.assertEqual(result, 0)
            self.assertTrue(all(json.loads(output_path.read_text())["gates"].values()))
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(MODULE.main([
                    str(input_path), "--expect-sha256", "0" * 64,
                ]), 2)


if __name__ == "__main__":
    unittest.main()
