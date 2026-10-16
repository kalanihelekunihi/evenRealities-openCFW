#!/usr/bin/env python3
"""Exhaustive halfword discharge input replay against authenticated product tables."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-discharge';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();D=0x20016b84

def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_discharge.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';apphash=sha(app);assert apphash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';data=app.read_bytes();evidence={}
 for suffix in ('body','pseudocode'):
  p=OUT/('rea-50004-'+suffix+'.json');p.write_bytes((BASE/'native-battery-runtime'/('rea-next-50004-'+suffix+'.json')).read_bytes());evidence[p.name]=sha(p)
 q=json.loads((OUT/'rea-50004-body.json').read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']=='0x50004' and q['normalized_result']['body']['total_bytes']==180 and q['normalized_result']['body']['span_bytes']==182
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 for name,a,z in [('body',0x50004,196),('tables',0x99d16,480)]:
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==data[a-0x27000:a-0x27000+z];p=OUT/('ghidra-'+name+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 tables=[[struct.unpack_from('<HHBB',data,0x99d16-0x27000+t*120+i*6) for i in range(20)] for t in range(4)]
 assert all(rows[0][0]==3350 and rows[-1][1]==4310 and sum(row[2] for row in rows)==100 and all(row[0]<row[1] and row[3]==0 for row in rows) and all(rows[i][1]==rows[i+1][0] for i in range(19)) for rows in tables)
 machines=[];states={};counts={'comparisons':0,'halfword_comparisons':0,'getter_calls':0};high_override={'native':0,'source':0};context_reads={'native':0,'source':0}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';tablefile=d/'tables.bin'
  ld.write_text('SECTIONS { .tables 0x99d16 : { *(.r1.battery.discharge_tables) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_batcfg_byte0_get=0x1100001','--defsym=r1_battery_device_context='+hex(D),str(obj),'-o',str(elf)],check=True,capture_output=True)
  for section,file in [('text',binary),('tables',tablefile)]:subprocess.run(['arm-none-eabi-objcopy','-j','.'+section,'-O','binary',str(elf),str(file)],check=True)
  assert tablefile.read_bytes()==data[0x99d16-0x27000:0x99d16-0x27000+480];tablehash=sha(tablefile)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def hook(u,a,size,_):
   side='source' if u is machines[1] else 'native'
   if a==0x500aa:high_override[side]+=1
   if a in (0x7bb44,0x1100000):
    f=states[id(u)];f['calls']+=1;u.mem_write(D+46,bytes([f['flag']]));u.reg_write(UC_ARM_REG_R0,f['kind']);u.reg_write(UC_ARM_REG_R1,0x87654321);u.reg_write(UC_ARM_REG_R2,0x76543210);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if side=='source' and a<0x1000000 and a!=0x20000100:raise AssertionError(('source used native provider',hex(a)))
  def readhook(u,access,a,size,value,_):context_reads['source' if u is machines[1] else 'native']+=1
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,data);u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ,readhook,begin=D+46,end=D+46)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  boundaries=sorted({0,2399,2400,4340,4341,65535,65536,0x7fffffff,0x80000000,0xffffffff,*[v+delta for table in tables for row in table for v in row[:2] for delta in (-1,0,1)]})
  for kind in (0,1,2,3,4,255,0xffffffff):
   values=range(65536) if kind in (0,1,2,3) else boundaries
   for voltage in values:
    rows=tables[kind-1 if 1<=kind<=3 else 3];expected=50
    if voltage>=2400:
     clamped=min(max(voltage,rows[0][0]),rows[-1][1]);total=0
     for lower,upper,weight,_ in rows:
      if clamped<=upper:expected=(total+(clamped-lower)*weight//(upper-lower))&255;break
      total=(total+weight)&255
    results=[]
    for candidate,u in enumerate(machines):
     states[id(u)]={'kind':kind,'calls':0,'flag':(voltage^kind)&255};u.mem_write(D-4,b'\xa5'*76)
     for reg,value in [(UC_ARM_REG_R0,voltage),(UC_ARM_REG_R1,(~voltage)&0xffffffff),(UC_ARM_REG_SP,0x2003f000),(UC_ARM_REG_LR,0x20000101)]:u.reg_write(reg,value)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((syms['r1_battery_discharge_curve'] if candidate else 0x50004)|1,0x20000100,count=2000)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
     assert states[id(u)]['calls']==1 and u.reg_read(UC_ARM_REG_R0)==expected,(kind,voltage,candidate,u.reg_read(UC_ARM_REG_R0),expected)
     results.append(bytes(u.mem_read(D-4,76)))
    assert results[0]==results[1];counts['comparisons']+=1;counts['getter_calls']+=1
    if kind in (0,1,2,3):counts['halfword_comparisons']+=1
 assert high_override=={'native':0,'source':0} and context_reads=={'native':0,'source':0}
 vp.write_text(json.dumps(dict(**counts,table_bytes=480,table_sha256=tablehash,table_maximum=4310,unreachable_override_threshold=4340,high_override_counts=high_override,device_context_reads=context_reads,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=apphash,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Config getter is fixture; actual configuration/updater composition remains open','Tables source-owned and byte-equal to authenticated data; native code instruction identity unproven','Locked table clamp4310 makes4340 override unreachable; source retains policy branch, compiler removes unreachable dependency','Full startup, remaining policy/provider graph and hardware proof remain open']),indent=2)+'\n');print('Battery discharge:',counts)
if __name__=='__main__':main()
