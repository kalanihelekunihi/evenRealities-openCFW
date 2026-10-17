#!/usr/bin/env python3
"""Direct stock/C replay of exit-prompt step-two fade callback."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_exit_prompt_fade_step_58bebc.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-exit-prompt-fade-step-58bebc"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_log_flags": (0x101010, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101020, 0x43d574, "extended"),
    "compressed_log_output": (0x101030, 0x43ce9e, "compact"),
    "audio_conversate_exit_prompt_fade_schedule_58c516": (0x101040, 0x58c516, "schedule"),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_exit_prompt_fade_step_58bebc",
                    "--defsym=audio_conversate_exit_prompt_state_200745d0=0x200745d0",
                    "--defsym=audio_conversate_exit_prompt_hold_20000be4=0x20000be4",
                    "--defsym=audio_conversate_exit_prompt_fade_step3_58be1a=0x1010a1",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, app, hold, flags):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data:
                    cpu.mem_write(start, data)
        cpu.mem_write(0x200745d0, struct.pack("<I", app))
        cpu.mem_write(0x20000be4, struct.pack("<I", hold))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def cstr(machine, pointer):
            return bytes(machine.mem_read(pointer, 170)).split(b"\0", 1)[0]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None:
                return
            r = [machine.reg_read(reg) for reg in (A.UC_ARM_REG_R0,
                 A.UC_ARM_REG_R1, A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                line, fmt, amount = struct.unpack("<III", machine.mem_read(sp, 12))
                events.append((kind, r[0], cstr(machine, r[1]),
                               cstr(machine, r[2]), cstr(machine, r[3]),
                               line, cstr(machine, fmt), amount))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            elif kind == "compact":
                events.append((kind, r[0], cstr(machine, r[1]),
                               cstr(machine, r[2]), r[3]))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            else:
                callback = "step3" if r[3] in (0x58be1b, 0x1010a1) else hex(r[3])
                events.append((kind, r[0], r[1], r[2], callback))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x58bebc if native else symbols["audio_conversate_exit_prompt_fade_step_58bebc"]
        cpu.emu_start(entry | 1, 0, count=150)
        if not done[0]:
            raise RuntimeError("step-two callback did not return")
        return events, bytes(cpu.mem_read(0x200745d0, 4)), bytes(cpu.mem_read(0x20000be4, 4))

    cases = [(app, hold, flags)
             for app in (0, 0x20001000)
             for hold in (0, 1, 1000, 0xffffffff)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"step-two mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_EXIT_PROMPT_FADE_STEP_58BEBC_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x58bebc..0x58bf11",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Log transport and fade scheduler remain controlled lower boundaries.",
                         "Step-three callback remains a named child import."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
