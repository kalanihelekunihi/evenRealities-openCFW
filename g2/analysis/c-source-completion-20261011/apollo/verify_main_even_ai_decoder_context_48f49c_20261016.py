#!/usr/bin/env python3
"""Compare C EvenAI decoder context/reader with authenticated Apollo main."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/even_ai_decoder_context_48f49c.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

with tempfile.TemporaryDirectory() as tmp:
    elf = Path(tmp) / "context.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_even_ai_decoder_context_init_48f49c",
                    str(SOURCE), "-o", str(elf)], check=True)
    with elf.open("rb") as f:
        parsed = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, entry, context, data, length, destination, count):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, blob in segments:
            cpu.mem_write(address, blob)
        cpu.mem_map(0x20000000, 0x10000)
        cpu.mem_write(0x20000100, bytes(range(64)))
        cpu.mem_write(0x20000200, b"\xa5" * 64)
        cpu.mem_write(0x20000300, b"\xa5" * 16)
        if entry == "read":
            cpu.mem_write(0x20000300, b"\x00" * 4 +
                          (0x20000100).to_bytes(4, "little") +
                          (64).to_bytes(4, "little") + b"\x00" * 4)
        cpu.reg_write(A.UC_ARM_REG_R0, context)
        cpu.reg_write(A.UC_ARM_REG_R1, data if entry == "init" else destination)
        cpu.reg_write(A.UC_ARM_REG_R2, length if entry == "init" else count)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        addresses = {"init": symbols["audio_even_ai_decoder_context_init_48f49c"]
                     if compiled else 0x48f49c,
                     "read": symbols["audio_even_ai_decoder_read_48f3a4"]
                     if compiled else 0x48f3a4}
        cpu.emu_start(addresses[entry] | 1, 0x600000, count=100000)
        return (cpu.reg_read(A.UC_ARM_REG_R0),
                bytes(cpu.mem_read(0x20000300, 16)),
                bytes(cpu.mem_read(0x20000200, 64)))

    cases = 0
    for length in (0, 1, 7, 32, 65535):
        stock = run(False, "init", 0x20000300, 0x20000100, length, 0, 0)
        source = run(True, "init", 0x20000300, 0x20000100, length, 0, 0)
        assert stock[1][4:] == source[1][4:], ("init", length, stock, source)
        assert int.from_bytes(stock[1][:4], "little") == 0x48f3a5
        assert int.from_bytes(source[1][:4], "little") == (symbols["audio_even_ai_decoder_read_48f3a4"] | 1)
        cases += 1
    for count in (0, 1, 7, 16, 32):
        for destination in (0, 0x20000200):
            results = []
            for compiled in (False, True):
                # Reader starts from the same cursor and buffer in both runs.
                # A separate init comparison above covers callback pointer.
                result = run(compiled, "read", 0x20000300,
                             0x20000100, 0, destination, count)
                results.append(result)
            assert results[0] == results[1], ("read", count, destination, results)
            cases += 1

    output = G2 / "build/c-firmware/20261016/main-even-ai-decoder-context-48f49c/oracle-receipt.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt = {"status": "PASS_NATIVE_MAIN_EVEN_AI_DECODER_CONTEXT_48F49C",
               "cases": cases,
               "stock_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "bounds": "five initializer states and ten reader memory comparisons; no protobuf decode"}
    output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], cases, hashlib.sha256(output.read_bytes()).hexdigest())
