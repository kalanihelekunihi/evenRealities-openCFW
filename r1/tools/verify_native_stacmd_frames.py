#!/usr/bin/env python3
"""Native frame packing/parity/partial-output contracts with bit-level fixtures."""
import csv,hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-stacmd-frames';C=0x200075c4;B=0x20003000
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_stacmd_read_frame_native':(0x28bb0,184),'r1_stacmd_write_frame_native':(0x28c6c,130)}
P={'r1_stacmd_idle_native':0x5cccc,'r1_stacmd_write_bits_native':0x5cc68,'r1_stacmd_drive_bit_native':0x5cbe4,'r1_stacmd_read_bit_adapter_native':0x969ec,'r1_stacmd_read_bit_native':0x87b30,'r1_stacmd_parity_native':0x968a8}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_stacmd_frames.o'
 assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';ghidra={}
 for n,(a,z) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/('ghidra-'+n+'.json');p.write_bytes(raw);ghidra[p.name]=sha(p)
 rows=[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and int(row['entry'],16) in [a for a,z in ENTRIES.values()]];(OUT/'evidence.json').write_text(json.dumps(dict(ownership_rows=rows,locked_ownership_changed=False,read_partial_byte_stored=True,length_comparison='signed32 index versus length',header='uint8((command&0xf0)+reg)',rea_scope='REA procedure_info reports no procedure at0x28bb0 or0x28c6c in current analysis; positive evidence is locked rows and authenticated Ghidra-MCP bytes'),indent=2)+'\n')
 counts={n:0 for n in ENTRIES};rng=random.Random(0x28bb0)
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_stacmd='+hex(C),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<65536;machines=[];states={};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def parity(value,f):return (0,1,2,0xffffffff)[value.bit_count()%4] if f['wide'] else value.bit_count()&1
  def hook(u,a,size,_):
   f=states[id(u)];r=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1)]
   if a in kinds:
    n=kinds[a];value=0
    if n=='r1_stacmd_idle_native':event=('idle',)
    elif n=='r1_stacmd_write_bits_native':
     event=('bits',*r);f['expected']=parity(((r[0]<<1)+(1 if f['reading'] else 0))&255,f) if r[1] else parity(r[0],f)
    elif n=='r1_stacmd_drive_bit_native':event=('drive',r[0])
    elif n=='r1_stacmd_parity_native':value=parity(r[0],f);event=('parity',r[0],value)
    else:
     index=f['read_index'];f['read_index']+=1;value=0 if index==f['fail_at'] else 0xffffffff
     received=(f['expected']^(1 if f['mismatch'] else 0)) if n=='r1_stacmd_read_bit_adapter_native' else ((0xffffffff,2,1,0)[index%4] if f['wide'] else index&1)
     u.mem_write(r[0],struct.pack('<I',received));event=('receive',n,received,value)
   elif a in (0x1100080,0x1100090):value=0xffffffff;event=('release',a,*r)
   else:
    if id(u)==id(machines[1]) and a<0x1000000 and a!=0x20000100:raise AssertionError(('unexpected native source execution',hex(a)))
    return
   f['trace'].append(event)
   if f['mutation']:
    index=len(f['trace']);u.mem_write(C+12,struct.pack('<I',0x80000000+index));u.mem_write(C+28,struct.pack('<I',0x1100091));u.mem_write(C+32,bytes([index&255]));u.mem_write(B,bytes([(index*13)&255])*8)
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for name,command,reg,length,fail_at,mismatch,mutation,wide in itertools.product(ENTRIES,(0,0x40,0x44,255,0xffffff40),(0,1,255,0xffffffff),(0,1,2,4,0x80000000,0xffffffff),(-1,0,1,7,8,9,16,32),(False,True),(False,True),(False,True)):
   results=[];buffer=rng.randbytes(8)
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'read_index':0,'expected':0,'reading':'read_frame' in name,'fail_at':fail_at,'mismatch':mismatch,'mutation':mutation,'wide':wide};u.mem_write(C-4,b'\x96'*116);u.mem_write(C+12,struct.pack('<I',33));u.mem_write(C+28,struct.pack('<I',0x1100081));u.mem_write(C+32,b'\x03');u.mem_write(B-4,b'\xa5'*4+buffer+b'\x69'*4)
    for r,v in [(UC_ARM_REG_R0,command),(UC_ARM_REG_R1,reg),(UC_ARM_REG_R2,length),(UC_ARM_REG_R3,B),(UC_ARM_REG_SP,0x2003f000),(UC_ARM_REG_LR,0x20000101)]:u.reg_write(r,v)
    for i,r in enumerate(saved):u.reg_write(r,0x12345600+i)
    u.emu_start((syms[name] if candidate else ENTRIES[name][0])|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(C-4,116)),bytes(u.mem_read(B-4,16))))
   assert results[0]==results[1],(name,command,reg,length,fail_at,mismatch,mutation,wide,results);counts[name]+=1
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_evidence=ghidra,body_evidence_sha256=sha(OUT/'evidence.json'),application_linked=False,instruction_identity=False,limitations=['Idle/bit/write-bits/parity and release callbacks are fixtures; actual wire composition remains open','Configuration is a test binding; no added device/null-buffer validation','High-bit lengths follow native signed comparison; unbounded large positive lengths not exercised','Physical timing/concurrency, shared registration and whole-image identity unproven']),indent=2)+'\n');print('STACMD frames:',counts)
if __name__=='__main__':main()
