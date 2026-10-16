#!/usr/bin/env python3
"""Compare Terminal event dispatcher branches with pinned Apollo stock."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_event_emit_5eadd4.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-event-emit-5eadd4"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
STUB = """#include <stdint.h>
void audio_terminal_event_type2_5eabde(const void*a){(void)a;}
void audio_terminal_event_type4_5ea9f6(void){}
void audio_terminal_event_default_5eaad4(const void*a){(void)a;}
void audio_terminal_event_type3_mask_5eaca0(uint32_t a){(void)a;}
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "event-emit-oracle-stub.c"
    stub.write_text(STUB)
    elf = OUT / "event-emit-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_event_emit_5eadd4",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, mode, mask, payload):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        names = ("audio_terminal_event_type2_5eabde", "audio_terminal_event_type4_5ea9f6",
                 "audio_terminal_event_default_5eaad4",
                 "audio_terminal_event_type3_mask_5eaca0")
        stock = (0x5eabde, 0x5ea9f6, 0x5eaad4, 0x5eaca0)
        cuts = {(symbols[name] if compiled else address)&~1: index
                for index, (name, address) in enumerate(zip(names, stock))}
        trace = []

        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            trace.append((index,) if index == 1 else
                         (index, cpu.reg_read(A.UC_ARM_REG_R0)))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, mode)
        u.reg_write(A.UC_ARM_REG_R1, mask)
        u.reg_write(A.UC_ARM_REG_R2, payload)
        entry = symbols["audio_terminal_event_emit_5eadd4"] if compiled else 0x5eadd4
        u.emu_start(entry|1, 0x600000, count=10000)
        return trace

    cases = 0
    for mode in (0, 1, 2, 3, 4, 5, 0x103, 0xffffffff):
        for mask in (0, 1, 0xfffe, 0xffff, 0x10000, 0xffffffff):
            for payload in (0, 0x20001000, 0xffffffff):
                stock = run(False, mode, mask, payload)
                selected = run(True, mode, mask, payload)
                if stock != selected:
                    raise RuntimeError(f"event emit mismatch {mode=:#x} "
                                       f"{mask=:#x} {payload=:#x}: {stock} vs {selected}")
                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_EVENT_EMIT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "all mode branches, byte/halfword truncation, mask sentinel and payload forwarding",
              "limits": ["Four event child effects remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
