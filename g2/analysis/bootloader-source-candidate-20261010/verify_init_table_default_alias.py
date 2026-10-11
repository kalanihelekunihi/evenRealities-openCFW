#!/usr/bin/env python3
"""Compare startup's stock no-argument init-table entry through its alias."""
import hashlib
import importlib.util
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/init_table"
spec = importlib.util.spec_from_file_location("init_verify", BASE / "verify_init_table.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/init_table_default_alias.c"
OUT = Path(__file__).with_name("init-table-default-alias-comparison.json")


def main():
    assert v.v.sha(v.v.BLOB) == v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-init-alias-") as temporary:
        p = Path(temporary)
        sources = [ALIAS, BASE / "init_table.c", BASE / "qsort.c"]
        objects = [p / f"unit{i}.o" for i in range(len(sources))]
        for src, obj in zip(sources, objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                            "-mthumb", "-mfloat-abi=soft",
                            "-fshort-enums", "-ffreestanding", "-fno-builtin",
                            "-ffunction-sections", "-fdata-sections", "-std=c11",
                            "-O2", "-fwrapv", "-DNDEBUG", "-c", str(src),
                            "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T", str(BASE / "module.ld"),
                        "-e", "opencfw_provider_41f9f8", *(str(obj) for obj in objects),
                        "-o", str(elf)], check=True, capture_output=True)
        _, segments, symbols = v.v.elf.elf_info(elf)
        # Four stock table slots; vary priorities and null callbacks while
        # comparing callback order and exact sorted scratch records.
        callbacks = [0x4301D7, 0x43194D, 0x415591, 0x41FD71]
        fixtures = [[(callbacks[i], priority[i]) for i in range(4)]
                    for priority in [(1,1,25,26),(4,3,2,1),(0,0,0,0),
                                     (0xffffffff,0,7,2),(26,25,1,1)]]
        fixtures += [[(callbacks[0],2),(0,1),(callbacks[2],1),(callbacks[3],2)],
                     [(0,0),(0,1),(callbacks[2],2),(callbacks[3],3)]]
        rows, trace = [], {}
        for records in fixtures:
            raw = v.packed(records)
            stock = v.InitMachine()
            stock.cpu.mem_write(v.TABLE, raw)
            stock.run_entry(0x41f9f8, [])
            source = v.InitMachine(True, segments, symbols)
            source.cpu.mem_write(v.TABLE, raw)
            source.run_entry(symbols["opencfw_provider_41f9f8"], [])
            expected = bytes(stock.cpu.mem_read(v.SCRATCH, len(raw)))
            actual = bytes(source.cpu.mem_read(v.SCRATCH, len(raw)))
            assert stock.events == source.events and expected == actual, (records,stock.events,source.events)
            trace.update(stock.trace)
            rows.append({"records":records,"callbacks":stock.events,
                         "sorted_sha256":hashlib.sha256(expected).hexdigest()})
        used = {int(pc,16)+i for pc,raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status":"PASS", "cases":len(rows),
                  "original_image_sha256":v.v.SHA,
                  "original_entry":"0x41f9f9", "source_elf_sha256":v.v.sha(elf),
                  "alias_sha256":v.v.sha(ALIAS),
                  "distinct_original_trace_bytes":len(used),
                  "comparisons":rows,
                  "limits":["Comparison uses the prior compatible Cortex-M4 source build; the Cortex-M55 archive build is checked separately for compilation/linking but is not emulated here.",
                            "Callback bodies are synthetic cuts; order and sorted records are compared.",
                            "The fixed four-slot startup table is varied in emulated memory; hardware startup and full-image linking are unmeasured."]}
        OUT.write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","distinct_original_trace_bytes"]}))


if __name__ == "__main__": main()
