#!/usr/bin/env python3
"""Receive callback tail ABI, short-circuit validation and dynamic log contract."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-receive';CELL=0x20006c24;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_0':0x799c0}
DESCRIPTORS=[('invalid_ring',0x82744,41),('invalid_sdk',0x82770,35),('missing_ring',0x82794,51),('missing_sdk',0x827c8,45)]
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());unit=r['units'][0];obj=Path(unit['command'][-1]);assert sha(obj)==unit['object_sha256'] and sha(ROOT/unit['source'])==unit['source_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';row=next(r for r in csv.DictReader(ledger.open()) if r['image']=='application' and r['entry']=='0x000826b4');assert row['size']=='130' and row['end']=='0x00082735';evidence={}
 p=OUT/'rea-boundary-gap.json';p.write_bytes((BASE/'native-battery-runtime/rea-next-826b4-body.json').read_bytes());j=json.loads(p.read_text());assert j['error']['code']=='invalid_request';evidence[p.name]=sha(p)
 raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket','/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock','http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x826b4&length=324']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x826b4-0x27000:0x826b4-0x27000+324];p=OUT/'ghidra-body-data.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 machines=[];states={};comparisons=0;callbacks=0;counts=dict.fromkeys(P,0);sections={};validation_counts={'invalid':0,'missing':0,'callback':0};modes=[(0,),(1,),(2,),(3,),(4,),(5,),(6,),(7,),(0,4,2),(0,0,2),(1,2),(4,0,0),(0xffffffff,)]
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={name:0x1100001+16*i for i,name in enumerate(P)};ld.write_text('SECTIONS { '+''.join('.'+name+' '+hex(address)+' : { *(.r1.protocol_receive.'+name+') } ' for name,address,size in DESCRIPTORS)+'.text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_protocol_receive_hook='+hex(CELL),*['--defsym='+name+'='+hex(address) for name,address in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for name,address,size in DESCRIPTORS:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[address-0x27000:address-0x27000+size];sections[name]={'address':address,'bytes':size,'sha256':sha(p)}
  kinds={address:name for name,address in P.items()};kinds.update({address&~1:name for name,address in bindings.items()})
  def hook(u,address,size,_):
   f=states[id(u)];regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if address in (0x20000200,0x20000220):
    assert regs==[f['handle'],f['packet'],f['length'],f['callback']] and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and u.reg_read(UC_ARM_REG_LR)==0x20000101;f['trace'].append(('callback',*regs));f['callbacks']+=1;value=f['raw']
    if f['mutation']:u.mem_write(CELL,struct.pack('<I',0x20000221));u.mem_write(f['packet'],b'\x73')
   else:
    name=kinds[address];f['counts'][name]+=1;value=f['raw'];event=(name,)
    if name=='r1_structured_log_mode_get':value=f['mode'][f['mode_index']%len(f['mode'])];f['mode_index']+=1;event+=(value,)
    elif name=='r1_structured_log_format':
     a=0x82744 if f['path']=='invalid' else 0x82794;assert regs[:3]==[0x04000000,a,a];event+=tuple(regs[:3])
    else:
     a=0x82770 if f['path']=='invalid' else 0x827c8;assert regs[:2]==[0x001c0001,a] and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and u.reg_read(UC_ARM_REG_LR)==0x20000101;event+=tuple(regs[:2])
    f['trace'].append(event);f['last']=(name,value)
    if f['mutation']:u.mem_write(CELL,struct.pack('<I',0x20000221))
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(value,0x11111111,0x22222222,0x33333333)):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u)
   for address in set(kinds)|{0x20000200,0x20000220}:u.hook_add(UC_HOOK_CODE,hook,begin=address,end=address)
   if len(machines)==2:
    def reject(u,address,size,_):raise AssertionError(('source executed native',hex(address)))
    u.hook_add(UC_HOOK_CODE,reject,begin=0x20000,end=0xe0000)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];values=(0,1,65535,65536,0x80000000,0xffffffff)
  cases=itertools.product(values,(0,0x20001000),(0,1,12,65535,65536,0xffffffff),(0,0x20000201,0x20000221),modes,(False,True),(0,7,0xffffffff))
  for index,(handle,packet,length,callback,mode,mutation,raw) in enumerate(cases):
   path='invalid' if not packet or not length else 'missing' if not callback else 'callback';results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'handle':handle,'packet':packet,'length':length,'callback':callback,'mode':mode,'mode_index':0,'mutation':mutation,'raw':raw,'path':path,'trace':[],'last':None,'callbacks':0,'counts':dict.fromkeys(P,0)};u.mem_write(0x20001000,b'\x5a'*16);u.mem_write(CELL-4,b'\x96'*12);u.mem_write(CELL,struct.pack('<I',callback));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(handle,packet,length,0xdeadbeef)):u.reg_write(reg,v)
    for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
    u.emu_start((syms['r1_proto_ble_recv_validate'] if candidate else 0x826b4)|1,0x20000100,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)];f=states[id(u)];expected=raw if path=='callback' or f['last'][0]=='nrf_log_frontend_std_0' else (f['last'][1]<<30)&0xffffffff;assert u.reg_read(UC_ARM_REG_R0)==expected
    if path=='callback':assert [u.reg_read(reg) for reg in (UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]==[0x11111111,0x22222222,0x33333333]
    assert f['callbacks']==int(path=='callback');results.append((expected,f['trace'],f['counts'],bytes(u.mem_read(CELL-4,12)),bytes(u.mem_read(0x20001000,16))))
   assert results[0]==results[1],(index,handle,packet,length,callback,mode,mutation,raw);comparisons+=1;callbacks+=path=='callback';validation_counts[path]+=1
   for name,count in results[0][2].items():counts[name]+=count
 vp.write_text(json.dumps(dict(comparisons=comparisons,callback_calls_per_side=callbacks,path_counts=validation_counts,provider_calls_per_side=counts,mode_sequences=len(modes),tail_stack_lr_and_register_forwarding=True,full_callback_return_registers=True,raw_invalid_return_r0=True,short_circuit_no_recheck=True,live_callback_mutation=True,source_descriptor_sections=sections,rea_boundary_available=False,ownership_row=row,ownership_sha256=sha(ledger),evidence=evidence,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,application_linked=False,instruction_identity=False,limitations=['Locked130-byte ownership body and exact Ghidra-MCP body/data bytes; REA entry unavailable','Registered ingress remains a callback fixture; no payload/header/CRC validation or transport delivery proof','Full callback return r0/r1/r2/r3 and tailSP/LR checked; invalid/logging scratchr1/r2/r3 and actual enabledlogger composition remain gated','Mapped callback packet mutation tested; no allocation bounds, warm init or physical concurrency proof']),indent=2)+'\n');print('Protocol receive:',comparisons,callbacks,validation_counts,counts)
if __name__=='__main__':main()
