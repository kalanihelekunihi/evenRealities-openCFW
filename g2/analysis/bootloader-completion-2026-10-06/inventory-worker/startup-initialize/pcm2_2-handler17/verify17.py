#!/usr/bin/env python3
"""Verify selector17 source against locked code and its natural walker path."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[5]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SELECTORS=ROOT/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/gx-native/scatter-selector-table.json'
BINDINGS=ROOT/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/pcm2_2-relocated/native-selector-bindings.json'
ELF_READER=ROOT/'g2/components/bootloader/update_core/elf_reader.py'
IMAGE_SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
ENTRY,END,DIGEST=0x429718,0x42984e,'1800926f5cd512a3f3b45b77aa8f9edc1969de9c3a658341aa6a23650c6e6480'
WALKER=(0x42a43a,0x42a4bc,'1075e4055c2ef66d985f8938f881a08d43a90791be3dc0b2700ff7e0074ed107')
SEQUENCER=(0x42a2b4,0x42a43a,'c02ca4144181ebe16c3dffc47e1bec89a89fbb832fa8bb134b38dd8bf287444f')
MATRIX=(0x433498,28,'d83c73b1f5370cc6063489aedc4f0701bdec2ca34a492233caa521c0cf2ea5e8')
TABLE=0x20000158; STOP=0x08000000; INIT_STOCK=0x415326
STATE=[0x200270b0,0x200270b4,0x200270b8,0x200270bc,0x200270c0,0x200270c4,0x40020044,0x40020048,0x40020080,0x400083e0,0x40008064,0x20026c04,0x400083e8,0x40008010,0x40008068,0x4002037c,0x40021000,0x2000055a]
spec=importlib.util.spec_from_file_location('elf_reader',ELF_READER);er=importlib.util.module_from_spec(spec);spec.loader.exec_module(er)
def p32(x): return struct.pack('<I',x&0xffffffff)
def pack(vddf,active,tempco,vddc): return (vddf&127)|((active&1023)<<7)|((tempco&15)<<17)|((vddc&127)<<21)
def fixtures():
 out=[]
 for i,(new,old) in enumerate(((10,9),(9,10),(7,2),(19,20),(20,1),(11,8),(15,14),(3,0))):
  prof=[pack((13+7*i+11*j)&127,(31+43*i+71*j)&1023,(i+3*j)&15,(17+9*i+13*j)&127) for j in range(21)]
  low=sum(((i*31+j*41)&127)<<(7*j) for j in range(4))
  out.append({'name':f'direct-{i}-{new}-{old}','args':[new,old,(i+2)&7,(i+3)&7],'profiles':prof,'low_voltage':low,'timer_control':0,'timer_status':0,'timer_state':0,'clock_user':False,'mode':(i&3)<<3})
 for state in (2,7,26):
  for ready in (True,False):
   i=state+(1 if ready else 7);prof=[pack((13+7*i+11*j)&127,(31+43*i+71*j)&1023,(i+3*j)&15,(17+9*i+13*j)&127) for j in range(21)]
   low=sum(((i*11+j*37)&127)<<(7*j) for j in range(4))
   out.append({'name':f'timer-{state}-{int(ready)}','args':[10,9,3,1],'profiles':prof,'low_voltage':low,'timer_control':0x80001235,'timer_status':0x40000000 if ready else 0,'timer_state':state,'clock_user':True,'mode':0})
 return out
def walker_fixture():
 i=4;prof=[pack((13+7*i+11*j)&127,(31+43*i+71*j)&1023,(i+3*j)&15,(17+9*i+13*j)&127) for j in range(21)]
 low=[(i*31+j*41)&127 for j in range(4)]
 return {'name':'walker-current9-target10-selector17','args':[10,9,3,1],'profiles':prof,'low_voltage':sum(x<<(7*j) for j,x in enumerate(low)),'timer_control':0,'timer_status':0,'timer_state':0,'clock_user':False,'mode':0,'walker_args':[10,9,3,1]}
def seed(u,f):
 for addr in STATE:u.mem_write(addr,p32(0x5a5a0000|(addr&0xffff)))
 info=bytearray(0x6c);struct.pack_into('<I',info,0,0x1f01600d)
 for i,w in enumerate(f['profiles']):struct.pack_into('<I',info,4+4*i,w)
 struct.pack_into('<I',info,0x64,f['low_voltage']);u.mem_write(0x20026ba0,bytes(info))
 for addr,val in [(0x40021000,f['mode']),(0x400083e0,f['timer_control']),(0x40008064,f['timer_status']),(0x400083e8,0x1234),(0x40008010,0x8000),(0x40008068,0x76543210),(0x4002037c,0xa5123456),(0x40004030,0x01000000),(0x40004044,0x20),(0x20027030,0),(0x20027044,0),(0x47ff0000,0x12345678)]:u.mem_write(addr,p32(val))
 u.mem_write(0x20000550,b'\x01');u.mem_write(0x2000055a,bytes([f.get('timer_state',0)]));u.mem_write(0x20026e74,bytes(56));u.mem_write(0x2002719c,b'\0');u.mem_write(0x2002719e,b'\0')
 if f.get('clock_user'):u.mem_write(0x20026ea8,p32(1<<17))
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1);u.reg_write(a.UC_ARM_REG_PRIMASK,0)
 for i,v in enumerate(f.get('walker_args',f['args'])):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),v)
def mapped():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,sz in [(0,0x1000),(0x08000000,0x1000),(0x10000,0x40000),(0x20000000,0x40000),(0x40000000,0x100000),(0x410000,0x25000),(0xe0000000,0x200000),(0x47ff0000,0x1000)]:u.mem_map(lo,sz)
 return u
def install_table(u,stock,image,segments,symbols,addon_entry):
 u.mem_write(0x20000000,b'\xa5'*1372);u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
 if stock:u.reg_write(a.UC_ARM_REG_R0,0x433104);u.reg_write(a.UC_ARM_REG_R1,0);u.reg_write(a.UC_ARM_REG_R9,0);entry=INIT_STOCK
 else:
  for seg in segments:u.mem_write(seg['address'],seg['data'])
  for reg in (a.UC_ARM_REG_R0,a.UC_ARM_REG_R1,a.UC_ARM_REG_R2,a.UC_ARM_REG_R3):u.reg_write(reg,0)
  entry=symbols['opencfw_boot_install_initialized_data']&~1
 done=[False]
 def hook(cpu,pc,size,_):
  if pc==STOP:done[0]=True;cpu.emu_stop();return
  if not stock and 0x410000<=pc<0x435000:raise AssertionError(f'source installer executed locked code {pc:#x}')
 h=u.hook_add(UC_HOOK_CODE,hook);u.emu_start(entry|1,0,count=500000);u.hook_del(h);assert done[0]
 raw=bytes(u.mem_read(0x20000000,1371));assert u.mem_read(0x20000000+1371,1)==b'\xa5'
 table=json.loads(SELECTORS.read_text()); assert hashlib.sha256(raw).hexdigest()==table['output_sha256'] if stock else True
 targets=[int(x['thumb_target'],16) for x in table['selectors']];norm=bytearray(raw)
 if not stock:
  binds=json.loads(BINDINGS.read_text())['slots']
  for slot,name in binds.items():
   off=0x158+4*int(slot);actual=struct.unpack_from('<I',raw,off)[0]
   assert name in symbols and actual==(symbols[name]|1),(slot,hex(actual),name,hex(symbols.get(name,0)))
   norm[off:off+4]=p32(targets[int(slot)])
  assert bytes(norm)==_stock_raw
  assert struct.unpack_from('<I',raw,0x158+17*4)[0]==targets[17], 'source installer slot17 must retain authenticated stock target before fixture binding'
  u.mem_write(TABLE+17*4,p32(addon_entry|1))
 return raw,hashlib.sha256(raw).hexdigest(),hashlib.sha256(norm).hexdigest()
def run(mode,base_segs,base_syms,addon_segs,addon_syms,image,f):
 u=mapped();segments=base_segs+addon_segs;symbols={**base_syms,**addon_syms};addon_entry=symbols['opencfw_spot_pcm22_transition17']&~1
 if mode.endswith('stock'):u.mem_write(0x410000,image)
 raw,rawhash,normhash=install_table(u,mode.endswith('stock'),image,segments,symbols,addon_entry)
 seed(u,f)
 writes=[];waits=[];visited=set();called=[];done=[False]
 start=ENTRY if mode=='stock' else addon_entry
 if mode=='walker-stock':start=WALKER[0]
 if mode=='walker-source':start=base_syms['event_a_temperature_transition_separate']&~1
 def code(cpu,pc,size,_):
  if pc==STOP:done[0]=True;cpu.emu_stop();return
  if pc==0x40:waits.append(cpu.reg_read(a.UC_ARM_REG_R0));cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  if mode.startswith('walker'):
   if mode=='walker-stock':
    for key,(lo,hi,_) in {'walker':WALKER,'selector':SEQUENCER,'handler':(ENTRY,END,DIGEST)}.items():
     if lo<=pc<hi:visited.add((key,pc))
   elif 0x410000<=pc<0x435000:raise AssertionError(f'source entered locked code at {pc:#x}')
  elif mode=='stock' and ENTRY<=pc<END:visited.add(('handler',pc))
  elif mode=='source' and 0x410000<=pc<0x435000:raise AssertionError(f'source entered locked code at {pc:#x}')
  target=ENTRY if mode.endswith('stock') else addon_entry
  if mode.startswith('walker') and pc==target:called.append([cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)])
 def wr(cpu,access,addr,size,value,_):
  if 0x40000000<=addr<0x40100000 or 0xe0000000<=addr<0xe0020000:writes.append([addr,size,value&((1<<(8*size))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40000000,end=0x400fffff)
 try:u.emu_start(start|1,0,count=5000000)
 except Exception as e:raise RuntimeError((f['name'],mode,hex(u.reg_read(a.UC_ARM_REG_PC)))) from e
 assert done[0],(f['name'],mode,'not returned',hex(u.reg_read(a.UC_ARM_REG_PC)))
 result={'return':[u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)],'state':{f'{x:08x}':bytes(u.mem_read(x,4)).hex() for x in STATE},'writes':writes,'wait_cycles':waits,'callee_saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],'sp':u.reg_read(a.UC_ARM_REG_SP),'primask':u.reg_read(a.UC_ARM_REG_PRIMASK),'callback_args':called,'table_normalized_sha256':normhash}
 return result,visited
def main():
 global _stock_raw
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--addon',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);aargs=ap.parse_args()
 image=IMAGE.read_bytes();assert hashlib.sha256(image).hexdigest()==IMAGE_SHA
 table=json.loads(SELECTORS.read_text());assert table['output_bytes']==1371 and table['callback_table_address']==hex(TABLE)
 recs={int((d:=json.loads(l))['entry'],16):d for l in (ROOT/'g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines()}
 body=image[ENTRY-0x410000:END-0x410000];assert len(body)==310 and hashlib.sha256(body).hexdigest()==DIGEST and int(recs[ENTRY]['body_end_inclusive'],16)+1==END
 assert hashlib.sha256(body[:-1]).hexdigest()!=DIGEST and hashlib.sha256(image[ENTRY-0x410000:END+1-0x410000]).hexdigest()!=DIGEST
 for ent,end,dig in (WALKER,SEQUENCER):assert hashlib.sha256(image[ent-0x410000:end-0x410000]).hexdigest()==dig
 assert hashlib.sha256(image[MATRIX[0]-0x410000:MATRIX[0]-0x410000+MATRIX[1]]).hexdigest()==MATRIX[2]
 _,base_segs,base_syms=er.elf_info(aargs.base);_,addon_segs,addon_syms=er.elf_info(aargs.addon)
 for name in ('opencfw_boot_install_initialized_data','event_a_temperature_transition_separate','event_a_state_transition_sequence'):assert name in base_syms,name
 assert 'opencfw_spot_pcm22_transition17' in addon_syms
 source_entry=addon_syms['opencfw_spot_pcm22_transition17']&~1
 # Stock initialized data is decoded from the locked instructions and compared to the source installer's relocated table.
 u=mapped();u.mem_write(0x410000,image);u.mem_write(0x20000000,b'\xa5'*1372);u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1);u.reg_write(a.UC_ARM_REG_R0,0x433104);u.reg_write(a.UC_ARM_REG_R1,0);u.reg_write(a.UC_ARM_REG_R9,0);d=[False]
 def stop(cpu,pc,size,_):
  if pc==STOP:d[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,stop);u.emu_start(INIT_STOCK|1,0,count=500000);assert d[0];_stock_raw=bytes(u.mem_read(0x20000000,1371));assert hashlib.sha256(_stock_raw).hexdigest()==table['output_sha256']
 rows=[];coverage=set()
 for f in fixtures():
  st,cv=run('stock',base_segs,base_syms,addon_segs,addon_syms,image,f);so,_=run('source',base_segs,base_syms,addon_segs,addon_syms,image,f);assert st==so,(f['name'],st,so)
  rows.append({'fixture':f,'result':st});coverage|=cv
 wf=walker_fixture();st,cv=run('walker-stock',base_segs,base_syms,addon_segs,addon_syms,image,wf);so,_=run('walker-source',base_segs,base_syms,addon_segs,addon_syms,image,wf)
 assert st==so,(wf['name'],st,so);assert st['callback_args']==[[10,9,3,1]],st['callback_args'];rows.append({'fixture':wf,'selector_matrix_cell':{'current_state':9,'target_state':10,'sequence':17,'reason':'current gt0 to target le0; special 9->10 case'},'result':st});coverage|=cv
 covered_handler={p for k,p in coverage if k=='handler'}
 out={'status':'PASS','image_sha256':IMAGE_SHA,'base_elf':str(aargs.base),'base_elf_sha256':hashlib.sha256(aargs.base.read_bytes()).hexdigest(),'addon_elf_sha256':hashlib.sha256(aargs.addon.read_bytes()).hexdigest(),'entry':hex(ENTRY),'end_exclusive':hex(END),'bytes':END-ENTRY,'body_sha256':DIGEST,'initialized_table_bytes':1371,'initialized_table_sha256':table['output_sha256'],'source_installed_slot17':hex(source_entry|1),'visited_stock_handler_bytes':len(covered_handler),'unvisited_stock_handler_addresses':[hex(x) for x in sorted(set(range(ENTRY,END))-covered_handler)],'visited_stock_walker_selector':{k:len({p for key,p in coverage if key==k}) for k in ('walker','selector')},'cases':len(rows),'comparisons':rows,'limits':['Source side executes candidate initialized-data installer before fixture initialization; callback slot17 is then bound to the separately compiled native handler for this comparison. Other installed source relocations are verified against the stock decoder output.','Source execution traps on locked-image code; stock executes authenticated handler and walker instructions. ROM cycle-wait service at 0x40 is the controlled timing boundary. Offline emulation is not a whole-firmware or hardware equivalence claim.']}
 aargs.output.write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(rows),'fixtures; selector17 bytes',out['visited_stock_handler_bytes'],'/',END-ENTRY,'walker coverage',out['visited_stock_walker_selector'])
if __name__=='__main__':main()
