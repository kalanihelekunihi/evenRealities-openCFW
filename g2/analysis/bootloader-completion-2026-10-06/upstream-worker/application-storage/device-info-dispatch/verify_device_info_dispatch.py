#!/usr/bin/env python3
"""Execute stock 0x41d792 and source dispatcher against synthetic MMIO."""
import argparse, hashlib, importlib.util, json, random, struct
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_READ
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
COMP = ROOT / "g2/components/bootloader/application_storage"
spec = importlib.util.spec_from_file_location("elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf = importlib.util.module_from_spec(spec); spec.loader.exec_module(elf)
spec = importlib.util.spec_from_file_location("bootv", ROOT / "g2/components/bootloader/update_core/verify.py")
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)

IMAGE_BASE, IMAGE, IMAGE_SHA = v.BASE, v.BLOB, v.SHA
STOP, SOURCE_WAIT, SOURCE_DELAY = 0x08000000, 0x08000280, 0x08000200
RECORD, STACK, SYS, POWER = 0x20001000, 0x2003f000, 0x40020014, 0x4002000c
OUT_BYTES = 64
STATUS_READS = {0x40020014}
DEBUG = (0xe00fefe0,0xe00fefe4,0xe00fefe8,0xe00fefec,
         0xe00feffc,0xe00feff8,0xe00feff4,0xe00feff0)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Machine:
    def __init__(self, source, segments, symbols):
        self.source, self.symbols = source, symbols
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.uc.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        self.uc.mem_map(IMAGE_BASE, 0x25000)
        self.exec_ranges=[]
        if source:
            for seg in segments:
                lo=seg['address'] & ~0xfff; hi=(seg['address']+seg['memory_size']+0xfff)&~0xfff
                if not (IMAGE_BASE <= lo < IMAGE_BASE+0x25000): self.uc.mem_map(lo,hi-lo)
                self.uc.mem_write(seg['address'],seg['data'])
                if seg['flags'] & 1: self.exec_ranges.append((seg['address'],seg['address']+len(seg['data'])))
        else:
            self.uc.mem_write(IMAGE_BASE,IMAGE.read_bytes())
            self.exec_ranges=[(IMAGE_BASE,IMAGE_BASE+IMAGE.stat().st_size)]
        self.uc.mem_map(0x20000000,0x40000); self.uc.mem_map(0x40020000,0x1000)
        self.uc.mem_map(0xe00f0000,0x10000); self.uc.mem_map(STOP,0x10000)
        self.trace={}; self.reads=[]; self.delays=[]; self.waits=[]; self.done=False
        self.uc.hook_add(UC_HOOK_CODE,self.code); self.uc.hook_add(UC_HOOK_MEM_READ,self.read)
    def read(self,uc,access,address,size,value,user):
        if address in (SYS,POWER) or address in DEBUG: self.reads.append([address,size])
    def code(self,uc,pc,size,user):
        if pc==STOP: self.done=True; uc.emu_stop(); return
        if (self.source and pc==SOURCE_DELAY) or (not self.source and pc==0x41f9e6):
            self.delays.append(uc.reg_read(a.UC_ARM_REG_R0)); self.ret(); return
        if (self.source and pc==SOURCE_WAIT) or (not self.source and pc==0x4213e6):
            r0,r1,r2,r3=[uc.reg_read(reg) for reg in (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3)]
            uc.mem_write(r3,struct.pack('<I',self.wait_value))
            self.waits.append([r0,r1,r2,self.wait_value])
            uc.reg_write(a.UC_ARM_REG_R0,self.wait_status); self.ret(); return
        if self.source:
            assert any(lo<=pc<hi for lo,hi in self.exec_ranges),("source escaped ELF",hex(pc))
        else:
            assert 0x430a60<=pc<0x430a9c or 0x41d69c<=pc<0x41d900 or 0x41d294<=pc<0x41d3e4 or 0x421548<=pc<0x42156e,("stock escaped scope",hex(pc))
            self.trace[hex(pc)]=bytes(uc.mem_read(pc,size)).hex()
    def ret(self): self.uc.reg_write(a.UC_ARM_REG_PC,self.uc.reg_read(a.UC_ARM_REG_LR))
    def setup(self,selector,sysword,debug,record=RECORD,power=0,wait_status=0,wait_value=0):
        self.done=False; self.trace.clear(); self.reads.clear(); self.delays.clear(); self.waits.clear()
        self.wait_status,self.wait_value=wait_status,wait_value
        self.record=record
        if record: self.uc.mem_write(record,b'\xcc'*OUT_BYTES)
        self.uc.mem_write(SYS,struct.pack('<I',sysword))
        self.uc.mem_write(POWER,struct.pack('<I',power))
        for addr,val in zip(DEBUG,debug): self.uc.mem_write(addr,struct.pack('<I',val))
        self.uc.reg_write(a.UC_ARM_REG_R0,selector); self.uc.reg_write(a.UC_ARM_REG_R1,record)
        self.uc.reg_write(a.UC_ARM_REG_SP,STACK); self.uc.reg_write(a.UC_ARM_REG_LR,STOP|1)
    def run(self,start=None):
        if start is None: start=0x41d792 if not self.source else self.symbols['opencfw_boot_device_info_query']&~1
        self.uc.emu_start(start|1,STOP+0x10000,count=100000)
        assert self.done,("did not return",hex(self.uc.reg_read(a.UC_ARM_REG_PC)))
        return dict(record=bytes(self.uc.mem_read(self.record,OUT_BYTES)).hex() if self.record else None,result=self.uc.reg_read(a.UC_ARM_REG_R0),reads=self.reads,delays=self.delays,waits=self.waits)

def main():
    p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    assert sha(IMAGE)==IMAGE_SHA
    _,segments,symbols=elf.elf_info(args.elf); image=IMAGE.read_bytes(); rng=random.Random(0x41d792)
    scenarios=[]
    for selector in [0,1,2,3,0x100,0x101,0x102,0x201,0xffffffff]:
        for mode in range(4):
            status=(rng.getrandbits(32)&~3)|mode
            scenarios.append((selector,status,[rng.getrandbits(32) for _ in DEBUG],0,0,rng.getrandbits(32)))
    scenarios.extend([(0,raw,[0]*len(DEBUG),0,0,7) for raw in [0,1,2,3,0xffffffff,0xaaaaaaaa,0x55555555]])
    scenarios.extend([(selector,0x12345678,[0]*len(DEBUG),0,0,0,0) for selector in [0,1,2,0x100,0x101]])
    for wait_status in [0,1,6]:
        for nibble in range(16):
            for wait_value in [0,1,2,3,254,255,256,0xffffffff]:
                scenarios.append((0,0x01000000,[rng.getrandbits(32) for _ in DEBUG],(2<<4)|nibble,wait_status,wait_value))
    details=[]; trace={}
    for index,item in enumerate(scenarios):
        selector,status,debug,power,wait_status,wait_value,*null_record=item
        record=0 if null_record else RECORD
        machines=[Machine(False,(),{}),Machine(True,segments,symbols)]
        # Source-side tables are supplied only by source ELF, not original image.
        src=machines[1]
        assert bytes(src.uc.mem_read(0x43401c,8))==image[0x43401c-IMAGE_BASE:0x43401c-IMAGE_BASE+8]
        assert bytes(src.uc.mem_read(0x433754,24))==image[0x433754-IMAGE_BASE:0x433754-IMAGE_BASE+24]
        for m in machines: m.setup(selector,status,debug,record,power,wait_status,wait_value)
        stock,source=(m.run() for m in machines)
        assert stock==source,(index,hex(selector),hex(status),{k:(stock[k],source[k]) for k in stock if stock[k]!=source[k]})
        if (selector&0xff)==1 and record: assert stock['delays']==[10]*10
        if (selector&0xff)==0 and record: assert stock['waits']==[[1,0x244,1,wait_value]]
        if not record: assert stock['result']==6
        if (selector&0xff) not in (0,1): assert stock['result']==6
        trace.update(machines[0].trace)
        details.append(dict(selector=selector,status=hex(status),power=hex(power),wait_status=wait_status,wait_value=wait_value,result=stock['result'],delay_calls=stock['delays'],wait_calls=len(stock['waits']),read_count=len(stock['reads'])))
    range_cases=[]
    limits=(0x100000,0x200000,0x300000,0x400000)
    for mode in range(4):
        for cached in [0,0x100000,0x200000,0x7fffff]:
            for address,size in [(0,1),(0x3fff,4),(0x4000,1),(0x4001,0),(0x4000,limits[mode]-1),(0x4000,limits[mode]),(0xffffffff,0xffffffff)]:
                status=(rng.getrandbits(32)&~0x0c)| (mode<<2)
                pair=[Machine(False,(),{}),Machine(True,segments,symbols)]
                for m in pair:
                    m.setup(1,status,[rng.getrandbits(32) for _ in DEBUG],RECORD)
                    m.uc.mem_write(0x200270c8,struct.pack('<I',cached))
                    m.uc.reg_write(a.UC_ARM_REG_R0,address);m.uc.reg_write(a.UC_ARM_REG_R1,size)
                original,source=pair
                got0=original.run(0x430a60);got1=source.run(symbols['opencfw_boot_storage_range_valid']&~1)
                assert got0['result']==got1['result']
                assert original.uc.mem_read(0x200270c8,4)==source.uc.mem_read(0x200270c8,4)
                assert got0['reads']==got1['reads'] and got0['delays']==got1['delays'],(mode,cached,address,size,got0,got1)
                trace.update(original.trace)
                range_cases.append(dict(mode=mode,cached=hex(cached),address=hex(address),size=hex(size),valid=got0['result'],resolved_limit=hex(struct.unpack('<I',original.uc.mem_read(0x200270c8,4))[0]),delay_calls=len(got0['delays'])))
    # The source selector gate and its own lower service cut are also tested
    # directly for all accepted/rejected selector bytes.
    wait_cases=[]
    for selector in [0,1,2,3,4,5,6,0x101,0x103,0x105,0xffffffff]:
        original,source=Machine(False,(),{}),Machine(True,segments,symbols)
        for m in (original,source):
            m.setup(0,0,[0]*len(DEBUG),RECORD,0,0,0xdeadbeef)
            m.uc.reg_write(a.UC_ARM_REG_R0,selector);m.uc.reg_write(a.UC_ARM_REG_R1,0x244)
            m.uc.reg_write(a.UC_ARM_REG_R2,1);m.uc.reg_write(a.UC_ARM_REG_R3,RECORD+0x30)
            m.uc.mem_write(RECORD+0x30,struct.pack('<I',0xa5a5a5a5))
        out0=original.run(0x421548);out1=source.run(symbols['opencfw_boot_device_mode_wait']&~1)
        assert out0==out1,("wait selector",hex(selector),out0,out1)
        wait_cases.append(dict(selector=selector,result=out0['result'],service_calls=len(out0['waits'])))
        trace.update(original.trace)
    tracked=[COMP/'device_info_dispatch.c',COMP/'device_info_dispatch.h',COMP/'device_info_mode0.c',COMP/'device_info_mode0.h',COMP/'device_mode_wait.c',COMP/'device_mode_wait.h',COMP/'device_info.c',COMP/'device_info.h',COMP/'storage_callbacks.c',COMP/'storage_callbacks.h',HERE/'device_info_dispatch.ld',HERE/'Makefile',HERE/'verify_device_info_dispatch.py']
    ibytes={int(pc,0)+off for pc,data in trace.items() for off in range(len(bytes.fromhex(data)))}
    report=dict(status='PASS',cases=len(scenarios),range_cache_cases=len(range_cases),wait_gate_cases=len(wait_cases),distinct_original_instruction_bytes=len(ibytes),original_sha256=IMAGE_SHA,source_elf_sha256=sha(args.elf),source_sha256={str(x.relative_to(ROOT)):sha(x) for x in tracked},functions={'stock':'0x41d792','source':hex(symbols['opencfw_boot_device_info_query']&~1),'mode0_stock':'0x41d69c','mode1_stock':'0x41d294','wait_gate_stock':'0x421548','source_wait_gate':hex(symbols['opencfw_boot_device_mode_wait']&~1),'stock_range_valid':'0x430a60','source_range_valid':hex(symbols['opencfw_boot_storage_range_valid']&~1)},cases_detail=details,range_cache_comparison=range_cases,wait_gate_comparison=wait_cases,limits=['Mode 0 helper 0x41d69c and selector gate 0x421548 are source reconstructed. The lower scheduler/event service at 0x4213e6 remains a callback that supplies status and result. The callback ABI and call arguments are compared.','Mode 1 invokes source helper 0x41d294 and compares the full 64-byte output, ordered MMIO reads, and ten delay callbacks. Delay callbacks are synthetic services.','The test also executes original 0x430a60 and source opencfw_boot_storage_range_valid on cache misses; both obtain the size limit through selector 1 and record word 11.','All MMIO/core-debug memory is synthetic Unicorn memory; no hardware behavior or timing is established.','This source ELF executes only its own text/data, with exact source-owned table bytes at 0x433754 and 0x43401c; no original executable fallback is permitted.'])
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','cases','distinct_original_instruction_bytes')},indent=2))
if __name__=='__main__': main()
