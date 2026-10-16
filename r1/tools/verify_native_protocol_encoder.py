#!/usr/bin/env python3
"""Actual packet encoder, pinned musl movement, native CRC and cold/live state."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-encoder';D=0x20010000;I=0x20024000;S=0x20006b88;T=0x20006ba0;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);reports={};objects=[]
 for module,source in [('native-protocol-encoder','r1/components/board/native_protocol_encoder.c'),('runtime-memmove','third-party/upstream/musl-memmove-1.2.5/memmove.c'),('runtime','third-party/upstream/musl-memory-1.2.5/memcpy.c'),('','r1/source/stock_checksums.c')]:
  path=BASE/module/'report.json';r=json.loads(path.read_text());u=next(u for u in r['units'] if u['source']==source);obj=Path(u['command'][-1]);assert sha(obj)==u['object_sha256'] and sha(ROOT/source)==u['source_sha256'];objects.append(obj);reports[str(path.relative_to(BASE))]=sha(path)
  if module=='native-protocol-encoder':
   for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 p=OUT/'rea-82f9c.json';p.write_bytes((BASE/'native-battery-runtime/rea-next-82f9c-body.json').read_bytes());q=json.loads(p.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==136;evidence[p.name]=sha(p)
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x82f9c&length=140']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x82f9c-0x27000:0x82f9c-0x27000+140];p=OUT/'ghidra-body.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 cold_runs=[]
 for poison in (0xa5,0x5a,0xff,0x3c):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x20000000,0x40000);u.mem_write(0x20000000,bytes([poison])*0x40000);writes=[]
  def writehook(uc,access,address,size,value,_):
   if address<S+2 and address+size>S or address<T+4 and address+size>T:writes.append({'pc':uc.reg_read(UC_ARM_REG_PC),'address':address,'bytes':size,'value':value})
  u.hook_add(UC_HOOK_MEM_WRITE,writehook);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.emu_start(0x283a1,0x27208,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(u.mem_read(S,2))==b'\0\0' and bytes(u.mem_read(T,4))==b'\0ddd';assert writes;cold_runs.append({'poison':poison,'writes':writes})
 machines=[];states={};comparisons=0;counts={'memmove':0,'crc':0};statuses={};sections={}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .sequence 0x20006b88 : { *(.r1.protocol.sequence) } .version_map 0x20006ba0 : { *(.r1.protocol.version_map) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  for n,a,data in [('sequence',S,b'\0\0'),('version_map',T,b'\0ddd')]:
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==data;sections[n]={'address':a,'bytes':len(data),'sha256':sha(p)}
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def hook(u,a,size,_):
   f=states[id(u)]
   if a in (0x2775c,syms['memmove']):f['trace'].append(('memmove',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2)))
   if a in (0x5d87c,syms['r1_stock_crc16_modbus']):
    pointer=u.reg_read(UC_ARM_REG_R0);length=u.reg_read(UC_ARM_REG_R1);assert pointer==f['destination'] and length==((f['length']+12)&65535);f['trace'].append(('crc',length,hashlib.sha256(bytes(u.mem_read(pointer,length))).hexdigest()))
   if u is machines[1] and a<0x1000000 and a!=0x20000100:raise AssertionError(('source native provider',hex(a)))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.mem_write(D,b'\x96'*65536);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  cases=itertools.chain(itertools.product((0,D,S,T-2),(0,1,11,12,19,256,0xffffffff),(0,1,2,3,4,0xffffffff),(0,1,2,0xffffffff),(0,65535),(0,7),(0,I)),((D,512,1,flags,seq,length,D+offset) for flags,seq,length,offset in itertools.product((0,1),(0,65535),(1,7,16,31,64),(-4,0,4,8,12,13,16,31))),((D,19,v,f,0xffff,7,I) for v,f in itertools.product(range(4),range(256))),((D,capacity,1,flags,65535,length,0) for length in (65523,65524,65535,65536,0xffffffff) for capacity in ((length+12)&0xffffffff,(length+12)&65535,1,0xffffffff) for flags in (0,1)))
  for index,(destination,capacity,version,flags,sequence,length,payload) in enumerate(cases):
   expected=2 if not destination or not capacity or version>=4 else 1 if length>((capacity-12)&0xffffffff) else 0;high=(index*37)&0xffffffff;low=(index*71)&0xffffffff;explicit=(index*997)^0xffff0000;results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'destination':destination,'length':length};u.mem_write(D-4,b'\x96'*264);u.mem_write(I,bytes(range(128)));u.mem_write(S-8,b'\xa5'*64);u.mem_write(S,struct.pack('<H',sequence));u.mem_write(T,bytes([0,0x55,0xa5,0xff]));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.mem_write(0x2003f000,struct.pack('<5I',low,flags,explicit,payload,length))
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(destination,capacity,version,high)):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_model_encode'] if candidate else 0x82f9c)|1,0x20000100,count=3000000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    assert u.reg_read(UC_ARM_REG_R0)==expected,(index,destination,capacity,version,flags,length,candidate,u.reg_read(UC_ARM_REG_R0),expected)
    f=states[id(u)];assert len([t for t in f['trace'] if t[0]=='crc'])==int(expected==0) and len([t for t in f['trace'] if t[0]=='memmove'])==int(expected==0 and bool(payload) and bool(length));results.append((bytes(u.mem_read(D-4,264)),bytes(u.mem_read(S-8,64)),bytes(u.mem_read(I,128)),f['trace']))
   assert results[0]==results[1],(index,destination,capacity,version,flags,sequence,length,payload);comparisons+=1;statuses[str(expected)]=statuses.get(str(expected),0)+1
   for event in results[0][-1]:counts[event[0]]+=1
 vp.write_text(json.dumps(dict(comparisons=comparisons,status_counts=statuses,actual_memmove_and_crc=True,provider_calls_per_side=counts,cold_runs=cold_runs,source_owned_sections=sections,provider_reports=reports,driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Capacity<12 unsigned underflow is preserved; mapped backing buffers do not prove physical allocator bounds','Cold sequence/version initialization verified for four poisons; live mutations and overlapping payload/global views tested; warm startup/interrupt ordering/concurrency remain gated','Actual musl movement and recovered CRC execute; original runtime/compiler and whole-image byte identity remain unproven']),indent=2)+'\n');print('Protocol encoder:',comparisons,statuses,counts)
if __name__=='__main__':main()
