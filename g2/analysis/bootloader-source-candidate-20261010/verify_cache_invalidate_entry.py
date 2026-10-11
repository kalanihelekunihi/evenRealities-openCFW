#!/usr/bin/env python3
"""Stock 41e348 clock-mux cache call versus alias and selected C provider."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/platform_control"
spec = importlib.util.spec_from_file_location("cache_verify", BASE / "verify_cache_runtime.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/cache_invalidate_entry.c"
SOURCE = BASE / "cache_runtime.c"
OUT = Path(__file__).with_name("cache-invalidate-round79-comparison.json")


def main():
    assert v.sha(v.BLOB) == v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-cache-invalidate-") as temporary:
        p = Path(temporary)
        objects = [p / "alias.o", p / "source.o"]
        for src,obj in zip([ALIAS,SOURCE],objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                            "-mthumb", "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp",
                            "-fshort-enums", "-ffreestanding", "-fno-builtin",
                            "-ffunction-sections", "-fdata-sections", "-std=c11",
                            "-O2", "-fwrapv", "-DNDEBUG", "-c", str(src),
                            "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T", str(BASE / "cache_module.ld"),
                        "-e", "opencfw_cache_invalidate", *(str(o) for o in objects),
                        "-o", str(elf)], check=True, capture_output=True)
        _, segments, syms = v.elf.elf_info(elf)
        assert syms["opencfw_cache_invalidate"] != syms["opencfw_boot_cache_maintain"]
        syms["opencfw_boot_cache_maintain"] = syms["opencfw_cache_invalidate"]
        ranges = [None,(0x438000,0),(0x438000,1),(0x438000,32),
                  (0x438003,32),(0x43801f,33),(0xfffffff0,65),
                  (0,0xffffffff),(0,0x80000000)]
        cases,trace = [],{}
        for enabled in [0,1]:
            for descriptor in [0,(2<<13)|(1<<3),(0x200<<13)|(3<<3)]:
                for rg in ranges:
                    for op in [0,1,0x100,0x101,0xff]:
                        original=v.Machine(False,segments,syms)
                        source=v.Machine(True,segments,syms)
                        a=original.call(enabled,descriptor,rg,op)
                        b=source.call(enabled,descriptor,rg,op)
                        assert a==b,(enabled,descriptor,rg,op,a,b)
                        trace.update(original.trace)
                        cases.append([enabled,descriptor,rg,op,a])
        used={int(pc,16)+i for pc,raw in trace.items()
              for i in range(len(bytes.fromhex(raw)))}
        report={"status":"PASS","cases":len(cases),"original_image_sha256":v.SHA,
                "original_entry":"0x41e349","source_elf_sha256":v.sha(elf),
                "alias_sha256":v.sha(ALIAS),"source_sha256":v.sha(SOURCE),
                "distinct_original_trace_bytes":len(used),"comparisons":cases,
                "limits":["SCB cache registers are synthetic; writes and barrier order are compared.",
                          "Physical cache behavior, interrupt timing and full firmware link/layout remain unverified."]}
        OUT.write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","distinct_original_trace_bytes"]}))


if __name__=="__main__":main()
