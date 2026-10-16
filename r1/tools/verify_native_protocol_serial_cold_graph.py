#!/usr/bin/env python3
"""Actual cold-class reader, serial kernels and headers; critical/transport callbacks are fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-serial-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rp=OUT/'cold-graph-report.json';r=json.loads(rp.read_text());obj=OUT/'serial-cold-class-graph-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();layout=ROOT/'r1/source-config/runtime/native_protocol_serial_cold_graph_verification.ld';states={};digest=hashlib.sha256();count=0;reads=0;callbacks=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for section in ['.text','.class','.handle']:
   p=d/(section[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(p)],check=True);sections[section]=p.read_bytes()
  assert sections['.class']==cold[0x630:0x630+148] and sections['.handle']==cold[0x1954:0x1958]
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==(syms['r1_kv_class_read'] if source else 0x73930):assert [u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R2]]==[0x20006ad8,124];st['events'].append(['read',u.reg_read(UC_ARM_REG_R1)]);return
   if a in [0x20000208,0x2000020c]:
    enter=a==0x20000208;st['events'].append(['enter' if enter else 'leave'])
    if enter and st['mutation']==1:u.mem_write(0x20006af0+31,b'MUTATED-SERIAL!X');u.mem_write(0x20006af0+61,b'\x00');u.mem_write(0x20005003,b'\x78\x56')
    if not enter and st['mutation']==2:u.mem_write(0x20007dfc,bytes(4))
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if a==(0x20000204 if source else 0x828b4):
    handle=u.reg_read(UC_ARM_REG_R0);header=u.reg_read(UC_ARM_REG_R1);payload=u.reg_read(UC_ARM_REG_R2);length=u.reg_read(UC_ARM_REG_R3);assert length==15;st['events'].append(['response',handle,bytes(u.mem_read(header,8)).hex(),payload,bytes(u.mem_read(payload,length)).hex()]);u.reg_write(UC_ARM_REG_R0,st['returned']);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['.text']);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for entry,size,sentinel,poison,handle,mutation in itertools.product(['read','serial'],[0,123,124,125],[0,255],[0,255,0x96],[1,0xffff,0x1000ffff],range(3)):
   results=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([poison])*0x40000);u.mem_write(0x20006ad8,sections['.class']);u.mem_write(0x20007dfc,sections['.handle']);u.mem_write(0x20006ad8+20,struct.pack('<H',size));u.mem_write(0x20006af0+31,b'R1-SERIAL-12345');u.mem_write(0x20006af0+61,bytes([sentinel]));u.mem_write(0x20006974,struct.pack('<I',0x20002000));u.mem_write(0x20002000+28,struct.pack('<2I',0x20000209,0x2000020d));u.mem_write(0x20005000,bytes(range(32)));states[id(u)]=dict(source=source,events=[],mutation=mutation,returned=0 if sentinel else 0xffffffff)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    args=[0x20003000,0x20004000,0x55667788,0x99aabbcc] if entry=='read' else [handle,0x20005000,0x55667788,0x99aabbcc]
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
    native=0x7ba78 if entry=='read' else 0x83db0;symbol='r1_native_product_serial_read' if entry=='read' else 'r1_device_serial_handler';u.emu_start((syms[symbol] if source else native)|1,0x20000100,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   assert results[0]==results[1],(entry,size,sentinel,poison,handle,mutation,results)
   count+=1;reads+=sum(e[0]=='read' for e in results[0][1]);callbacks+=sum(e[0] in ['enter','leave'] for e in results[0][1]);digest.update(json.dumps([entry,size,sentinel,poison,handle,mutation,results[0]],sort_keys=True).encode())
 receipt=dict(workflows=count,cached_reads_per_side=reads,critical_callbacks_per_side=callbacks,trace_sha256=digest.hexdigest(),actual_source_kv_class_memory_getter_headers_and_handler=True,only_critical_callbacks_and_lower_response_are_fixtures=True,cold_source_class_and_symbolic_handle_match=True,size_mismatch_preserves_raw_view=True,controlled_class_packet_and_cache_mutations=True,raw_r0_callee_sp_and_observed_nonstack_ram_checked=True,no_native_source_fallback=True,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app),whole_flash_or_transport_graph_executed=False,private_stack_history_verified=False,whole_image_complete=False)
 (OUT/'cold-graph-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
