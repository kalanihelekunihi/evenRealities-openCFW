#!/usr/bin/env python3
"""Bounded data-effect oracle for the image-B native 0x10011344 schedule."""
import ctypes
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_runtime_copy.c"
FILL_SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_runtime_helpers.c"
MOVE_SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_runtime_move.c"
HERE = Path(__file__).resolve().parent


def native_schedule(memory, destination, source, length):
    n = length
    if ((destination | source) & 3) != 0:
        while n:
            memory[destination] = memory[source]
            destination += 1
            source += 1
            n -= 1
        return
    while n >= 16:
        a = memory[source:source + 4]
        b = memory[source + 4:source + 8]
        c = memory[source + 8:source + 12]
        memory[destination:destination + 4] = a
        d = memory[source + 12:source + 16]
        memory[destination + 4:destination + 8] = b
        memory[destination + 8:destination + 12] = c
        memory[destination + 12:destination + 16] = d
        source += 16
        destination += 16
        n -= 16
    while n >= 4:
        word = memory[source:source + 4]
        source += 4
        memory[destination:destination + 4] = word
        destination += 4
        n -= 4
    while n:
        byte = memory[source]
        source += 1
        memory[destination] = byte
        destination += 1
        n -= 1


def main():
    with tempfile.TemporaryDirectory() as temporary:
        binary = Path(temporary) / "runtime_copy.so"
        subprocess.run(["clang", "-shared", "-fPIC", "-O2", "-std=c11",
                        str(SOURCE), str(FILL_SOURCE), str(MOVE_SOURCE),
                        "-o", str(binary)], check=True)
        library = ctypes.CDLL(str(binary))
        function = library.gx8002_image_b_copy_10011344
        function.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
        cases = 0
        for destination in (16, 17, 18, 19, 32, 33, 34, 35, 48, 49, 50, 51):
            for source in (16, 17, 18, 19, 32, 33, 34, 35, 48, 49, 50, 51):
                for length in range(66):
                    seed = bytearray((i * 37 + 11) & 255 for i in range(160))
                    expected = seed.copy()
                    native_schedule(expected, destination, source, length)
                    actual = (ctypes.c_uint8 * len(seed)).from_buffer(seed)
                    base = ctypes.addressof(actual)
                    function(base + destination, base + source, length)
                    if seed != expected:
                        raise AssertionError((destination, source, length))
                    cases += 1
        move = library.gx8002_image_b_move_10009968
        move.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]
        move.restype = ctypes.c_void_p
        move_cases = 0
        for destination in (16, 17, 18, 19, 32, 33, 34, 35, 48, 49, 50, 51):
            for source in (16, 17, 18, 19, 32, 33, 34, 35, 48, 49, 50, 51):
                for length in range(66):
                    seed = bytearray((i * 37 + 11) & 255 for i in range(160))
                    expected = seed.copy()
                    if destination >= source:
                        for index in range(length - 1, -1, -1):
                            expected[destination + index] = expected[source + index]
                    else:
                        native_schedule(expected, destination, source, length)
                    actual = (ctypes.c_uint8 * len(seed)).from_buffer(seed)
                    base = ctypes.addressof(actual)
                    returned = move(base + destination, base + source, length)
                    if seed != expected or returned != base + destination:
                        raise AssertionError(("move", destination, source, length))
                    move_cases += 1
        fill = library.gx8002_image_b_zero_100113c4
        fill.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32]
        fill_cases = 0
        for destination in (16, 17, 18, 19, 32, 33, 34, 35):
            for length in range(66):
                for value in (0, 0x12, 0xa5, 0x1ff):
                    seed = bytearray((i * 37 + 11) & 255 for i in range(160))
                    expected = seed.copy()
                    expected[destination:destination + length] = bytes([value & 255]) * length
                    actual = (ctypes.c_uint8 * len(seed)).from_buffer(seed)
                    fill(ctypes.addressof(actual) + destination, value, length)
                    if seed != expected:
                        raise AssertionError((destination, length, value))
                    fill_cases += 1
    receipt = {
        "native_entry": "0x10011344",
        "image_sha256": "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "bounded_effect_cases": cases,
        "fill_native_entry": "0x100113c4",
        "fill_source_sha256": hashlib.sha256(FILL_SOURCE.read_bytes()).hexdigest(),
        "fill_bounded_effect_cases": fill_cases,
        "move_native_entry": "0x10009968",
        "move_source_sha256": hashlib.sha256(MOVE_SOURCE.read_bytes()).hexdigest(),
        "move_bounded_effect_cases": move_cases,
        "result": "PASS",
        "limit": "Host C versus instruction-derived schedule over finite lengths, alignments, and overlaps; no C-SKY execution or physical RAM proof.",
    }
    path = HERE / "runtime-copy-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
