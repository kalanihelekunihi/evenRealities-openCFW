#!/usr/bin/env python3
"""Direct stock/C replay of foreground display registry selection."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_current_set_442456.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-current-set-442456"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
DATA = {"audio_uart_user_registry_rows": 0x20066230,
        "audio_uart_user_registry_count": 0x200744d4,
        "audio_uart_display_audio_handle": 0x200744d0}
LOWERS = {
    "audio_uart_display_audio_terminal_mode_45bbf4": (0x45bbf4, "terminal"),
    "audio_uart_display_audio_enqueue_45f3c8": (0x45f3c8, "enqueue"),
    "audio_log_flags": (0x43d0ce, "flags"),
    "audio_log_extended": (0x43d574, "extended"),
    "compressed_log_output": (0x43ce9e, "compressed"),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "display-current-set.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_display_current_set",
                    *[f"--defsym={name}=0x{address:x}" for name, address in DATA.items()],
                    *[f"--defsym={name}=0x{address:x}" for name, (address, _) in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, type_value, terminal, count, flags, app_id):
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
        state = 0x20070000
        cpu.mem_write(0x200744d0, struct.pack("<II", state, count))
        cpu.mem_write(state + 0x20, struct.pack("<I", 0x12345678))
        for index in range(4):
            config = 0x20071000 + index * 0x100
            cpu.mem_write(config, struct.pack("<I", app_id if index == 2 else
                                              (0x1000 + index)))
            cpu.mem_write(config + 11, bytes([0 if index == 1 else 1]))
            callback = 0 if index == 3 else 0x101011
            cpu.mem_write(0x20066230 + index * 16 + 8,
                          struct.pack("<II", callback, config))
        cpu.reg_write(A.UC_ARM_REG_R0, type_value)
        cpu.reg_write(A.UC_ARM_REG_R1, app_id)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        kinds = {address: name for address, name in LOWERS.values()}
        events, done = [], [False]

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def cstr(address):
            return bytes(cpu.mem_read(address, 160)).split(b"\0", 1)[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            r0, r1, r2, r3 = (machine.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            if pc == 0x101010:
                events.append(("callback", r0, r1, r2, r3))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
                return
            name = kinds.get(pc)
            if name is None:
                return
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if name == "terminal":
                events.append((name,))
                machine.reg_write(A.UC_ARM_REG_R0, terminal)
            elif name == "enqueue":
                events.append((name, r0, r1))
                machine.reg_write(A.UC_ARM_REG_R0, 0x20072000)
            elif name == "flags":
                events.append((name,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif name == "extended":
                events.append((name, r0, cstr(r1), cstr(r2), cstr(r3),
                               word(sp), cstr(word(sp + 4)), word(sp + 8)))
            else:
                events.append((name, r0, cstr(r1), cstr(r2), r3))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x442456 if native else symbols["audio_uart_display_current_set"]
        cpu.emu_start(entry | 1, 0, count=1000)
        if not done[0]:
            raise RuntimeError(f"display current set did not return: {native} {type_value} {terminal} {count}")
        return cpu.reg_read(A.UC_ARM_REG_R0), events

    cases = [(type_value, terminal, count, flags, app_id)
             for type_value in (0, 1, 2, 3)
             for terminal in (0, 1, 2)
             for count in (0, 1, 2, 3, 4)
             for flags in (0, 1, 2, 4, 7)
             for app_id in (0x1000, 0x9999)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"display current mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_CURRENT_SET_442456_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x442456..0x442521",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path), "source_complete": False,
              "flashable": False, "hardware_proof": False,
              "limits": ["Terminal predicate, logging, registry callback and PageManager enqueue are controlled lower boundaries; fixture rows cover four registration states."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt))


if __name__ == "__main__":
    main()
