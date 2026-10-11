#!/usr/bin/env python3
"""Stock startup platform-configure alias against selected source."""
import hashlib
import importlib.util
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location("bootv",ROOT/"g2/components/bootloader/update_core/verify.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
ALIAS=ROOT/"g2/components/bootloader/source_candidate_20261010/platform_configure_alias.c"
SOURCE=ROOT/"g2/components/bootloader/platform_startup/platform_startup.c"
ENTRY=0x41f846
BODY_SHA="dddf549840ff2c9a85c6cb5d9d613e8df8abb63de61f0fc46826f31a1787cb89"
ROWS=0x20000454
CONFIG=0x20032000
OBJECT=0x20032100


class Machine(v.Machine):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.apply_result=0

    def code(self,uc,pc,size,user):
        if pc in (0x422ba8,0x41d92c):
            r0,r1,r2,_=self.args()
            if pc==0x422ba8:
                self.events.append(["apply",r0,r1,r2])
                self.ret(self.apply_result)
            else:
                self.events.append(["register",r0,r1])
                self.ret(0x5678)
            return
        super().code(uc,pc,size,user)


def execute(machine,entry,selector,status):
    machine.apply_result=status
    for row in range(4):
        address=ROWS+row*28
        machine.w(address+4,OBJECT+row*16)
        machine.w(address+8,CONFIG+row*16)
        machine.cpu.mem_write(address+24,b"\xa5")
        for i,value in enumerate([10+row,20+row,30+row,40+row]):
            machine.w(CONFIG+row*16+i*4,value)
    machine.cpu.reg_write(v.a.UC_ARM_REG_R0,selector)
    machine.cpu.reg_write(v.a.UC_ARM_REG_R1,0x12345678)
    machine.cpu.reg_write(v.a.UC_ARM_REG_SP,v.SP)
    machine.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
    machine.cpu.emu_start(entry|1,v.STOP+2,count=500)
    assert machine.finished
    return {"r0":machine.cpu.reg_read(v.a.UC_ARM_REG_R0),
            "events":machine.events,
            "rows":bytes(machine.cpu.mem_read(ROWS,4*28)).hex(),
            "configs":bytes(machine.cpu.mem_read(CONFIG,4*16)).hex(),
            "sp":machine.cpu.reg_read(v.a.UC_ARM_REG_SP),
            "r4":machine.cpu.reg_read(v.a.UC_ARM_REG_R4),
            "r7":machine.cpu.reg_read(v.a.UC_ARM_REG_R7)}


def main():
    assert v.sha(v.BLOB)==v.SHA
    body=v.BLOB.read_bytes()[ENTRY-v.BASE:ENTRY-v.BASE+116]
    assert hashlib.sha256(body).hexdigest()==BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-platform-configure-alias-") as tmp:
        p=Path(tmp);objs=[p/"alias.o",p/"source.o"]
        for src,obj in zip([ALIAS,SOURCE],objs):
            subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m55",
                            "-mthumb","-mfloat-abi=soft","-ffreestanding",
                            "-fno-builtin","-std=c11","-O2","-fwrapv",
                            "-c",str(src),"-o",str(obj)],check=True)
        ld=p/"module.ld"
        ld.write_text("ENTRY(opencfw_provider_41f846)\n"
                      "opencfw_boot_control_power_apply = 0x422ba9;\n"
                      "opencfw_bl_power_register_update = 0x41d92d;\n"
                      "SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } "
                      "/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) } }\n")
        elf=p/"source.elf"
        subprocess.run(["arm-none-eabi-ld","-T",str(ld),*(str(o) for o in objs),
                        "-o",str(elf)],check=True,capture_output=True)
        _,segments,syms=v.elf.elf_info(elf)
        cases,trace=[],{}
        for selector,status in itertools.product(
                [0,1,2,3,4,5,0xff,0x100,0x101,0x103,0xffffffff],[0,1,7,0xffffffff]):
            original=Machine()
            source=Machine(True,segments,syms)
            a=execute(original,ENTRY,selector,status)
            b=execute(source,syms["opencfw_provider_41f846"],selector,status)
            assert a==b,(selector,status,a,b)
            trace.update(original.trace)
            cases.append([selector,status,a])
        visited={int(pc,16)+i for pc,raw in trace.items()
                 if ENTRY<=int(pc,16)<ENTRY+116
                 for i in range(len(bytes.fromhex(raw)))}
        assert visited==set(range(ENTRY,ENTRY+116))
        report={"status":"PASS","cases":len(cases),"original_image_sha256":v.SHA,
                "original_body_sha256":BODY_SHA,"original_body_visited_bytes":len(visited),
                "source_elf_sha256":v.sha(elf),"alias_sha256":v.sha(ALIAS),
                "comparisons":cases,"limits":["Power-apply and register-update lower calls are controlled cuts.",
                "The startup caller uses void(uint32_t); R0 comparison is additional status evidence, while incidental R1 is outside its ABI.",
                "Rows/configs are synthetic SRAM; physical power configuration is unverified."]}
        Path(__file__).with_name("platform-configure-alias-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","original_body_visited_bytes"]}))


if __name__=="__main__":main()
