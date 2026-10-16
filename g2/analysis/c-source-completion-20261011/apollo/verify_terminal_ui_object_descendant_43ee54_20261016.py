#!/usr/bin/env python3
"""Compare native/C recursive LVGL descendant checks on finite trees."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_object_descendant_43ee54.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-object-descendant-43ee54"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    elf = OUT / "object-descendant-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_ui_object_descendant_43ee54",
                    str(SOURCE), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, root_count, child_count, target_index, root_spec):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x200000)
        objects = [0x20090000+0x100*i for i in range(4)]
        specs = [0x200a0000+0x100*i for i in range(4)]
        arrays = [0x200b0000+0x100*i for i in range(4)]
        graph = [[objects[1], objects[2]][:root_count],
                 [objects[3]][:child_count], [], []]
        for i, obj in enumerate(objects):
            spec = specs[i] if (i != 0 or root_spec) else 0
            u.mem_write(obj+8, spec.to_bytes(4, "little"))
            u.mem_write(specs[i], arrays[i].to_bytes(4, "little"))
            u.mem_write(specs[i]+0x30, len(graph[i]).to_bytes(2, "little"))
            for j, child in enumerate(graph[i]):
                u.mem_write(arrays[i]+4*j, child.to_bytes(4, "little"))
        target = objects[target_index] if target_index < 4 else 0x2009f000
        u.reg_write(A.UC_ARM_REG_R0, objects[0])
        u.reg_write(A.UC_ARM_REG_R1, target)
        u.reg_write(A.UC_ARM_REG_SP, 0x201ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_terminal_ui_object_descendant_43ee54"] if compiled else 0x43ee54
        u.emu_start(entry|1, 0x600000, count=100000)
        return u.reg_read(A.UC_ARM_REG_R0)

    cases = 0
    for args in itertools.product((0, 1, 2), (0, 1), (0, 1, 2, 3, 4), (False, True)):
        stock, selected = run(False, *args), run(True, *args)
        if stock != selected:
            raise RuntimeError(f"descendant mismatch {args}: {stock} vs {selected}")
        cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_UI_OBJECT_DESCENDANT_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "null spec, 0-2 root children, nested child and all target positions",
              "limits": ["Cycles, malformed child pointers, concurrent LVGL mutation and hardware remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))


if __name__ == "__main__":
    main()
