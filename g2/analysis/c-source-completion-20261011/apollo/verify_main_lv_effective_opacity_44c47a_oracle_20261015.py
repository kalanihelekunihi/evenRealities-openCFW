#!/usr/bin/env python3
"""Compare Apollo LV style opacity and effective parent-chain opacity with stock."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_effective_opacity_44c47a.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-effective-opacity-44c47a"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        shim, elf = directory / "shim.c", directory / "opacity.elf"
        shim.write_text("#include <stdint.h>\nuint32_t audio_uart_lv_style_property_44bdea(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}\nvoid*audio_uart_lv_obj_parent_44dca2(void*a){(void)a;return 0;}\n")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_effective_opacity_44c47a",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        nodes = (0x20011000, 0x20012000, 0x20013000)
        patterns = ((0, 255, 255, 255), (2, 255, 255, 255),
                    (3, 255, 255, 255), (128, 255, 255, 255),
                    (252, 128, 255, 255), (253, 252, 128, 255),
                    (255, 255, 2, 255), (255, 255, 255, 0),
                    (255, 255, 255, 255))
        def run(compiled, case):
            kind, selector, depth, initial, self0, parent1, parent2 = case
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            for node in nodes: c.mem_write(node, bytes([0xa5]) * 0x40)
            if kind == "accessor":
                targets = {(syms["audio_uart_lv_style_property_44bdea"] if compiled
                            else 0x44bdea) & ~1: "style"}
            else:
                targets = {(syms["audio_uart_lv_style_property_44bdea"] if compiled
                            else 0x44b8b8) & ~1: "opacity",
                           (syms["audio_uart_lv_obj_parent_44dca2"] if compiled
                            else 0x44dca2) & ~1: "parent"}
            trace = []
            def hook(c, address, size, _):
                op = targets.get(address)
                if op is None: return
                r0, r1, r2 = (c.reg_read(r) for r in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                if op == "style":
                    trace.append((op, r0, r1, r2)); value = initial
                elif op == "opacity":
                    trace.append((op, r0, r1))
                    value = initial if r1 != 0 else {nodes[0]: self0,
                                                       nodes[1]: parent1,
                                                       nodes[2]: parent2}[r0]
                else:
                    trace.append((op, r0))
                    index = nodes.index(r0)
                    value = nodes[index + 1] if index < depth else 0
                c.reg_write(A.UC_ARM_REG_R0, value & 0xffffffff)
                c.reg_write(A.UC_ARM_REG_PC, c.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, nodes[0])
            c.reg_write(A.UC_ARM_REG_R1, selector)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            name = ("audio_uart_lv_style_opacity_44b8b8" if kind == "accessor"
                    else "audio_uart_lv_effective_opacity_44c47a")
            start = syms[name] if compiled else (0x44b8b8 if kind == "accessor" else 0x44c47a)
            c.emu_start(start | 1, 0x600000, count=10000)
            return c.reg_read(A.UC_ARM_REG_R0), trace
        cases = [("accessor", selector, 0, value, value, 255, 255)
                 for selector in (0, 0x10000)
                 for value in (0, 2, 3, 128, 252, 253, 255, 0x100)]
        cases += [("effective", selector, depth, *pattern)
                  for selector in (0, 0x10000) for depth in range(3)
                  for pattern in patterns]
        for index, case in enumerate(cases):
            native, source = run(False, case), run(True, case)
            if native != source: raise AssertionError((index, case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_EFFECTIVE_OPACITY_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_spans": ["0x44b8b8", "0x44c47a"], "cases": len(cases),
               "limits": ["Acyclic parent chains and controlled style values only; live theme mutation remains open."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
