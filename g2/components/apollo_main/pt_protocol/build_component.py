#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build and install the complete source-owned G2 PT protocol in place."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path
from typing import Any


COMPONENT_ROOT = Path(__file__).resolve().parent
OPENCFW_ROOT = COMPONENT_ROOT.parents[2]
SOURCE_ROOT = COMPONENT_ROOT.parent / "core_overlay"
RUN_BASE = 0x00437FE0
INTERVAL_START = 0x0056F178
INTERVAL_END = 0x00577C3C
INTERVAL_SHA256 = "a543c819bc9fc21577cdc71d8cab14aeb61cce8f684509b7517e7ed853025b59"
SOURCES = tuple(SOURCE_ROOT / name for name in (
    "pt_protocol_procsr.c", "pt_protocol_handlers_basic.c",
    "pt_protocol_handlers_config.c", "pt_protocol_handlers_data.c",
    "pt_protocol_handlers_display.c", "pt_protocol_handlers_sensors.c",
    "pt_protocol_handlers_services.c", "pt_protocol_handlers_audio.c",
    "pt_protocol_handlers_transfer.c", "pt_protocol_service.c",
    "pt_protocol_platform_adapter.c", "pt_protocol_production_entry.c",
    "pt_protocol_board_backend.c", "pt_protocol_board_leaf_candidates.c",
))
LEGACY_INGRESS = (
    (0x00538716, 0x0056F4A0, "stock_direct_call"),
    (0x0053A218, 0x0056F4A0, "source_uart_relocation"),
    (0x0053A356, 0x0056F92C, "source_uart_relocation"),
)
SOURCE_UART_ROUTE_REQUIREMENTS = (
    ("open_cfw_retained_box_uart_product_test", "R_ARM_THM_CALL",
     0x0056F4A0, 88, 10),
    ("open_cfw_retained_box_uart_execute", "R_ARM_THM_CALL", 0x0056F92C,
     148, 10),
)
SOURCE_UART_LEAF_EXPECTED = {
    "size": 158,
    "sha256": "8ee49d1869b320dca68aadc10d91f27cfa12205c48d038b969cf46746c159d4d",
    "unrelocated_sha256": (
        "0ad53c357754dc504d7cb6dcfd9a96fdee5cf5b63000d29c76fa6a35785597ad"
    ),
    "alignment": 4,
    "offset": 332508,
}
SOURCE_PROVIDER_ROUTES = (
    ("post_input_message_id3", 28, 0x005130A6,
     "open_cfw_pt_board_post_input_message_id3"),
    ("buzzer_start", 60, 0x00502C88, "open_cfw_pt_board_buzzer_start"),
    ("buzzer_stop", 64, 0x00502D4C, "open_cfw_pt_board_buzzer_stop"),
    ("production_reset", 84, 0x0058F950,
     "open_cfw_pt_board_production_reset"),
    ("charger_test_disable", 88, 0x005128F8,
     "open_cfw_pt_board_charger_test_disable"),
    ("charger_test_enable", 92, 0x0051299C,
     "open_cfw_pt_board_charger_test_enable"),
    ("codec_platform_identifier", 176, 0x0052DEE6,
     "open_cfw_pt_board_codec_platform_identifier"),
    ("system_reset", 320, 0x0044B0AE, "open_cfw_pt_board_system_reset"),
    ("display_postprocess", 328, 0x00542D4C,
     "open_cfw_pt_board_display_postprocess"),
    ("font_crc_check_0", 332, 0x0058F486,
     "open_cfw_pt_board_font_crc_check_0"),
    ("font_crc_check_1", 336, 0x0058F490,
     "open_cfw_pt_board_font_crc_check_1"),
    ("hardware_identifier_0", 344, 0x00512C84,
     "open_cfw_pt_board_hardware_identifier_0"),
    ("hardware_identifier_1", 348, 0x004700B4,
     "open_cfw_pt_board_hardware_identifier_1"),
    ("hardware_identifier_2", 352, 0x00512B20,
     "open_cfw_pt_board_hardware_identifier_2"),
    ("display_hardware_identifier", 364, 0x004CA070,
     "open_cfw_pt_board_display_hardware_identifier"),
    ("ambient_identifier_initialize", 368, 0x0058F936,
     "open_cfw_pt_board_ambient_identifier_initialize"),
    ("ambient_identifier_step_1", 376, 0x0058F8CC,
     "open_cfw_pt_board_ambient_identifier_step_1"),
    ("ambient_identifier_step_2", 380, 0x0058F8D8,
     "open_cfw_pt_board_ambient_identifier_step_2"),
    ("ambient_identifier_low", 384, 0x0058F922,
     "open_cfw_pt_board_ambient_identifier_low"),
    ("ambient_identifier_high", 388, 0x0058F92C,
     "open_cfw_pt_board_ambient_identifier_high"),
    ("uart_sync_write", 392, 0x00541790,
     "open_cfw_pt_board_uart_sync_write"),
    ("lens_sync_send", 412, 0x004651E0,
     "open_cfw_pt_board_lens_sync_send"),
    ("screen_show", 424, 0x004441EC, "open_cfw_pt_board_screen_show"),
    ("screen_hide", 428, 0x004443CC, "open_cfw_pt_board_screen_hide"),
    ("display_state", 432, 0x0044347A, "open_cfw_pt_board_display_state"),
    ("display_brightness", 436, 0x004CA1EE,
     "open_cfw_pt_board_display_brightness"),
    ("display_stage_1", 440, 0x0046C984,
     "open_cfw_pt_board_display_stage_1"),
    ("display_stage_2", 444, 0x0046C9DC,
     "open_cfw_pt_board_display_stage_2"),
    ("display_stage_3", 448, 0x0046C9AA,
     "open_cfw_pt_board_display_stage_3"),
    ("display_offset", 452, 0x004CA24A,
     "open_cfw_pt_board_display_offset"),
    ("audio_status_get", 456, 0x0050938E,
     "open_cfw_pt_board_audio_status_get"),
    ("audio_path_format", 464, 0x0057B352,
     "open_cfw_pt_board_audio_path_format"),
    ("audio_channel_0_start", 468, 0x0058F69A,
     "open_cfw_pt_board_audio_channel_0_start"),
    ("audio_channel_0_stop", 472, 0x0058F7B0,
     "open_cfw_pt_board_audio_channel_0_stop"),
    ("audio_channel_1_start", 476, 0x0058F74A,
     "open_cfw_pt_board_audio_channel_1_start"),
    ("audio_channel_1_stop", 480, 0x0058F806,
     "open_cfw_pt_board_audio_channel_1_stop"),
    ("audio_codec_route", 484, 0x0053A5BE,
     "open_cfw_pt_board_audio_codec_route"),
    ("time_configure", 520, 0x0044A1FE,
     "open_cfw_pt_board_time_configure"),
    ("time_capture", 524, 0x0044A19A, "open_cfw_pt_board_time_capture"),
    ("ambient_read", 532, 0x0058F8E4, "open_cfw_pt_board_ambient_read"),
)


class BuildError(RuntimeError):
    pass


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _tool(environment: str, *candidates: str) -> str:
    configured = os.environ.get(environment)
    if configured:
        resolved = shutil.which(configured) if "/" not in configured else configured
        if resolved and Path(resolved).is_file():
            return resolved
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    for candidate in candidates:
        homebrew = Path("/opt/homebrew/opt/llvm/bin") / candidate
        if homebrew.is_file():
            return str(homebrew)
    raise BuildError(f"required tool unavailable: {environment}")


def _elf_sections(path: Path) -> dict[str, dict[str, int]]:
    data = path.read_bytes()
    if len(data) < 52 or data[:6] != b"\x7fELF\x01\x01":
        raise BuildError("PT final link is not ELF32 little-endian")
    section_offset = struct.unpack_from("<I", data, 0x20)[0]
    entry_size, count, names_index = struct.unpack_from("<HHH", data, 0x2E)
    if entry_size != 40 or count < 1 or names_index >= count:
        raise BuildError("PT ELF section table changed")
    raw = [struct.unpack_from("<IIIIIIIIII", data,
            section_offset + index * entry_size) for index in range(count)]
    names_record = raw[names_index]
    names = data[names_record[4]:names_record[4] + names_record[5]]
    result: dict[str, dict[str, int]] = {}
    for record in raw:
        end = names.find(b"\0", record[0])
        if record[0] >= len(names) or end < 0:
            raise BuildError("PT ELF section name table changed")
        name = names[record[0]:end].decode("ascii")
        result[name] = {
            "type": record[1], "flags": record[2], "address": record[3],
            "offset": record[4], "size": record[5], "alignment": record[8],
        }
    return result


def _decode_thumb_bl(instruction: int, encoded: bytes) -> int:
    first, second = struct.unpack("<HH", encoded)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        raise BuildError("generated PT callsite is not Thumb BL")
    sign = (first >> 10) & 1
    j1, j2 = (second >> 13) & 1, (second >> 11) & 1
    immediate = ((sign << 24) | ((~(j1 ^ sign) & 1) << 23) |
                 ((~(j2 ^ sign) & 1) << 22) |
                 ((first & 0x3FF) << 12) | ((second & 0x7FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return instruction + 4 + immediate


def _build_input_snapshot() -> tuple[tuple[str, int, str], ...]:
    """Authenticate every source input before compilation and publication."""
    paths = (Path(__file__).resolve(), *SOURCES,
             *sorted(SOURCE_ROOT.glob("pt_protocol*.h")))
    records = []
    for path in paths:
        data = path.read_bytes()
        records.append((str(path.relative_to(OPENCFW_ROOT)), len(data),
                        sha256(data)))
    return tuple(sorted(records))


def _authenticated_component(
    path: Path, expected: dict[str, Any] | None, *, role: str
) -> bytes:
    if not isinstance(expected, dict):
        raise BuildError(f"{role} requires an exact size/SHA-256 contract")
    try:
        expected_size = int(expected["size"])
        expected_sha256 = expected["sha256"]
    except (KeyError, TypeError, ValueError) as error:
        raise BuildError(
            f"{role} requires an exact size/SHA-256 contract"
        ) from error
    if (not isinstance(expected_sha256, str) or
            len(expected_sha256) != 64 or
            any(value not in "0123456789abcdef" for value in expected_sha256)):
        raise BuildError(f"{role} SHA-256 contract is invalid")
    data = path.read_bytes()
    if len(data) != expected_size or sha256(data) != expected_sha256:
        raise BuildError(f"{role} changed")
    if (len(data) < 8 or
            struct.unpack_from("<I", data, 4)[0] !=
            zlib.crc32(data[8:]) & 0xFFFFFFFF):
        raise BuildError(f"{role} nested CRC-32 is invalid")
    return data


def _validate_source_uart_route_receipt(
    receipt: dict[str, Any] | None, *, profile: str, routed: bool
) -> dict[str, Any] | None:
    if receipt is None:
        if routed:
            raise BuildError("PT source-UART route receipt missing")
        return None
    expected_mode = (
        "source_overlay_relocation" if routed else "authenticated_donor_direct"
    )
    if (receipt.get("mode") != expected_mode or
            receipt.get("profile") != profile or
            receipt.get("function") != "open_cfw_box_uart_handle" or
            receipt.get("strict_relocation_contract") is not True or
            receipt.get("profile_route_active") is not routed):
        raise BuildError("PT source-UART route receipt changed")
    stage_overlay = receipt.get("stage_overlay")
    if not isinstance(stage_overlay, dict):
        raise BuildError("PT source-UART stage identity missing")
    try:
        overlay_size = int(stage_overlay["size"])
        overlay_sha256 = stage_overlay["sha256"]
    except (KeyError, TypeError, ValueError) as error:
        raise BuildError("PT source-UART stage identity changed") from error
    if (overlay_size <= 0 or not isinstance(overlay_sha256, str) or
            len(overlay_sha256) != 64 or
            any(value not in "0123456789abcdef" for value in overlay_sha256)):
        raise BuildError("PT source-UART stage identity changed")
    relocations = receipt.get("relocations")
    if not isinstance(relocations, list):
        raise BuildError("PT source-UART relocation receipt missing")
    observed = tuple(sorted(
        (item.get("symbol"), item.get("type"),
         int(item.get("target_address", -1)), int(item.get("offset", -1)),
         int(item.get("type_id", -1)))
        for item in relocations if isinstance(item, dict)
    ))
    if observed != tuple(sorted(SOURCE_UART_ROUTE_REQUIREMENTS)):
        raise BuildError("PT source-UART relocation receipt changed")
    if receipt.get("leaf") != SOURCE_UART_LEAF_EXPECTED:
        raise BuildError("PT source-UART leaf identity changed")
    return receipt


def build(*, base_path: Path, output_dir: Path, clang: str,
          profile: str = "apple-clang",
          base_expected: dict[str, Any] | None = None,
          ingress_authentication_base_path: Path,
          ingress_authentication_base_expected: dict[str, Any],
          source_uart_routed: bool = False,
          source_uart_route_receipt: dict[str, Any] | None = None
          ) -> dict[str, Any]:
    initial_inputs = _build_input_snapshot()
    base = base_path.read_bytes()
    if base_expected is not None and (len(base) != int(base_expected["size"]) or
            sha256(base) != base_expected["sha256"]):
        raise BuildError("PT provider input component changed")
    if (len(base) < 8 or
            struct.unpack_from("<I", base, 4)[0] !=
            zlib.crc32(base[8:]) & 0xFFFFFFFF):
        raise BuildError("PT provider input nested CRC-32 is invalid")
    donor = _authenticated_component(
        ingress_authentication_base_path,
        ingress_authentication_base_expected,
        role="PT ingress authentication base",
    )
    route_receipt = _validate_source_uart_route_receipt(
        source_uart_route_receipt, profile=profile, routed=source_uart_routed
    )
    start_offset, end_offset = INTERVAL_START - RUN_BASE, INTERVAL_END - RUN_BASE
    if start_offset < 0 or end_offset > len(base):
        raise BuildError("PT interval is outside the Apollo component")
    if sha256(base[start_offset:end_offset]) != INTERVAL_SHA256:
        raise BuildError("PT stock interval changed before source replacement")
    ld = _tool("OPENCFW_LLD", "ld.lld", "lld")
    nm = _tool("OPENCFW_NM", "llvm-nm", "nm")
    with tempfile.TemporaryDirectory(prefix="g2-pt-provider-") as temporary_name:
        temporary = Path(temporary_name)
        objects = []
        flags = [
            "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
            "-std=c11", "-Oz", "-ffreestanding", "-fno-builtin",
            "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
            "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
            "-DOPEN_CFW_PT_PRODUCTION_SOURCE_PROVIDERS=1",
            "-I", str(SOURCE_ROOT),
        ]
        for source in SOURCES:
            output = temporary / (source.stem + ".o")
            subprocess.run([clang, *flags, "-c", str(source), "-o", str(output)],
                           check=True, capture_output=True, text=True)
            objects.append(output)
        script = temporary / "pt.ld"
        script.write_text(
            "SECTIONS { "
            ". = 0x0056F4A0; .pt_legacy_entry : "
            "{ KEEP(*(.pt_legacy_entry)) } "
            ". = 0x0056F92C; .pt_legacy_postprocess : "
            "{ KEEP(*(.pt_legacy_postprocess)) } "
            ". = 0x0056F940; .text : { *(.text*) *(.rodata*) } "
            "/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) "
            "*(.comment) *(.ARM.attributes) } } "
            "ASSERT(ADDR(.pt_legacy_entry) == 0x0056F4A0, "
            "\"PT entry ABI moved\") "
            "ASSERT(SIZEOF(.pt_legacy_entry) <= 0x48C, "
            "\"PT entry ABI veneer overflow\") "
            "ASSERT(ADDR(.pt_legacy_postprocess) == 0x0056F92C, "
            "\"PT postprocess ABI moved\") "
            "ASSERT(SIZEOF(.pt_legacy_postprocess) <= 0x14, "
            "\"PT postprocess ABI veneer overflow\") "
            "ASSERT(ADDR(.text) + SIZEOF(.text) <= 0x00577C3C, "
            "\"PT interval overflow\")\n",
            encoding="utf-8")
        linked = temporary / "pt.elf"
        subprocess.run([ld, "-T", str(script), "-e",
                        "open_cfw_pt_protocol_production_entry", "-o",
                        str(linked), *map(str, objects)], check=True,
                       capture_output=True, text=True)
        sections = _elf_sections(linked)
        section_names = (".pt_legacy_entry", ".pt_legacy_postprocess", ".text")
        loadable_sections = []
        linked_bytes = linked.read_bytes()
        for name in section_names:
            section = sections.get(name)
            if (section is None or section["size"] == 0 or
                    not INTERVAL_START <= section["address"] < INTERVAL_END or
                    section["address"] + section["size"] > INTERVAL_END):
                raise BuildError(f"PT linked section placement changed: {name}")
            data = linked_bytes[
                section["offset"]:section["offset"] + section["size"]]
            if len(data) != section["size"]:
                raise BuildError(f"PT linked section extraction changed: {name}")
            loadable_sections.append((name, section, data))
        text = sections[".text"]
        if text["size"] == 0:
            raise BuildError("PT linked text placement changed")
        if any(sections.get(name, {}).get("size", 0) for name in (".data", ".bss")):
            raise BuildError("PT provider requires unbound writable storage")
        source_payload = b"".join(data for _, _, data in loadable_sections)
        symbol_output = subprocess.run([nm, "-n", str(linked)], check=True,
                                       capture_output=True, text=True).stdout
        symbols = {}
        for line in symbol_output.splitlines():
            fields = line.split()
            if len(fields) == 3:
                try:
                    symbols[fields[2]] = int(fields[0], 16)
                except ValueError:
                    pass
        calls_symbol = symbols.get(
            "open_cfw_pt_board_backend_initialize_production.calls")
        if calls_symbol is None:
            raise BuildError("PT production board call table symbol missing")
        provider_routes = []
        def read_linked_word(address: int) -> int:
            for _name, section, data in loadable_sections:
                relative = address - section["address"]
                if 0 <= relative and relative + 4 <= len(data):
                    return struct.unpack_from("<I", data, relative)[0]
            raise BuildError(
                f"PT linked word is outside loadable sections: 0x{address:08X}")

        for field, field_offset, stock_address, symbol in SOURCE_PROVIDER_ROUTES:
            target = symbols.get(symbol)
            if (target is None or not INTERVAL_START <= target < INTERVAL_END or
                    not text["address"] <= calls_symbol + field_offset <
                    text["address"] + text["size"]):
                raise BuildError(f"PT source-provider route changed: {field}")
            pointer = read_linked_word(calls_symbol + field_offset)
            if pointer != (target | 1):
                raise BuildError(
                    f"PT production board field is not source-routed: {field}")
            provider_routes.append({
                "field": field,
                "stock_runtime_address": stock_address,
                "table_slot_runtime_address": calls_symbol + field_offset,
                "target_function": symbol,
                "target_runtime_address": target,
                "target_thumb_pointer": pointer,
            })
        legacy_symbols = {
            "open_cfw_pt_protocol_legacy_entry": 0x0056F4A0,
            "open_cfw_pt_protocol_legacy_postprocess": 0x0056F92C,
        }
        for symbol, address in legacy_symbols.items():
            if symbols.get(symbol) != address:
                raise BuildError(f"PT legacy ABI symbol moved: {symbol}")
    patched = bytearray(base)
    patched[start_offset:end_offset] = b"\xFF" * (end_offset - start_offset)
    for _name, section, data in loadable_sections:
        payload_offset = section["address"] - RUN_BASE
        patched[payload_offset:payload_offset + len(data)] = data
    ingress_report = []
    for address, target, route in LEGACY_INGRESS:
        offset = address - RUN_BASE
        authenticated = bytes(donor[offset:offset + 4])
        working = bytes(base[offset:offset + 4])
        if (len(authenticated) != 4 or
                _decode_thumb_bl(address, authenticated) != target):
            raise BuildError("authenticated PT donor ingress branch changed")
        if route == "stock_direct_call" or not source_uart_routed:
            if working != authenticated:
                raise BuildError(
                    "PT working ingress differs from authenticated donor")
            evidence = "authenticated donor BL retained byte-for-byte"
        else:
            evidence = "authenticated core-stage relocation to legacy ABI"
        ingress_report.append({
            "runtime_address": address,
            "authenticated_size": len(authenticated),
            "authenticated_sha256": sha256(authenticated),
            "route": route, "evidence": evidence,
            "target_address": target,
            "target_function": (
                "open_cfw_pt_protocol_legacy_entry"
                if target == 0x0056F4A0 else
                "open_cfw_pt_protocol_legacy_postprocess"),
        })
    nested_crc32 = zlib.crc32(patched[8:]) & 0xFFFFFFFF
    struct.pack_into("<I", patched, 4, nested_crc32)
    loadable_size = len(source_payload)
    report = {
        "schema_version": 1,
        "profile": profile,
        "source": {
            "translation_units": len(SOURCES),
            "files": [{"path": str(path.relative_to(OPENCFW_ROOT)),
                       "size": path.stat().st_size,
                       "sha256": sha256(path.read_bytes())} for path in SOURCES],
        },
        "placement": {
            "runtime_start": INTERVAL_START, "runtime_end_exclusive": INTERVAL_END,
            "capacity": INTERVAL_END - INTERVAL_START,
            "linked_start": min(section["address"] for _, section, _ in
                                loadable_sections),
            "linked_end_exclusive": max(section["address"] + section["size"]
                                        for _, section, _ in loadable_sections),
            "loadable_size": loadable_size,
            "padding_size": INTERVAL_END - INTERVAL_START - loadable_size,
            "payload_sha256": sha256(source_payload),
            "interval_sha256": sha256(bytes(patched[start_offset:end_offset])),
            "sections": {
                name: {"runtime_address": section["address"],
                       "size": section["size"], "sha256": sha256(data)}
                for name, section, data in loadable_sections
            },
            "writable_bytes": 0,
        },
        "symbols": {name: symbols[name] for name in (
            "open_cfw_pt_protocol_production_entry",
            "open_cfw_pt_protocol_production_postprocess",
            "open_cfw_pt_protocol_production_bootstrap",
            "open_cfw_pt_protocol_legacy_entry",
            "open_cfw_pt_protocol_legacy_postprocess")},
        "patch_sites": [],
        "ingress_sites": ingress_report,
        "source_uart_route_receipt": route_receipt,
        "source_provider_routes": provider_routes,
        "component": {"size": len(patched), "sha256": sha256(patched)},
        "nested_crc32": nested_crc32,
        "hardware": {"validation": "blocked by unavailable physical evidence",
                     "qualification_complete": False},
    }
    if _build_input_snapshot() != initial_inputs:
        raise BuildError("PT build inputs changed during build")
    output_dir.mkdir(parents=True, exist_ok=True)
    component_path = output_dir / "ota_s200_firmware_ota.bin"
    component_path.write_bytes(patched)
    payload_path = output_dir / "pt-protocol-in-place.bin"
    payload_path.write_bytes(bytes(patched[start_offset:end_offset]))
    (output_dir / "build-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--clang", default=os.environ.get("OPENCFW_CLANG", "clang"))
    parser.add_argument("--profile", default="apple-clang")
    parser.add_argument("--ingress-authentication-base", type=Path)
    parser.add_argument("--ingress-authentication-size", type=int, required=True)
    parser.add_argument("--ingress-authentication-sha256", required=True)
    arguments = parser.parse_args()
    print(json.dumps(build(
        base_path=arguments.base, output_dir=arguments.output_dir,
        clang=arguments.clang, profile=arguments.profile,
        ingress_authentication_base_path=(
            arguments.ingress_authentication_base or arguments.base),
        ingress_authentication_base_expected={
            "size": arguments.ingress_authentication_size,
            "sha256": arguments.ingress_authentication_sha256,
        }),
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
