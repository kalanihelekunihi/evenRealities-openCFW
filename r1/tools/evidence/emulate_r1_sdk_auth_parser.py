#!/usr/bin/env python3
"""Execute isolated production-Thumb SDK authorization-parser fixtures."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_SP,
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


SDK_AUTH_PARSER = 0x0008EA0C
ZERO_FILL = 0x000277AA
DEVICE_UUID = 0x0006AB88
PKEY_COPY = 0x0006AD28
STRING_LENGTH = 0x0008F674
BASE64_DECODE = 0x0005C064
DUAL_AES_DECRYPT = 0x000891A4
MESSAGE_MATCH = 0x0005D560
FIELD_COUNT = 0x000327E4
TOKENIZE = 0x00027854
LOG = 0x000823D8

STATUS = 0x20007C50
PARSER_TABLE = 0x20007D88
VALIDATOR_TABLE = 0x20007CF8
PARAMETERS = RAM_BASE + 0x64000
PKEY = RAM_BASE + 0x64100
UUID = RAM_BASE + 0x64200
DUMMY_BASE = RAM_BASE + 0x68000


def signed32(value: int) -> int:
    return struct.unpack("<i", struct.pack("<I", value & 0xFFFFFFFF))[0]


class AuthParserFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.uuid = b"a1b2c3d40123456789abcdef"
        self.plaintexts: list[bytes] = []
        self.accepted_attempt: int | None = None
        self.parser_results = [0, 0, 0, 0]
        self.validator_results = [0, 0, 0]
        self.decrypt_calls = 0
        self.parser_trace: list[dict[str, Any]] = []
        self.validator_trace: list[dict[str, Any]] = []
        self.token_cursor = 0
        self.machine.uc.mem_write(DUMMY_BASE, b"\x70\x47" * 16)
        parser_entries = [DUMMY_BASE + index * 4 for index in range(4)]
        validator_entries = [DUMMY_BASE + 0x20 + index * 4 for index in range(3)]
        self.machine.uc.mem_write(
            PARSER_TABLE,
            struct.pack("<4I", *(entry | 1 for entry in parser_entries)),
        )
        self.machine.uc.mem_write(
            VALIDATOR_TABLE,
            struct.pack("<3I", *(entry | 1 for entry in validator_entries)),
        )
        self.parser_addresses = set(parser_entries)
        self.validator_addresses = set(validator_entries)
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value & 0xFFFFFFFF)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _cstring(self, address: int) -> bytes:
        data = bytearray()
        while len(data) < 256:
            value = self.machine.uc.mem_read(address + len(data), 1)[0]
            if value == 0:
                return bytes(data)
            data.append(value)
        raise ValueError("unterminated fixture string")

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == DEVICE_UUID:
            destination = uc.reg_read(UC_ARM_REG_R0)
            uc.mem_write(destination, self.uuid + b"\x00")
            self._return(uc)
        elif address == PKEY_COPY:
            destination = uc.reg_read(UC_ARM_REG_R0)
            encoded = b"QUFB" * 16
            uc.mem_write(destination, encoded)
            self._return(uc, len(encoded))
        elif address == DUAL_AES_DECRYPT:
            output = uc.reg_read(UC_ARM_REG_R3)
            length_output = struct.unpack(
                "<I", uc.mem_read(uc.reg_read(UC_ARM_REG_SP), 4)
            )[0]
            plaintext = self.plaintexts[self.decrypt_calls]
            self.decrypt_calls += 1
            uc.mem_write(output, plaintext)
            uc.mem_write(length_output, struct.pack("<I", len(plaintext)))
            self._return(uc)
        elif address == MESSAGE_MATCH:
            attempt = self.decrypt_calls - 1
            result = 0 if attempt == self.accepted_attempt else -1
            self._return(uc, result)
        elif address == TOKENIZE:
            source = uc.reg_read(UC_ARM_REG_R0)
            if source != 0:
                self.token_cursor = source
            if self.token_cursor == 0:
                self._return(uc, 0)
                return
            token = self.token_cursor
            while True:
                value = uc.mem_read(self.token_cursor, 1)[0]
                if value == 0:
                    self.token_cursor = 0
                    break
                if value == ord(","):
                    uc.mem_write(self.token_cursor, b"\x00")
                    self.token_cursor += 1
                    break
                self.token_cursor += 1
            self._return(uc, token)
        elif address in self.parser_addresses:
            index = (address - DUMMY_BASE) // 4
            parameters = uc.reg_read(UC_ARM_REG_R1)
            self.parser_trace.append({
                "index": index,
                "token": self._cstring(uc.reg_read(UC_ARM_REG_R0)).decode(),
                "uuid": self._cstring(struct.unpack(
                    "<I", uc.mem_read(parameters + 4, 4)
                )[0]).decode(),
                "uuid_length": uc.mem_read(parameters + 8, 1)[0],
            })
            self._return(uc, self.parser_results[index])
        elif address in self.validator_addresses:
            index = (address - DUMMY_BASE - 0x20) // 4
            self.validator_trace.append({
                "index": index,
                "token": self._cstring(uc.reg_read(UC_ARM_REG_R0)).decode(),
            })
            self._return(uc, self.validator_results[index])
        elif address == LOG:
            self._return(uc)

    def execute(
        self,
        plaintexts: list[bytes],
        accepted_attempt: int | None,
        parser_results: list[int] | None = None,
        validator_results: list[int] | None = None,
        uuid: bytes = b"a1b2c3d40123456789abcdef",
    ) -> dict[str, Any]:
        self.uuid = uuid
        self.plaintexts = [value + b"\x00" for value in plaintexts]
        self.accepted_attempt = accepted_attempt
        self.parser_results = parser_results or [0, 0, 0, 0]
        self.validator_results = validator_results or [0, 0, 0]
        self.decrypt_calls = 0
        self.parser_trace.clear()
        self.validator_trace.clear()
        self.token_cursor = 0
        self.machine.uc.mem_write(STATUS, b"\xA5" * 20)
        self.machine.uc.mem_write(PKEY, b"K" * 64 + b"\x00")
        self.machine.uc.mem_write(UUID, uuid + b"\x00")
        self.machine.uc.mem_write(
            PARAMETERS,
            struct.pack("<III", PKEY, UUID, len(uuid)) +
            struct.pack("<I", 0x12345678),
        )
        result = signed32(self.machine.call(SDK_AUTH_PARSER, PARAMETERS))
        status = bytes(self.machine.uc.mem_read(STATUS, 20))
        return {
            "return": result,
            "decrypt_calls": self.decrypt_calls,
            "status_error": struct.unpack_from("<h", status, 4)[0],
            "parser_trace": list(self.parser_trace),
            "validator_trace": list(self.validator_trace),
        }


def run(image: bytes) -> dict[str, Any]:
    fixture = AuthParserFixture(image)
    invalid_uuid = fixture.execute([], None, uuid=b"short")
    first_key = fixture.execute(
        [b"one,two,three,four"], 0,
        parser_results=[10, 11, 12, 13],
        validator_results=[1, 2, 1],
    )
    second_key = fixture.execute(
        [b"bad,data,for,key", b"a,b,c,d"], 1,
    )
    rejected = fixture.execute(
        [b"bad,data,for,key", b"wrong,field,count"], None,
    )
    parser_failure = fixture.execute(
        [b"a,b,c,d"], 0,
        parser_results=[0, 0, -7, 0],
    )

    assert invalid_uuid == {
        "return": -1005,
        "decrypt_calls": 0,
        "status_error": -1,
        "parser_trace": [],
        "validator_trace": [],
    }
    assert first_key["return"] == 11 and first_key["decrypt_calls"] == 1
    assert [entry["token"] for entry in first_key["parser_trace"]] == [
        "one", "two", "three", "four",
    ]
    assert all(
        entry["uuid"] == "0123456789ABCDEF" and
        entry["uuid_length"] == 16
        for entry in first_key["parser_trace"]
    )
    assert [entry["index"] for entry in first_key["validator_trace"]] == [0, 1, 2]
    assert second_key["return"] == 0 and second_key["decrypt_calls"] == 2
    assert rejected["return"] == -1002 and rejected["status_error"] == -1002
    assert parser_failure["return"] == -7
    assert len(parser_failure["parser_trace"]) == 3
    return {
        "fixture_groups": 5,
        "invalid_uuid": invalid_uuid,
        "first_key": first_key,
        "second_key": second_key,
        "rejected": rejected,
        "parser_failure": parser_failure,
        "safety": {
            "stock_authorization_key_material_emitted": False,
            "physical_device_access": False,
            "ble_access": False,
            "flash_writes": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.image.read_bytes()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
