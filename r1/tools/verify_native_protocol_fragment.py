#!/usr/bin/env python3
"""Execute fragmenter with real CRC32/musl memmove, mutable callbacks and logs."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-fragment';I=0x20010000;CELL=0x20006960;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_1':0x799c8,'nrf_log_frontend_std_2':0x799d6}
DESCRIPTORS=[('large_ring',0x32524,36),('large_sdk',0x32548,27),('remaining_ring',0x32568,26),('remaining_sdk',0x32584,17)]
def crc32(data):
 c=0
 for byte in data:
  c^=byte<<24
  for _ in range(8):c=((c<<1)^(0x1edc6f41 if c&0x80000000 else 0))&0xffffffff
 return c
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);objects=[];reports={}
 for module,source in [('native-protocol-fragment','r1/components/board/native_protocol_fragment.c'),('runtime-memmove','third-party/upstream/musl-memmove-1.2.5/memmove.c'),('runtime','third-party/upstream/musl-memory-1.2.5/memcpy.c'),('','r1/source/stock_checksums.c')]:
  path=BASE/module/'report.json';r=json.loads(path.read_text());unit=next(u for u in r['units'] if u['source']==source);obj=Path(unit['command'][-1]);assert sha(obj)==unit['object_sha256'] and sha(ROOT/source)==unit['source_sha256'];objects.append(obj);reports[str(path.relative_to(BASE))]=sha(path)
  if module=='native-protocol-fragment':
   for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={};ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';row=next(r for r in csv.DictReader(ledger.open()) if r['image']=='application' and int(r['entry'],16)==0x32408);assert int(row['size'])==272 and int(row['end'],16)==0x32519
 gap=OUT/'rea-boundary-gap.json';assert json.loads(gap.read_text())['error']['code']=='invalid_request';evidence[gap.name]=sha(gap)
 for label,address,length in [('body-data',0x32408,400),('registration-target',0x830a8,96)]:
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket','/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock','http://localhost/read_memory?program=stock-r1-native-analysis.elf&address='+hex(address)+'&length='+str(length)]);assert bytes(json.loads(raw)['data'])==app.read_bytes()[address-0x27000:address-0x27000+length];p=OUT/('ghidra-'+label+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 assert struct.unpack_from('<I',app.read_bytes(),0x83100-0x27000)[0]==0x32409
 assert app.read_bytes()[0x32486-0x27000:0x32488-0x27000]==bytes.fromhex('00bf')
 comparisons=0;counts={'crc':0,'memmove':0,'callback':0,'mode':0,'ring':0,'std1':0,'std2':0};statuses={};sections={};machines=[];states={}
 modes=[(0,),(1,),(2,),(3,),(4,),(5,),(6,),(7,),(0,4,2),(0,0,2),(1,2),(4,0,0),(0xffffffff,)]
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={name:0x1100001+16*i for i,name in enumerate(P)}
  ld.write_text('SECTIONS { '+''.join('.'+name+' '+hex(a)+' : { *(.r1.fragment.'+name+') } ' for name,a,z in DESCRIPTORS)+'.text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_fragment_send_callback='+hex(CELL),*['--defsym='+name+'='+hex(a) for name,a in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for name,a,z in DESCRIPTORS:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[a-0x27000:a-0x27000+z];sections[name]={'address':a,'bytes':z,'sha256':sha(p)}
  kinds={a:name for name,a in P.items()};kinds.update({a&~1:name for name,a in bindings.items()});names={'r1_structured_log_mode_get':'mode','r1_structured_log_format':'ring','nrf_log_frontend_std_1':'std1','nrf_log_frontend_std_2':'std2'}
  def hook(u,a,size,_):
   f=states[id(u)];r=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if a in (0x5d8a4,syms['r1_stock_crc32_update']):
    assert r[:2]==[f['pointer'],f['length']] and bytes(u.mem_read(r[2],4))==b'\0'*4;f['trace'].append(('crc',r[1],hashlib.sha256(bytes(u.mem_read(r[0],r[1]))).hexdigest()));f['counts']['crc']+=1
   if a in (0x2775c,syms['memmove']):
    offset=f['moves']*239;expected=min(239,f['length']-offset);assert r[1:3]==[f['pointer']+offset,expected];f['trace'].append(('move',offset,r[2]));f['counts']['memmove']+=1;f['moves']+=1
   if a in (0x20000200,0x20000220):
    index=f['callbacks'];counter=f['length']//239-index;size=min(239,max(0,f['length']-index*239));assert r[0]==f['handle'] and r[2]==size+5 and r[3]==a+1
    data=bytes(u.mem_read(r[1],r[2]));expected=bytes([counter])+struct.pack('<I',f['crc'])+bytes(u.mem_read(f['pointer']+index*239,size));assert data==expected,(f['length'],index,data.hex(),expected.hex());f['trace'].append(('callback',a+1,r[0],data.hex()));f['callbacks']+=1;f['counts']['callback']+=1
    if f['mutation']:
     u.mem_write(CELL,struct.pack('<I',0x20000221));u.mem_write(r[1],b'\xa5'*r[2]);offset=(index+1)*239
     if offset<f['length']:u.mem_write(f['pointer']+offset,b'\x73')
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(f['status'],0x11111111,0x22222222,0x33333333)):u.reg_write(reg,value)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if a in kinds:
    name=kinds[a];f['counts'][names[name]]+=1;event=(name,);value=0
    if name=='r1_structured_log_mode_get':value=f['mode'][f['mode_index']%len(f['mode'])];f['mode_index']+=1;event+=(value,)
    elif name=='r1_structured_log_format':assert r[:3]==[0x04800000,0x32524,0x32524] and r[3]==f['length'] and struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0]==4096;event+=(r[0],r[1],r[3],4096)
    elif name=='nrf_log_frontend_std_2':assert r==[0x001c0001,0x32548,f['length'],4096];event+=tuple(r)
    else:raise AssertionError(name)
    f['trace'].append(event)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(value,0x11111111,0x22222222,0x33333333)):u.reg_write(reg,v)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if u is machines[1] and a<0x1000000:raise AssertionError(('source executed native',hex(a)))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u)
   entries=set(kinds)|{0x20000200,0x20000220}|({0x5d8a4,0x2775c} if len(machines)==1 else {syms['r1_stock_crc32_update'],syms['memmove']})
   for address in entries:u.hook_add(UC_HOOK_CODE,hook,begin=address,end=address)
   if len(machines)==2:
    def reject_native(u,a,n,_):raise AssertionError(('source executed native',hex(a)))
    u.hook_add(UC_HOOK_CODE,reject_native,begin=0x20000,end=0xe0000)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  cases=itertools.chain(((length,(0,),False,0) for length in range(4098)),itertools.product((0,1,238,239,240,478,479,3824,4096,4097,8192),modes,(False,True),(0,7,0xffffffff)),((0,(0,),False,0),))
  for index,(length,mode,mutation,status) in enumerate(cases):
   pointer=0 if index==4956 else I;initial=bytes((i*37+index)&255 for i in range(length));crc=crc32(initial);results=[];handle=(index*997)&0xffffffff
   for candidate,u in enumerate(machines):
    u.mem_write(I,initial or b'\x55');u.mem_write(CELL-4,b'\x96'*12);u.mem_write(CELL,struct.pack('<I',0x20000201));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);states[id(u)]={'length':length,'pointer':pointer,'handle':handle,'crc':crc,'trace':[],'counts':dict.fromkeys(counts,0),'moves':0,'callbacks':0,'mutation':mutation,'status':status,'mode':mode,'mode_index':0}
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(handle,pointer,length,0xdeadbeef)):u.reg_write(reg,v)
    for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
    u.emu_start((syms['r1_fragment_message'] if candidate else 0x32408)|1,0x20000100,count=1000000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)];f=states[id(u)];expected=0xffffffff if length>4096 else 0;assert u.reg_read(UC_ARM_REG_R0)==expected;assert f['callbacks']==(length//239+1 if length<=4096 else 0) and f['counts']['crc']==1;results.append((expected,f['trace'],f['counts'],bytes(u.mem_read(I,max(1,length))),bytes(u.mem_read(CELL-4,12))))
   assert results[0]==results[1],(index,length,mode,mutation,status);comparisons+=1;statuses[str(expected)]=statuses.get(str(expected),0)+1
   for name,count in results[0][2].items():counts[name]+=count
   if comparisons%1024==0:print('Fragment cases',comparisons,flush=True)
 vp.write_text(json.dumps(dict(comparisons=comparisons,status_counts=statuses,provider_calls_per_side=counts,all_lengths_0_through_4097=True,null_empty_input=True,native_body_ranges=[{'start':'0x32408','end':'0x32485','bytes':126},{'start':'0x32488','end':'0x32519','bytes':146}],native_body_bytes=272,native_span_bytes=274,excluded_nop_bytes=2,mode_sequences=len(modes),actual_crc32_and_memmove=True,extra_empty_fragment_preserved=True,callback_returns_ignored=True,live_callback_and_input_mutation=True,source_descriptor_sections=sections,ownership_row=row,ownership_sha256=sha(ledger),rea_boundary_available=False,evidence=evidence,provider_reports=reports,driver_sha256=sha(Path(__file__)),application_sha256=ah,application_linked=False,instruction_identity=False,limitations=['Locked272-byte ownership body, native registered pointer and exact Ghidra-MCP bytes; REA has no function entry','Callback slot is a live external binding; initialization, valid target registration and BLE delivery remain gated','Mapped valid input buffers tested; input alias to compiler-private stack or callback writes outside packet bounds remain gated','Full32-bit CRC length executes before rejection; mapped lengths only0..8192 covered; full-width address/fault behavior not proven','Returnr0 and callee-saved ABI checked; volatile scratch r1/r2/r3 and instruction identity remain open']),indent=2)+'\n');print('Fragment:',comparisons,statuses,counts)
if __name__=='__main__':main()
