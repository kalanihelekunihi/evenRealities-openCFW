#!/usr/bin/env python3
"""Actual shared search, full module-tail ABI, symbolic tables and fault boundaries."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-modules';SP=0x2003f000;I=0x20010000;RAM=0x20008008;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
MODULES=[('health',0x82be8,'r1_health_registration_dispatcher',0x9a454,14),('system',0x83ca8,'r1_eus_system_dispatch_plan_build',0x9a4cc,20),('special',0x84c98,'r1_ble_event_dispatch',0x9a588,1)]
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());unit=report['units'][0];obj=Path(unit['command'][-1]);assert sha(obj)==unit['object_sha256'] and sha(ROOT/unit['source'])==unit['source_sha256']
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';rows=[row for row in csv.DictReader(ledger.open()) if row['image']=='application' and int(row['entry'],16) in (0x82be8,0x83ca8,0x84c98,0x83298)];assert len(rows)==4;evidence={};targets=json.loads((OUT/'command-targets.json').read_text());handlers={int(row['native_target'],16):row['symbol'] for row in targets['targets']};assert len(handlers)==35
 for address in (0x82be8,0x83ca8,0x84c98,0x83298):
  p=OUT/('rea-'+format(address,'x')+'.json');p.write_bytes((BASE/'native-battery-runtime'/('rea-next-'+format(address,'x')+'-body.json')).read_bytes());j=json.loads(p.read_text());assert j['error']['code']=='invalid_request';evidence[p.name]=sha(p)
  length=58 if address==0x83298 else 40;raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket','/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock','http://localhost/read_memory?program=stock-r1-native-analysis.elf&address='+hex(address)+'&length='+str(length)]);assert bytes(json.loads(raw)['data'])==app.read_bytes()[address-0x27000:address-0x27000+length];p=OUT/('ghidra-'+format(address,'x')+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 machines=[];states={};sections={};helper_cases=0;helper_success=0;helper_faults=0;wrapper_cases=0;callbacks=0;counts={name:0 for name,entry,symbol,address,count in MODULES};trace_hash=hashlib.sha256();fault_hash=hashlib.sha256();underflow_receipt=None
 with tempfile.TemporaryDirectory() as temporary:
  d=Path(temporary);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={name:entry|1 for entry,name in handlers.items()};ld.write_text('SECTIONS { '+''.join('.'+name+' '+hex(address)+' : { *(.r1.protocol_commands.'+name+') } ' for name,entry,symbol,address,count in MODULES)+'.text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+name+'='+hex(address) for name,address in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for name,entry,symbol,address,count in MODULES:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==app.read_bytes()[address-0x27000:address-0x27000+count*8];sections[name]={'address':address,'bytes':count*8,'sha256_at_native_targets':sha(p),'symbolic_targets':{str(r['key']):r['symbol'] for r in targets['targets'] if r['table']==name}}
  def readhook(u,access,address,size,value,_):
   if states[id(u)]['kind']=='wrapper' and address in (0x82c0c,0x83ccc,0x84cbc):return
   if 0x20000<=address<0xe0000 or 0x20008000<=address<0x20009000:states[id(u)]['reads'].append((address,size))
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=(access,address,size);return False
  def callback(u,address,size,_):
   f=states[id(u)];regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert regs==[f['handle'],I,address|1,f['lower']] and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_LR)==0x20000101,(f,regs,address);f['callbacks'].append((address,*regs));u.mem_write(I+10,b'\x73')
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(f['raw'],0x11111111,0x22222222,0x33333333)):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_MEM_READ,readhook,begin=0x20000,end=0xe0000);u.hook_add(UC_HOOK_MEM_READ,readhook,begin=0x20008000,end=0x20009000);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
   for address in handlers:u.hook_add(UC_HOOK_CODE,callback,begin=address,end=address)
   if len(machines)==2:
    def reject(u,address,size,_):
     if address not in handlers:raise AssertionError(('source executed native',hex(address)))
    u.hook_add(UC_HOOK_CODE,reject,begin=0x20000,end=0xe0000)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def start(u,args,entry,kind):
   states[id(u)]={'reads':[],'fault':None,'callbacks':[],'kind':kind};u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
   for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
   try:u.emu_start(entry|1,0x20000100,count=10000)
   except UcError:
    assert states[id(u)]['fault'];return None
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)]
   return [u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
  synthetic=struct.pack('<HHI',0,0,0x12345679)+b''.join(struct.pack('<HHI',i,0,0x76540001+i*2) for i in range(1,9))
  helper_inputs=itertools.chain(((address,count,key>>8,key&255,'stock') for name,entry,symbol,address,count in MODULES for key in range(65536)),((table,count,command,subcommand,'synthetic') for table,count,command,subcommand in itertools.product((0,RAM),(0,1,8),(0,1,255,256,0xffffffff),(0,1,8,9,255,65535,0xffffffff))))
  for index,(table,count,command,subcommand,kind) in enumerate(helper_inputs):
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(RAM-8,synthetic);regs=start(u,[table,count,command,subcommand],syms['r1_health_registration_binary_search'] if candidate else 0x83298,'helper');f=states[id(u)];results.append((regs,f['fault'],f['reads']))
   assert results[0]==results[1],(index,table,count,command,subcommand,results);helper_cases+=1
   if results[0][1]:helper_faults+=1;fault_hash.update(json.dumps((table,count,command,subcommand,results[0][1])).encode())
   else:helper_success+=1
   trace_hash.update(json.dumps((table,count,command,subcommand,results[0])).encode())
   if kind=='synthetic' and table==RAM and count==8 and command==0 and subcommand==0:
    assert results[0][0]==[0x12345679,0xffffffff,0x7fffffff,0] and (RAM-8,2) in results[0][2];underflow_receipt={'input':[table,count,command,subcommand],'registers':results[0][0],'reads':results[0][2]}
  for name,entry,symbol,address,count in MODULES:
   data=app.read_bytes()[address-0x27000:address-0x27000+count*8];keys=[struct.unpack_from('<H',data,i*8)[0] for i in range(count)];keycases=keys+[keys[-1]+1]
   for packet,key,handle,raw,seed in itertools.product((0,I),keycases,(0,1,65535,65536,0x80000000,0xffffffff),(0,7,0xffffffff),(0,0x12345678,0xffffffff)):
    upper=count-1;lower=0;expected_callback=0
    while lower<=upper:
     mid=lower+((upper-lower)>>1);observed=keys[mid]
     if observed==key:expected_callback=struct.unpack_from('<I',data,mid*8+4)[0];break
     if observed<key:lower=mid+1
     else:upper=mid-1
    results=[]
    for candidate,u in enumerate(machines):
     header=bytearray(b'\x5a'*16);header[6]=key>>8;header[7]=key&255;u.mem_write(I,bytes(header));states[id(u)]={'reads':[],'fault':None,'callbacks':[],'kind':'wrapper','handle':handle,'raw':raw,'lower':lower};u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(handle,packet,seed,seed^0xffffffff)):u.reg_write(reg,value)
     for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
     u.emu_start((syms[symbol] if candidate else entry)|1,0x20000100,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)];f=states[id(u)];regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];expected=[handle,packet,seed,seed^0xffffffff] if not packet else [raw,0x11111111,0x22222222,0x33333333] if expected_callback else [0,upper,0,lower];assert regs==expected,(name,packet,key,candidate,regs,expected);assert len(f['callbacks'])==int(bool(packet and expected_callback));results.append((regs,f['reads'],f['callbacks'],bytes(u.mem_read(I,16))))
    assert results[0]==results[1],(name,packet,key,handle,raw,seed,results);wrapper_cases+=1;counts[name]+=1;callbacks+=bool(packet and expected_callback)
 vp.write_text(json.dumps(dict(helper_comparisons=helper_cases,helper_returned=helper_success,helper_faulted=helper_faults,all_command_halfwords_per_stock_table=True,full_word_command_inputs=True,helper_trace_sha256=trace_hash.hexdigest(),fault_trace_sha256=fault_hash.hexdigest(),underflow_mapped_predecessor=underflow_receipt,wrapper_comparisons=wrapper_cases,wrapper_counts=counts,callback_calls_per_side=callbacks,full_r0_r1_r2_r3=True,tail_stack_and_lr=True,actual_shared_search=True,source_owned_command_tables=sections,command_targets_sha256=sha(OUT/'command-targets.json'),unowned_target_entries=targets['unowned_target_entries'],rea_boundary_available=False,ownership_rows=rows,ownership_sha256=sha(ledger),evidence=evidence,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,application_linked=False,instruction_identity=False,limitations=['35 symbolic leaf references are callback fixtures, not source-complete leaf handlers; nine targets lack locked ownership entries','Unsigned below-minimum underflow and wrapped reads/fault addresses preserved; faults are emulated evidence, not physical exception proof','Symbolic command-table data matches native-target link; source-target/actual handler admission remains gated','Locked ownership/native calls/Ghidra-MCP attribute bodies; REA entries unavailable; no hardware/fullstartup/wholeimage proof']),indent=2)+'\n');print('Protocol modules:',helper_cases,'helper',helper_success,'returns',helper_faults,'faults;',wrapper_cases,'wrappers',callbacks,'callbacks',counts)
if __name__=='__main__':main()
