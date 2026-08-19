#!/usr/bin/env python3
"""Fail-closed build verification for the source-constructed R1 bootloader."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parents[2]
LIVE_IMAGE = REPO / "firmware/analysis/r1-live-2026-08-10/r1-bootloader-live.bin"
FLASH_START = 0x000F8000
FLASH_END = 0x000FE000
PUBLIC_KEY = bytes.fromhex(
    "9d1156448bb5b73f5e36c6dcacb54991"
    "8b82f9bd8981171033de5eb904e37d7a"
    "98a30f9fc447d76df6f195633c7f3e81"
    "301a5084815be517a4a604dfc9423455"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output(command: list[str], *, input_text: str | None = None) -> str:
    return subprocess.run(
        command,
        input=input_text,
        text=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def parse_ihex(path: Path) -> dict[int, int]:
    memory: dict[int, int] = {}
    upper = 0
    eof = False
    for line_number, raw in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        require(raw.startswith(":"), f"invalid HEX record at line {line_number}")
        record = bytes.fromhex(raw[1:])
        require(sum(record) & 0xFF == 0, f"HEX checksum failure at line {line_number}")
        length = record[0]
        address = int.from_bytes(record[1:3], "big")
        kind = record[3]
        payload = record[4 : 4 + length]
        require(len(payload) == length, f"truncated HEX record at line {line_number}")
        if kind == 0:
            base = upper + address
            for index, value in enumerate(payload):
                require(base + index not in memory, "overlapping HEX data records")
                memory[base + index] = value
        elif kind == 1:
            eof = True
        elif kind == 4:
            require(length == 2, "invalid extended-linear-address record")
            upper = int.from_bytes(payload, "big") << 16
    require(eof, "HEX file has no EOF record")
    return memory


def parse_sections(objdump_text: str) -> dict[str, dict[str, int]]:
    sections: dict[str, dict[str, int]] = {}
    pattern = re.compile(
        r"^\s*\d+\s+(\S+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+"
        r"([0-9a-fA-F]+)\s+([0-9a-fA-F]+)"
    )
    for line in objdump_text.splitlines():
        match = pattern.match(line)
        if match:
            name, size, vma, lma, offset = match.groups()
            sections[name] = {
                "size": int(size, 16),
                "vma": int(vma, 16),
                "lma": int(lma, 16),
                "offset": int(offset, 16),
            }
    return sections


def preprocessor_macros(compiler: str, profile: str) -> dict[str, str]:
    config = PROJECT / "config/r1_recovered_config.h"
    sdk_config = (
        PROJECT
        / "vendor/nrf5-sdk/examples/dfu/secure_bootloader/pca10056_s140_ble/config/sdk_config.h"
    )
    text = output(
        [
            compiler,
            "-dM",
            "-E",
            "-x",
            "c",
            f"-DR1_BUILD_PROFILE_CAPTURED={1 if profile == 'captured' else 0}",
            "-include",
            str(config),
            "-include",
            str(sdk_config),
            "-",
        ],
        input_text="",
    )
    macros: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"#define\s+(\w+)(?:\s+(.*))?$", line)
        if match:
            macros[match.group(1)] = match.group(2) or ""
    return macros


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("captured", "hardened"), required=True)
    parser.add_argument("--tool-prefix", default="arm-none-eabi-")
    parser.add_argument("--live-image", type=Path, default=LIVE_IMAGE)
    args = parser.parse_args()

    build = PROJECT / "build" / args.profile
    elf = build / "r1_bootloader.out"
    ihex = build / "r1_bootloader.hex"
    binary = build / "r1_bootloader.bin"
    link_map = build / "r1_bootloader.map"
    for path in (elf, ihex, binary, link_map):
        require(path.is_file(), f"missing build output: {path}")

    subprocess.run(
        ["python3", str(PROJECT / "tools/vendor_sdk_subset.py"), "--verify-only"],
        check=True,
    )

    live = args.live_image.read_bytes()
    require(len(live) == 0x6000, "unexpected live bootloader dump length")
    require(
        hashlib.sha256(live).hexdigest()
        == "566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b",
        "live bootloader dump hash mismatch",
    )
    live_key_offset = 0x000FD868 - FLASH_START
    require(live[live_key_offset : live_key_offset + 64] == PUBLIC_KEY, "live public key changed")

    compiler = args.tool_prefix + "gcc"
    readelf = args.tool_prefix + "readelf"
    objdump = args.tool_prefix + "objdump"
    size_tool = args.tool_prefix + "size"

    version = output([compiler, "--version"]).splitlines()[0]
    require("9.3.1" in version, f"unvalidated compiler: {version}")

    image = binary.read_bytes()
    require(len(image) == FLASH_END - FLASH_START, f"bootloader BIN is {len(image)} bytes")
    initial_sp, reset_vector = struct.unpack_from("<II", image)
    require(initial_sp == 0x20040000, f"unexpected initial SP: 0x{initial_sp:08x}")
    require(reset_vector & 1, "reset vector is not a Thumb address")
    require(FLASH_START <= (reset_vector & ~1) < FLASH_END, "reset vector is outside bootloader")
    require(image.count(PUBLIC_KEY) == 1, "public key must occur exactly once in BIN")

    sections = parse_sections(output([objdump, "-h", str(elf)]))
    expected_sections = {
        ".text": FLASH_START,
        ".data": 0x20005978,
        ".uicr_bootloader_start_address": 0x10001014,
        ".bootloader_settings_page": 0x000FF000,
        ".uicr_mbr_params_page": 0x10001018,
        ".mbr_params_page": 0x000FE000,
    }
    for name, address in expected_sections.items():
        require(name in sections, f"missing ELF section: {name}")
        require(sections[name]["vma"] == address, f"wrong {name} address")

    symbols_text = output([readelf, "-sW", str(elf)])
    symbols: dict[str, int] = {}
    function_addresses: set[int] = set()
    for line in symbols_text.splitlines():
        fields = line.split()
        if len(fields) < 8:
            continue
        try:
            address = int(fields[1], 16)
        except ValueError:
            continue
        name = fields[7]
        symbols[name] = address
        if fields[3] == "FUNC" and FLASH_START <= address < FLASH_END:
            function_addresses.add(address & ~1)
    required_symbols = {
        "Reset_Handler",
        "main",
        "nrf_bootloader_init",
        "nrf_bootloader_app_start_final",
        "nrf_bootloader_fw_activate",
        "nrf_dfu_settings_init",
        "nrf_dfu_req_handler_on_req",
        "nrf_dfu_validation_signature_check",
        "nrf_dfu_validation_boot_validate",
        "nrf_crypto_ecdsa_verify",
        "ble_dfu_transport_init",
        "pb_decode",
        "crc32_compute",
        "pk",
    }
    missing_symbols = sorted(required_symbols - symbols.keys())
    require(not missing_symbols, f"missing required symbols: {', '.join(missing_symbols)}")
    require(len(function_addresses) == 321, f"unexpected flash function count: {len(function_addresses)}")
    key_offset = symbols["pk"] - FLASH_START
    require(image[key_offset : key_offset + 64] == PUBLIC_KEY, "ELF pk symbol does not address key")

    hex_memory = parse_ihex(ihex)
    require(
        bytes(hex_memory[0x10001014 + index] for index in range(4))
        == struct.pack("<I", FLASH_START),
        "UICR bootloader-start word is wrong",
    )
    require(
        bytes(hex_memory[0x10001018 + index] for index in range(4))
        == struct.pack("<I", 0x000FE000),
        "UICR MBR-parameter word is wrong",
    )
    for address, value in hex_memory.items():
        if FLASH_START <= address < FLASH_END:
            require(image[address - FLASH_START] == value, "HEX/BIN flash payload mismatch")

    macros = preprocessor_macros(compiler, args.profile)
    required_macros = {
        "NRF_DFU_REQUIRE_SIGNED_APP_UPDATE": "1",
        "NRF_DFU_SINGLE_BANK_APP_UPDATES": "0",
        "NRF_DFU_HW_VERSION": "52",
        "NRF_DFU_BLE_REQUIRES_BONDS": "0",
        "NRF_SDH_CLOCK_LF_SRC": "0",
        "NRF_SDH_CLOCK_LF_RC_CTIV": "16",
        "NRF_SDH_CLOCK_LF_RC_TEMP_CTIV": "2",
        "NRF_SDH_CLOCK_LF_ACCURACY": "1",
        "NRF_BL_DFU_ENTER_METHOD_BUTTON": "0",
        "NRF_BL_DFU_ENTER_METHOD_PINRESET": "0",
        "NRF_BL_DFU_ENTER_METHOD_GPREGRET": "1",
        "NRF_BL_DFU_ENTER_METHOD_BUTTONLESS": "1",
    }
    for name, expected in required_macros.items():
        require(macros.get(name) == expected, f"security/config macro changed: {name}")
    require(
        ("NRF_DFU_DEBUG_VERSION" in macros) == (args.profile == "captured"),
        "profile/debug-validation macro mismatch",
    )

    object_dir = build / "r1_bootloader"
    object_count = len(list(object_dir.glob("*.o")))
    require(object_count == 74, f"unexpected linked source-object count: {object_count}")

    size_lines = output([size_tool, str(elf)]).splitlines()
    values = size_lines[-1].split()
    text_size, data_size, bss_size = map(int, values[:3])
    require(text_size + data_size <= 0x6000, "linked load image exceeds bootloader region")
    require(data_size == 184 and bss_size == 21976, "RAM layout changed unexpectedly")

    used_length = len(image.rstrip(b"\xff"))
    manifest = {
        "profile": args.profile,
        "compiler": version,
        "source_objects": object_count,
        "flash_function_addresses": len(function_addresses),
        "text_bytes": text_size,
        "data_bytes": data_size,
        "bss_bytes": bss_size,
        "bootloader_bin_bytes": len(image),
        "bootloader_used_bytes": used_length,
        "initial_stack_pointer": f"0x{initial_sp:08x}",
        "reset_vector": f"0x{reset_vector:08x}",
        "public_key_address": f"0x{symbols['pk']:08x}",
        "signed_updates_required": True,
        "artifacts": {
            path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in (elf, ihex, binary)
        },
        "link_map_bytes": link_map.stat().st_size,
    }
    manifest_path = build / "build-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"verified {args.profile} R1 bootloader: {object_count} source objects, "
        f"{len(function_addresses)} flash functions, {used_length} used bytes, signatures required"
    )


if __name__ == "__main__":
    main()
