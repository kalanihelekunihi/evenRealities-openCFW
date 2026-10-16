#!/usr/bin/env python3
"""SDK millisecond loop clones: bounded request flow plus real source cycle execution."""
import csv,hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-nordic-delay-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'nordic-delay-source.o';assert sha(obj)==r['delay_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';rows=[x for x in csv.DictReader(ownership.open()) if x['image']=='application' and x['upstream_symbol']=='nrf_delay_ms'];assert len(rows)==9;states={};digest=hashlib.sha256();counts={'fixture':0,'actual':0,'prefix':0};requests=steps=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','--entry=nrf_delay_ms',str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);text=binary.read_bytes();syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};primitive=syms['r1_rtt_delay_cycles'];entries={int(x['entry'],16):struct.unpack_from('<I',raw,int(x['entry'],16)-0x27000+28)[0] if int(x['size'])==28 else 0x9d3d0 for x in rows};assert len(entries)==9
  for p in entries.values():assert raw[p-0x27000:p-0x27000+6]==text[primitive-0x1000000:primitive-0x1000000+6]==bytes.fromhex('0338fdd87047')
  def hook(u,a,size,_):
   st=states[id(u)];assert not st['source'] or not 0x27000<=a<0xc4d08
   p=st['primitive']
   if p<=a<p+6:
    st['steps']+=1
    if a==p+4:st['in_cycle']=False
    if a==p and not st['in_cycle']:
     st['in_cycle']=st['tier']=='actual'
     st['events'].append(u.reg_read(UC_ARM_REG_R0));assert st['events'][-1]==64000
     if st['tier']=='prefix' and len(st['events'])==3:st['stopped']=True;u.emu_stop();return
     if st['tier']!='actual':
      u.reg_write(UC_ARM_REG_R0,0x80000000)
      for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
      u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,text);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  cases=[(a,ms,'fixture') for a in entries for ms in [0,1,2,3,7,255,256,1000]]+[(a,ms,'actual') for a in entries for ms in [0,1,2]]+[(a,ms,'prefix') for a in entries for ms in [0x80000000,0xffffffff]]
  for number,(entry,ms,tier) in enumerate(cases):
   results=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);states[id(u)]=dict(source=source,primitive=primitive if source else entries[entry],events=[],steps=0,tier=tier,stopped=False,in_cycle=False)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[ms,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,v)
    u.emu_start((syms['nrf_delay_ms'] if source else entry)|1,0x20000100,count=1000000);st=states[id(u)];assert st['stopped']==(tier=='prefix')
    if not st['stopped']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    expected=3 if tier=='prefix' else ms;assert len(st['events'])==expected
    if tier=='actual':assert st['steps']==ms*(21334*2+1)
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([st['events'],st['steps'],st['stopped'],hashlib.sha256(memory).hexdigest()])
   assert results[0]==results[1],(number,entry,ms,tier,results);counts[tier]+=1;requests+=len(results[0][0]);steps+=results[0][1];digest.update(json.dumps([number,entry,ms,tier,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,requests_per_side=requests,cycle_instruction_steps_per_side=steps,trace_sha256=digest.hexdigest(),clone_entries=[x['entry'] for x in rows],sdk_loop_unchanged=True,cycle_primitive_body_matches_all_used_native_clones=True,actual_cycle_tier_present=True,large_values_only_three_request_prefix_checked=True,callee_sp_and_nonstack_ram_checked_on_return=True,void_raw_r0_r3_and_apsr_not_compared=True,no_native_candidate_execution=True,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),ownership_sha256=sha(ownership),application_sha256=sha(app),hardware_elapsed_time_verified=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
