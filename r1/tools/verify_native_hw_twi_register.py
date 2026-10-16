#!/usr/bin/env python3
"""Register adapters with exact external frames; SDK/wait/logging fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-hw-twi-register-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PTRS=[(44,'r1_hw_twi0_irq',0x70778),(80,'r1_hw_twi0_open',0x55278),(84,'r1_hw_twi0_close',0x55180),(88,'r1_hw_twi0_read',0x55414),(92,'r1_hw_twi0_write',0x55ce0),(152,'r1_hw_twi1_irq',0x707cc),(188,'r1_hw_twi1_open',0x552e4),(192,'r1_hw_twi1_close',0x551b4),(196,'r1_hw_twi1_read',0x55448),(200,'r1_hw_twi1_write',0x55d50)]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'hw-register-source.o';assert sha(obj)==b['graph_object_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_hw_twi_register_verification.ld';cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert hashlib.sha256(cold).hexdigest()=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317'
 counts=dict(read0=0,read1=0,write0=0,write1=0);hits=dict(tx=0,rx=0,wait=0,log=0,write80_saved_r4=0);states={};digest=hashlib.sha256()
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';cmd=['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)]
  for i,n in enumerate(b['graph_undefined_symbols']):cmd+=['--defsym='+n+'='+hex(0x20000401+i*4)]
  subprocess.run(cmd,check=True,capture_output=True);sections={}
  for section in ['text','r1.hw_twi.primary','r1.hw_twi.secondary']:
   p=d/(section+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
  syms={x[2]:int(x[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x:=line.split())==3};config=sections['r1.hw_twi.primary']+sections['r1.hw_twi.secondary'];normalized=bytearray(config)
  for off,n,a in PTRS:assert struct.unpack_from('<I',normalized,off)[0]==syms[n]|1;struct.pack_into('<I',normalized,off,a|1)
  stock=cold[0x20006fe8-0x200064a8:0x20006fe8-0x200064a8+216];assert bytes(normalized)==stock
  lower={'nrfx_twim_tx':'tx','nrfx_twim_rx':'rx','r1_twi_primary_wait_adapter':'wait','r1_twi_secondary_wait_adapter':'wait','r1_adc_error':'log'};source_hooks={syms[n]&~1:k for n,k in lower.items()};native_hooks={0x7b3a0:'tx',0x7b370:'rx',0x70820:'wait',0x7088c:'wait',0x4e5bc:'log'}
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   kind=(source_hooks if source else native_hooks).get(a)
   if not kind:assert a<0x20000400 or a>=0x20000500;return
   args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];event=[kind];ret=0
   if kind=='tx':
    stop=struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0];assert stop==int(st['read']);assert args[0]==st['instance']+4
    buf=args[2];st['buffer']=buf;assert buf==(0x2003efdc if st['read'] else 0x2003ef9c)
    event += [args,stop,bytes(u.mem_read(buf,args[3])).hex()]
    if st['read']:event += [bytes(u.mem_read(buf,4)).hex()]
    ret=st['sequence'][min(st['ti'],len(st['sequence'])-1)];st['ti']+=1;event += [ret]
    if st['mutation']==1:u.mem_write(st['base'],b'\x01');u.mem_write(st['base']+1,b'\xff')
   elif kind=='rx':
    assert args[0]==st['instance']+4;event += [args];ret=st['rx']
    u.mem_write(args[2],bytes([0x9a])*min(args[3],16))
   elif kind=='wait':
    ret=st['waits'][min(st['wi'],1)];st['wi']+=1;event += [args[0],ret]
    if st['mutation']==1:u.mem_write(st['base'],b'\x01')
   elif kind=='log':
    event += [args[0]]
    if st['mutation']==2:
     u.mem_write(st['buffer'],b'\xe7');u.mem_write(0x20003000,bytes([0xfa])*128);u.mem_write(st['base'],b'\xff')
   st['events'].append(event)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[ret,0x11223344,0x55667788,0x99aabbcc]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  functions=[('read0','r1_twi_primary_register_read_adapter',0x54ff8,0,True),('read1','r1_twi_secondary_register_read_adapter',0x550c0,1,True),('write0','r1_twi_primary_register_write_adapter',0x5505c,0,False),('write1','r1_twi_secondary_register_write_adapter',0x55120,1,False)]
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];number=0
  for key,name,native,bus,read in functions:
   for length,reg,sequence,waits,seed,mutation in itertools.product(([0,1,49,50,255,256,65535,0xffffffff] if read else [0,1,2,79,80,81,255,0xffffffff]),[0,255,256,65535],[[0],[17],[1,0],[0x100,0],[0xffffffff,2,0]],[[0,0],[1,0],[0,0x100],[0xffffffff,0]],[0,0x55,0xaa,255],range(3)):
    outputs=[];base=0x20006fe8+bus*108;instance=base+28;rx=[0,1,256,0xffffffff][(number//4)%4]
    for source,u in enumerate(machines):
     u.mem_write(0x20000000,bytes([seed])*0x40000);u.mem_write(0x20006fe8,config if source else stock);u.mem_write(0x20003000,bytes((i+seed)&255 for i in range(128)));u.mem_write(0x2003f000,struct.pack('<I',instance))
     states[id(u)]=dict(source=source,read=read,events=[],instance=instance,base=base,sequence=sequence,ti=0,waits=waits,wi=0,rx=rx,mutation=mutation,buffer=None)
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for register,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[(number*17)&255,reg,0x20003000,length]):u.reg_write(register,value)
     for i,register in enumerate(saved):u.reg_write(register,0x12345600+i)
     u.emu_start((syms[name] if source else native)|1,0x20000100,count=20000)
     callee=[u.reg_read(register) for register in saved];expected=[0x12345600+i for i in range(8)]
     if not read and length==80:expected[0]=0x12345600|((79+seed)&255)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and callee==expected,(number,callee,expected)
     mem=bytearray(u.mem_read(0x20000000,0x3e000))+bytearray(u.mem_read(0x2003f000,0x1000))
     if source:
      for off,n,a in PTRS:assert struct.unpack_from('<I',mem,0x6fe8+off)[0]==syms[n]|1;struct.pack_into('<I',mem,0x6fe8+off,a|1)
     regs=[u.reg_read(UC_ARM_REG_R0),callee]
     if read:regs += [u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3)]
     outputs.append([regs,states[id(u)]['events'],hashlib.sha256(mem).hexdigest()])
    if outputs[0]!=outputs[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[key,length,reg,sequence,waits,seed,mutation,rx],outputs=outputs),indent=2)+'\n');raise AssertionError(number)
    counts[key]+=1;hits['write80_saved_r4']+=int(not read and length==80)
    for event in outputs[0][1]:hits[event[0]]+=1
    digest.update(json.dumps([number,key,length,reg,sequence,waits,seed,mutation,rx,outputs[0]],sort_keys=True).encode());number+=1
 assert all(hits.values())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=hits,trace_sha256=digest.hexdigest(),actual_four_product_adapters=True,only_nrfx_wait_error_are_fixtures=True,external_read_register_frame_and_saved_r2_r3_checked=True,write80_saved_r4_overwrite_preserved=True,read_length_width_and_timeout_asymmetry_checked=True,write_retry17_and_full_error_status_checked=True,retry_uses_original_copied_buffer_with_mutations=True,raw_r0_callee_sp_nonstack_ram_checked=True,no_native_candidate_execution=True,all_address_fullwords_verified=False,unbounded_retry_termination_proven=False,full_raw_abi_verified=False,cross_call_private_frame_history_verified=False,sdk_hardware_transfer_verified=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app))
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
