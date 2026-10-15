#!/usr/bin/env python3
"""Compare Apollo object class cleanup callback order with compiled C."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_delete_cleanup_44d16e.c"
OUT = G2 / "build/c-firmware/20261015/main-lv-obj-delete-cleanup-44d16e"
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    blob = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    digest = hashlib.sha256(blob).hexdigest()
    if digest != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo image changed")
    with tempfile.TemporaryDirectory() as td:
        elf = Path(td) / "oracle.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                        "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_obj_delete_cleanup_44d16e",
                        str(SOURCE), "-o", str(elf)], check=True)
        syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
            ["arm-none-eabi-nm", str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
        with elf.open("rb") as f:
            segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                        if s["p_type"] == "PT_LOAD"]
        def run(compiled, count, callbacks):
            u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
            u.mem_map(0x100000, 0x100000)
            for addr, data in segments: u.mem_write(addr, data)
            u.mem_map(0x20000000, 0x400000)
            obj = 0x20010000
            nodes = [0x20011000 + i * 0x100 for i in range(count)]
            callback = 0x20030001
            u.mem_write(obj, nodes[0].to_bytes(4, "little"))
            for i, node in enumerate(nodes):
                u.mem_write(node, (nodes[i + 1] if i + 1 < count else 0).to_bytes(4, "little"))
                u.mem_write(node + 8, (callback if callbacks & (1 << i) else 0).to_bytes(4, "little"))
            trace = []
            def hook(cpu, address, size, user):
                if address != (callback & ~1): return
                r0, r1 = cpu.reg_read(A.UC_ARM_REG_R0), cpu.reg_read(A.UC_ARM_REG_R1)
                if r0 not in nodes or r1 != obj: raise AssertionError((hex(r0), hex(r1)))
                trace.append(nodes.index(r0))
                cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
            u.hook_add(UC_HOOK_CODE, hook)
            u.reg_write(A.UC_ARM_REG_R0, obj)
            u.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
            u.reg_write(A.UC_ARM_REG_LR, 0x600001)
            u.emu_start((syms["audio_uart_lv_obj_delete_cleanup_44d16e"] if compiled else 0x44d16e) | 1,
                        0x600000, count=100000)
            return trace, int.from_bytes(u.mem_read(obj, 4), "little")
        cases = [(count, callbacks) for count in range(1, 5)
                 for callbacks in range(1 << count)]
        for case in cases:
            native, source = run(False, *case), run(True, *case)
            if native != source: raise AssertionError((case, native, source))
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LV_OBJ_DELETE_CLEANUP_ORACLE",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "official_payload_sha256": digest, "native_span": "0x44d16e..0x44d199",
               "cases": len(cases),
               "limits": ["Callbacks controlled and side-effect free; dynamic class mutation remains unproved.",
                          "No null-chain case because native routine dereferences its initial node."]}
    (OUT / "oracle.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases))

if __name__ == "__main__": main()
