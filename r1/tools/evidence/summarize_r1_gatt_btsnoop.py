#!/usr/bin/env python3
"""Summarize R1 GATT discovery and lane use from an Android btsnoop log.

The report deliberately omits Bluetooth addresses and attribute values. It maps
service/characteristic declarations, characteristic property bits, CCCD writes,
and payload-free ATT event counts so direct R1 lane roles can be verified without
publishing device identity or health data.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import struct
from typing import Any, Iterator


BTSNOOP_HEADER = b"btsnoop\x00"
R1_SERVICE_PREFIX = "bae800"
CHARACTERISTIC_PROPERTIES = (
    (0x01, "broadcast"),
    (0x02, "read"),
    (0x04, "write_without_response"),
    (0x08, "write"),
    (0x10, "notify"),
    (0x20, "indicate"),
    (0x40, "authenticated_signed_writes"),
    (0x80, "extended_properties"),
)


def iter_btsnoop(path: Path) -> Iterator[tuple[int, int, bytes]]:
    with path.open("rb") as source:
        header = source.read(16)
        if not header.startswith(BTSNOOP_HEADER):
            raise ValueError("not a Bluetooth btsnoop v1 file")
        while True:
            record = source.read(24)
            if len(record) < 24:
                return
            _, included, flags, _, ts_hi, ts_lo = struct.unpack(">IIIIII", record)
            packet = source.read(included)
            if len(packet) != included:
                return
            timestamp_us = ((ts_hi << 32) | ts_lo) - 0x00DCDDB30F2F8000
            yield timestamp_us, flags, packet


def normalize_uuid(raw: bytes) -> str:
    if len(raw) == 2:
        return f"{int.from_bytes(raw, 'little'):04x}"
    if len(raw) == 4:
        return f"{int.from_bytes(raw, 'little'):08x}"
    if len(raw) == 16:
        value = raw[::-1].hex()
        return (
            f"{value[0:8]}-{value[8:12]}-{value[12:16]}-"
            f"{value[16:20]}-{value[20:32]}"
        )
    return raw.hex()


def properties(raw: int) -> list[str]:
    return [name for mask, name in CHARACTERISTIC_PROPERTIES if raw & mask]


@dataclass
class Characteristic:
    declaration_handle: int
    value_handle: int
    uuid: str
    raw_properties: int


@dataclass
class Service:
    start_handle: int
    end_handle: int
    uuid: str


@dataclass
class Session:
    ordinal: int
    started_at_us: int | None = None
    services: list[Service] = field(default_factory=list)
    characteristics: dict[int, Characteristic] = field(default_factory=dict)
    descriptors: dict[int, str] = field(default_factory=dict)
    pending_read_type: str | None = None
    pending_group_type: str | None = None
    att_counts: Counter[tuple[str, int]] = field(default_factory=Counter)
    cccd_writes: Counter[tuple[int, str]] = field(default_factory=Counter)
    eus_counts: Counter[tuple[str, int]] = field(default_factory=Counter)

    def nearest_characteristic(self, descriptor_handle: int) -> Characteristic | None:
        candidates = [
            item for handle, item in self.characteristics.items()
            if handle < descriptor_handle
        ]
        return max(candidates, key=lambda item: item.value_handle, default=None)


def parse_characteristics(pdu: bytes, session: Session) -> None:
    if len(pdu) < 2 or session.pending_read_type != "2803":
        return
    record_length = pdu[1]
    if record_length not in (7, 21):
        return
    offset = 2
    while offset + record_length <= len(pdu):
        record = pdu[offset:offset + record_length]
        declaration_handle = int.from_bytes(record[0:2], "little")
        raw_properties = record[2]
        value_handle = int.from_bytes(record[3:5], "little")
        session.characteristics[value_handle] = Characteristic(
            declaration_handle=declaration_handle,
            value_handle=value_handle,
            uuid=normalize_uuid(record[5:]),
            raw_properties=raw_properties,
        )
        offset += record_length


def parse_services(pdu: bytes, session: Session) -> None:
    if len(pdu) < 2 or session.pending_group_type != "2800":
        return
    record_length = pdu[1]
    if record_length not in (6, 20):
        return
    offset = 2
    while offset + record_length <= len(pdu):
        record = pdu[offset:offset + record_length]
        session.services.append(Service(
            start_handle=int.from_bytes(record[0:2], "little"),
            end_handle=int.from_bytes(record[2:4], "little"),
            uuid=normalize_uuid(record[4:]),
        ))
        offset += record_length


def parse_find_information(pdu: bytes, session: Session) -> None:
    if len(pdu) < 2:
        return
    record_length = 4 if pdu[1] == 0x01 else 18
    offset = 2
    while offset + record_length <= len(pdu):
        record = pdu[offset:offset + record_length]
        session.descriptors[int.from_bytes(record[0:2], "little")] = normalize_uuid(record[2:])
        offset += record_length


def crc32_r1(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) & 0xFFFFFFFF) ^ (
                0x1EDC6F41 if crc & 0x80000000 else 0
            )
    return crc


def is_single_fragment_eus(value: bytes) -> bool:
    if len(value) < 17 or value[0] != 0:
        return False
    logical = value[5:]
    if logical[0] != 100 or logical[2] != 100:
        return False
    if int.from_bytes(logical[8:10], "little") != len(logical):
        return False
    return crc32_r1(logical) == int.from_bytes(value[1:5], "little")


def parse_att(pdu: bytes, direction: str, session: Session) -> None:
    if not pdu:
        return
    opcode = pdu[0]
    if opcode == 0x08 and len(pdu) >= 7:  # Read By Type Request
        session.pending_read_type = normalize_uuid(pdu[5:])
    elif opcode == 0x09:  # Read By Type Response
        parse_characteristics(pdu, session)
        session.pending_read_type = None
    elif opcode == 0x10 and len(pdu) >= 7:  # Read By Group Type Request
        session.pending_group_type = normalize_uuid(pdu[5:])
    elif opcode == 0x11:  # Read By Group Type Response
        parse_services(pdu, session)
        session.pending_group_type = None
    elif opcode == 0x05:  # Find Information Response
        parse_find_information(pdu, session)
    elif opcode in (0x12, 0x52) and len(pdu) >= 3:
        handle = int.from_bytes(pdu[1:3], "little")
        value = pdu[3:]
        kind = "write_request" if opcode == 0x12 else "write_command"
        session.att_counts[(kind, handle)] += 1
        if is_single_fragment_eus(value):
            session.eus_counts[(kind, handle)] += 1
        if session.descriptors.get(handle) == "2902" and len(value) == 2:
            cccd = int.from_bytes(value, "little")
            label = {
                0: "disabled", 1: "notifications", 2: "indications"
            }.get(cccd, f"unknown_0x{cccd:04x}")
            session.cccd_writes[(handle, label)] += 1
    elif opcode in (0x1B, 0x1D) and len(pdu) >= 3:
        handle = int.from_bytes(pdu[1:3], "little")
        value = pdu[3:]
        kind = "notification" if opcode == 0x1B else "indication"
        session.att_counts[(kind, handle)] += 1
        if is_single_fragment_eus(value):
            session.eus_counts[(kind, handle)] += 1


def timestamp(value_us: int | None) -> str | None:
    if value_us is None:
        return None
    return datetime.fromtimestamp(value_us / 1_000_000, tz=timezone.utc).isoformat()


def summarize(path: Path) -> dict[str, Any]:
    active: dict[int, Session] = {}
    completed: list[Session] = []
    next_ordinal = 1
    records = 0

    for timestamp_us, flags, packet in iter_btsnoop(path):
        records += 1
        if not packet:
            continue
        if packet[0] == 0x04 and len(packet) >= 4:  # HCI Event
            event_code = packet[1]
            if event_code == 0x05 and len(packet) >= 7:  # Disconnection Complete
                handle = int.from_bytes(packet[4:6], "little") & 0x0FFF
                old = active.pop(handle, None)
                if old is not None:
                    completed.append(old)
            elif event_code == 0x3E and len(packet) >= 7:  # LE Meta Event
                subevent = packet[3]
                if subevent in (0x01, 0x0A) and packet[4] == 0:
                    handle = int.from_bytes(packet[5:7], "little") & 0x0FFF
                    old = active.pop(handle, None)
                    if old is not None:
                        completed.append(old)
                    active[handle] = Session(next_ordinal, timestamp_us)
                    next_ordinal += 1
            continue
        if packet[0] != 0x02 or len(packet) < 9:  # HCI ACL
            continue
        handle_and_flags, acl_length = struct.unpack_from("<HH", packet, 1)
        connection_handle = handle_and_flags & 0x0FFF
        packet_boundary = (handle_and_flags >> 12) & 0x03
        if packet_boundary not in (0x00, 0x02):
            continue
        acl = packet[5:5 + acl_length]
        if len(acl) < 4:
            continue
        l2cap_length, channel_id = struct.unpack_from("<HH", acl, 0)
        if channel_id != 0x0004:
            continue
        session = active.get(connection_handle)
        if session is None:
            session = Session(next_ordinal)
            active[connection_handle] = session
            next_ordinal += 1
        direction = "rx" if flags & 0x01 else "tx"
        parse_att(acl[4:4 + l2cap_length], direction, session)

    completed.extend(active.values())
    reports = []
    for session in completed:
        r1_services = [service for service in session.services if service.uuid.startswith(R1_SERVICE_PREFIX)]
        r1_characteristics = [
            item for item in session.characteristics.values()
            if item.uuid.startswith(R1_SERVICE_PREFIX)
        ]
        if not r1_services and not r1_characteristics and not session.eus_counts:
            continue
        service_ranges = [(item.start_handle, item.end_handle) for item in r1_services]

        def belongs_to_r1(handle: int) -> bool:
            return any(start <= handle <= end for start, end in service_ranges) or (
                handle in session.characteristics
                and session.characteristics[handle].uuid.startswith(R1_SERVICE_PREFIX)
            )

        characteristics = []
        for item in sorted(r1_characteristics, key=lambda value: value.value_handle):
            counts = {
                kind: count for (kind, handle), count in sorted(session.att_counts.items())
                if handle == item.value_handle
            }
            cccd = []
            for (descriptor_handle, mode), count in sorted(session.cccd_writes.items()):
                owner = session.nearest_characteristic(descriptor_handle)
                if owner is not None and owner.value_handle == item.value_handle:
                    cccd.append({
                        "descriptor_handle": descriptor_handle,
                        "mode": mode,
                        "writes": count,
                    })
            characteristics.append({
                "uuid": item.uuid,
                "declaration_handle": item.declaration_handle,
                "value_handle": item.value_handle,
                "properties": properties(item.raw_properties),
                "att_events": counts,
                "cccd_writes": cccd,
            })
        unmapped = [
            {"kind": kind, "handle": handle, "events": count}
            for (kind, handle), count in sorted(session.att_counts.items())
            if belongs_to_r1(handle) and handle not in session.characteristics
            and session.descriptors.get(handle) != "2902"
        ]
        reports.append({
            "session": session.ordinal,
            "started_at": timestamp(session.started_at_us),
            "r1_inferred_from_valid_eus": bool(session.eus_counts),
            "r1_gatt_declarations_present": bool(r1_services or r1_characteristics),
            "eus_att_handles": [
                {"kind": kind, "handle": handle, "models": count}
                for (kind, handle), count in sorted(session.eus_counts.items())
            ],
            "services": [
                {
                    "uuid": item.uuid,
                    "start_handle": item.start_handle,
                    "end_handle": item.end_handle,
                }
                for item in r1_services
            ],
            "characteristics": characteristics,
            "unmapped_r1_handle_events": unmapped,
        })

    return {
        "source": str(path),
        "privacy": "peer addresses and attribute values omitted",
        "btsnoop_records": records,
        "r1_sessions": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("btsnoop_log", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.btsnoop_log), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
