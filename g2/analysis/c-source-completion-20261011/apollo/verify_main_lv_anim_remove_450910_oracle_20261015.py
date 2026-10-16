#!/usr/bin/env python3
"""Compare LV animation removal and repeat/reverse effects with official Main."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_anim_remove_450910.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BODY_SHA = hashlib.sha256(IMAGE[0x450910-0x438000:0x4509da-0x438000]).hexdigest()
OUT = G2 / "build/c-firmware/20261015/main-lv-anim-remove-450910"
OUT.mkdir(parents=True, exist_ok=True)
PROVIDERS = {
    "list_remove": (0x482c0e, "audio_uart_lv_list_remove_482c0e"),
    "schedule": (0x4509da, "audio_uart_lv_transition_schedule_4509da"),
    "free": (0x44f758, "audio_uart_lv_heap_free"),
}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text("#include <stdint.h>\nuint8_t audio_uart_display_lv_state[0x200];\n" +
                    "\n".join(
        f'__attribute__((naked)) uint32_t {symbol}(void*a,uint32_t b){{__asm volatile("bx lr");}}'
        for _, symbol in PROVIDERS.values()))
    elf = Path(temp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_anim_remove_450910",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def u32(v): return (v & 0xffffffff).to_bytes(4, "little")

    def run(compiled, config):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments: uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        uc.mem_map(0x300000, 0x1000)
        anim = 0x20010000
        uc.mem_write(anim + 0x5c, bytes([config["flags"]]))
        for offset, value in ((0x44, config["repeat"]),
                              (0x3c, config["reverse_duration"]),
                              (0x30, config["duration"]),
                              (0x34, config["progress"]),
                              (0x38, 7), (0x40, 3), (0x24, 11), (0x2c, 29),
                              (0x10, 0x300001 if config["complete"] else 0),
                              (0x14, 0x300101 if config["deleted"] else 0)):
            uc.mem_write(anim + offset, u32(value))
        uc.reg_write(A.UC_ARM_REG_R0, anim)
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {(symbols[symbol] & ~1 if compiled else address): name
                 for name, (address, symbol) in PROVIDERS.items()}
        hooks.update({0x300000: "complete", 0x300100: "deleted"})
        trace = []

        def observe(cpu, address, size, _):
            name = hooks.get(address)
            if name is None: return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            trace.append((name, r0 if name != "list_remove" else anim))
            cpu.reg_write(A.UC_ARM_REG_R0, 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        start = symbols["audio_uart_lv_anim_remove_450910"] if compiled else 0x450910
        uc.emu_start(start | 1, 0x600000, count=1000)
        return trace, bytes(uc.mem_read(anim + 0x24, 0x39))

    cases = 0
    for flags in (0, 2, 0x10, 0x12):
        for repeat in (0, 1, 2, 0xffffffff):
            for reverse_duration in (0, 9):
                for progress in (4, 10, 13):
                    for complete, deleted in ((False, False), (True, False),
                                              (False, True), (True, True)):
                        config = {"flags": flags, "repeat": repeat,
                                  "reverse_duration": reverse_duration,
                                  "duration": 10, "progress": progress,
                                  "complete": complete, "deleted": deleted}
                        native = run(False, config)
                        candidate = run(True, config)
                        if native != candidate:
                            raise AssertionError((config, native, candidate))
                        cases += 1

    receipt = {"status": "PASS_NATIVE_MAIN_LV_ANIM_REMOVE_450910",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": IMAGE_SHA,
               "native_body_sha256": BODY_SHA,
               "source_owned_symbols": ["audio_uart_lv_anim_remove_450910"],
               "cases": cases,
               "limits": ["List, schedule, free and callback providers were controlled hooks; final placement and hardware behavior remain unverified."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases, hashlib.sha256(path.read_bytes()).hexdigest())
