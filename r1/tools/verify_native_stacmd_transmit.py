#!/usr/bin/env python3
"""Native transmit callback/NOP/parity contracts; hardware and idle delay are fixtures."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-stacmd-transmit';C=0x200075c4
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_stacmd_drive_bit_native':(0x5cbe4,126),'r1_stacmd_write_bits_native':(0x5cc68,36),'r1_stacmd_idle_native':(0x5cccc,42),'r1_stacmd_parity_native':(0x968a8,26)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_stacmd_transmit.o'
 assert sha(obj)==r['units'][0]['object_sha256'] and '-falign-loops=1' in r['units'][0]['command']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';ghidra={}
 for n,(a,z) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/('ghidra-'+n+'.json');p.write_bytes(raw);ghidra[p.name]=sha(p)
 rows=[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and int(row['entry'],16) in [a for a,z in ENTRIES.values()]];(OUT/'evidence.json').write_text(json.dumps(dict(ownership_rows=rows,locked_ownership_changed=False,drive_body_bytes=118,drive_span_bytes=126,drive_ranges=[{'start':'0x5cbe4','end':'0x5cbed'},{'start':'0x5cbf0','end':'0x5cc25'},{'start':'0x5cc2c','end':'0x5cc61'}],zero_bit_iterations=13,nonzero_bit_iterations=52,nops_per_iteration=4,header_bits='7 only when second argument equals1; otherwise8',parity='xor of low8 bits',scope='Native bytes and locked rows; physical timing and instruction identity separate'),indent=2)+'\n')
 counts={n:0 for n in ENTRIES};totals={'native':0,'source':0}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_stacmd='+hex(C),'--defsym=r1_stacmd_recovery_delay_native=0x1100001',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<65536;machines=[];states={}
  def hook(u,a,size,_):
   f=states[id(u)];side='source' if id(u)==id(machines[1]) else 'native'
   if bytes(u.mem_read(a,2))==b'\x00\xbf':f['nops']+=1;totals[side]+=1
   if a in (0x5c0fa,0x1100000):f['trace'].append(('delay',));value=0
   elif a in (0x1100020,0x1100030,0x1100040,0x1100050,0x1100060,0x1100070):f['trace'].append(('line',a,u.reg_read(UC_ARM_REG_R0)));value=f['result']
   else:
    if side=='source' and a<0x1000000 and a!=0x20000100:raise AssertionError(('unexpected native source execution',hex(a)))
    return
   index=len(f['trace'])-1
   if f['mutation']==index or f['mutation']==99:u.mem_write(C+12,struct.pack('<I',(f['pin']+index+1)&0xffffffff));u.mem_write(C+16,struct.pack('<3I',0x1100051,0x1100061,0x1100071))
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,value=0,header=0,pin=33,result=0,mutation=-1):
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'nops':0,'pin':pin,'result':result,'mutation':mutation};u.mem_write(C-4,b'\x96'*116);u.mem_write(C+12,struct.pack('<4I',pin,0x1100021,0x1100031,0x1100041));u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_R1,header);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,r in enumerate(saved):u.reg_write(r,0x12345600+i)
    u.emu_start((syms[name] if candidate else ENTRIES[name][0])|1,0x20000100,count=15000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
    expected=value.bit_count()&1 if name.endswith('parity_native') else result
    if name.endswith('parity_native'):expected=(value&255).bit_count()&1
    assert u.reg_read(UC_ARM_REG_R0)==expected
    if name.endswith('drive_bit_native'):assert states[id(u)]['nops']==(208 if value else 52) and len(states[id(u)]['trace'])==5
    if name.endswith('write_bits_native'):
     bits=7 if header==1 else 8;ones=(value&((1<<bits)-1)).bit_count();assert states[id(u)]['nops']==ones*208+(bits-ones)*52 and len(states[id(u)]['trace'])==bits*5
    if name.endswith('idle_native'):assert states[id(u)]['nops']==0 and [e[0] for e in states[id(u)]['trace']]==['line','line','line','line','delay','line']
    results.append((states[id(u)]['trace'],states[id(u)]['nops'],bytes(u.mem_read(C-4,116))))
   assert results[0]==results[1],(name,value,header,pin,result,mutation,results);counts[name]+=1
  for value,high in itertools.product(range(256),(0,0x100,0x80000000,0xffffff00)):case('r1_stacmd_parity_native',value|high)
  for value,pin,result,mutation in itertools.product((0,1,2,0x80000000,0xffffffff),(0,1,33,0xffffffff),(0,1,0x80000000,0xffffffff),(-1,0,1,2,3,4,99)):case('r1_stacmd_drive_bit_native',value,pin=pin,result=result,mutation=mutation)
  for pin,result,mutation in itertools.product((0,1,33,0xffffffff),(0,1,0x80000000,0xffffffff),(-1,0,1,2,3,4,99)):case('r1_stacmd_idle_native',pin=pin,result=result,mutation=mutation)
  for value,header,mutation,result in itertools.product(range(256),(0,1,2,0xffffffff),(-1,99),(0,0xffffffff)):case('r1_stacmd_write_bits_native',value,header,result=result,mutation=mutation)
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,total_nops=totals,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_evidence=ghidra,body_evidence_sha256=sha(OUT/'evidence.json'),application_linked=False,instruction_identity=False,limitations=['GPIO callbacks and idle long-delay are fixtures; drive-bit body executes inside write-bits','NOP counts verified; compiler scheduling/cycle count and physical timing unproven','Fixed configuration remains a test binding; typed registration/state integration open','Full frame/adapter/transport composition and whole-image byte identity remain gated']),indent=2)+'\n');print('STACMD transmit:',counts,totals)
if __name__=='__main__':main()
