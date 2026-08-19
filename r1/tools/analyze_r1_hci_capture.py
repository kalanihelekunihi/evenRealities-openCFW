#!/usr/bin/env python3
"""Strict Apple PacketLogger HCI/ATT evidence analyzer for owned R1 traces.

The .pklg record envelope and packet-type values are independently documented
by Wireshark's upstream wiretap/packetlogger.c reader. This implementation is
small, allocation-bounded by the input file, rejects truncated records, and
emits only protocol metadata: it never reproduces peer addresses, keys, or ATT
value bytes in its JSON output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


PKT_HCI_COMMAND = 0x00
PKT_HCI_EVENT = 0x01
PKT_SENT_ACL_DATA = 0x02
PKT_RECV_ACL_DATA = 0x03
PKT_SENT_SCO_DATA = 0x08
PKT_RECV_SCO_DATA = 0x09
PKT_LMP_SEND = 0x0A
PKT_LMP_RECV = 0x0B
PKT_SYSLOG = 0xF7
PKT_KERNEL = 0xF8
PKT_KERNEL_DEBUG = 0xF9
PKT_ERROR = 0xFA
PKT_POWER = 0xFB
PKT_NOTE = 0xFC
PKT_CONFIG = 0xFD
PKT_NEW_CONTROLLER = 0xFE

KNOWN_RECORD_TYPES = {
    PKT_HCI_COMMAND,
    PKT_HCI_EVENT,
    PKT_SENT_ACL_DATA,
    PKT_RECV_ACL_DATA,
    PKT_SENT_SCO_DATA,
    PKT_RECV_SCO_DATA,
    PKT_LMP_SEND,
    PKT_LMP_RECV,
    PKT_SYSLOG,
    PKT_KERNEL,
    PKT_KERNEL_DEBUG,
    PKT_ERROR,
    PKT_POWER,
    PKT_NOTE,
    PKT_CONFIG,
    PKT_NEW_CONTROLLER,
}

RECORD_TYPE_NAMES = {
    PKT_HCI_COMMAND: "hci_command",
    PKT_HCI_EVENT: "hci_event",
    PKT_SENT_ACL_DATA: "acl_sent",
    PKT_RECV_ACL_DATA: "acl_received",
    PKT_SENT_SCO_DATA: "sco_sent",
    PKT_RECV_SCO_DATA: "sco_received",
    PKT_LMP_SEND: "lmp_sent",
    PKT_LMP_RECV: "lmp_received",
    PKT_SYSLOG: "syslog",
    PKT_KERNEL: "kernel",
    PKT_KERNEL_DEBUG: "kernel_debug",
    PKT_ERROR: "error",
    PKT_POWER: "power",
    PKT_NOTE: "note",
    PKT_CONFIG: "config",
    PKT_NEW_CONTROLLER: "new_controller",
}

ATT_NAMES = {
    0x01: "error_response",
    0x02: "exchange_mtu_request",
    0x03: "exchange_mtu_response",
    0x12: "write_request",
    0x13: "write_response",
    0x16: "prepare_write_request",
    0x17: "prepare_write_response",
    0x18: "execute_write_request",
    0x19: "execute_write_response",
    0x1B: "handle_value_notification",
    0x1D: "handle_value_indication",
    0x1E: "handle_value_confirmation",
    0x52: "write_command",
}

GATE_NAMES = (
    "hci",
    "mtu",
    "data-length",
    "phy",
    "encryption",
    "completed-packets",
    "queued-write-rejection",
    "channel2-traffic",
)


class CaptureError(ValueError):
    """The capture is malformed or does not satisfy a strict parser rule."""


@dataclass(frozen=True)
class PacketLoggerRecord:
    index: int
    seconds: int
    microseconds: int
    packet_type: int
    payload: bytes


@dataclass
class L2CAPFragment:
    expected_length: int
    cid: int
    data: bytearray


@dataclass
class ConnectionEvidence:
    handle: int
    role: str | None = None
    connection_complete: dict[str, Any] | None = None
    interval_updates: list[dict[str, Any]] = field(default_factory=list)
    data_length_changes: list[dict[str, Any]] = field(default_factory=list)
    phy_updates: list[dict[str, Any]] = field(default_factory=list)
    encryption_changes: list[dict[str, Any]] = field(default_factory=list)
    completed_packets: int = 0
    acl_sent: int = 0
    acl_received: int = 0
    att_events: list[dict[str, Any]] = field(default_factory=list)
    disconnected_reason: int | None = None


def _u16(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise CaptureError("truncated little-endian UInt16")
    return data[offset] | (data[offset + 1] << 8)


def _choose_endian(data: bytes) -> str:
    if len(data) < 12:
        raise CaptureError("PacketLogger file is shorter than one record header")
    candidates: list[str] = []
    for endian in (">", "<"):
        length, _, microseconds = struct.unpack_from(f"{endian}III", data, 0)
        if 8 <= length < 65536 and microseconds < 1_000_000:
            candidates.append(endian)
    if not candidates:
        raise CaptureError("first PacketLogger record has invalid length or timestamp")
    if len(candidates) == 1:
        return candidates[0]
    # Contemporary macOS captures are big-endian. If both interpretations are
    # superficially possible, require the first known packet type to decide.
    for endian in candidates:
        length = struct.unpack_from(f"{endian}I", data, 0)[0]
        if length > 8 and data[12] in KNOWN_RECORD_TYPES:
            return endian
    raise CaptureError("PacketLogger byte order is ambiguous")


def parse_packetlogger(data: bytes) -> tuple[str, list[PacketLoggerRecord]]:
    endian = _choose_endian(data)
    records: list[PacketLoggerRecord] = []
    offset = 0
    while offset < len(data):
        if len(data) - offset < 12:
            raise CaptureError(f"truncated PacketLogger header at byte {offset}")
        length, seconds, microseconds = struct.unpack_from(
            f"{endian}III", data, offset)
        if length < 9 or length >= 65536:
            raise CaptureError(f"invalid PacketLogger record length {length} at byte {offset}")
        if microseconds >= 1_000_000:
            raise CaptureError(f"invalid PacketLogger microseconds at record {len(records)}")
        end = offset + 4 + length
        if end > len(data):
            raise CaptureError(f"truncated PacketLogger record {len(records)}")
        packet_type = data[offset + 12]
        if packet_type not in KNOWN_RECORD_TYPES:
            raise CaptureError(
                f"unknown PacketLogger packet type 0x{packet_type:02x} at record {len(records)}")
        records.append(PacketLoggerRecord(
            index=len(records),
            seconds=seconds,
            microseconds=microseconds,
            packet_type=packet_type,
            payload=data[offset + 13:end],
        ))
        offset = end
    if not records:
        raise CaptureError("PacketLogger file contains no records")
    return ("big" if endian == ">" else "little"), records


def _connection(connections: dict[int, ConnectionEvidence], handle: int) -> ConnectionEvidence:
    if handle < 0 or handle > 0x0EFF:
        raise CaptureError(f"invalid HCI connection handle 0x{handle:04x}")
    return connections.setdefault(handle, ConnectionEvidence(handle=handle))


def _parse_hci_event(record: PacketLoggerRecord,
                     connections: dict[int, ConnectionEvidence]) -> None:
    data = record.payload
    if len(data) < 2:
        raise CaptureError(f"truncated HCI event at record {record.index}")
    event_code = data[0]
    parameter_length = data[1]
    if len(data) != parameter_length + 2:
        raise CaptureError(f"HCI event length mismatch at record {record.index}")
    params = data[2:]

    if event_code == 0x05:  # Disconnection Complete
        if len(params) != 4:
            raise CaptureError("malformed Disconnection Complete event")
        connection = _connection(connections, _u16(params, 1) & 0x0FFF)
        connection.disconnected_reason = params[3]
        return
    if event_code == 0x08:  # Encryption Change
        if len(params) != 4:
            raise CaptureError("malformed Encryption Change event")
        connection = _connection(connections, _u16(params, 1) & 0x0FFF)
        connection.encryption_changes.append({
            "record": record.index,
            "status": params[0],
            "enabled": params[3],
        })
        return
    if event_code == 0x13:  # Number Of Completed Packets
        if not params:
            raise CaptureError("malformed Number Of Completed Packets event")
        count = params[0]
        if len(params) != 1 + count * 4:
            raise CaptureError("Number Of Completed Packets length mismatch")
        for index in range(count):
            base = 1 + index * 4
            handle = _u16(params, base) & 0x0FFF
            completed = _u16(params, base + 2)
            _connection(connections, handle).completed_packets += completed
        return
    if event_code == 0x0E:  # Command Complete; capture LE Read PHY result
        if len(params) < 3:
            raise CaptureError("malformed Command Complete event")
        opcode = _u16(params, 1)
        returned = params[3:]
        if opcode == 0x2030 and len(returned) == 5:
            connection = _connection(connections, _u16(returned, 1) & 0x0FFF)
            connection.phy_updates.append({
                "record": record.index,
                "source": "le_read_phy",
                "status": returned[0],
                "tx_phy": returned[3],
                "rx_phy": returned[4],
            })
        return
    if event_code != 0x3E:  # LE Meta Event
        return
    if not params:
        raise CaptureError("malformed LE Meta event")
    subevent = params[0]
    if subevent == 0x01:  # LE Connection Complete
        if len(params) != 19:
            raise CaptureError("malformed LE Connection Complete event")
        connection = _connection(connections, _u16(params, 2) & 0x0FFF)
        interval = _u16(params, 12)
        connection.role = "central" if params[4] == 0 else "peripheral"
        connection.connection_complete = {
            "record": record.index,
            "status": params[1],
            "kind": "le_connection_complete",
            "interval_units": interval,
            "interval_ms": interval * 1.25,
            "latency": _u16(params, 14),
            "supervision_timeout_units": _u16(params, 16),
            "supervision_timeout_ms": _u16(params, 16) * 10,
        }
    elif subevent == 0x0A:  # LE Enhanced Connection Complete
        if len(params) != 31:
            raise CaptureError("malformed LE Enhanced Connection Complete event")
        connection = _connection(connections, _u16(params, 2) & 0x0FFF)
        interval = _u16(params, 24)
        connection.role = "central" if params[4] == 0 else "peripheral"
        connection.connection_complete = {
            "record": record.index,
            "status": params[1],
            "kind": "le_enhanced_connection_complete",
            "interval_units": interval,
            "interval_ms": interval * 1.25,
            "latency": _u16(params, 26),
            "supervision_timeout_units": _u16(params, 28),
            "supervision_timeout_ms": _u16(params, 28) * 10,
        }
    elif subevent == 0x03:  # LE Connection Update Complete
        if len(params) != 10:
            raise CaptureError("malformed LE Connection Update Complete event")
        connection = _connection(connections, _u16(params, 2) & 0x0FFF)
        interval = _u16(params, 4)
        connection.interval_updates.append({
            "record": record.index,
            "status": params[1],
            "interval_units": interval,
            "interval_ms": interval * 1.25,
            "latency": _u16(params, 6),
            "supervision_timeout_units": _u16(params, 8),
            "supervision_timeout_ms": _u16(params, 8) * 10,
        })
    elif subevent == 0x07:  # LE Data Length Change
        if len(params) != 11:
            raise CaptureError("malformed LE Data Length Change event")
        connection = _connection(connections, _u16(params, 1) & 0x0FFF)
        connection.data_length_changes.append({
            "record": record.index,
            "max_tx_octets": _u16(params, 3),
            "max_tx_time_us": _u16(params, 5),
            "max_rx_octets": _u16(params, 7),
            "max_rx_time_us": _u16(params, 9),
        })
    elif subevent == 0x0C:  # LE PHY Update Complete
        if len(params) != 6:
            raise CaptureError("malformed LE PHY Update Complete event")
        connection = _connection(connections, _u16(params, 2) & 0x0FFF)
        connection.phy_updates.append({
            "record": record.index,
            "source": "le_phy_update_complete",
            "status": params[1],
            "tx_phy": params[4],
            "rx_phy": params[5],
        })


def _att_event(record: PacketLoggerRecord, direction: str, att: bytes) -> dict[str, Any]:
    if not att:
        raise CaptureError(f"empty ATT PDU at record {record.index}")
    opcode = att[0]
    event: dict[str, Any] = {
        "record": record.index,
        "direction": direction,
        "opcode": opcode,
        "name": ATT_NAMES.get(opcode, "unknown"),
        "pdu_bytes": len(att),
    }
    if opcode in {0x02, 0x03}:
        if len(att) != 3:
            raise CaptureError(f"malformed ATT MTU PDU at record {record.index}")
        event["mtu"] = _u16(att, 1)
    elif opcode == 0x01:
        if len(att) != 5:
            raise CaptureError(f"malformed ATT Error Response at record {record.index}")
        event.update({
            "request_opcode": att[1],
            "attribute_handle": _u16(att, 2),
            "error_code": att[4],
        })
    elif opcode in {0x12, 0x16, 0x17, 0x1B, 0x1D, 0x52}:
        if len(att) < 3:
            raise CaptureError(f"truncated handle-bearing ATT PDU at record {record.index}")
        event["attribute_handle"] = _u16(att, 1)
        event["value_bytes"] = len(att) - 3
        if opcode in {0x12, 0x52}:
            value = att[3:]
            if value == bytes.fromhex("00008900000000"):
                event["r1_frame"] = "channel1_nonmutating"
            elif len(value) >= 17 and value[0] == 0:
                event["r1_frame"] = "channel2_fragment_candidate"
    elif opcode == 0x18:
        if len(att) != 2:
            raise CaptureError(f"malformed Execute Write Request at record {record.index}")
        event["flags"] = att[1]
    elif opcode in {0x13, 0x19, 0x1E}:
        if len(att) != 1:
            raise CaptureError(f"malformed zero-payload ATT response at record {record.index}")
    return event


def _decode_l2cap(record: PacketLoggerRecord, direction: str, handle: int,
                  cid: int, payload: bytes,
                  connections: dict[int, ConnectionEvidence]) -> None:
    if cid != 0x0004:  # ATT fixed channel
        return
    connection = _connection(connections, handle)
    connection.att_events.append(_att_event(record, direction, payload))


def _parse_acl(record: PacketLoggerRecord, direction: str,
               connections: dict[int, ConnectionEvidence],
               fragments: dict[tuple[str, int], L2CAPFragment]) -> None:
    data = record.payload
    if len(data) < 4:
        raise CaptureError(f"truncated HCI ACL header at record {record.index}")
    handle_flags = _u16(data, 0)
    handle = handle_flags & 0x0FFF
    pb_flag = (handle_flags >> 12) & 0x03
    declared = _u16(data, 2)
    if len(data) != 4 + declared:
        raise CaptureError(f"HCI ACL length mismatch at record {record.index}")
    acl_payload = data[4:]
    connection = _connection(connections, handle)
    if direction == "sent":
        connection.acl_sent += 1
    else:
        connection.acl_received += 1
    key = (direction, handle)
    if pb_flag == 1:  # continuation fragment
        fragment = fragments.get(key)
        if fragment is None:
            raise CaptureError(f"orphan HCI ACL continuation at record {record.index}")
        fragment.data.extend(acl_payload)
        if len(fragment.data) > fragment.expected_length:
            raise CaptureError(f"oversized L2CAP reassembly at record {record.index}")
        if len(fragment.data) == fragment.expected_length:
            _decode_l2cap(record, direction, handle, fragment.cid,
                          bytes(fragment.data), connections)
            del fragments[key]
        return
    if len(acl_payload) < 4:
        raise CaptureError(f"truncated L2CAP header at record {record.index}")
    l2cap_length = _u16(acl_payload, 0)
    cid = _u16(acl_payload, 2)
    body = acl_payload[4:]
    if len(body) > l2cap_length:
        raise CaptureError(f"L2CAP payload exceeds declared length at record {record.index}")
    if key in fragments:
        raise CaptureError(f"new L2CAP start before prior completion at record {record.index}")
    if len(body) == l2cap_length:
        _decode_l2cap(record, direction, handle, cid, body, connections)
    else:
        fragments[key] = L2CAPFragment(l2cap_length, cid, bytearray(body))


def analyze_capture(data: bytes) -> dict[str, Any]:
    byte_order, records = parse_packetlogger(data)
    connections: dict[int, ConnectionEvidence] = {}
    fragments: dict[tuple[str, int], L2CAPFragment] = {}
    type_counts: dict[str, int] = {}
    for record in records:
        name = RECORD_TYPE_NAMES[record.packet_type]
        type_counts[name] = type_counts.get(name, 0) + 1
        if record.packet_type == PKT_HCI_EVENT:
            _parse_hci_event(record, connections)
        elif record.packet_type == PKT_SENT_ACL_DATA:
            _parse_acl(record, "sent", connections, fragments)
        elif record.packet_type == PKT_RECV_ACL_DATA:
            _parse_acl(record, "received", connections, fragments)
    if fragments:
        pending = ", ".join(f"{direction}:0x{handle:04x}"
                            for direction, handle in sorted(fragments))
        raise CaptureError(f"capture ends with incomplete L2CAP reassembly: {pending}")

    serialized_connections: list[dict[str, Any]] = []
    for handle in sorted(connections):
        connection = connections[handle]
        mtu_requests = [event["mtu"] for event in connection.att_events
                        if event["opcode"] == 0x02]
        mtu_responses = [event["mtu"] for event in connection.att_events
                         if event["opcode"] == 0x03]
        effective_mtu = (min(mtu_requests[-1], mtu_responses[-1])
                         if mtu_requests and mtu_responses else None)
        queued_errors = [event for event in connection.att_events
                         if event["opcode"] == 0x01 and
                         event.get("request_opcode") in {0x16, 0x18}]
        by_attribute: dict[str, dict[str, int]] = {}
        for event in connection.att_events:
            attribute = event.get("attribute_handle")
            if attribute is None:
                continue
            key = f"0x{attribute:04x}"
            counts = by_attribute.setdefault(key, {})
            counts[event["name"]] = counts.get(event["name"], 0) + 1
        serialized_connections.append({
            "handle": f"0x{handle:04x}",
            "role": connection.role,
            "connection_complete": connection.connection_complete,
            "interval_updates": connection.interval_updates,
            "data_length_changes": connection.data_length_changes,
            "phy_updates": connection.phy_updates,
            "encryption_changes": connection.encryption_changes,
            "completed_packets": connection.completed_packets,
            "acl_sent_records": connection.acl_sent,
            "acl_received_records": connection.acl_received,
            "att_event_count": len(connection.att_events),
            "att_counts_by_attribute": by_attribute,
            "mtu_requests": mtu_requests,
            "mtu_responses": mtu_responses,
            "effective_att_mtu": effective_mtu,
            "queued_write_errors": [{
                "record": event["record"],
                "request_opcode": event["request_opcode"],
                "attribute_handle": f"0x{event['attribute_handle']:04x}",
                "error_code": event["error_code"],
            } for event in queued_errors],
            "disconnected_reason": connection.disconnected_reason,
        })
    return {
        "format": "apple-packetlogger",
        "byte_order": byte_order,
        "capture_sha256": hashlib.sha256(data).hexdigest(),
        "capture_bytes": len(data),
        "record_count": len(records),
        "record_type_counts": type_counts,
        "privacy": "peer addresses keys and ATT values omitted",
        "connections": serialized_connections,
    }


def _parse_handle(value: str) -> int:
    try:
        parsed = int(value, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid handle: {value}") from error
    if parsed < 1 or parsed > 0x0EFF:
        raise argparse.ArgumentTypeError("handle must be 1..0x0eff")
    return parsed


def evaluate_gates(report: dict[str, Any], *,
                   channel2_write_handle: int | None = None,
                   channel2_notify_handle: int | None = None) -> dict[str, bool]:
    connections = report["connections"]
    hci_count = sum(report["record_type_counts"].get(name, 0)
                    for name in ("hci_command", "hci_event", "acl_sent", "acl_received"))
    mtu = any(connection["effective_att_mtu"] is not None for connection in connections)
    data_length = any(connection["data_length_changes"] for connection in connections)
    phy = any(any(update.get("status") == 0 for update in connection["phy_updates"])
              for connection in connections)
    encryption = any(any(change["status"] == 0 and change["enabled"] != 0
                         for change in connection["encryption_changes"])
                     for connection in connections)
    completed = any(connection["completed_packets"] > 0 for connection in connections)
    queued = any(connection["queued_write_errors"] for connection in connections)
    channel2 = False
    if channel2_write_handle is not None and channel2_notify_handle is not None:
        write_key = f"0x{channel2_write_handle:04x}"
        notify_key = f"0x{channel2_notify_handle:04x}"
        channel2 = any(
            connection["att_counts_by_attribute"].get(write_key, {}).get("write_command", 0) > 0 and
            connection["att_counts_by_attribute"].get(notify_key, {}).get("handle_value_notification", 0) > 0
            for connection in connections)
    return {
        "hci": hci_count > 0,
        "mtu": mtu,
        "data-length": data_length,
        "phy": phy,
        "encryption": encryption,
        "completed-packets": completed,
        "queued-write-rejection": queued,
        "channel2-traffic": channel2,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Strictly summarize Apple PacketLogger HCI evidence without emitting private payloads")
    parser.add_argument("capture", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expect-sha256")
    parser.add_argument("--channel2-write-handle", type=_parse_handle)
    parser.add_argument("--channel2-notify-handle", type=_parse_handle)
    parser.add_argument("--require", action="append", choices=GATE_NAMES, default=[])
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    try:
        data = args.capture.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if args.expect_sha256 is not None and digest.lower() != args.expect_sha256.lower():
            raise CaptureError(
                f"capture SHA-256 mismatch: expected {args.expect_sha256.lower()}, observed {digest}")
        if ((args.channel2_write_handle is None) !=
                (args.channel2_notify_handle is None)):
            raise CaptureError("both channel-2 handles are required together")
        report = analyze_capture(data)
        gates = evaluate_gates(
            report,
            channel2_write_handle=args.channel2_write_handle,
            channel2_notify_handle=args.channel2_notify_handle,
        )
        report["gates"] = gates
        missing = [name for name in args.require if not gates[name]]
        if missing:
            raise CaptureError("required evidence missing: " + ", ".join(missing))
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.output is None:
            sys.stdout.write(rendered)
        else:
            args.output.write_text(rendered, encoding="utf-8")
        return 0
    except (CaptureError, OSError) as error:
        print(f"R1 HCI capture rejected: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
