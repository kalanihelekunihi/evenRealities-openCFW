# SPDX-License-Identifier: MIT

from __future__ import annotations

import hashlib
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
COMPONENT = ROOT / "research" / "candidates" / "freetype"
SOURCE = COMPONENT / "runtime_freetype_jump_candidate.c"
EVIDENCE = COMPONENT / "JUMP_ABI_EVIDENCE.md"
LOAD_BASE = 0x00437FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

SAVE_START = 0x0056777C
SAVE_END = 0x0056778E
SAVE_BYTES = bytes.fromhex("ec46a0e8f00fa0e80050a0ec108b00207047")
SAVE_SHA256 = "205f3a06127e5125d848bcbcf69d4faddb5504e5477e5b28d49e0ea601df66bd"
RESTORE_START = 0x00567790
RESTORE_END = 0x005677A8
RESTORE_BYTES = bytes.fromhex(
    "002908bf491cb0e8f00fb0e80050b0ec108be54608007047"
)
RESTORE_SHA256 = "720424552af7541d51b4eb65dbdfd5a7f65c4f6f1c4d871d2f27e5e02559c0bb"
VALIDATOR_START = 0x00524F70
VALIDATOR_END = 0x00524F84
VALIDATOR_SHA256 = "ceff9037d72ed544f9a460ff557f1707f89d13009ca63a0731a1187dd8064d1a"

BUFFER_BYTES = 128
SAVED_BYTES = 104
BUFFER_ALIGNMENT = 8


def image_slice(image: bytes, start: int, end: int) -> bytes:
    return image[start - LOAD_BASE:end - LOAD_BASE]


def wide_branch_target(address: int, first: int, second: int) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    immediate = (
        sign << 24
        | (1 ^ (j1 ^ sign)) << 23
        | (1 ^ (j2 ^ sign)) << 22
        | (first & 0x03FF) << 12
        | (second & 0x07FF) << 1
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFFFFFF


def direct_callers(image: bytes, target: int) -> list[int]:
    callers: list[int] = []
    for offset in range(0, len(image) - 3, 2):
        first, second = struct.unpack_from("<HH", image, offset)
        address = LOAD_BASE + offset
        if wide_branch_target(address, first, second) == target:
            callers.append(address)
    return callers


def model_save(
    core: tuple[int, ...],
    stack_pointer: int,
    link_register: int,
    vfp: tuple[int, ...],
) -> bytearray:
    if len(core) != 8 or len(vfp) != 8:
        raise ValueError("model requires r4-r11 and d8-d15")
    buffer = bytearray([0xA5] * BUFFER_BYTES)
    struct.pack_into("<8I", buffer, 0x00, *core)
    struct.pack_into("<II", buffer, 0x20, stack_pointer, link_register)
    struct.pack_into("<8Q", buffer, 0x28, *vfp)
    return buffer


def model_restore(buffer: bytes, value: int) -> tuple[tuple[int, ...], int, int, tuple[int, ...], int]:
    return (
        struct.unpack_from("<8I", buffer, 0x00),
        struct.unpack_from("<I", buffer, 0x20)[0],
        struct.unpack_from("<I", buffer, 0x24)[0],
        struct.unpack_from("<8Q", buffer, 0x28),
        value if value != 0 else 1,
    )


def llvm_tool(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    for root in (Path("/opt/homebrew/opt/llvm/bin"), Path("/usr/local/opt/llvm/bin")):
        candidate = root / name
        if candidate.exists():
            return str(candidate)
    return None


class RuntimeFreeTypeJumpCandidateTests(unittest.TestCase):
    def test_official_leaves_and_validator_layout_are_authenticated(self) -> None:
        image = IMAGE.read_bytes()
        self.assertEqual(len(image), IMAGE_SIZE)
        self.assertEqual(hashlib.sha256(image).hexdigest(), IMAGE_SHA256)
        save = image_slice(image, SAVE_START, SAVE_END)
        restore = image_slice(image, RESTORE_START, RESTORE_END)
        validator = image_slice(image, VALIDATOR_START, VALIDATOR_END)
        self.assertEqual(save, SAVE_BYTES)
        self.assertEqual(hashlib.sha256(save).hexdigest(), SAVE_SHA256)
        self.assertEqual(restore, RESTORE_BYTES)
        self.assertEqual(hashlib.sha256(restore).hexdigest(), RESTORE_SHA256)
        self.assertEqual(hashlib.sha256(validator).hexdigest(), VALIDATOR_SHA256)

        # Four stores prove the fields after jmp_buf start at 0x80.
        for encoded_offset in (b"\x80\x10", b"\x84\x20", b"\x88\x30", b"\x8c\x10"):
            self.assertIn(encoded_offset, validator)

    def test_direct_ingress_is_exactly_cmap_validator_and_smooth_raster(self) -> None:
        image = IMAGE.read_bytes()
        self.assertEqual(
            direct_callers(image, SAVE_START),
            [0x005DED32, 0x005E1F14],
        )
        self.assertEqual(
            direct_callers(image, RESTORE_START),
            [0x00524F90, 0x005E15D6],
        )

    def test_host_model_round_trips_registers_and_preserves_reserved_tail(self) -> None:
        core = tuple(0x44000000 + index for index in range(8))
        vfp = tuple(0xD800000000000000 + index for index in range(8))
        buffer = model_save(core, 0x20012340, 0x005E1F19, vfp)
        self.assertEqual(len(buffer), BUFFER_BYTES)
        self.assertEqual(buffer[SAVED_BYTES:], bytes([0xA5] * 24))
        restored = model_restore(buffer, 37)
        self.assertEqual(restored, (core, 0x20012340, 0x005E1F19, vfp, 37))
        self.assertEqual(model_restore(buffer, 0)[-1], 1)
        self.assertEqual(model_restore(buffer, -9)[-1], -9)

    def test_cortex_m55_provider_emits_the_authenticated_leaf_bodies(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or llvm_tool("clang")
        objcopy = llvm_tool("llvm-objcopy")
        nm = llvm_tool("llvm-nm")
        if clang is None or objcopy is None or nm is None:
            self.skipTest("Clang and LLVM object tools are required")
        with tempfile.TemporaryDirectory(prefix="opencfw-freetype-jump-") as temporary:
            temporary_path = Path(temporary)
            output = temporary_path / "jump.o"
            text = temporary_path / "jump.text"
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    "-mcpu=cortex-m55",
                    "-mthumb",
                    "-mfloat-abi=hard",
                    "-std=c11",
                    "-O2",
                    "-ffreestanding",
                    "-fno-builtin",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    f"-DOPEN_CFW_FREETYPE_JMP_BUF_BYTES={BUFFER_BYTES}",
                    f"-DOPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT={BUFFER_ALIGNMENT}",
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [objcopy, "--dump-section", f".text={text}", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )
            emitted = text.read_bytes()
            self.assertEqual(emitted[0:len(SAVE_BYTES)], SAVE_BYTES)
            self.assertEqual(emitted[20:20 + len(RESTORE_BYTES)], RESTORE_BYTES)
            symbols = subprocess.run(
                [nm, "--print-size", "--size-sort", str(output)],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertIn("00000012 T open_cfw_freetype_external_setjmp", symbols)
            self.assertIn("00000018 T open_cfw_freetype_external_longjmp", symbols)

    def test_license_evidence_and_production_exclusion(self) -> None:
        self.assertIn("SPDX-License-Identifier: MIT", SOURCE.read_text())
        report = EVIDENCE.read_text()
        for value in (
            "0x0056777C",
            "0x00567790",
            "128-byte buffer",
            "r4-r11",
            "d8-d15",
            "zero to one",
        ):
            self.assertIn(value, report)
        overlay = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
        self.assertNotIn("runtime_freetype_jump_candidate", overlay.read_text())


if __name__ == "__main__":
    unittest.main()
