#!/usr/bin/env python3
"""Count native/source NOPs and verify the bounded delay's return/preservation."""
import csv,hashlib,json,random,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-stacmd-delay';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_stacmd_delay.o'
 assert sha(obj)==r['units'][0]['object_sha256'] and '-falign-loops=1' in r['units'][0]['command']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x5c0fa&length=20']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x5c0fa-0x27000:0x5c10e-0x27000];(OUT/'ghidra-memory.json').write_bytes(raw)
 row=next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x0005c0fa');(OUT/'evidence.json').write_text(json.dumps(dict(ownership_row=row,locked_ownership_changed=False,iterations=209,nops_per_iteration=4,rea_structured_metadata_obtained=False,scope='Native byte/ownership evidence; REA query did not yield structured metadata',compiler_scope='Loop alignment disabled only for selected delay module to avoid extra alignment NOP execution'),indent=2)+'\n')
 rng=random.Random(0x5c0fa);totals=[0,0]
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();machines=[];states={}
  def hook(u,a,size,_):
   if bytes(u.mem_read(a,2))==b'\x00\xbf':states[id(u)]+=1
   if id(u)==id(machines[1]) and a<0x1000000 and a!=0x20000100:raise AssertionError(('unexpected native source execution',hex(a)))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for case in range(64):
   values=[rng.getrandbits(32) for _ in saved];args=[rng.getrandbits(32) for _ in range(4)]
   for candidate,u in enumerate(machines):
    states[id(u)]=0;u.mem_write(0x2003efc0,b'\xa5'*64);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip(saved,values):u.reg_write(reg,v)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    u.emu_start((syms['r1_stacmd_recovery_delay_native'] if candidate else 0x5c0fa)|1,0x20000100,count=2000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and u.reg_read(UC_ARM_REG_R0)==0 and [u.reg_read(reg) for reg in saved]==values
    assert bytes(u.mem_read(0x2003efc0,64))==b'\xa5'*64 and states[id(u)]==836;totals[candidate]+=states[id(u)]
 vp.write_text(json.dumps(dict(comparisons=64,nops_per_call=836,total_nops={'native':totals[0],'source':totals[1]},report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_memory_sha256=sha(OUT/'ghidra-memory.json'),body_evidence_sha256=sha(OUT/'evidence.json'),application_linked=False,instruction_identity=False,limitations=['Emitted NOP count and preserved return/register/stack tested; compiler scheduling/cycle count differ','Physical clock calibration/interrupt timing and GPIO behavior unproven','REA structured metadata unavailable; native bytes and locked ownership are positive evidence']),indent=2)+'\n');print('STACMD delay:64 comparisons;836 NOPs per call')
if __name__=='__main__':main()
