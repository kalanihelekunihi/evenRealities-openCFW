#!/usr/bin/env python3
"""Manager publisher entry against locked stock and selected DFU context."""
import importlib.util
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/dfu_task"
spec = importlib.util.spec_from_file_location("context_verify", BASE / "verify_context.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ALIAS = ROOT / "g2/components/bootloader/source_candidate_20261010/dfu_send_alias.c"
SOURCE = BASE / "context.c"


def main():
    assert v.v.sha(v.v.BLOB) == v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-dfu-send-alias-") as tmp:
        p = Path(tmp)
        objects = [p / "alias.o", p / "context.o"]
        for source, obj in zip([ALIAS, SOURCE], objects):
            subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                            "-mthumb", "-mfloat-abi=soft", "-ffreestanding",
                            "-fno-builtin", "-std=c11", "-O2", "-fwrapv", "-c",
                            str(source), "-o", str(obj)], check=True)
        elf = p / "source.elf"
        subprocess.run(["arm-none-eabi-ld", "-T", str(BASE / "context_module.ld"),
                        *(str(obj) for obj in objects), "-o", str(elf)],
                       check=True, capture_output=True)
        _, segments, syms = v.v.elf.elf_info(elf)
        cases, trace = [], {}
        for queue, thread, status in itertools.product(
                [0, 0x62, 0xffffffff], [0, 0x63, 0xffffffff],
                [0, 1, 0xfffffffd, 0xfffffffc]):
            pair = [v.Machine(), v.Machine(True, segments, syms)]
            pair[1].symbols["opencfw_boot_dfu_send"] = syms["opencfw_provider_42dca2"]
            observed = []
            for m in pair:
                m.w(v.THREAD, thread)
                m.w(v.QUEUE, queue)
                m.put_status = status
                m.cpu.mem_write(v.MSG, bytes(range(40)))
                observed.append(m.invoke("dfu_send", [v.MSG]))
            assert observed[0] == observed[1], (queue, thread, status, observed)
            trace.update(pair[0].trace)
            cases.append({"queue": queue, "thread": thread,
                          "kernel_status": status, "observed": observed[0]})
        used = {int(pc, 0) + i for pc, raw in trace.items()
                for i in range(len(bytes.fromhex(raw)))}
        report = {"status": "PASS", "cases": len(cases),
                  "original_sha256": v.v.SHA, "source_elf_sha256": v.v.sha(elf),
                  "source_sha256": v.v.sha(SOURCE), "alias_sha256": v.v.sha(ALIAS),
                  "stock_entry": "0x42dca3", "distinct_original_trace_bytes": len(used),
                  "comparisons": cases,
                  "limits": ["Manager caller passes one 40-byte message pointer and ignores the 32-bit result; the verifier checks that result as additional evidence.",
                             "Queue put, notification set and logger are controlled cuts. No concurrent manager/DFU execution or physical device behavior is established."]}
        Path(__file__).with_name("dfu-send-alias-comparison.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({k: report[k] for k in ["status", "cases", "distinct_original_trace_bytes"]}))


if __name__ == "__main__":
    main()
