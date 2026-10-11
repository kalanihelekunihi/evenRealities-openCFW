#!/usr/bin/env python3
"""NOR mode-publish alias versus stock selector and selected source."""
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OLD=ROOT/"g2/analysis/bootloader-completion-2026-10-06/upstream-worker/mode-publisher"
spec=importlib.util.spec_from_file_location("publisher_verify",OLD/"verify_mode_publisher.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ALIAS=ROOT/"g2/components/bootloader/source_candidate_20261010/publish_device_mode_alias.c"
COMP=ROOT/"g2/components/bootloader/clock_manager"


def main():
    assert v.sha(v.v.BLOB)==v.v.SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-publish-device-alias-") as tmp:
        p=Path(tmp)
        sources=[ALIAS,COMP/"mode_publisher.c",COMP/"mode_publisher_abi.S",
                 COMP/"clock_class_providers.c"]
        objects=[p/f"unit{i}.o" for i in range(len(sources))]
        for src,obj in zip(sources,objects):
            subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4",
                            "-mthumb","-mfloat-abi=soft","-ffreestanding","-fno-builtin",
                            "-ffunction-sections","-fdata-sections","-std=c11","-O2",
                            "-c",str(src),"-o",str(obj)],check=True)
        elf=p/"source.elf"
        subprocess.run(["arm-none-eabi-ld","-T",str(OLD/"mode_publisher.ld"),
                        *(str(o) for o in objects),"-o",str(elf)],
                       check=True,capture_output=True)
        _,segments,syms=v.elf.elf_info(elf)
        assert syms["opencfw_publish_device_mode"]!=syms["opencfw_publish_mspi_mode"]
        entry=syms["opencfw_publish_device_mode"]
        original=v.Machine(False)
        source=v.Machine(True,segments,syms)
        source.symbols["opencfw_publish_mspi_mode"]=entry
        fixtures=[];seed=0x41fadc
        for module in (0,1):
            for mode in range(0x100):
                fixtures.append((module,mode,seed,(module+mode)&1));seed+=1
        for module in (2,3,4,0x100,0xffffffff):
            for mode in (0,1,4,6,0x10,0x100,0xffffffff):
                fixtures.append((module,mode,seed,seed&1));seed+=1
        # The selected NOR caller declares uint8_t mode; include explicit
        # upper-bit source tests only for the existing 32-bit core contract.
        for module,mode,case_seed,primask in fixtures:
            original.setup(module,mode,case_seed,primask)
            source.setup(module,mode,case_seed,primask)
            a=original.run();b=source.run()
            assert a==b,(module,mode,case_seed,a,b)
        used={int(pc,16)+i for pc,raw in original.trace.items()
              for i in range(len(bytes.fromhex(raw)))}
        report={"status":"PASS","cases":len(fixtures),
                "original_image_sha256":v.v.SHA,"source_elf_sha256":v.sha(elf),
                "alias_sha256":v.sha(ALIAS),"original_trace_bytes":len(used),
                "limits":["Compatible M4 build is emulated; M55 archive and direct branch are checked separately.",
                          "Stock selector and register updater execute; RAM values and power-register memory are synthetic.",
                          "The alias preserves saved-R7 R0 return, SP, callee-saved registers and PRIMASK; no physical MSPI mode is proved."]}
        Path(__file__).with_name("publish-device-mode-alias-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","original_trace_bytes"]}))


if __name__=="__main__":main()
