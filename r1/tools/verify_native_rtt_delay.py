#!/usr/bin/env python3
"""SDK delay clones: source-compiled primitive bytes, flags, register and loop counts."""
import csv,hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-rtt-delay';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'rtt-delay.o';receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';rows=[row for row in csv.DictReader(ownership.open()) if row['image']=='application' and row['upstream_symbol']=='nrfx_coredep_delay_us::delay_machine_code'];assert len(rows)==21;addresses=[int(row['entry'],16) for row in rows];comparisons=0;total_steps=0;states={}
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);elf=t/'test.elf';binary=t/'text.bin';subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','--entry=r1_rtt_delay_cycles',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);body=binary.read_bytes();assert len(body)==6
  for row in rows:a=int(row['entry'],16);assert int(row['size'])==6 and a%16==0 and app.read_bytes()[a-0x27000:a-0x27000+6]==body
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x1000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,body);saved=[UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12]
  def hook(u,a,size,user):
   f=states[id(u)];offset=a-f['base'];assert offset in (0,2,4);f['counts'][offset//2]+=1
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  def compare(address,cycles):
   nonlocal comparisons,total_steps
   results=[];iterations=max(1,(cycles+2)//3)
   for u in (stock,candidate):
    base=address if u is stock else 0x1000000;states[id(u)]={'base':base,'counts':[0,0,0]};u.reg_write(UC_ARM_REG_R0,cycles);u.reg_write(UC_ARM_REG_APSR,0x20000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start(base|1,0x20000100,count=1000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(12)];counts=states[id(u)]['counts'];assert counts==[iterations,iterations,1] and u.reg_read(UC_ARM_REG_R0)==(cycles-iterations*3)&0xffffffff;results.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_APSR)&0xf0000000,counts))
   assert results[0]==results[1],(hex(address),cycles,results);comparisons+=1;total_steps+=2*iterations+1
  values=sorted(set(range(1024))|{(1<<n)+d for n in range(10,17) for d in (-1,0,1)}|{64000,128000,192000})
  for cycles in values:compare(0x9c9e0,cycles)
  for address in addresses:
   for cycles in (0,1,2,3,4,5,6,64000):compare(address,cycles)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),ownership_sha256=sha(ownership),comparisons=comparisons,instruction_steps_per_implementation=total_steps,clone_entries=[row['entry'] for row in rows],identical_body_bytes_per_entry=6,body_bytes_identical=True,scope='Explicit three-mnemonic C compilation unit matches21 native aligned SDK delay clones; bounded counts, zero/underflow, NZCV/register preservation and exact instruction counts',limitations=['Positive inputs up to192000 tested; larger counts follow the same byte-identical loop but are not exhaustively executed.','Instruction count and body identity do not measure elapsed hardware time, interrupt preemption, flash/cache wait states or clock frequency.','Whole-image duplicate placement, startup/linking, compiler identity and firmware byte equality remain unresolved.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'delay comparisons;',len(rows),'native clones;',total_steps,'instructions each')
if __name__=='__main__':main()
