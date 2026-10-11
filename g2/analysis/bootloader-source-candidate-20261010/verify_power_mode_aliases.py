#!/usr/bin/env python3
"""Stock mode-one/two caller aliases versus reviewed platform-control source."""
import importlib.util
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OLD=ROOT/"g2/analysis/bootloader-completion-2026-10-06/upstream-worker/platform-control-runtime"
spec=importlib.util.spec_from_file_location("mode_verify",OLD/"verify_runtime.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ALIAS=ROOT/"g2/components/bootloader/source_candidate_20261010/power_mode_aliases.c"


def main():
    assert v.sha(v.BLOB)==v.BLOB_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-power-mode-alias-") as tmp:
        p=Path(tmp)
        sources=[ALIAS,
                 ROOT/"g2/components/bootloader/platform_control/runtime.c",
                 ROOT/"g2/components/bootloader/platform_control/runtime_transition.c",
                 ROOT/"g2/components/bootloader/platform_control/runtime_query.c",
                 ROOT/"g2/components/bootloader/clock_manager/clock_class_providers.c",
                 OLD/"fixture_apply.c",
                 ROOT/"g2/components/bootloader/platform_control/critical_save.S"]
        objects=[p/f"unit{i}.o" for i in range(len(sources))]
        for src,obj in zip(sources,objects):
            subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m33",
                            "-mthumb","-mfloat-abi=soft","-ffreestanding","-fno-builtin",
                            "-std=c11","-O2","-fwrapv","-ffunction-sections",
                            "-fdata-sections","-c",str(src),"-o",str(obj)],check=True)
        elf=p/"source.elf"
        subprocess.run(["arm-none-eabi-ld","-T",str(OLD/"module.ld"),
                        *(str(obj) for obj in objects),"-o",str(elf)],
                       check=True,capture_output=True)
        _,segments,syms=v.elf_reader.elf_info(elf)
        cases,trace=[],{}
        for mode in [0,1,2,3,4,0x100,0x101,0x104,0xffffffff]:
            for primask in [0,1]:
                for kind in ["null","zero","wrong"] if (mode&0xff)<4 else ["zero"]:
                    original=v.Machine()
                    source=v.Machine(True,segments,syms)
                    source.entry=syms["opencfw_bl_post_record_initialized"]&~1
                    a=original.run(mode,primask,kind)
                    b=source.run(mode,primask,kind)
                    assert a==b,("mode_one",mode,primask,kind,a,b)
                    trace.update(original.trace)
                    cases.append({"alias":"opencfw_bl_post_record_initialized",
                                  "args":[mode,primask,kind],"observed":a})
        mode_two=[(1,0,3,0,False,0,False),(1,1,3,0,False,2,False),
                  (1,0,0,0,False,None,False),(1,0,3,1,False,0,False),
                  (2,2,3,0,True,0,False),(2,0,3,0,True,0,False),
                  (2,2,0,0,True,0,False),(2,2,3,2,False,None,False),
                  (2,2,3,0,False,0,False),(2,2,3,0,True,None,False),
                  (2,2,3,0,True,0,True),(1,1,3,0,False,1,False,1),
                  (0x102,2,3,0,True,0,False),(3,2,3,0,False,0,False)]
        for fixture in mode_two:
            original=v.Machine()
            source=v.Machine(True,segments,syms)
            source.mode_two_entry=syms["opencfw_provider_41ba80"]&~1
            a=original.run_mode_two(*fixture)
            b=source.run_mode_two(*fixture)
            assert a==b,("mode_two",fixture,a,b)
            trace.update(original.trace)
            cases.append({"alias":"opencfw_provider_41ba80","args":fixture,"observed":a})
        used={pc+i for pc,raw in trace.items() for i in range(len(raw))}
        report={"status":"PASS","cases":len(cases),
                "per_alias":{alias:sum(row["alias"]==alias for row in cases)
                             for alias in ["opencfw_bl_post_record_initialized","opencfw_provider_41ba80"]},
                "original_image_sha256":v.BLOB_SHA,"source_elf_sha256":v.sha(elf),
                "alias_sha256":v.sha(ALIAS),
                "visited_mode_one_bytes":len(used&set(range(0x41f8ba,0x41f91c))),
                "visited_mode_two_bytes":len(used&set(range(0x41ba80,0x41bae8))),
                "comparisons":cases,
                "limits":["Compatible Cortex-M33 source build is emulated; M55 archive compilation/linking is verified separately.",
                          "Accepted power-object configuration, elapsed delay and registered callbacks are controlled boundaries.",
                          "Synthetic RAM/MMIO mode state does not prove physical power transition or timing."]}
        Path(__file__).with_name("power-mode-alias-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","per_alias","visited_mode_one_bytes","visited_mode_two_bytes"]}))


if __name__=="__main__":main()
