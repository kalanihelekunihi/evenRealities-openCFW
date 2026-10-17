#!/usr/bin/env python3
"""Composed stock/C replay of timer-manager init and RAM clear."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_init_5b3cba.c"
CLEAR = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_clear_5b38cc.c"
LINKER = G2 / "analysis/c-source-completion-20261011/apollo/main_conversate_timer_mgr_ram_20261016.ld"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-timer-init-5b3cba"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_uart_device_role_get": (0x101010, 0x45a568, "role"),
          "audio_log_flags": (0x101020, 0x43d0ce, "flags"),
          "audio_log_extended": (0x101030, 0x43d574, "extended"),
          "audio_log_simple": (0x101040, 0x43ce9e, "simple")}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, clear_obj, elf_path = OUT / "oracle-init.o", OUT / "oracle-clear.o", OUT / "oracle-init.elf"
    for source, target in ((SOURCE, obj), (CLEAR, clear_obj)):
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                        str(source), "-o", str(target)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-T", str(LINKER), "-e",
                    "audio_conversate_timer_init_5b3cba",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), str(clear_obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
        section = elf.get_section_by_name(".g2_conversate_timer_mgr_ram_20073a3c")
        if section is None or section["sh_addr"] != 0x20073a3c or section["sh_size"] != 0x1c:
            raise RuntimeError("timer-manager RAM layout changed")

    def run(native, role, flags, fill):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data: cpu.mem_write(start, data)
        cpu.mem_write(0x20073a38, bytes([fill])*0x24)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}
        clear_pc = 0x5b38cc if native else symbols["audio_conversate_timer_clear_5b38cc"]&~1

        def word(addr):
            return struct.unpack("<I", cpu.mem_read(addr, 4))[0]

        def string(addr):
            return bytes(cpu.mem_read(addr, 160)).split(b"\0")[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            if pc == clear_pc:
                events.append(("clear",))
                return
            kind = names.get(pc)
            if kind is None: return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "role":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, role)
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), string(word(sp+4))))
            else:
                events.append((kind, r[0], string(r[1]), string(r[2])))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b3cba if native else symbols["audio_conversate_timer_init_5b3cba"])|1,
                      0, count=300)
        if not done[0]: raise RuntimeError(f"timer init did not return: {native, role, flags, fill}")
        return {"events": events, "ram": bytes(cpu.mem_read(0x20073a38, 0x24)).hex()}

    cases = [(role, flags, fill) for role in (0, 1, 2, 255)
             for flags in (0, 1, 2, 4, 7) for fill in (0, 0x5a, 0xff)]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b: raise RuntimeError(f"timer init mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_COMPOSED_MAIN_CONVERSATE_TIMER_INIT_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "clear_source": str(CLEAR.relative_to(ROOT)),
              "clear_source_sha256": hashlib.sha256(CLEAR.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Role and logger are controlled lower contracts.",
                         "Incidental return register is not compared."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True)+"\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
