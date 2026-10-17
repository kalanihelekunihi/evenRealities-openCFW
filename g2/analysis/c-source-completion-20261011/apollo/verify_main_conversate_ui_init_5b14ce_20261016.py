#!/usr/bin/env python3
"""Bounded stock/C replay of Conversate UI root initialization."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_init_5b14ce.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-ui-init-5b14ce"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_page_43de82": (0x101010, 0x43de82, "create"),
    "audio_uart_page_43f4c0": (0x101020, 0x43f4c0, "size"),
    "audio_uart_page_43f09a": (0x101030, 0x43f09a, "position"),
    "audio_uart_page_44129e": (0x101040, 0x44129e, "style_a"),
    "audio_uart_page_44131c": (0x101050, 0x44131c, "style_b"),
    "audio_uart_page_44146a": (0x101060, 0x44146a, "style_c"),
    "audio_conversate_ui_style_5b0ac4": (0x101070, 0x5b0ac4, "style_d"),
    "audio_uart_page_43dfa4": (0x101080, 0x43dfa4, "flag"),
    "audio_conversate_timer_init_5b3cba": (0x101090, 0x5b3cba, "timer_init"),
    "audio_terminal_list_anim_init_58966c": (0x1010a0, 0x58966c, "anim_init"),
    "audio_log_flags": (0x1010b0, 0x43d0ce, "log_flags"),
    "audio_log_extended": (0x1010c0, 0x43d574, "extended"),
    "audio_log_simple": (0x1010d0, 0x43ce9e, "simple"),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    assert payload[0x5b1a0c-0x438000:0x5b1a10-0x438000] == (0x200743a0).to_bytes(4, "little")
    obj, elf_path = OUT / "oracle-init.o", OUT / "oracle-init.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_start_5b14ce",
                    "--defsym=audio_conversate_ui_app_id_200743a0=0x200743a0",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, parent, root, flags):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data: cpu.mem_write(start, data)
        cpu.mem_write(0x200743a0, struct.pack("<I", 0xaaaaaaaa))
        cpu.reg_write(A.UC_ARM_REG_R0, parent)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def word(addr):
            return struct.unpack("<I", cpu.mem_read(addr, 4))[0]

        def string(addr):
            return bytes(cpu.mem_read(addr, 160)).split(b"\0")[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None: return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "create":
                events.append((kind, r[0]))
                machine.reg_write(A.UC_ARM_REG_R0, root)
            elif kind in ("size", "position", "style_a", "style_b", "style_c", "style_d"):
                events.append((kind, *r[:3]))
            elif kind == "flag":
                events.append((kind, *r[:2]))
            elif kind == "log_flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), string(word(sp+4))))
            elif kind == "simple":
                events.append((kind, r[0], string(r[1]), string(r[2])))
            else:
                events.append((kind,))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b14ce if native else symbols["audio_conversate_ui_start_5b14ce"])|1,
                      0, count=350)
        if not done[0]: raise RuntimeError(f"UI init did not return: {native, parent, root, flags}")
        return {"events": events, "app_id": word(0x200743a0)}

    cases = [(parent, root, flags) for parent in (0, 0x1234, 0x20022000)
             for root in (0, 0x20031000, 0xdeadbeef)
             for flags in (0, 1, 2, 4, 7)]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b: raise RuntimeError(f"UI init mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_INIT_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LV objects, style, timer init, animation init and logger are controlled lower contracts.",
                         "Incidental return register is not compared."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True)+"\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
