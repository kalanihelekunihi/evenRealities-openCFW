#!/usr/bin/env python3
"""Compare Apollo display geometry and area copy with compiled C."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_flush_geometry_44fb4e.c"
OUT = G2 / "build/c-firmware/20261015/main-display-flush-geometry-44fb4e"
ENTRIES = {
    "copy": (0x439c04, "audio_uart_display_area_copy_439c04"),
    "current": (0x44fa1a, "audio_uart_display_current_44fa1a"),
    "width": (0x44fad2, "audio_uart_display_area_width_44fad2"),
    "height": (0x44fb10, "audio_uart_display_area_height_44fb10"),
    "x": (0x44fb4e, "audio_uart_display_area_x_44fb4e"),
    "y": (0x44fb9a, "audio_uart_display_area_y_44fb9a"),
    "ready": (0x44fc42, "audio_uart_display_flush_ready_44fc42"),
}
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    if int.from_bytes(blob[0x44fcf0-0x438000:0x44fcf4-0x438000], "little") != 0x2006f548:
        raise RuntimeError("LVGL display state literal changed")
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / "shim.c", Path(td) / "oracle.elf"
        shim.write_text("#include <stdint.h>\nuint8_t audio_uart_display_lv_state[512];\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_display_area_x_44fb4e",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, entry, mode, fields, fallback, current_present, copy_len=0, align=0):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            display, out, source = 0x20010000, 0x20011000 + align, 0x20012000 + align
            state = syms["audio_uart_display_lv_state"] if compiled else 0x2006f548
            u.mem_write(state + 0x14, (display if current_present else 0).to_bytes(4, "little"))
            u.mem_write(display + 0x2fc, bytes([mode]))
            for i, val in enumerate(fields):
                u.mem_write(display + 4 * i, (val & 0xffffffff).to_bytes(4, "little"))
            u.mem_write(display + 0x34, (fields[0] & 0xffffffff).to_bytes(4, "little"))
            u.mem_write(source, bytes((n * 17 + 3) & 0xff for n in range(80)))
            u.mem_write(out, bytes([0xcc]) * 80)
            if entry == "copy":
                u.reg_write(A.UC_ARM_REG_R0, out)
                u.reg_write(A.UC_ARM_REG_R1, source)
                u.reg_write(A.UC_ARM_REG_R2, copy_len)
            else:
                u.reg_write(A.UC_ARM_REG_R0, 0 if fallback else display)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            native, name = ENTRIES[entry]
            u.emu_start((syms[name] if compiled else native) | 1, 0x600000, count=100000)
            return (bytes(u.mem_read(out, 80)) if entry == "copy" else
                    u.reg_read(A.UC_ARM_REG_R0))
        cases = []
        field_sets = [(100, 80, 120, 90, 11, 13),
                      (100, 80, 0, 0, -4, 5),
                      (100, 80, -1, 1, 3, -7),
                      (0, 1, 2, 3, 0, 0)]
        for entry, mode, fields, fallback, present in itertools.product(
                ("current", "width", "height", "x", "y", "ready"),
                range(8), field_sets, (False, True), (False, True)):
            if (not fallback and not present) or (entry == "ready" and fallback): continue
            cases.append((entry, mode, fields, fallback, present, 0, 0))
        for length, align in itertools.product((0, 1, 2, 3, 7, 8, 15, 16, 17, 31, 32, 63), range(4)):
            cases.append(("copy", 0, field_sets[0], False, True, length, align))
        for case in cases:
            try:
                native, source = run(False, *case), run(True, *case)
            except Exception as error:
                raise RuntimeError((case, error)) from error
            if native != source: raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DISPLAY_FLUSH_GEOMETRY_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "cases": len(cases),
               "native_state_base": "0x2006f548",
               "native_spans": [hex(address) for address, _ in ENTRIES.values()],
               "limits": ["Area copy tested on disjoint buffers; invalid pointers and signed overflow omitted.",
                          "Display state initialization and live panel geometry remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()
