#!/usr/bin/env python3
"""Compare filesystem mutex aliases with stock wrappers and selected source."""
import importlib.util
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"g2/components/bootloader/queue"
spec=importlib.util.spec_from_file_location("mutex_verify",BASE/"verify_mutex.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ALIAS=ROOT/"g2/components/bootloader/source_candidate_20261010/fs_mutex_aliases.c"
NAMES={"mutex_acquire":"opencfw_boot_fs_mutex_acquire",
       "mutex_release":"opencfw_boot_fs_mutex_release"}


def main():
    assert v.v.sha(v.v.BLOB)==v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-fs-mutex-alias-") as tmp:
        p=Path(tmp)
        sources=[ALIAS]+[BASE/name for name in ["queue_wrappers.c","runtime_mode.c","mutex.c"]]
        objects=[p/f"unit{i}.o" for i in range(len(sources))]
        for src,obj in zip(sources,objects):
            subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4",
                            "-mthumb","-mfloat-abi=soft","-ffreestanding",
                            "-fno-builtin","-std=c11","-O2","-fwrapv",
                            "-c",str(src),"-o",str(obj)],check=True)
        elf=p/"source.elf"
        subprocess.run(["arm-none-eabi-ld","-T",str(BASE/"mutex_runtime_module.ld"),
                        *(str(obj) for obj in objects),"-o",str(elf)],
                       check=True,capture_output=True)
        _,segments,syms=v.v.elf.elf_info(elf)
        contexts=[(0,0,0),(0,1,0),(0,0,32),(1,1,32),(2,0,0),(2,1,32)]
        rows,trace=[],{}
        for name,alias in NAMES.items():
            assert alias in syms
            timeouts=[0,1000,0xffffffff] if name=="mutex_acquire" else [0]
            for handle,timeout,result,context in itertools.product(
                    [0,1,0x50,0x51],timeouts,[0,1,2],contexts):
                mode,primask,basepri=context
                pair=[v.Machine(),v.Machine(True,segments,syms)]
                pair[1].symbols["opencfw_boot_"+name]=syms[alias]
                output=[]
                for m in pair:
                    m.kernel_result=result
                    m.w(0x20027150,0 if mode==1 else 1)
                    m.w(0x2002716c,0 if mode==2 else 1)
                    m.cpu.reg_write(v.v.a.UC_ARM_REG_PRIMASK,primask)
                    m.cpu.reg_write(v.v.a.UC_ARM_REG_BASEPRI,basepri)
                    d=m.run(name,[handle,timeout])
                    output.append({"return":d["return"],"events":d["events"],
                                   "primask":m.cpu.reg_read(v.v.a.UC_ARM_REG_PRIMASK),
                                   "basepri":m.cpu.reg_read(v.v.a.UC_ARM_REG_BASEPRI)})
                assert output[0]==output[1],(alias,handle,timeout,result,context,output)
                trace.update(pair[0].trace)
                rows.append({"alias":alias,"handle":handle,"timeout":timeout,
                             "kernel_result":result,"context":context,"observed":output[0]})
        used={int(pc,16)+i for pc,raw in trace.items()
              for i in range(len(bytes.fromhex(raw)))}
        report={"status":"PASS","cases":len(rows),
                "per_alias":{alias:sum(row["alias"]==alias for row in rows)
                             for alias in NAMES.values()},
                "original_image_sha256":v.v.SHA,"source_elf_sha256":v.v.sha(elf),
                "alias_sha256":v.v.sha(ALIAS),
                "distinct_original_trace_bytes":len(used),"comparisons":rows,
                "limits":["The compatible Cortex-M4 build is emulated; M55 archive compilation/linking is checked separately because Unicorn rejects one M55 instruction.",
                          "Tagged/plain kernel mutex operations are synthetic cuts; context/runtime queries execute.",
                          "Nonzero IPSR, scheduling, ownership and blocking time remain unverified."]}
        Path(__file__).with_name("fs-mutex-alias-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","per_alias","distinct_original_trace_bytes"]}))


if __name__=="__main__":main()
