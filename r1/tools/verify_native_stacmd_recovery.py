#!/usr/bin/env python3
"""Native STACMD recovery callback order, state reloads and raw tail return."""
import argparse,csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-stacmd-recovery';C=0x200075c4
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--real-delay',action='store_true');args=parser.parse_args();real_delay=args.real_delay
 vp=OUT/('delay-integration-verification.json' if real_delay else 'verification.json');vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_stacmd_recovery.o'
 assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';app_hash=sha(app);assert app_hash=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x5cc8c&length=58']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x5cc8c-0x27000:0x5ccc6-0x27000];(OUT/'ghidra-memory.json').write_bytes(raw)
 row=next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x0005cc8c');(OUT/'evidence.json').write_text(json.dumps(dict(ownership_row=row,locked_ownership_changed=False,rea_structured_metadata_obtained=False,scope='REA procedure_info did not yield structured metadata; native bytes and locked row authenticate recovery',callback_offsets={'low':16,'high':20,'output':24},delay_entry='0x5c0fa',delay_calls=5),indent=2)+'\n')
 count=0;provider_reports={};total_nops={'native':0,'source':0};delay_entries={'native':0,'source':0};extra_objects=[]
 if real_delay:
  delay_dir=OUT.parent/'native-stacmd-delay';delay_report=delay_dir/'report.json';delay=json.loads(delay_report.read_text());delay_object=delay_dir/'native_stacmd_delay.o';assert sha(delay_object)==delay['units'][0]['object_sha256'];extra_objects=[delay_object];provider_reports['native-stacmd-delay/report.json']=sha(delay_report)
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_stacmd='+hex(C),*([] if real_delay else ['--defsym=r1_stacmd_recovery_delay_native=0x1100001']),str(obj),*map(str,extra_objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<65536;machines=[];states={}
  def hook(u,a,size,_):
   f=states[id(u)];side='source' if id(u)==id(machines[1]) else 'native';is_delay=a==(syms['r1_stacmd_recovery_delay_native'] if side=='source' else 0x5c0fa) if real_delay else a in (0x5c0fa,0x1100000)
   if real_delay and f.get('delay_end')==a:f['delay_end']=None
   if real_delay and f.get('delay_end') is not None and bytes(u.mem_read(a,2))==b'\x00\xbf':total_nops[side]+=1
   if is_delay:f['trace'].append(('delay',));value=0
   elif a in (0x1100020,0x1100030,0x1100040,0x1100050,0x1100060,0x1100070):f['trace'].append(('line',a,u.reg_read(UC_ARM_REG_R0)));value=f['result']
   else:
    if id(u)==id(machines[1]) and a<0x1000000 and a!=0x20000100:raise AssertionError(('unexpected native source execution',hex(a)))
    return
   index=len(f['trace'])-1
   if f['mutation']==index or f['mutation']==10:
    u.mem_write(C+12,struct.pack('<I',(f['pin']+index+1)&0xffffffff));u.mem_write(C+16,struct.pack('<3I',0x1100051,0x1100061,0x1100071))
   if real_delay and is_delay:
    delay_entries[side]+=1;f['delay_end']=u.reg_read(UC_ARM_REG_LR)&~1
   else:u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,image);u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for pin,result,mutation in itertools.product((0,1,31,33,0xffffffff),(0,1,0x80000000,0xffffffff),range(-1,11)):
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'pin':pin,'result':result,'mutation':mutation};u.mem_write(C-4,b'\x96'*116);u.mem_write(C+12,struct.pack('<4I',pin,0x1100021,0x1100031,0x1100041));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_stacmd_bus_recovery_native'] if candidate else 0x5cc8c)|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    trace=states[id(u)]['trace'];assert [e[0] for e in trace]==['line','line','line','delay','line','delay','delay','delay','delay','line'];assert u.reg_read(UC_ARM_REG_R0)==result
    results.append((trace,bytes(u.mem_read(C-4,116))))
   assert results[0]==results[1],(pin,result,mutation,results);count+=1
 if real_delay:assert total_nops=={'native':1003200,'source':1003200} and delay_entries=={'native':1200,'source':1200}
 vp.write_text(json.dumps(dict(comparisons=count,real_delay=real_delay,delay_provider_interception=not real_delay,provider_reports=provider_reports,total_nops=total_nops,executed_delay_entry_counts=delay_entries,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=app_hash,ghidra_memory_sha256=sha(OUT/'ghidra-memory.json'),body_evidence_sha256=sha(OUT/'evidence.json'),application_linked=False,instruction_identity=False,limitations=['GPIO callbacks remain fixtures; delay body executes in integration mode','Configuration is an address binding; shared registration ABI and source state integration remain open','REA did not provide structured metadata for this query; native bytes and locked row are positive evidence','Physical delay timing/GPIO behavior/concurrency and instruction identity unproven']),indent=2)+'\n');print('STACMD recovery:',count,'native/source comparisons')
if __name__=='__main__':main()
