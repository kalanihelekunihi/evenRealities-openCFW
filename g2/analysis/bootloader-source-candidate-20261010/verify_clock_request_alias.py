#!/usr/bin/env python3
"""Stock clock dispatcher versus NOR queue alias and selected source."""
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
ALIAS=ROOT/"g2/components/bootloader/source_candidate_20261010/clock_request_alias.c"
SOURCE=ROOT/"g2/components/bootloader/clock_manager/clock_manager.c"
ENTRY=0x4222f0
BODY_SHA="53cfb358989e68ae979d2814964a3e779ae0f0eba76836f99d409393d0e78d51"
CHILDREN={0:0x421a30,1:0x421a94,2:0x421bd2,3:0x421b08,
          4:0x421d5e,5:0x421eba,6:0x4220b2}


class Machine(v.Machine):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.child_source=(self.symbols.get("opencfw_bl_clock_request_id0",0)&~1)

    def code(self,uc,pc,size,user):
        if pc in CHILDREN.values() or (self.source and pc==self.child_source):
            clock=0 if self.source and pc==self.child_source else next(k for k,x in CHILDREN.items() if x==pc)
            arg=self.args()[0]
            self.events.append(["child",clock,arg])
            self.ret((0x100+clock*64+arg)&0xffffffff)
            return
        super().code(uc,pc,size,user)


def execute(machine,entry,clock,user):
    machine.cpu.reg_write(v.a.UC_ARM_REG_R0,clock)
    machine.cpu.reg_write(v.a.UC_ARM_REG_R1,user)
    machine.cpu.reg_write(v.a.UC_ARM_REG_R4,0x44556677)
    machine.cpu.reg_write(v.a.UC_ARM_REG_R7,0x76543210)
    machine.cpu.reg_write(v.a.UC_ARM_REG_SP,v.SP)
    machine.cpu.reg_write(v.a.UC_ARM_REG_LR,v.STOP|1)
    machine.cpu.emu_start(entry|1,v.STOP+2,count=100)
    assert machine.finished
    return {"r0":machine.cpu.reg_read(v.a.UC_ARM_REG_R0),
            "events":machine.events,
            "r4":machine.cpu.reg_read(v.a.UC_ARM_REG_R4),
            "r7":machine.cpu.reg_read(v.a.UC_ARM_REG_R7),
            "sp":machine.cpu.reg_read(v.a.UC_ARM_REG_SP)}


def main():
    assert v.sha(v.BLOB)==v.SHA
    body=v.BLOB.read_bytes()[ENTRY-v.BASE:ENTRY-v.BASE+116]
    assert hashlib.sha256(body).hexdigest()==BODY_SHA
    with tempfile.TemporaryDirectory(prefix="bootloader-clock-request-alias-") as tmp:
        p=Path(tmp);objs=[p/"alias.o",p/"source.o"]
        for src,obj in zip([ALIAS,SOURCE],objs):
            subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m55",
                            "-mthumb","-mfloat-abi=soft","-ffreestanding",
                            "-fno-builtin","-ffunction-sections","-fdata-sections",
                            "-std=c11","-O2","-fwrapv","-c",str(src),
                            "-o",str(obj)],check=True)
        ld=p/"module.ld"
        defs="".join(f"opencfw_bl_clock_request_id{k} = {address|1:#x};\n"
                     for k,address in CHILDREN.items() if k)
        ld.write_text("ENTRY(opencfw_bl_clock_request)\n"+defs+
                      "SECTIONS { . = 0x10000; .text : { *(.text*) } "
                      "/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) } }\n")
        elf=p/"source.elf"
        subprocess.run(["arm-none-eabi-ld","--gc-sections","-T",str(ld),
                        *(str(o) for o in objs),"-o",str(elf)],
                       check=True,capture_output=True)
        _,segments,syms=v.elf.elf_info(elf)
        cases,visited=[],set()
        for clock,user in itertools.product(
                list(range(1,8))+[0x101,0x106,0xff,0xffffffff],
                [0,1,0x10,0x38,0x39,0x3a,0xff,0x100,0x101,0x138,0xffffffff]):
            original=Machine()
            source=Machine(True,segments,syms)
            a=execute(original,ENTRY,clock,user)
            b=execute(source,syms["opencfw_bl_clock_request"],clock,user)
            assert a==b,(clock,user,a,b)
            for pc,raw in original.trace.items():
                address=int(pc,16)
                if ENTRY<=address<ENTRY+116:
                    visited.update(range(address,address+len(bytes.fromhex(raw))))
            cases.append([clock,user,a])
        assert len(visited)>=100
        report={"status":"PASS","cases":len(cases),
                "original_image_sha256":v.SHA,"original_body_sha256":BODY_SHA,
                "original_body_visited_bytes":len(visited),
                "source_elf_sha256":v.sha(elf),"alias_sha256":v.sha(ALIAS),
                "comparisons":cases,
                "limits":["Class-specific request children are controlled cuts at their exact entries; only dispatcher behavior and forwarded low-byte user are compared.",
                          "Class 0 is excluded from this alias comparison because the selected M55 compiler inlines its local child; the selected NOR caller uses class 4.",
                          "The NOR caller consumes R0 status. Incidental R1 is outside this caller ABI.",
                          "Clock-tree, peripheral timing and hardware behavior remain unverified."]}
        Path(__file__).with_name("clock-request-alias-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:report[k] for k in ["status","cases","original_body_visited_bytes"]}))


if __name__=="__main__":main()
