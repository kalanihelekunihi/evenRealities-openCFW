#!/usr/bin/env python3
"""Native ingress saved-frame/tail ABI, live header/table mutation and cold relocations."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-ingress';I=0x20010000;T=0x20006b90;SP=0x2003f000;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_4':0x799f8,'r1_eus_system_dispatch_plan_build':0x83ca8,'r1_health_registration_dispatcher':0x82be8,'r1_ble_event_dispatch':0x84c98}
DESCRIPTORS=[('ring',0x8321c,58),('sdk',0x83260,52)]
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());unit=r['units'][0];obj=Path(unit['command'][-1]);assert sha(obj)==unit['object_sha256'] and sha(ROOT/unit['source'])==unit['source_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';row=next(r for r in csv.DictReader(ledger.open()) if r['image']=='application' and r['entry']=='0x0008316c');assert row['size']=='176' and row['end']=='0x0008321b';evidence={}
 p=OUT/'rea-boundary-gap.json';p.write_bytes((BASE/'native-battery-runtime/rea-next-8316c-body.json').read_bytes());j=json.loads(p.read_text());assert j['error']['code']=='invalid_request';evidence[p.name]=sha(p)
 raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket','/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock','http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x8316c&length=300']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x8316c-0x27000:0x8316c-0x27000+300];p=OUT/'ghidra-body-data.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 cold=[];native_table=struct.pack('<4I',0,0x83ca9,0x82be9,0)
 for poison in (165,90,255,60):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x20000000,0x40000);u.mem_write(0x20000000,bytes([poison])*0x40000);writes=[]
  def wh(u,access,a,n,v,_):
   if a<T+16 and a+n>T:writes.append({'pc':u.reg_read(UC_ARM_REG_PC),'address':a,'bytes':n,'value':v})
  u.hook_add(UC_HOOK_MEM_WRITE,wh);u.reg_write(UC_ARM_REG_SP,SP);u.emu_start(0x283a1,0x27208,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(u.mem_read(T,16))==native_table;cold.append({'poison':poison,'writes':writes})
 machines=[];states={};comparisons=0;counts=dict.fromkeys(P,0);paths={'rejected':0,'null_module':0,'module':0,'special':0};sections={};statuses={};modes=[(0,),(1,),(2,),(3,),(4,),(5,),(6,),(7,),(0,4,2),(0,0,2),(1,2),(4,0,0),(0xffffffff,)]
 with tempfile.TemporaryDirectory() as temporary:
  d=Path(temporary);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={name:(address|1) if name in ('r1_eus_system_dispatch_plan_build','r1_health_registration_dispatcher','r1_ble_event_dispatch') else 0x1100001+16*i for i,(name,address) in enumerate(P.items())};ld.write_text('SECTIONS { .modules 0x20006b90 : { *(.r1.protocol.modules) } '+''.join('.'+name+' '+hex(address)+' : { *(.r1.protocol_ingress.'+name+') } ' for name,address,size in DESCRIPTORS)+'.text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+name+'='+hex(address) for name,address in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for name,address,size in DESCRIPTORS:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[address-0x27000:address-0x27000+size];sections[name]={'address':address,'bytes':size,'sha256':sha(p)}
  p=d/'modules.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.modules','-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==native_table;module_section={'address':T,'bytes':16,'sha256_at_native_targets':sha(p),'symbolic_targets':{'1':'r1_eus_system_dispatch_plan_build','2':'r1_health_registration_dispatcher'}}
  relocations=subprocess.check_output(['arm-none-eabi-objdump','-r',str(obj)],text=True);assert 'R_ARM_ABS32' in relocations and all(name in relocations for name in module_section['symbolic_targets'].values())
  kinds={address:name for name,address in P.items()};kinds.update({address&~1:name for name,address in bindings.items()})
  def mutate(u,f):
   if not f['mutation']:return
   f['mutation_index']+=1;index=f['mutation_index'];p=f['packet']
   # Packet is mapped; permitted mutations remain within header or mapped table.
   if f['mutation']==1:u.mem_write(p+1,b'\x7f')
   elif f['mutation']==2:u.mem_write(p+1,bytes([index%4]))
   elif f['mutation']==3:u.mem_write(p+1,b'\xc8');u.mem_write(T+200*4,struct.pack('<I',0x82be9))
   elif f['mutation']==4:
    module=bytes(u.mem_read(p+1,1))[0]
    if module!=127:u.mem_write(T+module*4,b'\0'*4)
   u.mem_write(p+3,struct.pack('<H',(index*997)&65535));u.mem_write(p+5,bytes([index&255]))
  def hook(u,address,size,_):
   f=states[id(u)];name=kinds[address];f['counts'][name]+=1;regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];value=f['raw'];event=(name,)
   if name in ('r1_eus_system_dispatch_plan_build','r1_health_registration_dispatcher','r1_ble_event_dispatch'):
    module=bytes(u.mem_read(f['packet']+1,1))[0];target=0x84c99 if module==127 else struct.unpack('<I',bytes(u.mem_read(T+module*4,4)))[0];assert address==(target&~1) and regs[:2]==[f['handle']&65535,f['packet']] and regs[2:]==[f['scratch2'] if module==127 else target,f['scratch3']] and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_LR)==0x20000101,(f['index'],name,regs,hex(target),module)
    f['callback']=name;event+=tuple(regs);u.mem_write(f['packet']+10,b'\x73')
   elif name=='r1_structured_log_mode_get':value=f['mode'][f['mode_index']%len(f['mode'])];f['mode_index']+=1;event+=(value,);mutate(u,f)
   elif name=='r1_structured_log_format':
    extra=struct.unpack('<3I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),12)));p=f['packet'];sequence=struct.unpack('<H',bytes(u.mem_read(p+3,2)))[0];flags=bytes(u.mem_read(p+5,1))[0];assert regs==[0x0d000000,0x8321c,0x8321c,f['handle']] and extra[0]==f['command'] and (p!=I or extra==(f['command'],flags,sequence)),(f['index'],regs,extra,flags,sequence);event+=(*regs,*extra);mutate(u,f)
   else:
    extra=struct.unpack('<2I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),8)));p=f['packet'];sequence=struct.unpack('<H',bytes(u.mem_read(p+3,2)))[0];flags=bytes(u.mem_read(p+5,1))[0];assert regs==[0x001c0003,0x83260,f['handle'],f['command']] and (p!=I or extra==(flags,sequence)),(f['index'],regs,extra,flags,sequence);event+=(*regs,*extra);mutate(u,f)
   f['trace'].append(event)
   preserve=name=='r1_structured_log_mode_get' and f['preserve_mode_scratch']
   if preserve:assert regs[2:]==[f['scratch2'],f['scratch3']],(f['index'],name,regs,f['scratch2'],f['scratch3'])
   out2,out3=regs[2:] if preserve else (0x22222222,0x33333333);f['scratch2']=out2;f['scratch3']=out3
   for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(value,0x11111111,out2,out3)):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u)
   for address in kinds:u.hook_add(UC_HOOK_CODE,hook,begin=address,end=address)
   if len(machines)==2:
    def reject(u,address,size,_):
     if address not in P.values():raise AssertionError(('source executed native',hex(address)))
    u.hook_add(UC_HOOK_CODE,reject,begin=0x20000,end=0xe0000)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  base=((p,length,module,magic,flag,(0,),0,0,0x12345678) for p,length,module,magic,flag in itertools.product((0,I),(0,1,11,12,13,65535,65536,0xffffffff),(0,1,2,3,4,126,127,128,255),(0,100,255),(0,99,100,101,255)))
  exhaustive=((I,length,1,100,100,(0,),0,7,0xffff0001) for length in range(65536))
  logs=((I,12,module,100,100,mode,mutation,raw,handle) for module,mode,mutation,raw,handle in itertools.product((0,1,2,3,127),modes,range(6),(0,7,0xffffffff,0x80000007),(0,0xffff0001)))
  alias=((p,0x00640164,1,100,100,mode,mutation,raw,0x12345678) for p,mode,mutation,raw in itertools.product((SP-32,SP-28,SP-20),modes,range(6),(0,0xffffffff)))
  preserving=((I,12,module,100,100,mode,mutation,raw,0x24681357) for module,mode,mutation,raw in itertools.product((1,2,127),modes,range(6),(0,7,0xffffffff,0x80000007)))
  for index,(packet,length,module,magic,flag,mode,mutation,raw,handle) in enumerate(itertools.chain(base,exhaustive,logs,alias,preserving)):
   results=[];header=bytes([magic,module,flag])+struct.pack('<H',index&65535)+bytes([index&255,(index*37)&255,(index*71)&255])+b'\xa5'*8;seed3=0x12345678;frame=struct.pack('<8I',packet,length,seed3,*[0x12345600+k for k in range(4)],0x20000101)
   for candidate,u in enumerate(machines):
    u.mem_write(I,header);u.mem_write(SP-128,b'\x96'*128);u.mem_write(SP-32,frame);u.mem_write(T,b'\0'*1024);u.mem_write(T,native_table);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
    initial=bytes(u.mem_read(packet,12)) if packet else bytes(12);command=(initial[1]<<16)|(initial[6]<<8)|initial[7];states[id(u)]={'index':index,'handle':handle,'packet':packet,'length':length,'mode':mode,'mode_index':0,'mutation':mutation,'mutation_index':0,'raw':raw,'trace':[],'counts':dict.fromkeys(P,0),'command':command,'callback':None,'scratch2':length,'scratch3':seed3,'preserve_mode_scratch':handle==0x24681357}
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(handle,packet,length,seed3)):u.reg_write(reg,v)
    for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
    u.emu_start((syms['r1_eus_ingress_plan_decode'] if candidate else 0x8316c)|1,0x20000100,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)];f=states[id(u)];regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    rejected=not packet or length<12 or initial[0]!=100 or initial[2]<100 or (initial[1]>=4 and initial[1]!=127)
    expected=handle if not packet or length<12 else initial[0] if initial[0]!=100 else initial[2] if initial[2]<100 else initial[1] if rejected else raw if f['callback'] else bytes(u.mem_read(packet+1,1))[0];assert regs[0]==expected,(index,candidate,regs,expected)
    results.append((regs,f['trace'],f['counts'],bytes(u.mem_read(I,16)),bytes(u.mem_read(SP-32,32)),bytes(u.mem_read(T,1024)),f['callback']))
   assert results[0]==results[1],(index,packet,length,module,magic,flag,mode,mutation,raw,[(k,a,b) for k,(a,b) in enumerate(zip(*results)) if a!=b]);comparisons+=1;path='rejected' if rejected else 'special' if results[0][-1]=='r1_ble_event_dispatch' else 'module' if results[0][-1] else 'null_module';paths[path]+=1;statuses[str(results[0][0][0])]=statuses.get(str(results[0][0][0]),0)+1
   for name,count in results[0][2].items():counts[name]+=count
 vp.write_text(json.dumps(dict(comparisons=comparisons,path_counts=paths,provider_calls_per_side=counts,all_length_halfwords=True,mode_sequences=len(modes),full_r0_r1_r2_r3=True,exact_saved_frame32=True,tail_stack_and_lr=True,header_and_table_mutation_modes=6,preserving_mode_scratch_cases=936,source_descriptor_sections=sections,source_owned_module_section=module_section,cold_runs=cold,rea_boundary_available=False,ownership_row=row,ownership_sha256=sha(ledger),evidence=evidence,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,application_linked=False,instruction_identity=False,limitations=['Module/special handler bodies and logger endpoints are fixtures; no authentication/CRC/advertised-length validation claim','Saved32-byte ABI boundary modeled in C/assembly; other compilers/LTO and logger writes into its outgoing stack arguments remain gated','Post-log mutation to module200 is tested in mapped table backing; physical out-of-bounds/fault behavior is unproven','Native-target symbolic table relocation matches four cold starts; actual source-handler composition/canonical admission remains gated','Locked176-byte ownership and exact Ghidra-MCP bytes; REA entry unavailable; hardware/concurrency/fullstartup/imageidentity unproven']),indent=2)+'\n');print('Protocol ingress:',comparisons,paths,counts)
if __name__=='__main__':main()
