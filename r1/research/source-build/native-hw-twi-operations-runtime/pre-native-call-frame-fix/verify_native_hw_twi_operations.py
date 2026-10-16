#!/usr/bin/env python3
"""Packet wrappers; preserve source/native composed-frame pointer counterexample."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-hw-twi-operations-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PTRS=[(44,'r1_hw_twi0_irq',0x70778),(80,'r1_hw_twi0_open',0x55278),(84,'r1_hw_twi0_close',0x55180),(88,'r1_hw_twi0_read',0x55414),(92,'r1_hw_twi0_write',0x55ce0),(152,'r1_hw_twi1_irq',0x707cc),(188,'r1_hw_twi1_open',0x552e4),(192,'r1_hw_twi1_close',0x551b4),(196,'r1_hw_twi1_read',0x55448),(200,'r1_hw_twi1_write',0x55d50)]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_hw_twi_operations_verification.ld';cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert hashlib.sha256(cold).hexdigest()=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317'
 counts=dict(read0=0,read1=0,write0=0,write1=0);hits=dict(register_read=0,register_write=0,tx=0,wait=0);digest=hashlib.sha256();states={};probe=None
 for composed in [False,True]:
  obj=OUT/('hw-operations-register-source.o' if composed else 'hw-operations-source.o');assert sha(obj)==b['composed_object_sha256' if composed else 'graph_object_sha256']
  with tempfile.TemporaryDirectory() as tmp:
   d=Path(tmp);elf=d/'test.elf';cmd=['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)]
   for i,n in enumerate(b['composed_undefined_symbols' if composed else 'graph_undefined_symbols']):cmd+=['--defsym='+n+'='+hex(0x20000401+i*4)]
   subprocess.run(cmd,check=True,capture_output=True);sections={}
   for section in ['text','r1.hw_twi.primary','r1.hw_twi.secondary']:
    p=d/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
   syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3};config=sections['r1.hw_twi.primary']+sections['r1.hw_twi.secondary'];normalized=bytearray(config)
   for off,n,a in PTRS:assert struct.unpack_from('<I',normalized,off)[0]==syms[n]|1;struct.pack_into('<I',normalized,off,a|1)
   stock=cold[0x20006fe8-0x200064a8:0x20006fe8-0x200064a8+216];assert bytes(normalized)==stock
   lower={'nrfx_twim_tx':'tx','r1_twi_primary_wait_adapter':'wait','r1_twi_secondary_wait_adapter':'wait'};native_hooks={0x7b3a0:'tx',0x70820:'wait',0x7088c:'wait'}
   if composed:lower.update(nrfx_twim_rx='rx',r1_adc_error='log');native_hooks.update({0x7b370:'rx',0x4e5bc:'log'})
   else:
    lower.update(r1_twi_primary_register_read_adapter='register_read',r1_twi_secondary_register_read_adapter='register_read',r1_twi_primary_register_write_adapter='register_write',r1_twi_secondary_register_write_adapter='register_write');native_hooks.update({0x54ff8:'register_read',0x550c0:'register_read',0x5505c:'register_write',0x55120:'register_write'})
   source_hooks={syms[n]&~1:k for n,k in lower.items()}
   def hook(u,a,size,_):
    st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
    kind=(source_hooks if source else native_hooks).get(a)
    if not kind:assert a<0x20000400 or a>=0x20000500;return
    args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['result'];event=[kind]
    if kind.startswith('register_'):event += [args,struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0]]
    elif kind=='tx':event += [args,struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0],bytes(u.mem_read(args[2],args[3])).hex(),bytes(u.mem_read(args[2],4)).hex()]
    elif kind=='wait':event += [args[0]]
    elif kind=='rx':event += [args]
    elif kind=='log':event += [args[0]]
    if st['mutation']==1:u.mem_write(0x20002000,bytes([0xfa])*20)
    if st['mutation']==2:u.mem_write(st['base']+12+4,b'\x00');u.mem_write(st['base'],b'\xff')
    st['events'].append(event)
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[ret,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   machines=[]
   for source in range(2):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
   functions=[('read0','r1_hw_twi0_read',0x55414,0,True),('read1','r1_hw_twi1_read',0x55448,1,True),('write0','r1_hw_twi0_write',0x55ce0,0,False),('write1','r1_hw_twi1_write',0x55d50,1,False)]
   cases=[(key,name,native,bus,read,opened,null,reg,length,result,seed,mutation) for key,name,native,bus,read in functions for opened,null,reg,length,result,seed,mutation in itertools.product([0,1,255],[False,True],[0,255,256,65535],[0,1,2,79,80,81,255,256,257,65535],[0,1,256,0xffffffff],[0,0x55,0xaa,255],range(3))] if not composed else [('read0','r1_hw_twi0_read',0x55414,0,True,1,False,34,1,0,0,0)]
   saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
   for number,case in enumerate(cases):
    key,name,native,bus,read,opened,null,reg,length,result,seed,mutation=case;outputs=[];base=0x20006fe8+bus*108
    for source,u in enumerate(machines):
     u.mem_write(0x20000000,bytes([seed])*0x40000);u.mem_write(0x20006fe8,config if source else stock);u.mem_write(base+16,bytes([opened]));request=bytearray(20);request[0]=(number*7)&255;struct.pack_into('<H',request,2,reg);struct.pack_into('<I',request,4,0x20004000);struct.pack_into('<H',request,8,length);struct.pack_into('<I',request,12,0x20004000);struct.pack_into('<H',request,16,length);u.mem_write(0x20002000,bytes(request));u.mem_write(0x20004000,bytes((i+seed)&255 for i in range(128)));states[id(u)]=dict(source=source,events=[],result=result,mutation=mutation,base=base)
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for register,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0xdeadbeef,0x11223344,0 if null else 0x20002000,0x99aabbcc^(seed<<16)]):u.reg_write(register,value)
     for i,register in enumerate(saved):u.reg_write(register,0x12345600+i)
     u.emu_start((syms[name] if source else native)|1,0x20000100,count=20000)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(register) for register in saved]==[0x12345600+i for i in range(8)]
     mem=bytearray(u.mem_read(0x20000000,0x3e000))+bytearray(u.mem_read(0x2003f000,0x1000))
     if source:
      for off,n,a in PTRS:assert struct.unpack_from('<I',mem,0x6fe8+off)[0]==syms[n]|1;struct.pack_into('<I',mem,0x6fe8+off,a|1)
     regs=[u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R3)]
     if not read:regs.append(u.reg_read(UC_ARM_REG_R2))
     outputs.append([regs,states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
    if composed:
     assert outputs[0][0]==outputs[1][0] and outputs[0][2]==outputs[1][2]
     tx=[next(e for e in out[1] if e[0]=='tx') for out in outputs];assert tx[0][1][2]!=tx[1][1][2] and tx[0][3]==tx[1][3]
     probe=dict(matched=False,kind='actual_register_caller_graph_tx_buffer_address',outputs=outputs,native_tx_buffer=tx[0][1][2],source_tx_buffer=tx[1][1][2],raw_r0_r3_and_nonstack_ram_match=True,payload_byte_matches=True,no_pointer_normalization=True,composed_object_sha256=b['composed_object_sha256'],driver_sha256=sha(Path(__file__)));(OUT/'composed-frame-probe.json').write_text(json.dumps(probe,indent=2)+'\n');continue
    if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=case,outputs=outputs),indent=2)+'\n');raise AssertionError(number)
    counts[key]+=1
    for event in outputs[0][1]:hits[event[0]]+=1
    digest.update(json.dumps([number,case,outputs[0]],sort_keys=True).encode())
 assert all(hits.values()) and probe is not None
 r=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=hits,trace_sha256=digest.hexdigest(),actual_packet_wrappers=True,register_tx_wait_are_explicit_fixtures=True,packet_width_and_fullword_error_mapping_checked=True,one_byte_direct_write_and_control_flag_asymmetry_checked=True,saved_r2_r3_and_early_return_words_checked=True,raw_r0_callee_sp_nonstack_ram_checked=True,no_native_candidate_execution=True,composed_register_frame_identity_verified=False,composed_probe_sha256=sha(OUT/'composed-frame-probe.json'),full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,metadata_operation_abi_migrated=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=b['graph_object_sha256'],layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
