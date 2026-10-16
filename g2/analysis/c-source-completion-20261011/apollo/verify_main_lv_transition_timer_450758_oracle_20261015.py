#!/usr/bin/env python3
"""Compare the LV animation timer callback with the official Main body."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_transition_timer_450758.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BODY_SHA = hashlib.sha256(IMAGE[0x450758-0x438000:0x450910-0x438000]).hexdigest()
OUT = G2 / "build/c-firmware/20261015/main-lv-transition-timer-450758"
OUT.mkdir(parents=True, exist_ok=True)
PROVIDERS = {
    "first": (0x482cd8, "audio_uart_lv_list_first"),
    "next": (0x482cf0, "audio_uart_lv_list_next"),
    "elapsed": (0x4734a0, "audio_uart_lv_elapsed"),
    "tick": (0x473482, "audio_uart_lv_tick"),
    "normalize": (0x450a3e, "audio_uart_lv_anim_normalize_450a3e"),
    "cancel": (0x450a74, "audio_uart_lv_anim_cancel_matching_450a74"),
    "remove": (0x450910, "audio_uart_lv_anim_remove_450910"),
}
CALLBACKS = {"delay": 0x300000, "start": 0x300100,
             "path": 0x300200, "exec": 0x300300, "custom": 0x300400}

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
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_transition_timer_callback_450758",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def u32(v): return (v & 0xffffffff).to_bytes(4, "little")
    def set32(cpu, at, value): cpu.mem_write(at, u32(value))

    def run(compiled, config):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments: uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        uc.mem_map(0x300000, 0x1000)
        state = (symbols["audio_uart_display_lv_state"] if compiled else 0x2006f548)
        anim = 0x20010000
        uc.mem_write(state + 0xa5, bytes([config["phase"]]))
        uc.mem_write(anim + 0x5c, bytes([config["flags"]]))
        set32(uc, anim + 0x50, 10)
        set32(uc, anim + 0x54, 20)
        set32(uc, anim + 0x58, config["start_at"])
        set32(uc, anim + 0x34, config["progress"])
        set32(uc, anim + 0x30, config["duration"])
        set32(uc, anim + 0x28, config["old_value"])
        set32(uc, anim + 0x24, 3)
        set32(uc, anim + 0x2c, 4)
        set32(uc, anim + 0, 0x20030000)
        for offset, name in ((0x18, "delay"), (0x0c, "start"), (0x20, "path"),
                             (4, "exec"), (8, "custom")):
            enabled = name == "path" or config.get(name, False)
            set32(uc, anim + offset, CALLBACKS[name] | 1 if enabled else 0)
        uc.reg_write(A.UC_ARM_REG_R0, 0x20031000)
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {(symbols[symbol] & ~1 if compiled else address): name
                 for name, (address, symbol) in PROVIDERS.items()}
        hooks.update({address: name for name, address in CALLBACKS.items()})
        trace, first_count = [], 0

        def observe(cpu, address, size, _):
            nonlocal first_count
            name = hooks.get(address)
            if name is None: return
            r0, r1 = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
            if name in ("first", "next", "tick"):
                trace.append((name,))
            elif name in ("exec", "custom"):
                trace.append((name, r0, r1))
            elif name == "elapsed":
                trace.append((name, r0))
            else:
                trace.append((name, r0))
            result = 0
            if name == "first":
                result = anim if first_count == 0 else 0
                first_count += 1
            elif name == "elapsed":
                result = config["elapsed"] if r0 == 10 else config["delay_elapsed"]
            elif name == "tick": result = 77
            elif name == "delay": result = config["shift"]
            elif name == "path": result = config["path_value"]
            cpu.reg_write(A.UC_ARM_REG_R0, result & 0xffffffff)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        start = (symbols["audio_uart_lv_transition_timer_callback_450758"]
                 if compiled else 0x450758)
        uc.emu_start(start | 1, 0x600000, count=3000)
        return (trace, bytes(uc.mem_read(state + 0xa4, 2)),
                bytes(uc.mem_read(anim + 0x24, 0x3c)))

    cases = 0
    for phase in (0, 1):
        for flags in (0, 1, 4, 5, 0x10, 0x14):
            for progress in (-2, 0, 12):
                for delay_elapsed in (3, 15):
                    for path_value in (5, 9):
                        config = {"phase": phase, "flags": flags, "progress": progress,
                                  "start_at": 10, "duration": 10, "old_value": 5,
                                  "elapsed": 4, "delay_elapsed": delay_elapsed,
                                  "shift": 2, "path_value": path_value,
                                  "delay": True, "start": True,
                                  "exec": True, "custom": True}
                        native = run(False, config)
                        candidate = run(True, config)
                        if native != candidate:
                            raise AssertionError((config, native, candidate))
                        cases += 1

    receipt = {"status": "PASS_NATIVE_MAIN_LV_TRANSITION_TIMER_450758",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": IMAGE_SHA,
               "native_body_sha256": BODY_SHA,
               "source_owned_symbols": ["audio_uart_lv_transition_timer_callback_450758"],
               "cases": cases,
               "limits": ["List and animation providers were controlled hooks; final placement and hardware behavior remain unverified."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases, hashlib.sha256(path.read_bytes()).hexdigest())
