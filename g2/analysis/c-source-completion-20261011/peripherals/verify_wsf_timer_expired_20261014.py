#!/usr/bin/env python3
"""Compare the complete stock WSF timer expiry body with selected C effects."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/foundation/wsf_radio/timer_expired.c"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
SHIM = OUT / "wsf-timer-expired-verifier-shim.c"
OBJECT = OUT / "wsf-timer-expired-verifier.o"
SHIM_OBJECT = OUT / "wsf-timer-expired-verifier-shim.o"
ELF = OUT / "wsf-timer-expired-verifier.elf"
RECEIPT = OUT / "wsf-timer-expired-native-comparison.json"
ENTRY = 0x52a542
STOP = 0x20001000
TIMER = 0x20010000
NATIVE_LIST = 0x200741b0


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(entry, native, segments, syms, state, ticks, argument, compiled):
    cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    cpu.mem_map(0x52a000, 0x2000)
    cpu.mem_map(0x538000, 0x1000)
    cpu.mem_write(ENTRY, native)
    cpu.mem_write(0x52a614, NATIVE_LIST.to_bytes(4, "little"))
    cpu.mem_map(0x100000, 0x10000)
    for address, data, memsize in segments:
        cpu.mem_write(address, data)
        if memsize > len(data):
            cpu.mem_write(address + len(data), bytes(memsize - len(data)))
    cpu.mem_map(0x20000000, 0x80000)
    queue = syms["audio_wsf_timer_list"] if compiled else NATIVE_LIST
    head = TIMER if state != "empty" else 0
    cpu.mem_write(queue, head.to_bytes(4, "little") * 2)
    cpu.mem_write(TIMER, (0).to_bytes(4, "little") + ticks.to_bytes(4, "little") + bytes(5) + b"\x7f")
    cpu.reg_write(UC_ARM_REG_SP, 0x2007f000)
    cpu.reg_write(UC_ARM_REG_LR, STOP | 1)
    cpu.reg_write(UC_ARM_REG_R0, argument)
    children = ({syms["WsfTaskLock"] & ~1: "lock",
                 syms["WsfTaskUnlock"] & ~1: "unlock",
                 syms["audio_wsf_queue_remove"] & ~1: "remove"} if compiled else
                {0x52b8c8: "lock", 0x52b8d0: "unlock", 0x538cc8: "remove"})
    log = []

    def hook(uc, address, size, _):
        kind = children.get(address)
        if kind is None:
            return
        if kind == "remove":
            assert uc.reg_read(UC_ARM_REG_R0) == queue
            assert uc.reg_read(UC_ARM_REG_R1) == TIMER
            assert uc.reg_read(UC_ARM_REG_R2) == 0
            log.append(kind)
            uc.mem_write(queue, bytes(8))
        else:
            log.append(kind)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    cpu.hook_add(UC_HOOK_CODE, hook)
    cpu.emu_start(entry | 1, STOP, count=10000)
    assert cpu.reg_read(UC_ARM_REG_PC) == STOP
    return (cpu.reg_read(UC_ARM_REG_R0), bytes(cpu.mem_read(queue, 8)),
            bytes(cpu.mem_read(TIMER + 13, 1)), log)


def main():
    blob = STOCK.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
    offset = 32 + ENTRY - 0x438000
    native = blob[offset:offset + 0x32]
    assert native[:8].hex() == "38b5002501f0bff9"
    SHIM.write_text("#include <stdint.h>\nuint32_t audio_wsf_timer_list[2];\n"
                    "void WsfTaskLock(void){}\nvoid WsfTaskUnlock(void){}\n"
                    "void audio_wsf_queue_remove(void **q,void *e,void *p){(void)q;(void)e;(void)p;}\n")
    flags = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
             "-std=c11", "-ffreestanding", "-Wall", "-Wextra", "-Werror", "-O2"]
    subprocess.run(flags + ["-c", str(SOURCE), "-o", str(OBJECT)], check=True)
    subprocess.run(flags + ["-c", str(SHIM), "-o", str(SHIM_OBJECT)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", str(OBJECT), str(SHIM_OBJECT),
                    "-o", str(ELF)], check=True)
    with ELF.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data(), s["p_memsz"]) for s in elf.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        syms = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    cases = [(state, ticks, argument) for state, ticks in
             [("empty", 0), ("pending", 5), ("due", 0)] for argument in [0, 123]]
    for state, ticks, argument in cases:
        original = run(ENTRY, native, segments, syms, state, ticks, argument, False)
        compiled = run(syms["opencfw_wsf_timer_expired"], native, segments,
                       syms, state, ticks, argument, True)
        assert original == compiled, (state, ticks, argument, original, compiled)
    receipt = {
        "status": "PASS_BOUNDED_NATIVE_WSF_TIMER_EXPIRED_C",
        "stock_blob_sha256": sha(STOCK), "stock_entry": hex(ENTRY),
        "stock_entry_bytes_sha256": hashlib.sha256(native).hexdigest(),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "cases": len(cases), "source_elf_sha256": sha(ELF),
        "whole_image_complete": False, "hardware_proof": False,
        "limits": ["Task locking and queue removal are explicit matching call boundaries; their internal concurrency effects are not verified here.",
                   "The cases cover empty, pending and due queue heads with two ignored arguments, not a full timer scheduler."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(RECEIPT))


if __name__ == "__main__":
    main()
