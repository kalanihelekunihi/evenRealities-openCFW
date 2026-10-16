#!/usr/bin/env python3
"""Actual operation/header/connection composition with lower response fixture."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-phone-operation';I=0x20002000;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_phone_cmd_send_op1':(0x83896,36),'r1_protocol_response_send_0x100':(0x84c0c,82)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);reports={};objects=[]
 for module,filename in [('native-phone-operation','native_phone_operation.o'),('native-protocol-response-header','native_protocol_response_header.o'),('connection-handle','connection_handle.o')]:
  path=BASE/module/'report.json';r=json.loads(path.read_text());obj=path.parent/filename;assert sha(obj)==r['units'][0]['object_sha256'];objects.append(obj);reports[module+'/report.json']=sha(path)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={};socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 for n,(a,z) in ENTRIES.items():
  p=OUT/f'rea-{a:x}.json';p.write_bytes((BASE/'native-battery-runtime'/f'rea-next-{a:x}-body.json').read_bytes());q=json.loads(p.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(a) and q['normalized_result']['body']['total_bytes']==z;evidence[p.name]=sha(p)
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/f'ghidra-{a:x}.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 machines=[];states={};counts={n:0 for n in ENTRIES};lower_calls=0;null_inputs=0
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .connection6 0x200064b8 : { *(.r1.connection.field6) } .connection8 0x200064ba : { *(.r1.connection.field8) } .connection10 0x200064bc : { *(.r1.connection.field10) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_protocol_send_response=0x1100001',*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def hook(u,a,size,_):
   f=states[id(u)]
   if a in (0x4cba4,syms['r1_phone_connection_handle_get']):f['connection_reads']+=1;u.mem_write(0x200064ba,struct.pack('<H',f['handle']&65535))
   if a in (0x84c0c,syms['r1_protocol_response_send_0x100']):
    f['header_calls']+=1
    if f['top']=='r1_phone_cmd_send_op1':
     args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];stack=struct.unpack('<2I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),8)));assert args==[f['handle']&65535,1,f['first'],f['second']] and stack==(f['pointer'],7)
   if a not in (0x828b4,0x1100000):
    if u is machines[1] and a<0x1000000 and a!=0x20000100:raise AssertionError(('source native provider',hex(a)))
    return
   args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert args[0]==f['effective_handle'] and args[2:]==[f['pointer'],f['effective_length']];header=bytes(u.mem_read(args[1],8));assert header==f['expected_header'];f['lower_calls']+=1;f['trace'].append((args[0],header,args[2],args[3]))
   if f['mutation']:f['expected_header']=bytes((i*31+7)&255 for i in range(8));u.mem_write(args[1],f['expected_header']);u.mem_write(I,b'\x39'*8)
   u.reg_write(UC_ARM_REG_R0,f['raw']);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_R2,0x76543210);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  # Tuple: top, operation, first, second, handle, raw, mutation, pointer, length, incoming-r3.
  cases=itertools.chain((('r1_protocol_response_send_0x100',op,op&255,op^0xa5a5,1,0 if op&1 else 0xffffffff,False,I,7,0) for op in range(65536)),(('r1_protocol_response_send_0x100',op,first,second,handle,raw,mutation,pointer,length,0) for op,first,second,handle,raw,mutation,pointer,length in itertools.product((0,1,0x1234,0x10000,0xffffffff),(0,1,2,0xffffffff),(0,1,65535,65536,0xffffffff),(0,1,65535,65536,0xffff0000,0xffffffff),(0,1,0x80000000,0xffffffff),(False,True),(0,I),(0,7,0xffffffff))),(('r1_phone_cmd_send_op1',1,first,second,handle,raw,mutation,pointer,7,incoming3) for first,second,handle,raw,mutation,pointer,incoming3 in itertools.product((0,1,2,0xffffffff),(0,1,65535,65536,0xffffffff),(0,1,65535,65536),(0,1,0x80000000,0xffffffff),(False,True),(0,I),(0,0x12345678,0xffffffff))))
  for top,op,first,second,handle,raw,mutation,pointer,length,incoming3 in cases:
   wrapper=top=='r1_phone_cmd_send_op1';effective_handle=handle&65535 if wrapper else handle;called=bool(pointer) if wrapper else True;sent=called and effective_handle!=65535;expected=int(raw==0) if sent else 0;header_word=(((first^1)|2)&255)|0x100|(((op>>8)&255)<<16)|((op&255)<<24);header=struct.pack('<II',header_word,second&65535);results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'top':top,'handle':handle,'effective_handle':effective_handle,'effective_length':7 if wrapper else length,'first':first,'second':second,'pointer':pointer,'raw':raw,'mutation':mutation,'expected_header':header,'connection_reads':0,'header_calls':0,'lower_calls':0,'trace':[]};u.mem_write(I,b'\xa5'*8);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    args=(pointer,first,second,incoming3) if wrapper else (handle,op,first,second)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
    if not wrapper:u.mem_write(0x2003f000,struct.pack('<II',pointer,length))
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms[top] if candidate else ENTRIES[top][0])|1,0x20000100,count=2000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    if not wrapper:assert bytes(u.mem_read(0x2003f000,8))==struct.pack('<II',pointer,length)
    f=states[id(u)];expected_regs=[pointer,7] if wrapper and called else [second,incoming3] if wrapper else list(struct.unpack('<II',f['expected_header'])) if sent else [first,second];assert [u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3)]==expected_regs and u.reg_read(UC_ARM_REG_R0)==expected,(top,op,first,second,handle,raw,mutation,pointer,candidate)
    assert f['connection_reads']==int(wrapper and called) and f['header_calls']==int(called) and f['lower_calls']==int(sent);results.append((f['trace'],bytes(u.mem_read(I,8)),expected_regs))
   assert results[0]==results[1];counts[top]+=1;lower_calls+=int(sent);null_inputs+=int(wrapper and not pointer)
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,all_operation_halfwords=True,lower_calls=lower_calls,null_wrapper_inputs=null_inputs,actual_connection_getter=True,actual_header_wrapper=True,incoming_stack_arguments_unchanged=True,full_r2_r3_checked=True,raw_lower_zero_maps_to_one=True,provider_reports=reports,driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Lower response sender is fixture; incoming stack argument slots are read-only under authenticated common wrapper','Source saved-word/register boundary verified for selected compiler; other compilers/LTO and wrapper-stack-overlapping payloads require revalidation','Connection/state initialization, lower transport delivery and original image identity remain gates']),indent=2)+'\n');print('Phone operation/header:',counts,'lower calls',lower_calls,'null wrapper',null_inputs)
if __name__=='__main__':main()
