#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile the field-level C KWS sources and emit their ordered NPU stream.

This generator has no dependency on the official firmware. The optional
comparison with the locked artifact belongs in tests and evidence, not in
the production input path.
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

G2 = Path(__file__).resolve().parents[1]
REPO = G2.parent
NPU = G2 / "src/codec/npu"
SOURCES = (
    "kws_activation_commands.c",
    "kws_general_commands.c",
    "kws_batch_norm_commands.c",
    "kws_transpose_commands.c",
    "kws_special_commands.c",
    "kws_fc_commands.c",
    "kws_conv_commands.c",
)
COMMAND_COUNT = 212
COMMAND_BYTES = 9164

HARNESS = r'''
#include <stdint.h>
#include <stdio.h>
#include "g2/src/codec/npu/kws_activation_commands.h"
#include "g2/src/codec/npu/kws_general_commands.h"
#include "g2/src/codec/npu/kws_batch_norm_commands.h"
#include "g2/src/codec/npu/kws_transpose_commands.h"
#include "g2/src/codec/npu/kws_special_commands.h"
#include "g2/src/codec/npu/kws_fc_commands.h"
#include "g2/src/codec/npu/kws_conv_commands.h"
static int emit(unsigned index, const uint8_t *bytes, size_t length) {
    uint8_t meta[3] = {(uint8_t)index, (uint8_t)(index >> 8), (uint8_t)length};
    return fwrite(meta, 1, 3, stdout) == 3 &&
           fwrite(bytes, 1, length, stdout) == length;
}
int main(void) {
    uint8_t bytes[G2_KWS_CONV_COMMAND_BYTES];
    unsigned index;
    size_t length;
    for (unsigned i = 0; i < G2_KWS_ACTIVATION_COUNT; ++i) {
        if (g2_kws_emit_activation(i, bytes, sizeof bytes, &index) != 0 ||
            !emit(index, bytes, G2_KWS_ACTIVATION_COMMAND_BYTES)) return 2;
    }
    for (unsigned i = 0; i < G2_KWS_GENERAL_COMMAND_COUNT; ++i) {
        if (g2_kws_emit_general_command(i, bytes, sizeof bytes, &index, &length) != 0 ||
            !emit(index, bytes, length)) return 3;
    }
    for (unsigned i = 0; i < G2_KWS_BATCH_NORM_COMMAND_COUNT; ++i) {
        if (g2_kws_emit_batch_norm(i, bytes, sizeof bytes, &index) != 0 ||
            !emit(index, bytes, G2_KWS_BATCH_NORM_COMMAND_BYTES)) return 4;
    }
    for (unsigned i = 0; i < G2_KWS_TRANSPOSE_COMMAND_COUNT; ++i) {
        if (g2_kws_emit_transpose(i, bytes, sizeof bytes, &index) != 0 ||
            !emit(index, bytes, G2_KWS_TRANSPOSE_COMMAND_BYTES)) return 5;
    }
    for (unsigned i = 0; i < G2_KWS_SPECIAL_COMMAND_COUNT; ++i) {
        if (g2_kws_emit_special(i, bytes, sizeof bytes, &index) != 0 ||
            !emit(index, bytes, G2_KWS_SPECIAL_COMMAND_BYTES)) return 6;
    }
    for (unsigned i = 0; i < G2_KWS_FC_COMMAND_COUNT; ++i) {
        if (g2_kws_emit_fc(i, bytes, sizeof bytes, &index) != 0 ||
            !emit(index, bytes, G2_KWS_FC_COMMAND_BYTES)) return 7;
    }
    for (unsigned i = 0; i < G2_KWS_CONV_COMMAND_COUNT; ++i) {
        if (g2_kws_emit_conv(i, bytes, sizeof bytes, &index) != 0 ||
            !emit(index, bytes, G2_KWS_CONV_COMMAND_BYTES)) return 8;
    }
    for (unsigned i = 0; i < G2_KWS_DEPTHWISE_COMMAND_COUNT; ++i) {
        if (g2_kws_emit_depthwise(i, bytes, sizeof bytes, &index) != 0 ||
            !emit(index, bytes, G2_KWS_DEPTHWISE_COMMAND_BYTES)) return 9;
    }
    return 0;
}
'''


def build_stream(compiler: str | None = None) -> bytes:
    compiler = compiler or shutil.which("clang")
    if compiler is None:
        raise RuntimeError("host clang is required to emit the KWS command stream")
    (REPO / "build").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="g2-kws-", dir=REPO / "build") as directory:
        temporary = Path(directory)
        harness = temporary / "emit.c"
        executable = temporary / "emit"
        harness.write_text(HARNESS)
        subprocess.run(
            [compiler, "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(REPO),
             *(str(NPU / source) for source in SOURCES), str(harness), "-o", str(executable)],
            check=True, capture_output=True, text=True,
        )
        emitted = subprocess.run([str(executable)], check=True, capture_output=True).stdout

    records: dict[int, bytes] = {}
    position = 0
    while position < len(emitted):
        if position + 3 > len(emitted):
            raise ValueError("truncated KWS record metadata")
        index, length = struct.unpack_from("<HB", emitted, position)
        position += 3
        if index >= COMMAND_COUNT or index in records or length < 4 or position + length > len(emitted):
            raise ValueError("invalid or duplicate KWS command record")
        records[index] = emitted[position:position + length]
        position += length
    if records.keys() != set(range(COMMAND_COUNT)):
        raise ValueError("KWS command graph has missing record indices")
    stream = b"".join(records[index] for index in range(COMMAND_COUNT))
    if len(stream) != COMMAND_BYTES:
        raise ValueError(f"KWS command stream is {len(stream)} bytes, expected {COMMAND_BYTES}")
    return stream


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True,
                        help="path for the generated 9164-byte command stream")
    args = parser.parse_args()
    stream = build_stream()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(stream)
    print(f"wrote {len(stream)} source-authored KWS command bytes to {args.out}")
    print(f"sha256: {hashlib.sha256(stream).hexdigest()}")


if __name__ == "__main__":
    main()
