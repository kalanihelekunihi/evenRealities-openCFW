#!/usr/bin/env python3
"""Direct stock/C comparison of Conversate visible-position getter."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_tag_visible_index_5b0b58.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-conversate-tag-visible-5b0b58"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_lv_obj_y_44e498": (0x44e498, "scroll"),
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
    obj, elf_path = OUT / "tag-visible.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_tag_visible_index_5b0b58",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    *[f"--defsym={name}=0x{address:x}" for name, (address, _) in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, selected, index, scroll, flags):
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
        for offset, value in ((0x64, 0x20082000), (0x80, selected), (0x84, index)):
            cpu.mem_write(0x20071368 + offset, struct.pack("<I", value))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        kinds = {address: kind for address, kind in LOWERS.values()}
        events, done = [], [False]

        def cstr(address):
            out = bytearray()
            for i in range(180):
                byte = cpu.mem_read(address + i, 1)[0]
                if byte == 0:
                    return out.decode("utf-8", "replace")
                out.append(byte)
            raise RuntimeError("unterminated string")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = kinds.get(pc)
            if kind is None:
                return
            r0, r1, r2, r3 = (machine.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "scroll":
                events.append((kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0, scroll & 0xffffffff)
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                line, fmt = struct.unpack("<2I", machine.mem_read(sp, 8))
                values = struct.unpack("<2I", machine.mem_read(sp + 8, 8)) if line == 0x48 else ()
                events.append((kind, r0, cstr(r1), cstr(r2), cstr(r3), line,
                               cstr(fmt), *values))
            else:
                extra = struct.unpack("<I", machine.mem_read(sp, 4))[0] if r0 == 0x10800000 else None
                events.append((kind, r0, cstr(r1), cstr(r2),
                               r3 if extra is not None else None, extra))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b0b58 if native else symbols["audio_conversate_tag_visible_index_5b0b58"]
        cpu.emu_start(entry | 1, 0, count=400)
        if not done[0]:
            raise RuntimeError("visible index did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0)

    cases = [(selected, index, scroll, flags)
             for selected in (0, 0x20081000)
             for index in (0, 1, 17, 0xffffffff)
             for scroll in (-81, -40, -1, 0, 39, 40, 123)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"visible index mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_TAG_VISIBLE_INDEX_5B0B58_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b0b58..0x5b0c17",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LVGL scroll coordinate and logging calls are controlled lower boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt))


if __name__ == "__main__":
    main()
