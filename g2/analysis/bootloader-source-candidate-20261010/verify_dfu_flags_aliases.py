#!/usr/bin/env python3
"""DFU flag set/wait alias ABI against locked stock CMSIS wrappers."""
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"g2/components/bootloader/flags_runtime"
OLD=ROOT/"g2/analysis/bootloader-completion-2026-10-06/inventory-worker/flags-runtime/verify_cmsis_notifications.py"
spec=importlib.util.spec_from_file_location("flags_verify",OLD)
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ALIAS=ROOT/"g2/components/bootloader/source_candidate_20261010/dfu_flags_aliases.c"
NAMES={"cmsis_transfer":"opencfw_boot_dfu_flags_set",
       "cmsis_wait":"opencfw_boot_dfu_flags_wait"}


def main():
    assert v.v.sha(v.v.BLOB)==v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-dfu-flags-alias-") as tmp:
        p=Path(tmp)
        sources=[ALIAS,BASE/"flags_runtime.c",BASE/"cmsis_notifications.c"]
        objects=[p/f"unit{i}.o" for i in range(len(sources))]
        for src,obj in zip(sources,objects):
            subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4",
                            "-mthumb","-mfloat-abi=soft","-ffreestanding",
                            "-fno-builtin","-std=c11","-O2","-fwrapv",
                            "-c",str(src),"-o",str(obj)],check=True)
        elf=p/"source.elf"
        subprocess.run(["arm-none-eabi-ld","-T",str(BASE/"module.ld"),
                        *(str(obj) for obj in objects),"-o",str(elf)],
                       check=True,capture_output=True)
        _,segments,syms=v.v.elf.elf_info(elf)
        rows=[("cmsis_transfer",[v.THREAD,0x800000],{}),
              ("cmsis_transfer",[0,1],{}),
              ("cmsis_transfer",[v.THREAD,0x800000],{"context":1,"previous":0x800000}),
              ("cmsis_transfer",[v.THREAD,0x400000],{"context":1,"previous":0}),
              ("cmsis_wait",[0xffffff,0,60000,0],{"waits":[1],"outputs":[0x10],"ticks":[100]}),
              ("cmsis_wait",[3,1,0,0],{"waits":[1],"outputs":[1]}),
              ("cmsis_wait",[3,0,0,0],{"waits":[1],"outputs":[0]}),
              ("cmsis_wait",[3,0,15,0],{"waits":[0,1],"outputs":[0,2],"ticks":[100,104,115]}),
              ("cmsis_wait",[3,0,15,0],{"waits":[1],"outputs":[1],"ticks":[100]}),
              ("cmsis_wait",[0x80000000,0,5,0],{}),
              ("cmsis_wait",[3,0,5,0],{"context":1})]
        cases,trace=[],{}
        for name,args,fixture in rows:
            original=v.M()
            source=v.M(True,segments,syms)
            source.symbols["opencfw_boot_"+name]=syms[NAMES[name]]
            a=original.run_case(name,args,fixture)
            b=source.run_case(name,args,fixture)
            assert a==b,(name,args,fixture,a,b)
            trace.update(original.trace)
            cases.append({"alias":NAMES[name],"args":args,"fixture":fixture,"observed":a})
        used={int(pc,16)+i for pc,raw in trace.items()
              for i in range(len(bytes.fromhex(raw)))}
        report={"status":"PASS","cases":len(cases),
                "per_alias":{alias:sum(x["alias"]==alias for x in cases) for alias in NAMES.values()},
                "original_image_sha256":v.v.SHA,"source_elf_sha256":v.v.sha(elf),
                "alias_sha256":v.v.sha(ALIAS),
                "distinct_original_trace_bytes":len(used),"comparisons":cases,
                "limits":["Compatible M4 build is emulated; M55 archive compilation and direct branches are checked separately.",
                          "ISR notify, clock samples, wake results and thread notifications are controlled cuts; no live scheduling/tick unit proof.",
                          "Stock wait returns a 64-bit R0/R1 pair; both words are compared."]}
        Path(__file__).with_name("dfu-flags-alias-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","per_alias","distinct_original_trace_bytes"]}))


if __name__=="__main__":main()
