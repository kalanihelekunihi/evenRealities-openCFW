#!/usr/bin/env python3
"""Bounded locked-stock/source instruction oracle for new Bootloader bodies."""
import argparse
import hashlib
import json
import pathlib
import random
import struct

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = pathlib.Path(__file__).resolve().parents[4]
BLOB = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
HASH = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
BASE = 0x410000
STOP = 0x600000
REGS = [A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3]


def segments(path):
    with path.open("rb") as handle:
        elf = ELFFile(handle)
        result = [(part["p_vaddr"], part.data()) for part in elf.iter_segments()
                  if part["p_type"] == "PT_LOAD"]
        symbols = {}
        for section in elf.iter_sections():
            if section.header.sh_type == "SHT_SYMTAB":
                symbols.update({symbol.name: symbol["st_value"]
                                for symbol in section.iter_symbols()})
    return result, symbols


def machine(blob, source_segments, source, entry, arguments, setup=None,
            capture=()):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(0x400000, 0x50000)
    uc.mem_write(BASE, blob)
    uc.mem_map(0x500000, 0x10000)
    for address, data in source_segments:
        if data and 0x500000 <= address < 0x510000:
            uc.mem_write(address, data)
    uc.mem_map(0x600000, 0x1000)
    uc.mem_map(0x20000000, 0x30000)
    uc.mem_map(0x40020000, 0x20000)
    if setup:
        setup(uc)
    for register, value in zip(REGS, arguments):
        uc.reg_write(register, value)
    uc.reg_write(A.UC_ARM_REG_SP, 0x2002f000)
    uc.reg_write(A.UC_ARM_REG_LR, STOP | 1)
    uc.reg_write(A.UC_ARM_REG_XPSR, 0x01000000)
    seen = set()
    done = [False]

    def trace(cpu, address, size, _):
        if address == STOP:
            done[0] = True
            cpu.emu_stop()
        elif not source and entry <= address < entry + 0x400:
            seen.update(range(address, address + size))

    uc.hook_add(UC_HOOK_CODE, trace)
    uc.emu_start((entry if not source else source) | 1, STOP + 2,
                 count=250000)
    assert done[0], (hex(entry), source, hex(uc.reg_read(A.UC_ARM_REG_PC)))
    return ((uc.reg_read(A.UC_ARM_REG_R0), uc.reg_read(A.UC_ARM_REG_R1)),
            tuple(bytes(uc.mem_read(address, size)) for address, size in capture)), seen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--division-elf", type=pathlib.Path, required=True)
    parser.add_argument("--decoder-elf", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()
    blob = BLOB.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == HASH
    division_segments, division_symbols = segments(args.division_elf)
    decoder_segments, decoder_symbols = segments(args.decoder_elf)
    edges = [0, 1, 2, 3, 0xffff, 0x10000, 0xffffffff,
             0x100000000, 0x100000001, 0x8000000000000000,
             0xffffffffffffffff]
    cases = [(a, b) for a in edges for b in edges]
    rng = random.Random(0x42287c)
    cases += [(rng.getrandbits(64), rng.getrandbits(64)) for _ in range(300)]
    visited = set()
    for numerator, denominator in cases:
        words = [numerator & 0xffffffff, numerator >> 32,
                 denominator & 0xffffffff, denominator >> 32]
        original, seen = machine(blob, division_segments, None, 0x42287c, words)
        candidate, _ = machine(blob, division_segments,
                               division_symbols["opencfw_provider_42287c"],
                               0x42287c, words)
        assert original == candidate, ("division", words, original, candidate)
        visited |= seen
    decoder_visited = set()
    decoder_cases = 0
    for word0 in (0, 1, 0xc00000, 0x3fffffff, 0xffffffff):
        for word1 in (0, 0x4c4, 0xffffffff):
            for state in (0, 1, 2):
                for auxiliary in (0, 1, 2, 3):
                    for mode in (0, 1):
                        config = (word0 ^ (word1 << 4) ^
                                  (state << 8) ^ auxiliary) & 0xffffffff
                        hw = (word1 ^ state) & 3
                        input_bytes = bytearray(20)
                        struct.pack_into("<II", input_bytes, 0, word0, word1)
                        input_bytes[16:19] = bytes((word0 & 0xf, state, auxiliary))

                        def setup(cpu):
                            cpu.mem_write(0x20010000, bytes(input_bytes))
                            cpu.mem_write(0x20010100, b"\xa5" * 8)
                            cpu.mem_write(0x434168, struct.pack("<I", config))
                            cpu.mem_write(0x40021000, struct.pack("<I", hw))
                            cpu.mem_write(0x2002708c, bytes((mode,)))

                        words = [0x20010000, 0x20010100, 0x20010104, 0]
                        original, seen = machine(blob, decoder_segments, None,
                            0x42a550, words, setup, ((0x20010100, 8),))
                        candidate, _ = machine(blob, decoder_segments,
                            decoder_symbols["opencfw_provider_42a550"],
                            0x42a550, words, setup, ((0x20010100, 8),))
                        assert (original[0][0], original[1]) == (candidate[0][0], candidate[1]), (
                            "decoder", word0, word1, state, auxiliary, mode,
                            original, candidate)
                        decoder_visited |= seen
                        decoder_cases += 1
    receipt = {"status": "PASS", "original_sha256": HASH,
                      "division_source_elf_sha256": hashlib.sha256(args.division_elf.read_bytes()).hexdigest(),
                      "decoder_source_elf_sha256": hashlib.sha256(args.decoder_elf.read_bytes()).hexdigest(),
                      "runner_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
                      "division_cases": len(cases),
                      "division_stock_bytes_visited": len(visited),
                      "division_stock_body_bytes": 562,
                      "decoder_cases": decoder_cases,
                      "decoder_stock_bytes_visited": len(decoder_visited),
                      "decoder_stock_body_bytes": 782,
                      "limits": ["Unicorn Cortex-M33 compatible recompilation of unchanged C source, not selected Cortex-M55 object execution.",
                                 "Division compares R0:R1; decoder compares R0 and two output words. Other caller registers and FP state are outside this oracle.",
                                 "Decoder tests synthetic input snapshots, fixed simulated MMIO/configuration, and successful/invalid branches; no physical power transition or product data ownership proof.",
                                 "Original-byte visits count instruction bytes reached in tested cases, not exhaustive function coverage or image equality."]}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({key: receipt[key] for key in (
        "status", "division_cases", "division_stock_bytes_visited",
        "decoder_cases", "decoder_stock_bytes_visited")}))


if __name__ == "__main__":
    main()
