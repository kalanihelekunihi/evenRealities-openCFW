#!/usr/bin/env python3
"""Actual source formatting, clearing, getter and response header composition."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-device-info';SP=0x2003f000;I=0x20010000;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'formatting-integration-verification.json';vp.unlink(missing_ok=True);reports={};objects=[]
 for module,filename in [('native-protocol-device-info','native_protocol_device_info.o'),('native-protocol-response-header','native_protocol_response_header.o'),('connection-handle','connection_handle.o')]:
  p=BASE/module/'report.json';r=json.loads(p.read_text());unit=r['units'][0];obj=p.parent/filename;assert sha(obj)==unit['object_sha256'] and sha(ROOT/unit['source'])==unit['source_sha256'];objects.append(obj);reports[module+'/report.json']=sha(p)
  for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
 p=BASE/'runtime/report.json';r=json.loads(p.read_text())
 for source,filename in [('r1/components/runtime/memory_eabi.c','memory_eabi.o'),('third-party/upstream/musl-memory-1.2.5/memset.c','memset.o'),('third-party/upstream/musl-memory-1.2.5/memcpy.c','memcpy.o')]:
  unit=next(unit for unit in r['units'] if unit['source']==source);obj=p.parent/filename;assert sha(obj)==unit['object_sha256'] and sha(ROOT/source)==unit['source_sha256'];objects.append(obj)
 reports['runtime/report.json']=sha(p);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';rows=[row for row in csv.DictReader(ledger.open()) if row['image']=='application' and row['entry'] in ('0x00083d5c','0x00083872')];assert len(rows)==2;evidence={}
 old=OUT/'verification.json';prior=json.loads(old.read_text());reports['native-protocol-device-info/verification.json']=sha(old);evidence=prior['evidence']
 for name,digest in evidence.items():assert sha(OUT/name)==digest,name
 for directory,name in [('native-formatter-engine','native-formatter-engine.o'),('native-formatter-wrappers','native_formatter_wrappers.o')]:
  p=BASE/directory/'report.json';r=json.loads(p.read_text());obj=p.parent/name;assert sha(obj)==(r.get('linked_sha256') or r['units'][0]['object_sha256']);objects.append(obj);reports[directory+'/report.json']=sha(p)
  for path,digest in r['inputs'].items():assert sha(ROOT/path)==digest,path
 machines=[];states={};counts={'info':0,'wrapper':0};calls={'clear':0,'format':0,'lower':0};r1_differences=0;null_faults=0;trace_hash=hashlib.sha256();sections={}
 with tempfile.TemporaryDirectory() as temporary:
  d=Path(temporary);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .flags 0x43480 : { *(.r1.format.flags) } .lower 0x43484 : { *(.r1.format.lower) } .upper 0x43498 : { *(.r1.format.upper) } .minus 0x43728 : { *(.r1.format.minus) } .plus 0x4372c : { *(.r1.format.plus) } .space 0x43730 : { *(.r1.format.space) } .zero 0x3f6a8 : { *(.r1.format.decimal_zero) } .firmware 0x83d94 : { *(.r1.protocol_info.firmware) } .format 0x83da0 : { *(.r1.protocol_info.format) } .hardware 0x83da4 : { *(.r1.protocol_info.hardware) } .connection6 0x200064b8 : { *(.r1.connection.field6) } .connection8 0x200064ba : { *(.r1.connection.field8) } .connection10 0x200064bc : { *(.r1.connection.field10) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_protocol_send_response=0x1100011',*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for name,address,size in [('firmware',0x83d94,11),('format',0x83da0,3),('hardware',0x83da4,11)]:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[address-0x27000:address-0x27000+size];sections[name]={'address':address,'bytes':size,'sha256':sha(p)}
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=(access,address,size);return False
  def hook(u,address,size,_):
   f=states[id(u)];regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if address in (0x277aa,syms['__aeabi_memclr']):assert regs[:2]==[SP-40,32];f['calls']['clear']+=1;f['trace'].append(('clear',*regs[:2]));return
   if address in (0x38080,syms['snprintf']):
    index=f['format_calls'];source=0x83d94 if index==0 else 0x83da4;assert regs==[SP-40+index*16,16,0x83da0,source];assert index<2
    if index==0:assert bytes(u.mem_read(SP-40,32))==b'\0'*32
    else:assert bytes(u.mem_read(SP-40,16))==b'2.2.6.0009\0'+b'\0'*5
    f['trace'].append(('format',index));f['format_calls']+=1;f['calls']['format']+=1;return
   else:
    header=bytes(u.mem_read(regs[1],8));payload=bytes(u.mem_read(regs[2],32));sequence=struct.unpack('<H',bytes(u.mem_read(f['packet']+3,2)))[0] if f['kind']=='info' else f['second']&65535;expected_header=struct.pack('<II',0x02000100|(((f['first']^1)|2)&255),sequence);assert regs[0]==f['handle'] and regs[3]==32 and header==expected_header
    if f['kind']=='info':assert regs[2]==SP-40
    f['trace'].append(('lower',regs[0],header.hex(),payload.hex()));f['calls']['lower']+=1;value=f['lower_raw']
    if f['mutation']==2:u.mem_write(regs[2],bytes(byte^0xa5 for byte in payload));u.mem_write(regs[1],b'\x5a'*8)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(value,0x11111111,0x22222222,0x33333333)):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
   for address in (0x277aa,syms['__aeabi_memclr'],0x38080,syms['snprintf'],0x828b4,0x1100010):u.hook_add(UC_HOOK_CODE,hook,begin=address,end=address)
   if len(machines)==2:
    def reject(u,address,size,_):
     if address!=0x828b4:raise AssertionError(('source executed native',hex(address)))
    u.hook_add(UC_HOOK_CODE,reject,begin=0x20000,end=0xe0000)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  info=(('info',I,1,0,sequence,0,10,0,0) for sequence in range(65536))
  info_edges=(('info',I,handle,0,sequence,0,10,mutation,lower) for handle,sequence,mutation,lower in itertools.product((0,1,65535),(0,1,255,256,65535),(0,2),(0,7,0xffffffff)))
  alias=(('info',packet,1,0,0,0,10,0,lower) for packet,lower in itertools.product((SP-40,SP-39,SP-24,SP-16,SP-8),(0,7)))
  wrapper=[];wrapper_edges=[]
  nulls=[('info',0,1,0,0,0,10,0,0)]
  for index,(kind,packet,handle,first,second,format_mode,format_raw,mutation,lower_raw) in enumerate(itertools.chain(info,info_edges,alias,wrapper,wrapper_edges,nulls)):
   results=[];incoming3=0x87654321
   for candidate,u in enumerate(machines):
    u.mem_write(I,b'\xa5'*64);u.mem_write(I+3,struct.pack('<H',second&65535));u.mem_write(SP-1024,b'\x96'*2048);u.mem_write(SP-8,struct.pack('<II',0x12345600,0x20000101));u.mem_write(0x200064ba,struct.pack('<H',handle));u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);states[id(u)]={'kind':kind,'packet':packet,'handle':handle,'first':first,'second':second,'format_mode':format_mode,'format_raw':format_raw,'mutation':mutation,'lower_raw':lower_raw,'format_calls':0,'calls':dict.fromkeys(calls,0),'trace':[],'fault':None}
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),([index,packet,second,incoming3] if kind=='info' else [packet,first,second,incoming3])):u.reg_write(reg,value)
    for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
    entry=syms['r1_device_info_handler' if kind=='info' else 'r1_system_response_wrapper'] if candidate else 0x83d5c if kind=='info' else 0x83872
    try:u.emu_start(entry|1,0x20000100,count=50000)
    except UcError:assert kind=='info' and not packet and states[id(u)]['fault']==(19,3,2)
    f=states[id(u)]
    if f['fault']:results.append(('fault',f['fault'],f['trace'],f['calls']));continue
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)];regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];expected0=int(bool((kind=='info' or packet) and handle!=65535 and lower_raw==0));assert regs[0]==expected0 and regs[2:]==([SP-40,32] if kind=='info' else [packet,32] if packet else [second,incoming3]);assert f['format_calls']==(2 if kind=='info' else 0);results.append((regs,f['trace'],f['calls'],bytes(u.mem_read(I,64)),bytes(u.mem_read(SP-40,32)) if kind=='info' else None))
   if results[0][0]=='fault':assert results[0]==results[1];null_faults+=1
   else:
    if results[0][0][1]!=results[1][0][1]:r1_differences+=1
    comparable=lambda item:([item[0][0],*item[0][2:]],*item[1:]);assert comparable(results[0])==comparable(results[1]),(index,kind,packet,handle,first,second,format_mode,format_raw,mutation,lower_raw,results)
   counts[kind]+=1
   for name,count in results[0][3 if results[0][0]=='fault' else 2].items():calls[name]+=count
   trace_hash.update(json.dumps((kind,packet,handle,first,second,format_mode,format_raw,mutation,lower_raw,results[0]),default=lambda value:value.hex()).encode())
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,provider_calls_per_side=calls,all_info_sequence_halfwords=True,actual_source_formatting=True,formatting_boundary_fixture=False,actual_upstream_clear=True,actual_connection_getter_and_header=True,r0_r2_r3_checked=True,r1_scratch_differences=r1_differences,native_info_frame40=True,null_header_faults=null_faults,source_owned_metadata=sections,trace_sha256=trace_hash.hexdigest(),ownership_rows=rows,ownership_sha256=sha(ledger),evidence=evidence,provider_reports=reports,driver_sha256=sha(Path(__file__)),application_sha256=ah,application_linked=False,instruction_identity=False,limitations=['Actual source snprintf, parser, arithmetic and bounded callback execute; generic formatter proof is separately bound to its provider receipts','Device-info54-byte entry has locked manual row without extent; Ghidra-MCP native body/calls and return boundary supply extent; REA entry unavailable','Actual upstream memclear/memset and shared getter/header execute; lowerresponse remains a fixture','Caller-savedr1 is observed separately, not source-equivalence proof; private Cstack outside native40-byte buffer and othercompiler/LTO remain gated','Metadata is locked stock identity, not a released OpenCFW version; no fullstartup/hardware/delivery/imageidentity proof']),indent=2)+'\n');print('Protocol device info with source formatting:',counts,calls,'r1 scratch differences',r1_differences,'faults',null_faults)
if __name__=='__main__':main()
