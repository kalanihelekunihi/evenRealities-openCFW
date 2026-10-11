#!/usr/bin/env python3
"""Per-caller stock/source comparisons for manager and DFU queue put."""
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"g2/components/bootloader/queue"
spec=importlib.util.spec_from_file_location("queue_verify",BASE/"verify_queue.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ALIAS=ROOT/"g2/components/bootloader/source_candidate_20261010/queue_put_aliases.c"
NAMES=["opencfw_provider_4168a2","opencfw_boot_dfu_queue_put"]


def main():
    assert v.v.sha(v.v.BLOB)==v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-queue-put-alias-") as tmp:
        p=Path(tmp);objs=[p/"alias.o",p/"queue.o"]
        for src,obj in zip([ALIAS,BASE/"queue_wrappers.c"],objs):
            subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m55",
                            "-mthumb","-mfloat-abi=soft","-ffreestanding",
                            "-fno-builtin","-std=c11","-O2","-fwrapv",
                            "-c",str(src),"-o",str(obj)],check=True)
        elf=p/"source.elf"
        subprocess.run(["arm-none-eabi-ld","-T",str(BASE/"module.ld"),
                        *(str(obj) for obj in objs),"-o",str(elf)],
                       check=True,capture_output=True)
        _,segments,syms=v.v.elf.elf_info(elf)
        rows,trace=[],{}
        fixtures=[]
        for mode in [0,1]:
            for result in [0,1]:
                for timeout in [0,9,0xffffffff]:
                    fixtures.append(([v.QUEUE,v.DATA,0xa5,timeout],
                                     {"ctx_mode":mode,"kernel_result":result,"woken":1}))
        fixtures += [([0,v.DATA,0,0],{}),([v.QUEUE,0,0,0],{}),
                     ([v.QUEUE,v.DATA,0,5],{"ctx_mode":1})]
        for alias in NAMES:
            assert alias in syms
            for args,fixture in fixtures:
                original=v.QueueMachine()
                source=v.QueueMachine(True,segments,syms)
                source.symbols["opencfw_boot_queue_put"]=syms[alias]
                a=original.invoke("queue_put",args,fixture)
                b=source.invoke("queue_put",args,fixture)
                keys=["return","events","icsr"]
                left={key:a[key] for key in keys};right={key:b[key] for key in keys}
                assert left==right,(alias,args,fixture,left,right)
                trace.update(original.trace)
                rows.append({"alias":alias,"arguments":args,"fixture":fixture,"observed":left})
        used={int(pc,16)+i for pc,raw in trace.items()
              for i in range(len(bytes.fromhex(raw)))}
        report={"status":"PASS","cases":len(rows),
                "per_alias":{name:sum(row["alias"]==name for row in rows) for name in NAMES},
                "original_image_sha256":v.v.SHA,"source_elf_sha256":v.v.sha(elf),
                "alias_sha256":v.v.sha(ALIAS),
                "distinct_original_trace_bytes":len(used),"comparisons":rows,
                "limits":["Kernel queue providers and runtime-mode query are controlled cuts.",
                          "ICSR is synthetic memory; actual task scheduling and queue ownership are unverified."]}
        Path(__file__).with_name("queue-put-alias-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","per_alias","distinct_original_trace_bytes"]}))


if __name__=="__main__":main()
