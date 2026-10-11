#!/usr/bin/env python3
"""Compare DFU panic's stock mask entry to selected byte-identical provider."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("mask", Path(__file__).with_name("verify_mask_interrupts_alias.py"))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ENTRY, BODY_SHA = v.ENTRY, v.BODY_SHA
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/dfu_panic_alias.c"
PROVIDER = v.PROVIDER


def main():
    assert v.v.sha(v.v.BLOB) == v.v.SHA
    body = v.v.BLOB.read_bytes()[ENTRY-v.v.BASE:ENTRY-v.v.BASE+22]
    assert hashlib.sha256(body).hexdigest() == BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-dfu-panic-alias-") as temporary:
        p = Path(temporary)
        objects = [p / "alias.o", p / "provider.o"]
        for src, obj in zip([ALIAS, PROVIDER], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                            "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                            "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                            "-fdata-sections", "-std=c11", "-O2", "-fwrapv", "-DNDEBUG",
                            "-c", str(src), "-o", str(obj)], check=True)
        section = p / "selected-mask.bin"
        subprocess.run(["arm-none-eabi-objcopy",
                        f"--dump-section=.text.opencfw_bl_mask_interrupts={section}",
                        str(objects[1])], check=True)
        assert section.read_bytes() == body
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x10000", "--gc-sections",
                        "-e", "opencfw_boot_dfu_panic", *(str(o) for o in objects),
                        "-o", str(elf)], check=True, capture_output=True)
        _, segments, symbols = v.v.elf.elf_info(elf)
        cases, visited = [], set()
        for basepri in [0, 16, 48, 0x80, 0xff]:
            for r0 in [0, 0xabcdef01]:
                for r1 in [0, 0x12345678]:
                    for r7 in [0, 0x87654321]:
                        r2 = 0x44556677
                        original = v.v.Machine()
                        stock = v.execute(original, ENTRY, basepri, r0, r1, r2, r7)
                        for pc, instruction in original.trace.items():
                            address = int(pc, 16)
                            if ENTRY <= address < ENTRY + 22:
                                visited.update(range(address, address+len(instruction)//2))
                        source = v.execute(v.v.Machine(True, segments, symbols),
                                           symbols["opencfw_boot_dfu_panic"] & ~1,
                                           basepri, r0, r1, r2, r7)
                        assert stock == source, (basepri, r0, r1, r7, stock, source)
                        cases.append([basepri, r0, r1, r7, stock])
        assert visited == set(range(ENTRY, ENTRY+22))
        report = {"status":"PASS", "cases":len(cases), "original_image_sha256":v.v.SHA,
                  "original_body_sha256":BODY_SHA, "selected_body_byte_identical":True,
                  "original_body_visited_bytes":len(visited), "source_elf_sha256":v.v.sha(elf),
                  "alias_sha256":v.v.sha(ALIAS), "cases_detail":cases,
                  "limits":"Unicorn BASEPRI/register comparison; physical interrupt delivery remains unmeasured."}
        Path(__file__).with_name("dfu-panic-alias-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","original_body_visited_bytes"]}))


if __name__ == "__main__": main()
