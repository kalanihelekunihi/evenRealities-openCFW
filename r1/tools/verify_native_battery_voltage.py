#!/usr/bin/env python3
"""Voltage getter reload, full-word configuration comparison and service prefix flow."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-voltage';D=0x20016b84;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'r1_advertising_configuration_byte_get':0x7ba24,'r1_battery_runtime_update_service':0x31fd0};ENTRIES={'r1_battery_voltage_get':0x91290,'r1_battery_runtime_service':0x31fcc}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_voltage.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 for a,z in [(0x91290,20),(0x31fcc,4)]:
  p=OUT/f'rea-{a:x}.json';p.write_bytes((BASE/'native-battery-runtime'/f'rea-next-{a:x}-body.json').read_bytes());q=json.loads(p.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==z and q['normalized_result']['entrypoint']==hex(a);evidence[p.name]=sha(p)
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 for name,a,z in [('getter',0x91290,24),('service',0x31fcc,412)]:
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/f'ghidra-{name}.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 machines=[];states={};counts={n:0 for n in ENTRIES};prefix={'native':0,'source':0};provider_counts={n:0 for n in P}
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_battery_device_context='+hex(D),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,_):
   f=states[id(u)];side='source' if u is machines[1] else 'native'
   if a in (0x31fcc,syms['r1_battery_runtime_service']):assert bytes(u.mem_read(a,4))==bytes.fromhex('aff30080');prefix[side]+=1;f['prefix']+=1
   if a not in kinds:
    if side=='source' and a<0x1000000 and a!=0x20000100:raise AssertionError(('source native provider',hex(a)))
    return
   n=kinds[a];value=f['config'] if n=='r1_advertising_configuration_byte_get' else f['raw'];f['trace'].append((n,struct.unpack('<H',bytes(u.mem_read(D+42,2)))[0]))
   if n=='r1_advertising_configuration_byte_get':
    if f['mutation']:u.mem_write(D+42,struct.pack('<H',f['before']^0x5a5a))
   else:u.mem_write(D+42,struct.pack('<H',f['before']^0xa5a5))
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_R2,0x76543210);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  cases=itertools.chain((('r1_battery_voltage_get',v,c,m,0x80000007) for v,c,m in itertools.product(range(65536),(0,0x55),(False,True))),itertools.product(('r1_battery_voltage_get','r1_battery_runtime_service'),(0,1,3349,3350,65535),(0x55,0xffffff55,0x10055,0xffffffff),(False,True),(0,1,0xffffffff)))
  for name,before,config,mutation,raw in cases:
   refresh=name=='r1_battery_runtime_service' or config==0x55;expected=raw if name=='r1_battery_runtime_service' else before^0xa5a5 if refresh else before^0x5a5a if mutation else before;results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'before':before,'config':config,'mutation':mutation,'raw':raw,'prefix':0};u.mem_write(D-4,b'\xa5'*76);u.mem_write(D+42,struct.pack('<H',before));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms[name] if candidate else ENTRIES[name])|1,0x20000100,count=1000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    assert u.reg_read(UC_ARM_REG_R0)==expected and states[id(u)]['prefix']==int(refresh);results.append((bytes(u.mem_read(D-4,76)),states[id(u)]['trace']))
   assert results[0]==results[1];counts[name]+=1
   for event in results[0][1]:provider_counts[event[0]]+=1
 assert prefix['native']==prefix['source']
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,all_voltage_halfwords=True,prefix_nops=prefix,provider_calls_per_side=provider_counts,native_service_declared_body_bytes=4,overlapping_ownership_span_bytes=412,updater_body_bytes=406,trailing_padding_bytes=2,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Config/updater endpoints are fixtures; actual updater composition required for overlapping service ownership span','Getter reloads voltage after optional refresh; raw configuration comparison is full-word','Service prefix4 bytes and updater406 bytes are separately evidenced; whole-span instruction/image identity remains open','Runtime/config initialization, recursion policy, hardware and physical timing/concurrency remain gates']),indent=2)+'\n');print('Battery voltage:',counts,prefix,provider_counts)
if __name__=='__main__':main()
