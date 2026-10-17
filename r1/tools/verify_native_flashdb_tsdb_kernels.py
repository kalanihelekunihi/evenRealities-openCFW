#!/usr/bin/env python3
"""Compare pinned upstream C helpers with authenticated native typed contracts."""
import hashlib,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'r1/research/source-build/native-flashdb-tsdb-kernels'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FUNCS=[('get_next_sector_addr',0x6a194),('get_last_sector_addr',0x6a158),('get_next_tsl_addr',0x6a1b2),('get_last_tsl_addr',0x6a176),('query_count_cb',0x87428)]
def main():
 obj=OUT/'native_flashdb_tsdb_kernels.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
 assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 rng=random.Random(0x63694);digest=hashlib.sha256();counts={};raw={}
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS { . = 0x1000000; .text : { *(.text*) } }')
  elf=td/'kernels.elf';binary=td/'kernels.bin'
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True)
  subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);machines.append(u)
  regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  edge=[0,1,2,3,31,32,79,80,111,112,0x7fffffff,0x80000000,0xffffffe0,0xffffffff]
  for name,native in FUNCS:
   counts[name]=0;raw[name]=0
   for i in range(10000):
    values=[edge[(i//(len(edge)**j))%len(edge)] if i<2744 else rng.getrandbits(32) for j in range(4)]
    mem=bytearray(b'\xa5'*512);a,b,c,d=values
    struct.pack_into('<II',mem,12,a,b);struct.pack_into('<I',mem,128+4,c);struct.pack_into('<I',mem,128+20,d);mem[129]=i%256;struct.pack_into('<I',mem,256+12,b)
    if 'sector' in name:args=[0x20010000,0x20010080,d,0x98765432]
    elif 'tsl' in name:args=[0x20010080,0x20010100,0xabcdef01,0x98765432]
    else:
     mem[128]=i%256;mem[256]=(i//256)%256;struct.pack_into('<I',mem,260,a);args=[0x20010080,0x20010100,0xabcdef01,0x98765432]
    results=[]
    for side,u in enumerate(machines):
     u.mem_write(0x20010000,bytes(mem));u.mem_write(0x2003cf00,b'\x96'*512)
     for reg,v in zip(regs,args):u.reg_write(reg,v)
     for j,reg in enumerate(saved):u.reg_write(reg,0x12340000+j)
     u.reg_write(UC_ARM_REG_SP,0x2003d000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     u.emu_start((syms['r1_fdb_'+name] if side else native)|1,0x20000100,count=1000)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003d000
     assert [u.reg_read(r) for r in saved]==[0x12340000+j for j in range(8)]
     results.append(([u.reg_read(r) for r in regs],bytes(u.mem_read(0x20010000,512))))
    assert results[0][0][0]==results[1][0][0] and results[0][1]==results[1][1],(name,i,values)
    raw[name]+=results[0][0]!=results[1][0];counts[name]+=1
    digest.update(json.dumps([name,i,values,results[0][0][0],results[0][1].hex()]).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,raw_caller_saved_register_mismatches=raw,trace_sha256=digest.hexdigest(),source_sha256=sha(ROOT/'r1/components/runtime/native_flashdb_tsdb_kernels.c'),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),upstream_slices_sha256=sha(OUT/'upstream-slices.json'),typed_return_callee_saved_sp_and_input_memory_verified=True,raw_abi_verified=False,main_provider_graph_linked=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
