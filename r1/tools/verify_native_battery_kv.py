#!/usr/bin/env python3
"""Execute actual cached KV getters/setter and musl copy using owned cold classes."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-kv-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'byte':('r1_batcfg_byte0_get',0x7bb44),'flag':('r1_batcfg_flag1_get',0x7bb5c),'signed':('r1_batcfg_word1_signed_get',0x7bb7c),'fields':('r1_kv_dev_info_fields_set',0x73710)}
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'battery-kv-cached-source.o';assert sha(obj)==b['cached_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_battery_kv_verification.ld';states={};digest=hashlib.sha256();counts={n:0 for n in ENTRIES};obs=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text','power','devinfo','powerhandle','devinfohandle']:
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  cells={'power':0x20006abc,'devinfo':0x200069a8,'powerhandle':0x20007df8,'devinfohandle':0x20007de8};cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
  for n,a in cells.items():assert sections[n]==cold[a-0x200064a8:a-0x200064a8+len(sections[n])]
  assert syms['r1_kv_port']==0x20006974 and syms['r1_power_kv_class']==cells['power'] and syms['r1_dev_info_kv_class']==cells['devinfo']
  def hook(u,a,size,_):
   st=states[id(u)];assert not st['source'] or not 0x27000<=a<0xc4d08
   if a not in [0x20000200,0x20000204]:return
   enter=a==0x20000200;st['events'].append(['enter' if enter else 'leave',bytes(u.mem_read(st['node']+18,6)).hex()]);m=st['mutation'];payload=st['node']+24
   if enter and m==1:u.mem_write(payload,struct.pack('<I',0x89abcdef))
   elif enter and m==2:u.mem_write(st['node']+20,b'\xff\xff')
   elif enter and m==3:u.mem_write(st['slot'],struct.pack('<I',0x20001000))
   elif not enter and m==4 and st['input']:u.mem_write(st['input'],bytes.fromhex('12345678aabbccdd'))
   elif enter and m==5:u.mem_write(payload+36 if st['kind']=='fields' else payload,struct.pack('<I',0xabcdef01))
   u.reg_write(UC_ARM_REG_R0,0x80000000)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  seeds=[0,1,0x000100ff,0x7fff0055,0x80000002,0xffff0004,0xffffffff,0x12345678];cases=[]
  for kind,seed,size,m in itertools.product(['byte','flag','signed'],seeds,[0,3,4,5,52],range(6)):cases.append((kind,seed,size,m,0))
  for seed,size,m,input_ in itertools.product(seeds[:4],[0,51,52,53],range(6),[0,0x20002001,0x200069a8+60,0x2003efc0,0x2003efe4]):cases.append(('fields',seed,size,m,input_))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,seed,size,m,input_) in enumerate(cases):
   results=[];node=cells['devinfo' if kind=='fields' else 'power'];slot=cells['devinfohandle' if kind=='fields' else 'powerhandle']
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000)
    for n,a in cells.items():u.mem_write(a,sections[n])
    u.mem_write(node+20,struct.pack('<H',size));u.mem_write(0x20001000,sections['devinfo' if kind=='fields' else 'power']);u.mem_write(0x20006974,struct.pack('<I',0x20000800));u.mem_write(0x2000081c,struct.pack('<II',0x20000201,0x20000205))
    if input_:u.mem_write(input_,bytes.fromhex('78563412aabbccdd'))
    states[id(u)]=dict(source=source,events=[],node=node,slot=slot,mutation=m,input=input_,kind=kind)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[input_,0x11223344,0x55667788,seed]):u.reg_write(reg,v)
    u.emu_start((syms[ENTRIES[kind][0]] if source else ENTRIES[kind][1])|1,0x20000100,count=20000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([None if kind=='fields' else [u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R3)],states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,seed,size,m,input_],results=results),indent=2)+'\n');raise AssertionError((number,kind,seed,size,m,input_))
   counts[kind]+=1;obs+=len(results[0][1]);digest.update(json.dumps([number,kind,seed,size,m,input_,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),source_cold_classes_and_symbolic_handles_match=True,actual_cached_read_write_and_musl_copy=True,only_critical_callbacks_are_fixtures=True,callback_mutations_handle_reload_and_input_aliases_checked=True,raw_getter_r0_r3_callee_sp_and_nonstack_ram_checked=True,void_setter_raw_return_not_compared=True,failed_size_preserves_external_raw_stack_view=True,no_native_candidate_execution=True,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app),cross_call_private_stack_history_verified=False,whole_storage_graph_executed=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
