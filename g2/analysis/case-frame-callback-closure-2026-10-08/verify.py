"""Original/independent product parser, stopping at bulk/RTOS entry boundaries."""
from pathlib import Path
import sys,struct,json,hashlib,itertools
D=Path(__file__).resolve().parent;s=D.parent/'case-uart-receive-closure-2026-10-08/verify.py';text=s.read_text().split('rows=[]')[0];start=text.index('entries={w:');end=text.index('\ndef guest',start);text=text[:start]+'entries={}'+text[end:];ns={'__file__':str(s)};exec(text,ns);symbols=ns['symbols'];UART=0x20000e24;FRAME=0x20000974;CTX=0x20000108;rows=[]
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
def fixture(count,prefix,ch,state,mask,instance,last=0x5a):
 u=ns['guest'](state,1,0xff,0,0,0,mask,0);u.mem_write(UART,bytes(u.mem_read(ns['H'],148)));u.mem_write(UART,struct.pack('<I',instance));u.mem_write(UART+8,struct.pack('<I',0));u.mem_write(UART+16,struct.pack('<I',0));u.mem_write(UART+0x64,struct.pack('<IH',0,1));u.mem_write(FRAME,b'\xa7'*1200);u.mem_write(FRAME,bytes(prefix));u.mem_write(CTX,struct.pack('<BBH',ch,last,count));u.mem_write(0x200000f0,struct.pack('<I',0x20006000));return u
def run(u,entry,args):
 state={'endpoint':'return','args':[]};writes=[]
 def code(u,a,n,data):
  if a in (0x080063ec,0x0800a888):
   state['endpoint']='bulk_receive' if a==0x080063ec else 'event_post';state['args']=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]][:4 if a==0x080063ec else 2];u.emu_stop()
 def write(u,access,a,n,v,data):
  if ns['HW']<=a<ns['HW']+0x28:writes.append([hex(a),n,hex(v),u.reg_read(UC_ARM_REG_PRIMASK)])
  if a in (ns['HW'],ns['HW']+8):assert u.reg_read(UC_ARM_REG_PRIMASK)==1
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1],args):u.reg_write(reg,value)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(entry|1,0x20000000,count=20000);assert state['endpoint']!='return' or u.reg_read(UC_ARM_REG_PC)==0x20000000
 return (state,writes,bytes(u.mem_read(0x20000000,0x2000)),bytes(u.mem_read(ns['HW'],0x28)),u.reg_read(UC_ARM_REG_PRIMASK))
prefixes=[(0x5a,0xa5,0x7f,2,0),(0x5a,0xa5,0xcf,2,0),(ord('D'),ord('E'),0,0,0),(ord('d'),ord('f'),0,0,0),(0x5a,0,0xcf,255,255),(0x33,0,0,0,0)]
for count,prefix,ch,state,mask,instance in itertools.product([0,1,2,3,4,5,7,59,1199,1200],prefixes,[0,0x5a,0xa5,0x7f,0xcf,ord('D'),ord('d'),ord('E'),10,255],[0x20,0x22],[0,1],[0x40013800,0x40004400]):
 vals=[run(fixture(count,prefix,ch,state,mask,instance),a,[UART]) for a in [0x08006544,symbols['case_frame_callback']]];assert vals[0]==vals[1],('parser',count,prefix,ch,state,mask,hex(instance),[i for i,(a,b) in enumerate(zip(*vals)) if a!=b]);rows.append(dict(kind='frame_callback',initial_count=count,prefix=list(prefix),byte=ch,rx_state=state,primask=mask,instance=hex(instance),endpoint=vals[0][0]['endpoint'],boundary_arguments=[hex(x) for x in vals[0][0]['args']],final_count=struct.unpack_from('<H',vals[0][2],0x10a)[0]))
for count,last in itertools.product([0,1,2,3,1199,1200,0xffff],[0,0x5a]):
 vals=[run(fixture(count,prefixes[0],0x5a,0x20,0,0x40013800,last),a,[]) for a in [0x0800a358,symbols['case_frame_resync']]];assert vals[0]==vals[1];rows.append(dict(kind='resync',count=count,last=last,final_count=struct.unpack_from('<H',vals[0][2],0x10a)[0]))
for a,b in itertools.product([ord('D'),ord('d'),ord('Z'),0],[ord('E'),ord('e'),10,0]):
 vals=[]
 for entry in [0x0800be74,symbols['case_frame_de_prefix']]:
  u=fixture(0,prefixes[0],0,0x20,0,0x40013800);u.mem_write(0x20004000,bytes([a,b]));v=run(u,entry,[0x20004000]);vals.append((u.reg_read(UC_ARM_REG_R0),v))
 assert vals[0]==vals[1];rows.append(dict(kind='de_prefix',a=a,b=b,result=vals[0][0]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(ns['blob']).hexdigest(),elf_sha256=hashlib.sha256(ns['elf'].read_bytes()).hexdigest(),limits=['Original/independent parser, reset and predicate; full real/native receive-start providers execute on ordinary rearm paths.','External timed bulk receive080063ec and RTOS event post0800a888 stop before first instruction; arguments/state compared, no invented return or child semantic model.','Suffix after bulk return or event completion remains static reconstruction, not tested full callback equivalence.','Synthetic coherent USART1 context/stream states; guard frame region1200 and PRIMASK at rearm register writes checked. No physical IRQ/FIFO or scheduler evidence.','No new public-source attribution for this product-specific callback, no complete-source or byte-equality claim.']),indent=2)+'\n');print('PASS',len(rows))
