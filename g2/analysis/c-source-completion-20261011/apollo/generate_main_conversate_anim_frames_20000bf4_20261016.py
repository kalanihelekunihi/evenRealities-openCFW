#!/usr/bin/env python3
"""Generate source-owned Conversate animation data from authenticated Main bytes."""
import hashlib
import struct
from pathlib import Path

from decode_main_low_ram_20261016 import PACKAGE, PAYLOAD_SHA, decode

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/conversate_anim_frames_20000bf4.c"
BASE = 0x438000
DESCRIPTORS = 0x76bc00
PIXELS = 0x6c7930
COUNT = 6
FRAME_SIZE = 0x190


def main():
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("authenticated Main payload changed")
    ram = decode()
    pointers = struct.unpack_from("<6I", ram, 0xbf4)
    if pointers != tuple(DESCRIPTORS + i * 28 for i in range(COUNT)):
        raise RuntimeError("startup pointer table changed")
    for i in range(COUNT):
        words = struct.unpack_from("<7I", payload, DESCRIPTORS - BASE + i * 28)
        if words != (0x619, 0x00140014, 0x14, FRAME_SIZE,
                     PIXELS + i * FRAME_SIZE, 0, 0):
            raise RuntimeError(f"frame {i} descriptor changed")
    pixels = payload[PIXELS - BASE:PIXELS - BASE + COUNT * FRAME_SIZE]
    lines = ["/* Authenticated Main low-RAM pointers 0x20000bf4 and ROM frames 0x76bc00. */",
             "#include <stdint.h>",
             "struct conversate_frame_descriptor {",
             "    uint32_t magic, dimensions, stride, byte_count;",
             "    const uint8_t *pixels;",
             "    uint32_t reserved_a, reserved_b;",
             "};",
             "_Static_assert(sizeof(struct conversate_frame_descriptor) == 28u, \"frame descriptor\");",
             "__attribute__((used, section(\".g2_conversate_anim_pixels_6c7930\")))",
             f"const uint8_t audio_conversate_anim_pixels_6c7930[{len(pixels)}] = {{"]
    for i in range(0, len(pixels), 16):
        lines.append("    " + ", ".join(f"0x{value:02x}" for value in pixels[i:i+16]) + ",")
    lines += ["};", "__attribute__((used, section(\".g2_conversate_anim_descriptors_76bc00\")))",
              "const struct conversate_frame_descriptor audio_conversate_anim_descriptors_76bc00[6] = {"]
    for i in range(COUNT):
        lines.append(f"    {{0x619u, 0x00140014u, 0x14u, 0x190u, audio_conversate_anim_pixels_6c7930 + {i * FRAME_SIZE}u, 0u, 0u}},")
    lines += ["};", "__attribute__((used, section(\".g2_conversate_anim_frames_20000bf4\")))",
              "const void *audio_conversate_anim_frames_20000bf4[6] = {"]
    for i in range(COUNT):
        lines.append(f"    &audio_conversate_anim_descriptors_76bc00[{i}],")
    lines += ["};", ""]
    SOURCE.write_text("\n".join(lines))
    print("PASS_GENERATE_CONVERSATE_ANIM", len(pixels), hashlib.sha256(SOURCE.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
