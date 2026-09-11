#!/usr/bin/env python3
"""Register the NVIC system-reset leaf and its reset-now wrapper.

Relocates two independently callable, single-caller bootloader bodies to the
overlay's free tail and redirects their authenticated stock addresses to the
relocated code:

  * ``open_cfw_bootloader_nvic_system_reset_41a700`` at
    ``[0x0041A700,0x0041A71E)`` -- the architectural Cortex-M "request a
    system reset" sequence against SCB->AIRCR, structurally identical to the
    CMSIS-Core ``NVIC_SystemReset()`` helper.
  * ``open_cfw_bootloader_reset_now_41ac8a`` at ``[0x0041AC8A,0x0041AC92)``
    -- a trivial wrapper that calls the above.

See docs/research/g2-bootloader-nvic-system-reset-41a700-source-closure.md.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "components/bootloader/core_overlay/overlay.json"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_nvic_system_reset_41a700.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
EVIDENCE = "docs/research/g2-bootloader-nvic-system-reset-41a700-source-closure.md"
BASE = 0x00410000

SOURCE_SIZE = 2570
SOURCE_SHA = "753b1836a85c94003f204e09382ce48db94e9b82e14c62145fd0ab22f14019bb"

FLAGS = [
    "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-ffunction-sections", "-fdata-sections",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi",
    "-mllvm", "-enable-machine-outliner=never",
    "-Wall", "-Wextra", "-Werror", "-fno-ident",
]

RESET_FUNCTION = "open_cfw_bootloader_nvic_system_reset_41a700"
RESET_START = 0x0041A700
RESET_END = 0x0041A71E
RESET_STOCK_SHA = "f402a16ff40b62814b131682f04040969559f286afbb056a3895ac78614db1cf"
RESET_UNRELOCATED_SHA = "a040c2cdc58094b3319539c982f32dc9fa69441b668ba7e5c264ac1fae3e6bcd"
RESET_SIZE = 36
RESET_ALIGNMENT = 4
# Discovered from the initial (intentionally wrong) build attempt; see the
# audit for the observed-vs-reviewed transcript.
RESET_OFFSET = 15184
RESET_SHA = RESET_UNRELOCATED_SHA  # no relocations in this leaf

WRAPPER_FUNCTION = "open_cfw_bootloader_reset_now_41ac8a"
WRAPPER_START = 0x0041AC8A
WRAPPER_END = 0x0041AC92
WRAPPER_STOCK_SHA = "5f9a6b47f08eb58759df839c742eeae1a6c396a5731d2aa80cb635be744cc64f"
WRAPPER_UNRELOCATED_SHA = "216312cc611f7913183bf1408be71d17cc8774c388ccd585c665a347fdf98a83"
WRAPPER_SIZE = 4
WRAPPER_ALIGNMENT = 2
WRAPPER_OFFSET = 15220
WRAPPER_SHA = "PLACEHOLDER"

APPLE_OVERLAY_SHA = "PLACEHOLDER"
APPLE_OVERLAY_SIZE = 0
APPLE_COMPONENT_SHA = "PLACEHOLDER"
APPLE_COMPONENT_SIZE = 0


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: Any) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def source_record() -> dict[str, Any]:
    payload = SOURCE.read_bytes()
    if len(payload) != SOURCE_SIZE or digest(payload) != SOURCE_SHA:
        raise SystemExit("nvic-system-reset source identity changed")
    return {
        "path": SOURCE.relative_to(ROOT).as_posix(),
        "size": len(payload),
        "sha256": digest(payload),
        "license": "MIT",
        "origin": (
            "clean-room Cortex-M system-reset entry and its trivial "
            "reset-now wrapper"
        ),
        "evidence": EVIDENCE,
    }


def toolchain_block() -> dict[str, Any]:
    return {
        "target": "arm-none-eabi",
        "reviewed_version_prefix": "Apple clang version 21.0.0",
        "flags": list(FLAGS),
    }


def linux_profile(expected: dict[str, Any]) -> dict[str, Any]:
    return {
        "reviewed_version_prefix": "Homebrew clang version 22.1.8",
        "expected": expected,
        "relocations": expected.get("_relocations", []),
    }


def main() -> int:
    boot = BOOT.read_bytes()
    if digest(boot[RESET_START - BASE:RESET_END - BASE]) != RESET_STOCK_SHA:
        raise SystemExit("authenticated NVIC_SystemReset body changed")
    if digest(boot[WRAPPER_START - BASE:WRAPPER_END - BASE]) != WRAPPER_STOCK_SHA:
        raise SystemExit("authenticated reset-now wrapper body changed")

    source = source_record()
    toolchain = toolchain_block()

    reset_expected = {
        "size": RESET_SIZE,
        "sha256": RESET_SHA,
        "alignment": RESET_ALIGNMENT,
        "offset": RESET_OFFSET,
        "unrelocated_sha256": RESET_UNRELOCATED_SHA,
    }
    reset_entry = {
        "function": RESET_FUNCTION,
        "runtime_address": RESET_START,
        "source": source,
        "toolchain": toolchain,
        "strict_relocation_contract": True,
        "expected": reset_expected,
        "stock": {"size": RESET_SIZE, "sha256": RESET_SHA},
        "relocations": [],
        "allow_discarded_alloc_sections": True,
        "toolchain_profiles": {
            "linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": dict(reset_expected),
                "relocations": [],
            }
        },
    }

    wrapper_relocations = [
        {
            "offset": 0,
            "type": "R_ARM_THM_CALL",
            "symbol": RESET_FUNCTION,
            "target_function": RESET_FUNCTION,
            "symbol_type": "STT_FUNC",
        }
    ]
    wrapper_expected = {
        "size": WRAPPER_SIZE,
        "sha256": WRAPPER_SHA,
        "alignment": WRAPPER_ALIGNMENT,
        "offset": WRAPPER_OFFSET,
        "unrelocated_sha256": WRAPPER_UNRELOCATED_SHA,
    }
    wrapper_entry = {
        "function": WRAPPER_FUNCTION,
        "runtime_address": WRAPPER_START,
        "source": source,
        "toolchain": toolchain,
        "strict_relocation_contract": True,
        "expected": wrapper_expected,
        "stock": {"size": WRAPPER_SIZE, "sha256": WRAPPER_SHA},
        "relocations": wrapper_relocations,
        "allow_discarded_alloc_sections": True,
        "toolchain_profiles": {
            "linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": dict(wrapper_expected),
                "relocations": wrapper_relocations,
            }
        },
    }

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    names = {RESET_FUNCTION, WRAPPER_FUNCTION}
    retained_relocated = [
        item for item in overlay["relocated_leaves"]
        if item.get("function") not in names
    ]
    overlay["relocated_leaves"] = sorted(
        [*retained_relocated, reset_entry, wrapper_entry],
        key=lambda item: int(item["expected"]["offset"]),
    )

    reset_patch = {
        "name": f"replace_bootloader_{RESET_FUNCTION.removeprefix('open_cfw_bootloader_')}",
        "runtime_address": RESET_START,
        "expected_size": RESET_END - RESET_START,
        "expected_sha256": RESET_STOCK_SHA,
        "branch": "b_w",
        "target_function": RESET_FUNCTION,
    }
    wrapper_patch = {
        "name": f"replace_bootloader_{WRAPPER_FUNCTION.removeprefix('open_cfw_bootloader_')}",
        "runtime_address": WRAPPER_START,
        "expected_size": WRAPPER_END - WRAPPER_START,
        "expected_sha256": WRAPPER_STOCK_SHA,
        "branch": "b_w",
        "target_function": WRAPPER_FUNCTION,
    }
    retained_patches = [
        item for item in overlay["patch_sites"]
        if item.get("target_function") not in names
    ]
    overlay["patch_sites"] = sorted(
        [*retained_patches, reset_patch, wrapper_patch],
        key=lambda item: int(item["runtime_address"]),
    )

    overlay["expected"]["overlay_size"] = APPLE_OVERLAY_SIZE
    overlay["expected"]["overlay_sha256"] = APPLE_OVERLAY_SHA
    overlay["expected"]["component_size"] = APPLE_COMPONENT_SIZE
    overlay["expected"]["component_sha256"] = APPLE_COMPONENT_SHA

    write_json(OVERLAY, overlay)
    print("registered NVIC system-reset leaf and reset-now wrapper")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
