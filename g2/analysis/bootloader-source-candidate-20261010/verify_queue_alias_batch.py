#!/usr/bin/env python3
"""Per-caller stock/source comparisons for four exact queue aliases."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "g2/components/bootloader/queue"
spec = importlib.util.spec_from_file_location("queue_verify", BASE / "verify_queue.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
SOURCES = [ROOT / "g2/components/bootloader/source_candidate_20261010" / name
           for name in ["queue_create_aliases.c","queue_get_aliases.c"]]
ALIASES = {"opencfw_provider_416816":"queue_create",
           "opencfw_boot_dfu_queue_new":"queue_create",
           "opencfw_provider_416920":"queue_get",
           "opencfw_boot_dfu_queue_get":"queue_get"}


def main():
    assert v.v.sha(v.v.BLOB)==v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-queue-alias-batch-") as tmp:
        p=Path(tmp)
        sources=SOURCES+[BASE/"queue_wrappers.c"]
        objects=[p/f"unit{i}.o" for i in range(len(sources))]
        for src,obj in zip(sources,objects):
            subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m55",
                            "-mthumb","-mfloat-abi=soft","-ffreestanding",
                            "-fno-builtin","-std=c11","-O2","-fwrapv",
                            "-c",str(src),"-o",str(obj)],check=True)
        elf=p/"source.elf"
        subprocess.run(["arm-none-eabi-ld","-T",str(BASE/"module.ld"),
                        *(str(obj) for obj in objects),"-o",str(elf)],
                       check=True,capture_output=True)
        _,segments,syms=v.v.elf.elf_info(elf)
        rows,trace=[],{}
        attrs=v.DATA+0x400
        create=[([3,8,0],{}),
                ([3,8,attrs],{"attrs":(v.DATA+0x100,0x50,v.DATA+0x200,24)}),
                ([3,8,attrs],{"attrs":(0,0,0,0)}),
                ([3,8,attrs],{"attrs":(v.DATA+0x100,0x4f,v.DATA+0x200,24)}),
                ([0,8,0],{}),([3,0,0],{}),([1,8,0],{"ctx_mode":1})]
        get=[]
        for mode in [0,1]:
            for result in [0,1]:
                for timeout in [0,9,0xffffffff]:
                    get.append(([v.QUEUE,v.DATA,v.DATA+0x300,timeout],
                                {"ctx_mode":mode,"kernel_result":result,
                                 "woken":1,"priority_initial":0xa5a5a5a5}))
        get += [([0,v.DATA,0,0],{}),([v.QUEUE,0,0,0],{}),
                ([v.QUEUE,v.DATA,0,5],{"ctx_mode":1})]
        for alias,name in ALIASES.items():
            assert alias in syms
            for args,fixture in create if name=="queue_create" else get:
                original=v.QueueMachine()
                source=v.QueueMachine(True,segments,syms)
                source.symbols["opencfw_boot_"+name]=syms[alias]
                left=original.invoke(name,args,fixture)
                right=source.invoke(name,args,fixture)
                keys=["return","events","icsr"]
                if name=="queue_get" and args[2]:keys.append("priority_out")
                a={key:left[key] for key in keys}
                b={key:right[key] for key in keys}
                assert a==b,(alias,args,fixture,a,b)
                trace.update(original.trace)
                rows.append({"alias":alias,"arguments":args,"fixture":fixture,"observed":a})
        used={int(pc,16)+i for pc,raw in trace.items()
              for i in range(len(bytes.fromhex(raw)))}
        per={alias:sum(row["alias"]==alias for row in rows) for alias in ALIASES}
        report={"status":"PASS","cases":len(rows),"per_alias":per,
                "original_image_sha256":v.v.SHA,
                "source_elf_sha256":v.v.sha(elf),
                "alias_sha256":{src.name:v.v.sha(src) for src in SOURCES},
                "distinct_original_trace_bytes":len(used),
                "comparisons":rows,
                "limits":["Kernel queue providers and runtime-mode query use deterministic controlled cuts.",
                          "ICSR is synthetic memory; physical scheduling, queue ownership and interrupt delivery are unmeasured."]}
        Path(__file__).with_name("queue-alias-batch-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","per_alias","distinct_original_trace_bytes"]}))


if __name__=="__main__":main()
