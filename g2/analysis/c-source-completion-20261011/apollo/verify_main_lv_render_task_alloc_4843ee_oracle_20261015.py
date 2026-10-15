#!/usr/bin/env python3
"""Compare successful render-task allocation and queue insertion with stock Main."""
import hashlib, json, subprocess, tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_render_task_alloc_4843ee.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-render-task-alloc-4843ee"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SHIM = "#include <stdint.h>\nvoid *audio_uart_lv_heap_alloc(uint32_t n){return 0;}\n"

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PAYLOAD_SHA: raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        elf, shim = Path(directory) / "test.elf", Path(directory) / "shim.c"
        shim.write_text(SHIM)
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_render_task_alloc_4843ee",
                        str(SOURCE), str(shim), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
            if len(p := line.split()) == 3}
        with elf.open("rb") as stream:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(stream).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, chain, fill):
            c = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            c.mem_map(0x400000, 0x400000); c.mem_write(0x438000, blob)
            c.mem_map(0x100000, 0x100000)
            for address, data in segments: c.mem_write(address, data)
            c.mem_map(0x20000000, 0x400000)
            layer, area, task, node1, node2 = (0x20010000, 0x20011000, 0x20012000,
                                               0x20013000, 0x20014000)
            l = bytearray([fill] * 0x60)
            l[0x18:0x28] = bytes(range(0x40, 0x50))
            l[0x44:0x48] = (node1 if chain else 0).to_bytes(4, "little")
            c.mem_write(layer, bytes(l))
            c.mem_write(area, bytes(range(0x10, 0x20)))
            c.mem_write(task, bytes(0x5c))
            c.mem_write(node1, (node2 if chain == 2 else 0).to_bytes(4, "little") + bytes(0x58))
            c.mem_write(node2, bytes(0x5c))
            cut = (syms["audio_uart_lv_heap_alloc"] & ~1) if compiled else 0x44f730
            calls = []
            def hook(cpu, address, size, unused):
                if address != cut: return
                calls.append(cpu.reg_read(A.UC_ARM_REG_R0))
                cpu.reg_write(A.UC_ARM_REG_R0, task)
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            c.hook_add(UC_HOOK_CODE, hook)
            c.reg_write(A.UC_ARM_REG_R0, layer)
            c.reg_write(A.UC_ARM_REG_R1, area)
            c.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            c.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = syms["audio_uart_lv_render_task_alloc_4843ee"] if compiled else 0x4843ee
            c.emu_start(entry | 1, 0x600000, count=20000)
            return (c.reg_read(A.UC_ARM_REG_R0), calls,
                    bytes(c.mem_read(layer, 0x60)), bytes(c.mem_read(task, 0x5c)),
                    bytes(c.mem_read(node1, 0x5c)), bytes(c.mem_read(node2, 0x5c)))
        suite = [(chain, fill) for chain in (0, 1, 2) for fill in (0, 0xa5, 0xff)]
        for case in suite:
            native, source = run(False, *case), run(True, *case)
            if native != source:
                raise AssertionError((case, native[:2], source[:2],
                                      [a == b for a, b in zip(native[2:], source[2:])]))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_ALLOC_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": PAYLOAD_SHA,
               "native_span": "0x4843ee..0x484475", "cases": len(suite),
               "limits": ["Allocator return is controlled; successful zeroed allocations and list insertion compared.",
                          "Allocation failure logger and fatal loop were not executed."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(suite), sha(OUT / "oracle.json"))

if __name__ == "__main__": main()
