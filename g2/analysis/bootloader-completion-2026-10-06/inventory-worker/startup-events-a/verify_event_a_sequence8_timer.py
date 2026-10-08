#!/usr/bin/env python3
"""Strict stock/source differential for selector 8's active TIMER_A branch."""
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
from unicorn import Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
IMAGE=ROOT/"g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
TABLE=ROOT/"g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/gx-native/scatter-selector-table.json"
IMAGE_SHA="f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
STOP=0x08000000
PROFILE=0x20026ba0

spec=importlib.util.spec_from_file_location(
    "elf_reader",ROOT/"g2/components/bootloader/update_core/elf_reader.py")
elf_reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf_reader)
ap=argparse.ArgumentParser()
ap.add_argument("--elf",type=Path,required=True)
ap.add_argument("--output",type=Path,required=True)
args=ap.parse_args()
blob=IMAGE.read_bytes()
assert hashlib.sha256(blob).hexdigest()==IMAGE_SHA
table=json.loads(TABLE.read_text())
assert table["status"]=="PASS" and table["original_sha256"]==IMAGE_SHA
slot8=table["selectors"][8]
assert slot8["selector"]==8 and int(slot8["thumb_target"],16)==0x428bb1
_,segments,symbols=elf_reader.elf_info(args.elf)
entry_name="event_a_transition_sequence_8_timer_native"
assert entry_name in symbols
source_entry=symbols[entry_name]&~1

def p32(x):return struct.pack("<I",int(x)&0xffffffff)
def put(u,address,value):u.mem_write(address,p32(value))

def seed(u,target,current,target_ton,old_ton,service_state,status_ready):
    info=bytearray(0x6c);struct.pack_into("<I",info,0,0x1f01600d)
    for i in range(21):
        vf=(0x21+37*i)&0x7f;core=(0x124+19*i)&0x3ff
        temp=(3+7*i)&0xf;vdc=(0x23+11*i)&0x7f
        struct.pack_into("<I",info,4+4*i,vf|(core<<7)|(temp<<17)|(vdc<<21))
    for offset,value in ((0x54,0x00123456),(0x58,0x000fedcb),
                         (0x5c,0x000abcde),(0x60,0x00013579),
                         (0x64,0x0a654321),(0x68,0x0002a135)):
        struct.pack_into("<I",info,offset,value)
    u.mem_write(PROFILE,bytes(info))
    put(u,0x400083e0,0x111)  # TIMERCONTROL enabled at bit 0
    put(u,0x40008064,0x40000000 if status_ready else 0) # status bit 30
    put(u,0x40008010,0x8000);put(u,0x40008068,0)
    put(u,0x40020344,0x01020304);put(u,0x40020354,0x00543210)
    put(u,0x40020358,0x87654321)
    put(u,0x40020044,0xa5000014);put(u,0x4002004c,0x5a000026)
    put(u,0x40020080,0x15550384);put(u,0x4002037c,0x82000000)
    put(u,0x40020344,0x01020304);put(u,0x40020358,0x87654321)
    put(u,0x40004044,0x1);put(u,0x40021000,0x2)
    put(u,0x20000154,current);u.mem_write(0x2000055a,bytes((service_state,)))
    for address,value in ((0x200270b0,0x19),(0x200270b4,0x2a),
                          (0x200270b8,0x155),(0x200270bc,0x7),
                          (0x200270c0,old_ton),(0x200270c4,current)):
        put(u,address,value)
    u.reg_write(a.UC_ARM_REG_R0,target);u.reg_write(a.UC_ARM_REG_R1,current)
    u.reg_write(a.UC_ARM_REG_R2,target_ton);u.reg_write(a.UC_ARM_REG_R3,old_ton)

def run(stock,case):
    target,current,target_ton,old_ton,service_state,status_ready=case
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo,size in ((0,0x1000),(0x410000,0x25000),(0x08000000,0x20000),
                    (0x10000,0x10000),(0x30000,0x80000),(0x20000000,0x40000),
                    (0x40000000,0x300000),(0xe0000000,0x200000),(0x47ff0000,0x10000)):
        u.mem_map(lo,size)
    if stock:u.mem_write(0x410000,blob)
    else:
        for seg in segments:u.mem_write(seg["address"],seg["data"])
    seed(u,target,current,target_ton,old_ton,service_state,status_ready)
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
    u.reg_write(a.UC_ARM_REG_PRIMASK,0)
    done=[False];delays=[];writes=[];trace={}
    def onwrite(cpu,access,address,size,value,_):
        if (address<0x20030000 or 0x40000000<=address<0x40300000 or
                0xe0000000<=address<0xe0020000):
            writes.append((address,size,value&((1<<(8*size))-1)))
    def oncode(cpu,pc,size,_):
        if pc==STOP:done[0]=True;cpu.emu_stop();return
        if pc==0x40:
            delays.append(cpu.reg_read(a.UC_ARM_REG_R0))
            cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
        if stock and 0x410000<=pc<0x435000:trace[pc]=bytes(cpu.mem_read(pc,size)).hex()
        if not stock and 0x410000<=pc<0x435000:
            raise AssertionError(("source reached locked code",hex(pc)))
    u.hook_add(UC_HOOK_CODE,oncode)
    u.hook_add(UC_HOOK_MEM_WRITE,onwrite,begin=0x20000000,end=0x2003ffff)
    u.hook_add(UC_HOOK_MEM_WRITE,onwrite,begin=0x40000000,end=0x402fffff)
    u.hook_add(UC_HOOK_MEM_WRITE,onwrite,begin=0xe0000000,end=0xe001ffff)
    entry=0x428bb0 if stock else source_entry
    try:u.emu_start(entry|1,0,count=300000)
    except UcError as exc:
        raise AssertionError(("sequence8 timer fault",stock,case,hex(u.reg_read(a.UC_ARM_REG_PC)),str(exc))) from exc
    assert done[0],("sequence8 failed to return",stock,case,hex(u.reg_read(a.UC_ARM_REG_PC)))
    return {"r0":u.reg_read(a.UC_ARM_REG_R0),"primask":u.reg_read(a.UC_ARM_REG_PRIMASK),
            "sp":u.reg_read(a.UC_ARM_REG_SP),"delays":delays,
            "writes":[[f"{addr:08x}",size,f"{value:0{size*2}x}"] for addr,size,value in writes],
            "trace":trace}

cases=[]
for target,current,target_ton,old_ton in ((3,7,6,1),(7,3,4,2),(12,9,2,5)):
    for state in (0x1a,2,7,26):
        for ready in (False,True):
            cases.append((target,current,target_ton,old_ton,state,ready))
comparisons=[]
for case in cases:
    stock=run(True,case);source=run(False,case)
    assert {k:v for k,v in stock.items() if k!="trace"}=={k:v for k,v in source.items() if k!="trace"},(case,stock,source)
    assert stock["trace"]
    comparisons.append({"case":case,"stock":{k:v for k,v in stock.items() if k!="trace"},
                        "source":{k:v for k,v in source.items() if k!="trace"},
                        "stock_instruction_count":len(stock["trace"])})
out={"status":"PASS","image_sha256":IMAGE_SHA,
     "source_elf_sha256":hashlib.sha256(args.elf.read_bytes()).hexdigest(),
     "runner_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
     "installed_selector8_target":"0x428bb1","cases":len(comparisons),
     "controlled_external_boundary":"resident ROM delay Thumb 0x41; capture input and return void",
     "comparisons":comparisons,
     "limits":["TIMERCONTROL bit 0 and status bit 30 are set from locked instruction shifts.",
               "RAM/MMIO state is deterministic; this does not claim physical timer timing.",
               "The source machine never executes locked image code."]}
args.output.write_text(json.dumps(out,indent=2)+"\n")
print("PASS selector 8 timer enabled",len(comparisons),"fixtures")
