#!/usr/bin/env python3
"""Execute production packetAck matching with locks and callbacks intercepted.

The handler and resolver run only in private emulated RAM. No BLE, live pending-command table,
device callback, sensor, storage, physical hardware, or host health store is accessed.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


HANDLER = 0x000842CC
LOCK_ENTER = 0x00048234
LOCK_EXIT = 0x00048258
CALLBACK = 0x0004D2F0
CALLBACK_THUMB = CALLBACK | 1
PENDING_TABLE = 0x20019EF4
ENTRY_COUNT = 32
ENTRY_STRIDE = 20
REQUEST = RAM_BASE + 0x37400
SESSION = RAM_BASE + 0x37500


def entry_bytes(
    *,
    active: int = 0,
    module: int = 0,
    command: int = 0,
    subcommand: int = 0,
    sequence: int = 0,
    callback_thumb: int = 0,
    context: int = 0,
    tail: int = 0,
) -> bytes:
    return struct.pack(
        "<BBBBH2xIII",
        active,
        module,
        command,
        subcommand,
        sequence,
        callback_thumb,
        context,
        tail,
    )


def decode_entry(raw: bytes) -> dict[str, Any]:
    active, module, command, subcommand, sequence, callback, context, tail = struct.unpack(
        "<BBBBH2xIII", raw
    )
    return {
        "active": active,
        "module": module,
        "command": command,
        "subcommand": subcommand,
        "sequence": sequence,
        "callback_thumb": f"0x{callback:08x}",
        "context": f"0x{context:08x}",
        "tail": f"0x{tail:08x}",
    }


class PacketAckFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.effects: list[dict[str, Any]] = []
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == LOCK_ENTER:
            self.effects.append({"operation": "lock_enter"})
            self._return(uc)
        elif address == LOCK_EXIT:
            self.effects.append({"operation": "lock_exit"})
            self._return(uc)
        elif address == CALLBACK:
            self.effects.append({
                "operation": "callback",
                "context": f"0x{uc.reg_read(UC_ARM_REG_R0):08x}",
            })
            self._return(uc)

    def run(
        self,
        *,
        declared_frame_length: int,
        payload: bytes,
        entries: dict[int, bytes],
    ) -> dict[str, Any]:
        request = bytearray(32)
        request[12 : 12 + len(payload)] = payload
        struct.pack_into("<H", request, 8, declared_frame_length)
        table = bytearray(ENTRY_COUNT * ENTRY_STRIDE)
        for index, raw in entries.items():
            if not 0 <= index < ENTRY_COUNT or len(raw) != ENTRY_STRIDE:
                raise ValueError("invalid pending-table fixture entry")
            start = index * ENTRY_STRIDE
            table[start : start + ENTRY_STRIDE] = raw
        self.machine.uc.mem_write(REQUEST, bytes(request))
        self.machine.uc.mem_write(PENDING_TABLE, bytes(table))
        self.effects.clear()
        self.machine.call(HANDLER, SESSION, REQUEST, 0x55667788, 0x99AABBCC)
        final = bytes(self.machine.uc.mem_read(PENDING_TABLE, len(table)))
        return {
            "declared_frame_length": declared_frame_length,
            "payload_hex": payload.hex(),
            "effects": list(self.effects),
            "entries": {
                str(index): {
                    "before": decode_entry(raw),
                    "after": decode_entry(
                        final[index * ENTRY_STRIDE : (index + 1) * ENTRY_STRIDE]
                    ),
                }
                for index, raw in entries.items()
            },
        }


def run(image: bytes) -> dict[str, Any]:
    fixture = PacketAckFixture(image)
    key_payload = bytes([2, 1, 1, 0xA5, 0x34, 0x12])
    matching = entry_bytes(
        active=1,
        module=2,
        command=1,
        subcommand=1,
        sequence=0x1234,
        callback_thumb=CALLBACK_THUMB,
        context=0x10203040,
        tail=0xA1B2C3D4,
    )
    second_matching = entry_bytes(
        active=1,
        module=2,
        command=1,
        subcommand=1,
        sequence=0x1234,
        callback_thumb=CALLBACK_THUMB,
        context=0x55667788,
        tail=0x11223344,
    )
    nonmatching = entry_bytes(
        active=1,
        module=2,
        command=1,
        subcommand=1,
        sequence=0x9999,
        callback_thumb=CALLBACK_THUMB,
        context=0xDEADBEEF,
        tail=0x01020304,
    )
    null_callback = entry_bytes(
        active=1,
        module=2,
        command=1,
        subcommand=1,
        sequence=0x1234,
        callback_thumb=0,
        context=0xCAFEBABE,
        tail=0xAABBCCDD,
    )

    header_only = fixture.run(
        declared_frame_length=12,
        payload=key_payload,
        entries={0: matching},
    )
    no_match = fixture.run(
        declared_frame_length=18,
        payload=key_payload,
        entries={0: nonmatching},
    )
    last_slot_match = fixture.run(
        declared_frame_length=18,
        payload=key_payload,
        entries={31: matching},
    )
    duplicate_first_only = fixture.run(
        declared_frame_length=18,
        payload=key_payload,
        entries={5: matching, 7: second_matching},
    )
    null_callback_consumed = fixture.run(
        declared_frame_length=13,
        payload=key_payload,
        entries={9: null_callback},
    )

    assert header_only["effects"] == []
    assert header_only["entries"]["0"]["before"] == header_only["entries"]["0"]["after"]
    assert no_match["effects"] == [{"operation": "lock_enter"}, {"operation": "lock_exit"}]
    assert no_match["entries"]["0"]["before"] == no_match["entries"]["0"]["after"]
    assert last_slot_match["effects"] == [
        {"operation": "lock_enter"},
        {"operation": "lock_exit"},
        {"operation": "callback", "context": "0x10203040"},
    ]
    final_last = last_slot_match["entries"]["31"]["after"]
    assert final_last["active"] == 0
    assert final_last["callback_thumb"] == "0x00000000"
    assert final_last["context"] == "0x00000000"
    assert final_last["module"] == 2 and final_last["sequence"] == 0x1234
    assert final_last["tail"] == "0xa1b2c3d4"
    assert duplicate_first_only["effects"][-1] == {
        "operation": "callback",
        "context": "0x10203040",
    }
    assert duplicate_first_only["entries"]["5"]["after"]["active"] == 0
    assert duplicate_first_only["entries"]["7"]["after"]["active"] == 1
    assert null_callback_consumed["effects"] == [
        {"operation": "lock_enter"},
        {"operation": "lock_exit"},
    ]
    assert null_callback_consumed["entries"]["9"]["after"]["active"] == 0

    return {
        "fixture_groups": 5,
        "header_only_no_action": header_only,
        "full_payload_no_match": no_match,
        "last_slot_match_and_callback": last_slot_match,
        "duplicate_first_match_only": duplicate_first_only,
        "declared_one_byte_still_reads_six_and_consumes_null_callback": null_callback_consumed,
        "interpretation": {
            "first_exact_active_match_only": True,
            "callback_invoked_after_unlock": True,
            "null_callback_consumes_match": True,
            "key_and_tail_preserved": True,
            "minimum_payload_length_checked": False,
            "protocol_response_emitted": False,
        },
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "live_pending_table_access": False,
            "lock_helpers_intercepted": True,
            "callback_intercepted": True,
            "sensor_access": False,
            "storage_access": False,
            "health_store_access": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.image.read_bytes()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
