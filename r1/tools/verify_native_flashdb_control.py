#!/usr/bin/env python3
"""Native control TBB, exact init-byte assertions and alias/fault contracts."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-flashdb-control';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;DB=0x20010000;ARG=DB+128
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 obj=OUT/'native_flashdb_control.o';countobj=BASE/'native-flashdb-query-count/native_flashdb_query_count.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts={'returned':0,'assertion_loop':0,'fault':0};by_command={};proof=[]
 spans=[('control',0x63694,384,'.text.r1_health_sync_provider_00063694'),('name',0x9bdd8,17,'.r1.fdb.control_name'),('error',0xc0a68,75,'.r1.fdb.control_filemode_error'),('path',0x3f014,14,'.text.r1_fdb_native_db_path')]
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS {'+''.join(' .%s 0x%x : { *(%s) }'%(n,a,s) for n,a,l,s in spans)+' /DISCARD/ : { *(.ARM.exidx*) *(.text.r1_fdb_native_query_count*) } }\nr1_native_printf = 0x38061;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(countobj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacement=[]
  for sec,a,length,section in spans:
   p=td/(sec+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+sec,'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();native=image[a-0x27000:a-0x27000+length];assert len(data)==length and data==native,(sec,len(data),length,[(i,x,y) for i,(x,y) in enumerate(zip(data,native)) if x!=y][:8]);replacement.append((a,data));proof.append(dict(section=sec,address=hex(a),size=length,sha256=sha(p)))
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size,value];return False
  def hook(u,a,size,_):
   s=states[id(u)]
   if a in [0x636ce,0x636f4,0x6372e,0x6378a]:s['assert']=hex(a);u.emu_stop()
   elif a==0x38060:
    r=[u.reg_read(x) for x in REGS];s['trace'].append([r,bytes(u.mem_read(r[0],120)).split(b'\0')[0].decode()]);u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R1,0xa1);u.reg_write(UC_ARM_REG_R2,0xa2);u.reg_write(UC_ARM_REG_R3,0xa3);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,data in replacement:u.mem_write(a,data)
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  default=dict(db=DB,cmd=0,init=0,arg=ARG,value=1,rollover=0x96,last=0x80000001)
  cases=[dict(default,cmd=cmd,init=init,value=value) for cmd,init,value in itertools.product(range(256),[0,1,2,255],[0,1,0x80000000,0xffffffff])]
  cases += [dict(default,cmd=cmd,init=init) for cmd,init in itertools.product([0,4,11],range(256))]
  cases += [dict(default,cmd=cmd,init=init,arg=arg,value=value) for cmd,init,arg,value in itertools.product(range(12),[0,1,2,255],[DB+12,DB+24,DB+80,DB+92],[0,1,0x80000000,0xffffffff])]
  cases += [dict(default,cmd=cmd,db=db,arg=arg) for cmd,db,arg in itertools.product([*range(12),12,0x7fffffff,0x80000000,0xffffffff],[0,0x30000000,DB],[ARG,0x30000000])]
  for c in cases:
   data=bytearray(b'\x96'*256);struct.pack_into('<I',data,0,DB+192);struct.pack_into('<I',data,8,DB+208);struct.pack_into('<I',data,12,0x12345678);data[24]=c['init'];data[25]=0;struct.pack_into('<I',data,80,c['last']);data[92]=c['rollover'];data[192:197]=b'logs\0';data[212:217]=b'path\0'
   if DB<=c['arg']<DB+256:struct.pack_into('<I',data,c['arg']-DB,c['value'])
   expected=bytearray(data);init=data[24];expect_assert='0x636ce' if c['db']==0 else '0x636f4' if c['db']==DB and c['cmd']==0 and init!=0 else '0x6372e' if c['db']==DB and c['cmd']==4 and init!=1 else '0x6378a' if c['db']==DB and c['cmd']==11 and init!=0 else None
   if c['db']==DB and not expect_assert and DB<=c['arg']<DB+256:
    arg=c['arg']-DB
    if c['cmd']==0:expected[12:16]=data[arg:arg+4]
    if c['cmd']==1:expected[arg:arg+4]=data[12:16]
    if c['cmd']==4:expected[92]=data[arg]
    if c['cmd']==5:expected[arg]=data[92]
    if c['cmd']==6:expected[arg:arg+4]=data[80:84]
    if c['cmd']==11:expected[26]=data[arg]
   if c['db']==DB and c['cmd'] in [2,3]:struct.pack_into('<I',expected,28 if c['cmd']==2 else 32,c['arg'])
   outputs=[]
   for u in machines:
    u.mem_write(0,bytes(4096));u.mem_write(DB,bytes(data));u.mem_write(SP-128,b'\x96'*256)
    for r,v in zip(REGS,[c['db'],c['cmd'],c['arg'],0xabcdef01]):u.reg_write(r,v)
    for i,r in enumerate(SAVED):u.reg_write(r,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(trace=[],fault=None,**{'assert':None});states[id(u)]=s
    try:u.emu_start(0x63695,0x20000100,count=1000)
    except UcError:assert s['fault']
    assert s['assert']==expect_assert,(c,s,expect_assert)
    if not s['fault'] and not expect_assert:
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(r) for r in SAVED]==[0x12340000+i for i in range(8)]
     if c['db']==DB:assert bytes(u.mem_read(DB,256))==expected,(c,bytes(u.mem_read(DB,256)).hex(),expected.hex())
    outputs.append([[u.reg_read(r) for r in REGS],u.reg_read(UC_ARM_REG_SP),s,bytes(u.mem_read(DB,256)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1],c;kind='fault' if outputs[0][2]['fault'] else 'assertion_loop' if expect_assert else 'returned';counts[kind]+=1;by_command[str(c['cmd'])]=by_command.get(str(c['cmd']),0)+1;digest.update(json.dumps([c,outputs[0]],sort_keys=True).encode())
 receipt=dict(comparisons=len(cases),counts=counts,commands_checked=len(by_command),trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=sum(x['size'] for x in proof),object_sha256=sha(obj),count_object_sha256=sha(countobj),driver_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),application_sha256=sha(app),all_256_init_bytes_and_all_256_command_bytes_checked=True,independent_control_memory_mutation_oracle=True,actual_db_path_executes=True,printf_and_zero_low_rom_are_fixtures=True,jump_table_entries_are_symbolic_data_not_instruction_arrays=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
