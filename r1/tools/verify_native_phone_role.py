#!/usr/bin/env python3
"""Phone-role behavior through explicit native fatal-transfer boundary."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-phone-role';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TEXTS=[0xbe110,0xbe15c,0x4dbec,0x4dc18,0xbdc48,0x4dc40,0x4dc80,0x4dc94,0x4dcbc,0x4dcc8,0x99118,0x4dcd8,0x4dce8,0x4dcec,0x4dd00,0x4dd20,0xbdfac,0x4dd3c]
def main():
 rp=BASE/'native-phone-role-runtime/report.json';b=json.loads(rp.read_text());obj=rp.parent/'phone-role-source.o';assert sha(obj)==b['role_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_phone_role_verification.ld';states={};digest=hashlib.sha256();count=obs=fatal=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for section in ['.text']+['.text'+str(i) for i in range(len(TEXTS))]:
   p=d/(section[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  assert syms['r1_connection_field8']==0x200064ba and syms['r1_connection_field10']==0x200064bc
  for i,a in enumerate(TEXTS):assert sections['.text'+str(i)]==raw[a-0x27000:a-0x27000+len(sections['.text'+str(i)])]
  def fields(u):return list(struct.unpack('<HH',u.mem_read(0x200064ba,4)))
  def setfields(u,a,b):u.mem_write(0x200064ba,struct.pack('<HH',a,b))
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   kind=({0x20000200:'mode',0x20000204:'ring',0x20000208:'sdk1',0x2000020c:'sdk2',0x20000210:'sdk3',0x20000214:'delay',0x20000218:'sink',0x2000021c:'publish',0x20000220:'fatal'} if source else {0x914ec:'mode',0x91638:'ring',0x799c8:'sdk1',0x799d6:'sdk2',0x799e6:'sdk3',0x7d154:'delay',0x7f030:'sink',0x5e118:'publish',0x4db42:'fatal'}).get(a)
   if not kind:return
   regs=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=u.reg_read(UC_ARM_REG_SP);ret=st['status'];mutation=st['mutation']
   if kind=='mode':
    ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;st['events'].append(['mode',ret,fields(u)])
    if mutation==1:setfields(u,(st['mi']*257)&65535,(st['mi']*259)&65535)
    elif mutation==2 and st['mi']>=3:setfields(u,65535,st['handle']&65535)
    elif mutation==3 and st['mi']>=3:setfields(u,st['handle']&65535,65535)
   elif kind=='ring':
    i=TEXTS.index(regs[1]);n={0:3,2:1,4:2,14:1,16:2}[i];assert regs[2]==regs[1];args=[regs[3]]+list(struct.unpack('<'+'I'*(n-1),u.mem_read(sp,4*(n-1)))) if n>1 else [regs[3]]
    st['events'].append(['ring',regs[:3],args,fields(u)])
    if mutation==4:setfields(u,0x1234,0x5678)
   elif kind.startswith('sdk'):
    n=int(kind[-1]);args=regs[2:2+min(n,2)]+([struct.unpack('<I',u.mem_read(sp,4))[0]] if n==3 else []);st['events'].append([kind,regs[:2],args,fields(u)])
    if mutation==5:setfields(u,65535,0)
   elif kind=='delay':st['events'].append(['delay',regs[0],fields(u)])
   elif kind=='publish':st['events'].append(['publish',regs,fields(u)])
   elif kind=='sink':
    i=TEXTS.index(regs[0]);st['events'].append(['sink',regs[:1] if i==6 else regs[:2],fields(u)])
   else:
    if not source:assert struct.unpack('<I',u.mem_read(sp,4))[0]==0xe7f00000
    st['events'].append(['fatal_stack_transfer',0xe7f00000,fields(u)]);st['fatal']=True;u.emu_stop();return
   u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['.text']);u.mem_map(0x20000000,0x40000)
   for i,a in enumerate(TEXTS):u.mem_write(a,sections['.text'+str(i)])
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2],[1,0],[0xffffffff,0x80000000],[0x40000000],[0x80000000]];saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(handle,phone,glasses,mode,mutation) in enumerate(itertools.product([0,1,65535,0x1000ffff,0xffffffff],[0,1,65535,0x1234],[0,1,65535,0x5678],modes,range(6))):
   results=[];status=[0,1,0xffffffff,0x80000000,0x12345678][number%5]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000);setfields(u,phone,glasses);states[id(u)]=dict(source=source,events=[],modes=mode,mi=0,mutation=mutation,handle=handle,status=status,fatal=False)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[handle,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,v)
    u.emu_start((syms['r1_phone_connection_role_assign'] if source else 0x4da28)|1,0x20000100,count=10000);terminal=states[id(u)]['fatal']
    if not terminal:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([None if terminal else u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(memory).hexdigest(),terminal])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[handle,phone,glasses,mode,mutation],results=results),indent=2)+'\n');raise AssertionError((number,handle,phone,glasses,mode,mutation))
   count+=1;fatal+=results[0][3];obs+=len(results[0][1]);digest.update(json.dumps([number,handle,phone,glasses,mode,mutation,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=count,fatal_boundary_cases=fatal,observations_per_side=obs,trace_sha256=digest.hexdigest(),source_log_texts_match=True,fresh_connection_fields_and_modes_checked=True,full_word_handle_and_low_halfword_store_checked=True,raw_r0_callee_sp_checked_on_returning_paths=True,terminal_paths_stop_before_native_stack_blx=True,no_trap_or_executable_array_substitution=True,only_logging_delay_status_publish_and_terminal_boundary_are_fixtures=True,observed_nonstack_ram_checked=True,no_native_candidate_execution=True,driver_sha256=sha(Path(__file__)),runtime_report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app),fatal_transfer_implemented=False,whole_role_status_or_logging_graph_executed=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
