#!/usr/bin/env python3
"""Reproduce the bounded G2 littlefs block-device port audit.

This tool is intentionally read-only.  It verifies the authenticated input
images, extracts both lfs_config objects, pins the four callback bodies and
their direct call targets, and records the immediately underlying
MX25U25643G driver seams.  It never opens a device or performs a flash
operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from capstone import (
    CS_ARCH_ARM,
    CS_GRP_JUMP,
    CS_MODE_MCLASS,
    CS_MODE_THUMB,
    Cs,
)
from capstone.arm import ARM_INS_BL, ARM_INS_BLX, ARM_OP_IMM


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    sha256: str


@dataclass(frozen=True)
class Image:
    name: str
    path: Path
    file_sha256: str
    load_address: int
    file_header_size: int
    config_address: int
    config_sha256: str
    callbacks: dict[str, Span]
    driver_functions: dict[str, Span]
    expected_calls: dict[str, list[int]]
    diagnostic_strings: dict[str, str]


IMAGES = {
    "main": Image(
        name="main",
        path=(
            ROOT
            / "blobs"
            / "official"
            / "g2-2.2.6.10"
            / "ota_s200_firmware_ota.bin"
        ),
        file_sha256=(
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863"
        ),
        load_address=0x00438000,
        file_header_size=32,
        config_address=0x006E83A4,
        config_sha256=(
            "f38bd899e180d29ee60609a2452d25c2d2"
            "d6c6fef4eb455064e23a6ca7c6e813"
        ),
        callbacks={
            "read": Span(
                0x004763B8,
                0x004763F0,
                "7e8b4188becb1bdb7d8a777ef724b61ee9bf9fc0e48459e35bdca22e47f11b58",
            ),
            "prog": Span(
                0x004763F0,
                0x00476428,
                "dbabdf2f5643d8ea04715e492ffccc397fad2381af5a5d1ef4d17f89f46fe1d6",
            ),
            "erase": Span(
                0x00476428,
                0x00476452,
                "7f21bcf5257604c375938af66981e04db70054eb897b387e4af5354eb669ad2c",
            ),
            "sync": Span(
                0x004764DC,
                0x004764E0,
                "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4",
            ),
        },
        driver_functions={
            "erase": Span(
                0x0047075C,
                0x00470856,
                "b1593c790c17f28c6dc4bee59aec9ca05f4670b79dd3a4337da1024ca3240026",
            ),
            "prog": Span(
                0x004708A8,
                0x004709B0,
                "d8222d506ae8a3d206e822fe016823e36f8d90a03a71e7346a1eec1d5793c5d1",
            ),
            "read": Span(
                0x00471020,
                0x004710A2,
                "04e968ef80cb6bc9f4a5516d9fbf22204aad1768fc0de9d9c71cb03bf5ff5839",
            ),
            "write_transfer": Span(
                0x0047021C,
                0x004702CA,
                "59c5a67d44e4f1a4e88310fd61475bd34801e1d2a3513d3157266b2808c59225",
            ),
            "wait_idle": Span(
                0x004703BA,
                0x004703C6,
                "bceeab3a47379a62e78b6b07417c52a86da437468ee68ddb43e56468065e7329",
            ),
            "write_enable": Span(
                0x00470670,
                0x004706D0,
                "fbe943e80698b035df2d8e1004670d278bdc8a1425a576949af31123d685b731",
            ),
            "write_disable": Span(
                0x004706E0,
                0x00470740,
                "bfafa8dbffd706a4ad7beb719783bec6aadc453a5da753b8ec9061992091ffe0",
            ),
            "set_quad_mode": Span(
                0x00470E90,
                0x00470F58,
                "bc0038c5cc8a7fa2934176e6a324614fc266ab81847b42914b61fc1a063965ab",
            ),
            "set_serial_mode": Span(
                0x00470F68,
                0x0047100A,
                "eb87e9d695862f147aa533bfc7fa104081d3c20e49650d637cffb8a963c28491",
            ),
            "transaction_lock": Span(
                0x0046F65E,
                0x0046F674,
                "b415a20ac2017fe9c1e01927adb4cd950039e5b239244dcc117c0eca69b98dee",
            ),
            "transaction_unlock": Span(
                0x0046F674,
                0x0046F68A,
                "231e152d1fb28540e77498af6f9387f29908076cd73bc3822bcf45e1db4b60c8",
            ),
            "ambiq_hal_mspi_blocking_transfer": Span(
                0x004C2098,
                0x004C2204,
                "12dd31986d405542640cf5b2de6f46e691ed91628c645a4806b3134883b401c4",
            ),
        },
        expected_calls={
            "read": [0x00471020, 0x004733EE],
            "prog": [0x004708A8, 0x004733EE],
            "erase": [0x0047075C, 0x004733EE],
            "sync": [],
        },
        diagnostic_strings={
            "read": (
                "lfs READ fail: block=%u, off=%u, size=%u, "
                "addr=0x%08X, st=%d\n"
            ),
            "prog": (
                "lfs PROG fail: block=%u, off=%u, size=%u, "
                "addr=0x%08X, st=%d\n"
            ),
            "erase": "lfs ERASE fail: block=%u, addr=0x%08X, st=%d\n",
        },
    ),
    "boot": Image(
        name="boot",
        path=(
            ROOT
            / "blobs"
            / "official"
            / "g2-2.2.6.10"
            / "ota_s200_bootloader.bin"
        ),
        file_sha256=(
            "f89a4c4657537cec6bfc572bdb8318866"
            "309b90a5d180c4307680d39824167b5"
        ),
        load_address=0x00410000,
        file_header_size=0,
        config_address=0x00431070,
        config_sha256=(
            "724c351d2136e3c2f10b59ad84d547da"
            "4632739ea1f20eb839e9af2cfbd5b6e8"
        ),
        callbacks={
            "read": Span(
                0x004212D8,
                0x00421310,
                "26e2b4b9fe7f3389d15261fe01621eb3b37bfc4b9923ebfac70609216ac92a90",
            ),
            "prog": Span(
                0x00421310,
                0x00421348,
                "6d46e88d2df85850b8ec35b4f55e5e0522884210c8bf5a3419e328599ffebf60",
            ),
            "erase": Span(
                0x00421348,
                0x00421372,
                "df1788d1db60223b7af5050ab14307a3bf27f30fc6d61917adee77f679b3b872",
            ),
            "sync": Span(
                0x004213D4,
                0x004213D8,
                "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4",
            ),
        },
        driver_functions={
            "erase": Span(
                0x00420A08,
                0x00420ADA,
                "0a0a96db9e3a1c6fcbdfcebd96db6f16e22c780940889677a16ebc880d0dd899",
            ),
            "prog": Span(
                0x00420B0C,
                0x00420C14,
                "dcaf2a13af5fb811c228b4845363682411abf1acab703507368f6d1e4463b15e",
            ),
            "read": Span(
                0x00420F70,
                0x00420FF2,
                "ce201805b566c9d5c4a70d675e0bdb145133d2771bc9098e4255245a8d6067e3",
            ),
            "write_transfer": Span(
                0x0042069E,
                0x0042074E,
                "18bdd1fb9df8bf0b73bb5ed09e8f9ed218ba263f8f11caf97c98fc17af2aa20e",
            ),
            "busy_status": Span(
                0x0042074E,
                0x004207A2,
                "33e47f7e0bf37502f2f2dd20196d15b67a1f3ef336cd48538ac99f6ceed0e6e5",
            ),
            "wait_ready": Span(
                0x004207A2,
                0x004207F4,
                "b5d741edee4dcb847a20256e315ae4304b07a43e02ef189da8c6a36ff0f9e809",
            ),
            "wait_idle": Span(
                0x004207F4,
                0x00420800,
                "bceeab3a47379a62e78b6b07417c52a86da437468ee68ddb43e56468065e7329",
            ),
            "write_enable": Span(
                0x00420984,
                0x004209BE,
                "e675df17f3a419b27b088cd7cd0c5785537fe730f597f894ba648e3a76afa3e5",
            ),
            "write_disable": Span(
                0x004209C4,
                0x004209FC,
                "f29c57daa25ee3108fe92b65e0076a21ac49af5ded9c735c33624e26e4400cd2",
            ),
            "set_quad_mode": Span(
                0x00420E8C,
                0x00420F0C,
                "d3eeee3b649bcab6d485d604bb94fe739a753064b80b6918a4d5a9db616b86ef",
            ),
            "set_serial_mode": Span(
                0x00420F10,
                0x00420F6A,
                "b73005fad7b0cae8e2f2273bae21ab2877963d2d14534b5afc2918c515c26a13",
            ),
            "transaction_lock": Span(
                0x0041FF08,
                0x0041FF1E,
                "02963ef679faf897f9108a5e1526bd79eccabb28b11192d6325dfb4165ca0dc5",
            ),
            "transaction_unlock": Span(
                0x0041FF1E,
                0x0041FF34,
                "ecb3a585f0f910e6428aa9a722ff0f2a621ca1d195b8fd8b4a9d4f2820f0dddd",
            ),
            "ambiq_hal_mspi_blocking_transfer": Span(
                0x004262E0,
                0x0042644C,
                "91c3b42f59f32e97e91133a7c66234488e6b0076c4dd4362a0ed7dd9d56492e3",
            ),
        },
        expected_calls={
            "read": [0x00420F70, 0x00415FAE],
            "prog": [0x00420B0C, 0x00415FAE],
            "erase": [0x00420A08, 0x00415FAE],
            "sync": [],
        },
        diagnostic_strings={
            "read": (
                "lfs READ fail: block=%u, off=%u, size=%u, "
                "addr=0x%08X, st=%d\n"
            ),
            "prog": (
                "lfs PROG fail: block=%u, off=%u, size=%u, "
                "addr=0x%08X, st=%d\n"
            ),
            "erase": "lfs ERASE fail: block=%u, addr=0x%08X, st=%d\n",
        },
    ),
}

CONFIG_FIELDS = (
    "context",
    "read",
    "prog",
    "erase",
    "sync",
    "read_size",
    "prog_size",
    "block_size",
    "block_count",
    "block_cycles",
    "cache_size",
    "lookahead_size",
    "compact_thresh",
    "read_buffer",
    "prog_buffer",
    "lookahead_buffer",
    "name_max",
    "file_max",
    "attr_max",
    "metadata_max",
    "inline_max",
)

EXPECTED_CONFIG = {
    "main": (
        0,
        0x004763B9,
        0x004763F1,
        0x00476429,
        0x004764DD,
        16,
        256,
        4096,
        3008,
        500,
        4096,
        256,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ),
    "boot": (
        0,
        0x004212D9,
        0x00421311,
        0x00421349,
        0x004213D5,
        16,
        256,
        4096,
        3008,
        500,
        4096,
        256,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ),
}

PORT_SOURCE_PATH = (
    r"D:\01_workspace\s200_ap510b_iar_git"
    r"\third_party\littlefs\port\littlefs_mx25u25643g_porting.c"
)
DRIVER_SOURCE_PATH = (
    r"D:\01_workspace\s200_ap510b_iar_git"
    r"\driver\flash\drv_mx25u25643g.c"
)


class AuditError(RuntimeError):
    pass


class LoadedImage:
    def __init__(self, definition: Image) -> None:
        self.definition = definition
        self.data = definition.path.read_bytes()

    def read(self, address: int, size: int) -> bytes:
        offset = (
            self.definition.file_header_size
            + address
            - self.definition.load_address
        )
        if offset < 0 or offset + size > len(self.data):
            raise AuditError(
                f"{self.definition.name}: address range "
                f"0x{address:08x}..0x{address + size:08x} is outside image"
            )
        return self.data[offset : offset + size]

    def contains_ascii(self, text: str) -> bool:
        return text.encode("ascii") + b"\0" in self.data


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def direct_calls(code: bytes, start: int) -> list[int]:
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    decoder.detail = True
    calls: list[int] = []
    for instruction in decoder.disasm(code, start):
        if instruction.id not in (ARM_INS_BL, ARM_INS_BLX):
            continue
        if not instruction.operands or instruction.operands[0].type != ARM_OP_IMM:
            raise AuditError(f"indirect call at 0x{instruction.address:08x}")
        calls.append(instruction.operands[0].imm & ~1)
    return calls


def normalized_instructions(code: bytes, start: int) -> list[str]:
    """Normalize relocatable targets without erasing operation semantics."""

    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    decoder.detail = True
    normalized: list[str] = []
    for instruction in decoder.disasm(code, start):
        text = f"{instruction.mnemonic} {instruction.op_str}"
        if instruction.id in (ARM_INS_BL, ARM_INS_BLX):
            text = f"{instruction.mnemonic} <call>"
        elif (
            instruction.group(CS_GRP_JUMP)
            and instruction.operands
            and instruction.operands[-1].type == ARM_OP_IMM
        ):
            relative = instruction.operands[-1].imm - instruction.address
            if "," in instruction.op_str:
                prefix = instruction.op_str.rsplit(",", 1)[0]
                text = (
                    f"{instruction.mnemonic} {prefix}, "
                    f"<relative {relative:+#x}>"
                )
            else:
                text = f"{instruction.mnemonic} <relative {relative:+#x}>"
        elif (
            instruction.mnemonic.startswith("ldr")
            and "[pc," in instruction.op_str
        ):
            destination = instruction.op_str.split(",", 1)[0]
            text = f"{instruction.mnemonic} {destination}, <literal>"
        normalized.append(text)
    return normalized


def audit_image(definition: Image) -> tuple[LoadedImage, dict[str, Any]]:
    image = LoadedImage(definition)
    actual_file_sha = sha256(image.data)
    if actual_file_sha != definition.file_sha256:
        raise AuditError(
            f"{definition.name}: image hash {actual_file_sha} != "
            f"{definition.file_sha256}"
        )

    config_bytes = image.read(definition.config_address, 84)
    actual_config_sha = sha256(config_bytes)
    if actual_config_sha != definition.config_sha256:
        raise AuditError(
            f"{definition.name}: config hash {actual_config_sha} != "
            f"{definition.config_sha256}"
        )
    config_values = struct.unpack("<21I", config_bytes)
    if config_values != EXPECTED_CONFIG[definition.name]:
        raise AuditError(f"{definition.name}: unexpected lfs_config values")

    if not image.contains_ascii(PORT_SOURCE_PATH):
        raise AuditError(f"{definition.name}: littlefs port path not found")
    if not image.contains_ascii(DRIVER_SOURCE_PATH):
        raise AuditError(f"{definition.name}: flash driver path not found")
    for callback_name, diagnostic in definition.diagnostic_strings.items():
        if not image.contains_ascii(diagnostic):
            raise AuditError(
                f"{definition.name}: {callback_name} diagnostic not found"
            )

    callback_result: dict[str, Any] = {}
    for callback_name, span in definition.callbacks.items():
        code = image.read(span.start, span.end - span.start)
        actual_sha = sha256(code)
        if actual_sha != span.sha256:
            raise AuditError(
                f"{definition.name}: {callback_name} hash {actual_sha} != "
                f"{span.sha256}"
            )
        calls = direct_calls(code, span.start)
        if calls != definition.expected_calls[callback_name]:
            raise AuditError(
                f"{definition.name}: {callback_name} calls "
                f"{[hex(value) for value in calls]} != "
                f"{[hex(value) for value in definition.expected_calls[callback_name]]}"
            )
        callback_result[callback_name] = {
            "thumb_entry": f"0x{span.start + 1:08x}",
            "range": [f"0x{span.start:08x}", f"0x{span.end:08x}"],
            "size": len(code),
            "sha256": actual_sha,
            "direct_calls": [f"0x{value:08x}" for value in calls],
            "normalized_instructions": normalized_instructions(code, span.start),
        }

    driver_result: dict[str, Any] = {}
    for function_name, span in definition.driver_functions.items():
        code = image.read(span.start, span.end - span.start)
        actual_sha = sha256(code)
        if actual_sha != span.sha256:
            raise AuditError(
                f"{definition.name}: driver {function_name} hash "
                f"{actual_sha} != {span.sha256}"
            )
        driver_result[function_name] = {
            "thumb_entry": f"0x{span.start + 1:08x}",
            "range": [f"0x{span.start:08x}", f"0x{span.end:08x}"],
            "size": len(code),
            "sha256": actual_sha,
            "direct_calls": [
                f"0x{value:08x}" for value in direct_calls(code, span.start)
            ],
        }

    config = {
        field: f"0x{value:08x}"
        if field in {
            "context",
            "read",
            "prog",
            "erase",
            "sync",
            "read_buffer",
            "prog_buffer",
            "lookahead_buffer",
        }
        else value
        for field, value in zip(CONFIG_FIELDS, config_values)
    }
    return image, {
        "path": str(definition.path.relative_to(ROOT)),
        "file_sha256": actual_file_sha,
        "load_address": f"0x{definition.load_address:08x}",
        "file_header_size": definition.file_header_size,
        "config_address": f"0x{definition.config_address:08x}",
        "config_sha256": actual_config_sha,
        "config": config,
        "callbacks": callback_result,
        "driver_functions": driver_result,
        "source_paths": {
            "littlefs_port": PORT_SOURCE_PATH,
            "flash_driver": DRIVER_SOURCE_PATH,
        },
    }


def run_audit() -> dict[str, Any]:
    loaded: dict[str, LoadedImage] = {}
    result_images: dict[str, Any] = {}
    for image_name, definition in IMAGES.items():
        loaded[image_name], result_images[image_name] = audit_image(definition)

    normalized_matches: dict[str, bool] = {}
    for callback_name in ("read", "prog", "erase", "sync"):
        main_span = IMAGES["main"].callbacks[callback_name]
        boot_span = IMAGES["boot"].callbacks[callback_name]
        main_norm = normalized_instructions(
            loaded["main"].read(
                main_span.start, main_span.end - main_span.start
            ),
            main_span.start,
        )
        boot_norm = normalized_instructions(
            loaded["boot"].read(
                boot_span.start, boot_span.end - boot_span.start
            ),
            boot_span.start,
        )
        normalized_matches[callback_name] = main_norm == boot_norm
        if not normalized_matches[callback_name]:
            raise AuditError(
                f"main/boot {callback_name} normalized bodies differ"
            )

    main_hal = IMAGES["main"].driver_functions[
        "ambiq_hal_mspi_blocking_transfer"
    ]
    boot_hal = IMAGES["boot"].driver_functions[
        "ambiq_hal_mspi_blocking_transfer"
    ]
    hal_semantics_match = normalized_instructions(
        loaded["main"].read(main_hal.start, main_hal.end - main_hal.start),
        main_hal.start,
    ) == normalized_instructions(
        loaded["boot"].read(boot_hal.start, boot_hal.end - boot_hal.start),
        boot_hal.start,
    )
    if not hal_semantics_match:
        raise AuditError(
            "main/boot Ambiq HAL blocking-transfer bodies differ"
        )

    block_size = EXPECTED_CONFIG["main"][7]
    block_count = EXPECTED_CONFIG["main"][8]
    partition_start = 0x01400000
    partition_size = block_size * block_count
    flash_size = 0x02000000
    partition_end = partition_start + partition_size

    return {
        "status": "ok",
        "read_only": True,
        "images": result_images,
        "main_boot_callback_semantics_match": normalized_matches,
        "main_boot_ambiq_hal_blocking_transfer_semantics_match": (
            hal_semantics_match
        ),
        "partition": {
            "device": "Macronix MX25U25643G",
            "external_flash_size": flash_size,
            "start": partition_start,
            "size": partition_size,
            "end_exclusive": partition_end,
            "bytes_after_partition": flash_size - partition_end,
            "address_formula": (
                "0x01400000 + block * 0x1000 + offset"
            ),
        },
        "observed_commands": {
            "read": "0x6c QREAD4B",
            "program": "0x02 page program, split at 256-byte boundaries",
            "erase": "0x20 4 KiB sector erase",
            "write_enable": "0x06",
            "write_disable": "0x04",
            "read_timeout_us": 1_000_000,
        },
        "callback_result_mapping": {
            "driver_zero": 0,
            "driver_nonzero": -5,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit complete machine-readable evidence",
    )
    args = parser.parse_args()

    try:
        result = run_audit()
    except (AuditError, FileNotFoundError) as error:
        raise SystemExit(f"littlefs port audit: FAIL: {error}") from error

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        partition = result["partition"]
        print("littlefs port audit: OK")
        print(
            "main/boot callbacks: normalized read/prog/erase/sync bodies match"
        )
        print(
            "partition: "
            f"0x{partition['start']:08x}.."
            f"0x{partition['end_exclusive']:08x} "
            f"({partition['size']} bytes)"
        )
        print("analysis mode: read-only; no device or flash operation performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
