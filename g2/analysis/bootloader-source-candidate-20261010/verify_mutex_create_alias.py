#!/usr/bin/env python3
"""Initializer mutex-create alias versus stock constructor and selected source."""
import importlib.util
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"g2/components/bootloader/thread_creation"
spec=importlib.util.spec_from_file_location("resource_verify",BASE/"verify_resource_creators.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ALIAS=ROOT/"g2/components/bootloader/source_candidate_20261010/mutex_create_alias.c"
SOURCE=BASE/"resource_creators.c"


def main():
    assert v.v.sha(v.v.BLOB)==v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-mutex-create-alias-") as tmp:
        p=Path(tmp);objs=[p/"alias.o",p/"source.o"]
        for src,obj in zip([ALIAS,SOURCE],objs):
            subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4",
                            "-mthumb","-mfloat-abi=soft","-ffreestanding",
                            "-fno-builtin","-std=c11","-O2","-fwrapv",
                            "-c",str(src),"-o",str(obj)],check=True)
        elf=p/"source.elf"
        subprocess.run(["arm-none-eabi-ld","-T",str(BASE/"resource_creators_module.ld"),
                        *(str(o) for o in objs),"-o",str(elf)],
                       check=True,capture_output=True)
        _,segments,syms=v.v.elf.elf_info(elf)
        cases,trace=[],{}
        fixtures=[]
        for bits,cb,size,context in itertools.product(
                [0,1,8,9,0x100],[0,v.CB],[0,79,80],[0,1]):
            fixtures.append((v.ATTR,dict(cb=cb,size=size,context=context,bits=bits)))
        fixtures.append((0,dict(cb=0,size=0,context=0,bits=0)))
        for attr,fixture in fixtures:
            original=v.Machine()
            source=v.Machine(True,segments,syms)
            source.symbols["opencfw_boot_mutex_new"]=syms["opencfw_bl_mutex_create"]
            output=[]
            for m in [original,source]:
                m.context=fixture["context"]
                m.fail_alloc=False
                m.cpu.mem_write(v.CB,b"\xcc"*80)
                m.cpu.mem_write(v.POOL,b"\xcc"*512)
                for i,value in enumerate([0x433b50,fixture["bits"],fixture["cb"],fixture["size"]]):
                    m.w(v.ATTR+i*4,value)
                m.cpu.reg_write(v.v.a.UC_ARM_REG_R7,0x56789abc)
                result=m.run("mutex_new",[attr])
                output.append({"return":result["return"],"events":m.events,
                               "cb":bytes(m.cpu.mem_read(v.CB,80)).hex(),
                               "pool":bytes(m.cpu.mem_read(v.POOL,512)).hex()})
            assert output[0]==output[1],(attr,fixture,output)
            trace.update(original.trace)
            cases.append({"attribute":attr,"fixture":fixture,"observed":output[0]})
        used={int(pc,16)+i for pc,raw in trace.items()
              for i in range(len(bytes.fromhex(raw)))}
        report={"status":"PASS","cases":len(cases),
                "original_image_sha256":v.v.SHA,"source_elf_sha256":v.v.sha(elf),
                "alias_sha256":v.v.sha(ALIAS),
                "distinct_original_trace_bytes":len(used),"comparisons":cases,
                "limits":["Compatible M4 build is emulated; M55 archive compilation/linking and direct alias branch are checked separately.",
                          "Allocator, kernel queue creators/put and context guard are controlled cuts; wrapper/local constructor bytes execute.",
                          "Synthetic aligned storage and allocator success only; no scheduler ownership or physical mutex behavior is established."]}
        Path(__file__).with_name("mutex-create-alias-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","distinct_original_trace_bytes"]}))


if __name__=="__main__":main()
