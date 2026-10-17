#!/usr/bin/env python3
"""Native read policy/mapped copy with callback mutation and overlap oracles."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-internal-flash-read-frames';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;RECORD=0x20006f98;CONTEXT=0x20007dc0;REQ=0x20010000;DATA=0x20018000;BEFORE=0x20001000;AFTER=0x20001010
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 obj=OUT/'native_internal_flash_read_frames.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts={'policy':0,'copy':0,'faults':0,'before_calls':0,'after_calls':0}
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS { .policy 0x54a4c : { *(.text.r1_internal_flash_device_read) } .copy 0x5c464 : { *(.text.r1_internal_flash_mapped_read) } /DISCARD/ : { *(.ARM.exidx*) } }\nr1_internal_flash_record = 0x20006f98; r1_internal_flash_context = 0x20007dc0;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacement=[]
  for name,a,length in [('policy',0x54a4c,64),('copy',0x5c464,28)]:
   p=td/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);d=p.read_bytes();assert len(d)==length and d==image[a-0x27000:a-0x27000+length];replacement.append((a,d))
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size,value];return False
  def hook(u,a,size,_):
   if a not in [BEFORE,AFTER,AFTER+16]:return
   s=states[id(u)];c=s['case'];s['trace'].append([a,[u.reg_read(x) for x in REGS]])
   if a==BEFORE and c['mutation']:
    u.mem_write(REQ,struct.pack('<III',DATA+160,128,0x10003));u.mem_write(RECORD+16,struct.pack('<I',AFTER+17));u.mem_write(CONTEXT+12,struct.pack('<I',DATA+8))
   for r,v in zip(REGS,[0x89abcdef,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(r,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacement:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  cases=[dict(kind='policy',init=init,enabled=enabled,null=null,before=before,after=after,mutation=mutation,length=length,delta=delta) for init,enabled,null,before,after,mutation,length,delta in itertools.product([0,1,255],[0,1,255],range(2),range(2),range(2),range(2),[0,1,4,31,0x10000,0x10001,0xffff0004],[-1,0,1])]
  cases += [dict(kind='copy',init=1,enabled=0,null=0,before=1,after=1,mutation=0,length=length,delta=delta) for length,delta in itertools.product(range(66),[-4,-1,0,1,4,64])]
  for c in cases:
   results=[];should_call=c['kind']=='policy' and not c['null'] and c['init'] and c['enabled'];should_fault=bool(should_call and (not c['before'] or not c['after'] and not c['mutation']));initial=bytes(i%251 for i in range(512));expected=bytearray(initial)
   if c['kind']=='copy' or not c['null'] and c['init']:
    if should_call and c['mutation']:src=136;dest=160;length=3
    else:src=128;dest=128+c['delta'];length=c['length'] if c['kind']=='copy' else c['length']&65535
    if not should_fault:
     for i in range(length):expected[dest+i]=expected[src+i]
   for u in machines:
    u.mem_write(DATA,initial);u.mem_write(RECORD,bytes(80));u.mem_write(RECORD+4,bytes([c['init']]));u.mem_write(RECORD+8,bytes([c['enabled']]));u.mem_write(RECORD+12,struct.pack('<II',BEFORE+1 if c['before'] else 0,AFTER+1 if c['after'] else 0));u.mem_write(CONTEXT,bytes(20));u.mem_write(CONTEXT+12,struct.pack('<I',DATA));u.mem_write(REQ,struct.pack('<III',DATA+128+c['delta'],128,c['length']));u.mem_write(SP-256,b'\x96'*512)
    args=[DATA+128+c['delta'],c['length'],128,0xabcdef01] if c['kind']=='copy' else [0x12345678,0x87654321,0 if c['null'] else REQ,0xabcdef01]
    for r,v in zip(REGS,args):u.reg_write(r,v)
    for i,r in enumerate(SAVED):u.reg_write(r,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=c,trace=[],fault=None);states[id(u)]=s
    try:u.emu_start(0x5c465 if c['kind']=='copy' else 0x54a4d,0x20000100,count=100000)
    except UcError as e:
     if not s['fault']:s['fault']=['engine',e.errno,u.reg_read(UC_ARM_REG_PC)]
    assert bool(s['fault'])==should_fault,(c,s['fault'])
    if not s['fault']:
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(r) for r in SAVED]==[0x12340000+i for i in range(8)] and bytes(u.mem_read(DATA,512))==expected,c
     if c['kind']=='policy':assert u.reg_read(UC_ARM_REG_R0)==(26 if c['null'] else 27 if not c['init'] else 0)
    results.append([[u.reg_read(r) for r in REGS],u.reg_read(UC_ARM_REG_SP),s['trace'],s['fault'],bytes(u.mem_read(DATA,512)).hex(),bytes(u.mem_read(RECORD,80)).hex(),bytes(u.mem_read(CONTEXT,20)).hex(),bytes(u.mem_read(REQ,12)).hex(),bytes(u.mem_read(SP-256,512)).hex()])
   assert results[0]==results[1],c;counts[c['kind']]+=1;counts['faults']+=int(should_fault);counts['before_calls']+=sum(x[0]==BEFORE for x in results[0][2]);counts['after_calls']+=sum(x[0] in [AFTER,AFTER+16] for x in results[0][2]);digest.update(json.dumps([c,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=len(cases),counts=counts,trace_sha256=digest.hexdigest(),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),application_sha256=sha(app),actual_read_policy_and_mapped_copy_execute=True,read_io_provider_is_fixture=False,mapped_data_and_before_after_callbacks_are_fixtures=True,bytewise_overlap_low16_length_and_callback_mutation_oracle=True,native_null_callback_faults_retained=True,shared_state_native_addresses_are_verification_bindings=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'direct-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
