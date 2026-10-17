#!/usr/bin/env python3
"""Direct stock/C replay of Conversate expand scheduler and four callbacks."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_expand_animation_5b7704.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-expand-animation-5b7704"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLBACKS = {
    "audio_conversate_expand_width_5b7684": 0x5b7684,
    "audio_conversate_expand_height_5b76a4": 0x5b76a4,
    "audio_conversate_expand_x_5b76c4": 0x5b76c4,
    "audio_conversate_expand_y_5b76e4": 0x5b76e4,
}
LOWERS = {
    "audio_terminal_ui_object_valid_43e2ea": (0x101010, 0x43e2ea, "valid"),
    "audio_log_flags": (0x101020, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101030, 0x43d574, "extended"),
    "compressed_log_output": (0x101040, 0x43ce9e, "compact"),
    "audio_uart_lv_style_unlink_450500": (0x101050, 0x450500, "unlink"),
    "audio_uart_page_43f09a": (0x101060, 0x43f09a, "position"),
    "audio_uart_page_43f4c0": (0x101070, 0x43f4c0, "size"),
    "audio_uart_lv_anim_init_4503d6": (0x101080, 0x4503d6, "init"),
    "audio_uart_lv_anim_values_4506ce": (0x101090, 0x4506ce, "values"),
    "audio_uart_lv_anim_start_450408": (0x1010a0, 0x450408, "start"),
    "audio_uart_page_43f506": (0x1010b0, 0x43f506, "width"),
    "audio_uart_page_43f568": (0x1010c0, 0x43f568, "height"),
    "audio_uart_page_43f0e0": (0x1010d0, 0x43f0e0, "x"),
    "audio_uart_page_43f142": (0x1010e0, 0x43f142, "y"),
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
                    "audio_conversate_expand_animation_5b7704",
                    "--defsym=audio_uart_lv_anim_path_450672=0x450673",
                    *[f"--defsym={name}=0x{row[0]|1:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
    normalize = {symbols[name] | 1: native | 1 for name, native in CALLBACKS.items()}

    def run(native, entry_name, object_id, valid, config_present, duration,
            delay, completion, flags):
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
        cfg = bytearray(36)
        struct.pack_into("<HH", cfg, 0, duration, delay)
        for i, value in enumerate((11, 22, 33, 44, 55, 66, 77, 88)):
            struct.pack_into("<I", cfg, 4 + i * 4, value)
        cpu.mem_write(0x20002000, bytes(cfg))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3),
                              (object_id, (0x20002000 if config_present else 0)
                               if entry_name == "scheduler" else 0x89abcdef,
                               completion, 0x12345678)):
            cpu.reg_write(reg, value)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def cstr(machine, address):
            return bytes(machine.mem_read(address, 180)).split(b"\0", 1)[0]

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
            value = 0
            if kind == "valid":
                events.append((kind, r[0]))
                value = valid
            elif kind == "flags":
                events.append((kind,))
                value = flags
            elif kind == "extended":
                line, fmt = struct.unpack("<II", machine.mem_read(sp, 8))
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2]),
                               cstr(machine, r[3]), line, cstr(machine, fmt)))
            elif kind == "compact":
                events.append((kind, r[0], cstr(machine, r[1]), cstr(machine, r[2])))
            elif kind == "unlink":
                events.append((kind, r[0], (r[1] if native else normalize.get(r[1], r[1]))))
            elif kind in ("position", "size"):
                events.append((kind, r[0], r[1], r[2]))
            elif kind == "init":
                events.append((kind,))
                machine.mem_write(r[0], bytes(96))
                for off, item in ((0x30, 500), (0x2c, 100), (0x44, 1), (0x20, 0x450635)):
                    machine.mem_write(r[0] + off, struct.pack("<I", item))
                machine.mem_write(r[0] + 0x5c, b"\x10")
            elif kind == "values":
                events.append((kind, r[1], r[2]))
                for off, item in ((0x24, r[1]), (0x28, 0x80000000), (0x2c, r[2])):
                    machine.mem_write(r[0] + off, struct.pack("<I", item))
            elif kind == "start":
                words = list(struct.unpack("<24I", machine.mem_read(r[0], 96)))
                if not native:
                    words[1] = normalize.get(words[1], words[1])
                events.append((kind, words))
            else:
                events.append((kind, r[0], r[1]))
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        if entry_name == "scheduler":
            entry = 0x5b7704 if native else symbols["audio_conversate_expand_animation_5b7704"]
        else:
            entry = CALLBACKS[entry_name] if native else symbols[entry_name]
        cpu.emu_start(entry | 1, 0, count=700)
        if not done[0]:
            raise RuntimeError("expand routine did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0) if entry_name != "scheduler" else None

    cases = [(obj, valid, cfg, dur, delay, completion, flags)
             for obj in (0, 0x20001000)
             for valid in (0, 1)
             for cfg in (False, True)
             for dur in (0, 300)
             for delay in (0, 17)
             for completion in (0, 0x1010f1)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, selected = run(True, "scheduler", *case), run(False, "scheduler", *case)
        if stock != selected:
            raise RuntimeError(f"expand scheduler mismatch {case}: {stock} != {selected}")
    callback_cases = [(name, obj, valid)
                      for name in CALLBACKS
                      for obj in (0, 0x20001000)
                      for valid in (0, 1)]
    for name, obj, valid in callback_cases:
        case = (obj, valid, True, 300, 17, 0x1010f1, 0)
        stock, selected = run(True, name, *case), run(False, name, *case)
        if stock != selected:
            raise RuntimeError(f"expand callback mismatch {(name, obj, valid)}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_EXPAND_ANIMATION_5B7704_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases) + len(callback_cases),
              "native_bodies": ["0x5b7704..0x5b7901", "0x5b7684..0x5b7703"],
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["LVGL object, animation and log calls remain controlled lower boundaries.",
                         "Animation descriptor fields and callback addresses are compared at the start boundary."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
