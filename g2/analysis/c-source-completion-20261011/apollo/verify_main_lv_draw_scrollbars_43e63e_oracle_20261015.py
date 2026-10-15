#!/usr/bin/env python3
"""Compare Apollo LV event scrollbar drawing wrapper with stock."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_scrollbars_43e63e.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-draw-scrollbars-43e63e"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWER = {"areas": (0x44eb28, "audio_uart_lv_get_scrollbar_areas_44eb28"),
         "size": (0x450b80, "audio_uart_lv_area_size_450b80"),
         "descriptor": (0x43e6a6, "audio_uart_lv_scrollbar_draw_descriptor_43e6a6"),
         "draw": (0x451c6e, "audio_uart_lv_draw_task_render_451c6e")}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        shim, elf = directory / "shim.c", directory / "scrollbars.elf"
        shim.write_text("#include <stdint.h>\n" + "\n".join(
            f"uint32_t {name}(void){{return 0;}}" for _, name in LOWER.values()) + "\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_draw_scrollbars_43e63e",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, case):
            first_size, second_size, descriptor = case
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            obj_addr, layer = 0x20011000, 0x20012000
            c.mem_write(obj_addr, bytes([0xa5]) * 0x40)
            targets = {(syms[name] if compiled else address) & ~1: kind
                       for kind, (address, name) in LOWER.items()}
            trace = []
            def hook(c, address, size, _):
                kind = targets.get(address)
                if kind is None: return
                r0, r1, r2 = (c.reg_read(r) for r in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                value = 0
                if kind == "areas":
                    trace.append((kind, r0))
                    c.mem_write(r1, bytes([0x11]) * 16)
                    c.mem_write(r2, bytes([0x22]) * 16)
                elif kind == "size":
                    area = bytes(c.mem_read(r0, 16))
                    trace.append((kind, area))
                    value = first_size if area[0] == 0x11 else second_size
                elif kind == "descriptor":
                    trace.append((kind, r0))
                    c.mem_write(r1, bytes((i * 3 + 7) & 0xff for i in range(0x70)))
                    value = descriptor
                else:
                    trace.append((kind, r0, bytes(c.mem_read(r1, 0x70)),
                                  bytes(c.mem_read(r2, 16))))
                c.reg_write(A.UC_ARM_REG_R0, value)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, obj_addr)
            c.reg_write(A.UC_ARM_REG_R1, layer)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms["audio_uart_lv_draw_scrollbars_43e63e"] if compiled else 0x43e63e
            c.emu_start(start | 1, 0x600000, count=10000)
            return trace, bytes(c.mem_read(obj_addr, 0x40))
        cases = [(first, second, descriptor) for first in (0, 1)
                 for second in (0, 1) for descriptor in (0, 1, 2, 0x101)]
        for index, case in enumerate(cases):
            native, source = run(False, case), run(True, case)
            if native != source: raise AssertionError((index, case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_DRAW_SCROLLBARS_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x43e63e..0x43e6a5", "cases": len(cases),
               "controlled_providers": sorted(LOWER),
               "limits": ["Scrollbar areas, descriptor and draw calls are controlled; live rendering remains open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
