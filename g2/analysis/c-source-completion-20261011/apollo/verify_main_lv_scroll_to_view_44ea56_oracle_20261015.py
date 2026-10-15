#!/usr/bin/env python3
"""Compare Apollo LV scroll-to-view ancestor walk with stock."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_scroll_to_view_44ea56.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-scroll-to-view-44ea56"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWER = {"page": (0x43f66c, "audio_uart_page_43f66c"),
         "parent": (0x44dca2, "audio_uart_lv_obj_parent_44dca2"),
         "step": (0x44f40c, "audio_uart_lv_scroll_view_step_44f40c")}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        shim, elf = directory / "shim.c", directory / "view.elf"
        shim.write_text("#include <stdint.h>\nvoid audio_uart_page_43f66c(void*a){(void)a;}\nvoid*audio_uart_lv_obj_parent_44dca2(void*a){(void)a;return 0;}\nvoid audio_uart_lv_scroll_view_step_44f40c(void*a,void*b,void*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;}\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_scroll_to_view_44ea56",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        nodes = [0x20011000 + i * 0x1000 for i in range(4)]
        def run(compiled, case):
            depth, animation = case
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            for node in nodes: c.mem_write(node, bytes([0xa5]) * 0x60)
            targets = {(syms[name] if compiled else native) & ~1: kind
                       for kind, (native, name) in LOWER.items()}
            trace = []
            def hook(c, address, size, _):
                kind = targets.get(address)
                if kind is None: return
                r0, r1, r2, r3 = (c.reg_read(r) for r in
                                  (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                   A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                value = 0
                if kind == "page": trace.append((kind, r0))
                elif kind == "parent":
                    trace.append((kind, r0))
                    index = nodes.index(r0)
                    value = nodes[index + 1] if index < depth else 0
                else:
                    trace.append((kind, r0, r1, bytes(c.mem_read(r2, 8)), r3))
                    c.mem_write(r2, (0x1000 + len(trace)).to_bytes(4, "little") +
                                (0x2000 + len(trace)).to_bytes(4, "little"))
                c.reg_write(A.UC_ARM_REG_R0, value)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, nodes[0])
            c.reg_write(A.UC_ARM_REG_R1, animation)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            start = syms["audio_uart_lv_scroll_to_view_44ea56"] if compiled else 0x44ea56
            c.emu_start(start | 1, 0x600000, count=10000)
            return trace, bytes(c.mem_read(nodes[0], 0x40))
        cases = [(depth, animation) for depth in range(4)
                 for animation in (0, 1, 0x100, 0xffffffff)]
        for index, case in enumerate(cases):
            native, source = run(False, case), run(True, case)
            if native != source: raise AssertionError((index, case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_SCROLL_TO_VIEW_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x44ea56..0x44ea97", "cases": len(cases),
               "controlled_providers": sorted(LOWER),
               "limits": ["Acyclic parent chains and controlled scroll-step effects only; live layout and animation remain open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
