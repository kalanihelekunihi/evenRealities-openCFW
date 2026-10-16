#!/usr/bin/env python3
"""Compare Terminal row-bind lower-call decisions with pinned Apollo stock."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_row_bind_5ea564.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-row-bind-5ea564"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (
    ("audio_lv_child_44dce2", 0x44dce2, 2),
    ("audio_lv_label_create_499416", 0x499416, 1),
    ("audio_uart_page_43f09a", 0x43f09a, 3),
    ("audio_lv_width_43f506", 0x43f506, 2),
    ("audio_lv_label_mode_499678", 0x499678, 2),
    ("audio_lv_style_a_44145a", 0x44145a, 3),
    ("audio_lv_style_font_44143e", 0x44143e, 3),
    ("audio_terminal_item_spacing_5ea2c2", 0x5ea2c2, 0),
    ("audio_lv_style_spacing_44144c", 0x44144c, 3),
    ("audio_terminal_row_color_5ea2f2", 0x5ea2f2, 1),
    ("audio_lv_label_text_49942e", 0x49942e, 2),
    ("audio_lv_color_44104c", 0x44104c, 1),
    ("audio_lv_style_color_44140e", 0x44140e, 3),
    ("audio_lv_style_alpha_44142e", 0x44142e, 3),
    ("audio_lv_child_count_44ddea", 0x44ddea, 1),
    ("audio_terminal_row_image_5ea524", 0x5ea524, 2),
    ("audio_lv_image_create_498668", 0x498668, 1),
    ("audio_lv_image_source_498680", 0x498680, 2),
    ("audio_terminal_image_y_5ea2b0", 0x5ea2b0, 0),
    ("audio_lv_style_opa_441488", 0x441488, 3),
    ("audio_lv_delete_44d7b8", 0x44d7b8, 1),
)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5eadbc-0x438000:0x5eadc0-0x438000], "little") != 0x200746dc or \
            int.from_bytes(blob[0x5eb284-0x438000:0x5eb288-0x438000], "little") != 0x333333:
        raise RuntimeError("Apollo stock payload or row-bind literals changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "row-bind-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint32_t audio_uart_ring_primary_head_cell;\n" +
                    "\n".join(f"__attribute__((noinline,used)) uint32_t {name}"
                              "(uint32_t a,uint32_t b,uint32_t c)"
                              "{(void)a;(void)b;(void)c;return 0;}"
                              for name, _, _ in CALLS) + "\n")
    elf = OUT / "row-bind-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_row_bind_5ea564",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, parent_on, item_on, label_on, colored, count, source_on, image_on):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        font_cell = symbols["audio_uart_ring_primary_head_cell"] if compiled else 0x200746dc
        u.mem_write(font_cell, (0x619).to_bytes(4, "little"))
        cuts = {(symbols[name] if compiled else address) & ~1: index
                for index, (name, address, _) in enumerate(CALLS)}
        trace = []
        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            args = tuple(cpu.reg_read(reg) for reg in
                         (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            name, _, arity = CALLS[index]
            trace.append((name, args[:arity]))
            value = 0
            if name == "audio_lv_child_44dce2":
                value = 0x20006000 if args[1] == 0 and label_on else \
                        0x20007000 if args[1] == 1 and image_on else 0
            elif name == "audio_lv_label_create_499416":
                value = 0x20006000
            elif name == "audio_lv_child_count_44ddea":
                value = count
            elif name == "audio_terminal_row_color_5ea2f2":
                value = colored
            elif name == "audio_terminal_row_image_5ea524":
                value = 0x20009000 if source_on else 0
            elif name == "audio_lv_image_create_498668":
                value = 0x20007000
            elif name == "audio_lv_color_44104c":
                value = 0x20008000
            elif name == "audio_terminal_image_y_5ea2b0":
                value = 0x44
            elif name == "audio_terminal_item_spacing_5ea2c2":
                value = 4
            cpu.reg_write(A.UC_ARM_REG_R0, value)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, 0x20003000 if parent_on else 0)
        u.reg_write(A.UC_ARM_REG_R1, 0x20004000 if item_on else 0)
        u.reg_write(A.UC_ARM_REG_R2, 3)
        entry = symbols["audio_terminal_row_bind_5ea564"] if compiled else 0x5ea564
        u.emu_start(entry | 1, 0x600000, count=10000)
        return trace

    cases = 0
    for parent_on in (False, True):
        for item_on in (False, True):
            for label_on in (False, True):
                for colored in (0, 1):
                    for count in (1, 2):
                        for source_on in (False, True):
                            for image_on in (False, True):
                                stock = run(False, parent_on, item_on, label_on, colored,
                                            count, source_on, image_on)
                                selected = run(True, parent_on, item_on, label_on, colored,
                                               count, source_on, image_on)
                                if stock != selected:
                                    raise RuntimeError(f"row-bind mismatch {parent_on=} {item_on=} "
                                                       f"{label_on=} {colored=} {count=} "
                                                       f"{source_on=} {image_on=}: {stock} vs {selected}")
                                cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_ROW_BIND_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "row text/image branch decisions and ordered lower-call arguments",
              "limits": ["Lower-call effects, font global relocation and final placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()
