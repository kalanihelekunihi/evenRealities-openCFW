#!/usr/bin/env python3
"""Compare LV object flag add/remove effects with the official Main body."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_flags_43ded4.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
FUNCTIONS = {"audio_uart_page_43ded4": (0x43ded4, 0x43dfa4),
             "audio_uart_page_43dfa4": (0x43dfa4, 0x43e046),
             "audio_uart_lv_obj_has_state_43e184": (0x43e184, 0x43e1be)}
OUT = G2 / "build/c-firmware/20261015/main-lv-obj-flags-43ded4"
OUT.mkdir(parents=True, exist_ok=True)
PROVIDERS = {
    "has_flag": (0x43e0e0, "audio_uart_lv_obj_has_flag_43e0e0"),
    "has_any": (0x43e11c, "audio_uart_lv_obj_has_flag_any_43e11c"),
    "positioned": (0x43f612, "audio_uart_lv_layout_positioned_43f612"),
    "invalidate": (0x440656, "audio_uart_page_invalidate_440656"),
    "group": (0x43e1be, "audio_uart_lv_obj_group_43e1be"),
    "update": (0x44d45c, "audio_uart_page_update_unbound_44d45c"),
    "active": (0x44d58c, "audio_uart_page_active_object_44d58c"),
    "parent": (0x44dca2, "audio_uart_lv_obj_parent_44dca2"),
    "mark": (0x43f648, "audio_uart_lv_mark_layout_43f648"),
    "areas": (0x44eb28, "audio_uart_lv_get_scrollbar_areas_44eb28"),
    "area_invalidate": (0x4405d4, "audio_uart_lv_invalidate_area_4405d4"),
}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text("#include <stdint.h>\n" + "\n".join(
        f'__attribute__((naked)) uint32_t {symbol}(void*a,uint32_t b,uint32_t c){{__asm volatile("bx lr");}}'
        for _, symbol in PROVIDERS.values()))
    elf = Path(temp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_43ded4",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def u32(v): return (v & 0xffffffff).to_bytes(4, "little")

    def run(compiled, name, config):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments: uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        obj = 0x20001000
        uc.mem_write(obj + 0x24, u32(config["initial_flags"]))
        uc.mem_write(obj + 0x28, config["state"].to_bytes(2, "little"))
        uc.reg_write(A.UC_ARM_REG_R0, obj)
        uc.reg_write(A.UC_ARM_REG_R1, config["mask"])
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {(symbols[symbol] & ~1 if compiled else address): key
                 for key, (address, symbol) in PROVIDERS.items()}
        trace, position_count = [], 0

        def observe(cpu, address, size, _):
            nonlocal position_count
            key = hooks.get(address)
            if key is None: return
            r0 = cpu.reg_read(A.UC_ARM_REG_R0)
            if key == "areas":
                cpu.mem_write(cpu.reg_read(A.UC_ARM_REG_R1), b"A" * 16)
                cpu.mem_write(cpu.reg_read(A.UC_ARM_REG_R2), b"B" * 16)
                trace.append((key, r0))
            elif key == "area_invalidate":
                trace.append((key, r0,
                              bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_R1), 16))))
            else:
                trace.append((key, r0))
            result = 0
            if key == "has_flag": result = config["has_flag"]
            elif key == "has_any": result = config["has_any"]
            elif key == "positioned":
                result = config["old_layout"] if position_count == 0 else config["new_layout"]
                position_count += 1
            elif key == "group": result = 0x20004000
            elif key == "active": result = 0x20003000
            elif key == "parent": result = 0x20002000
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        start = symbols[name] if compiled else FUNCTIONS[name][0]
        uc.emu_start(start | 1, 0x600000, count=1800)
        return trace, bytes(uc.mem_read(obj + 0x24, 6)), uc.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for name in FUNCTIONS:
        if name == "audio_uart_lv_obj_has_state_43e184":
            for state in (0, 1, 2, 3, 0xffff):
                for mask in (0, 1, 2, 4, 0xffff):
                    config = {"initial_flags": 0, "state": state,
                              "mask": mask, "has_flag": 0, "has_any": 0,
                              "old_layout": 0, "new_layout": 0}
                    native = run(False, name, config)
                    candidate = run(True, name, config)
                    if native != candidate:
                        raise AssertionError((name, config, native, candidate))
                    cases += 1
            continue
        for flags in (0, 1, 0x10, 0x11, 0x800000, 0x1000000, 0x1800000):
            for present in (0, 1):
                for old_layout, new_layout in ((0, 0), (0, 1), (1, 1)):
                    for state in (0, 2):
                        config = {"initial_flags": 0x01000011, "state": state,
                                  "mask": flags, "has_flag": present,
                                  "has_any": present, "old_layout": old_layout,
                                  "new_layout": new_layout}
                        native = run(False, name, config)
                        candidate = run(True, name, config)
                        if native[:2] != candidate[:2]:
                            raise AssertionError((name, config, native, candidate))
                        cases += 1

    receipt = {"status": "PASS_NATIVE_MAIN_LV_OBJ_FLAGS_43DED4",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": IMAGE_SHA,
               "native_body_sha256": {name: hashlib.sha256(
                   IMAGE[start-0x438000:end-0x438000]).hexdigest()
                   for name, (start, end) in FUNCTIONS.items()},
               "source_owned_symbols": sorted(FUNCTIONS), "cases": cases,
               "limits": ["Null-object fatal branches were outside the controlled cases; provider calls were hooks.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases, hashlib.sha256(path.read_bytes()).hexdigest())
