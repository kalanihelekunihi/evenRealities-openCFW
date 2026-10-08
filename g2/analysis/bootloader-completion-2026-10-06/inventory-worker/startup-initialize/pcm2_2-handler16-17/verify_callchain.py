#!/usr/bin/env python3
"""Compare the authenticated stock selector16 call chain with standalone source ELF."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[5]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
SELECTORS=ROOT/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/gx-native/scatter-selector-table.json'
NATIVE_BINDINGS=ROOT/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/pcm2_2-relocated/native-selector-bindings.json'
ELF_READER=ROOT/'g2/components/bootloader/update_core/elf_reader.py'
IMAGE_SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
WALKER=(0x42a43a,0x42a4bc,'1075e4055c2ef66d985f8938f881a08d43a90791be3dc0b2700ff7e0074ed107')
SEQUENCER=(0x42a2b4,0x42a43a,'c02ca4144181ebe16c3dffc47e1bec89a89fbb832fa8bb134b38dd8bf287444f')
MATRIX=(0x433498,28,'d83c73b1f5370cc6063489aedc4f0701bdec2ca34a492233caa521c0cf2ea5e8')
HANDLER=(0x42962c,0x429700,'2b4c090e8bf6f3a2913292d2a4c7b9e1c8ef90ea746d0575bdca6c8153cdca17')
TABLE=0x20000158; STOP=0x08000000; ENTRY=0x415326
_stock_raw=None
spec=importlib.util.spec_from_file_location('elf_reader',ELF_READER); er=importlib.util.module_from_spec(spec); spec.loader.exec_module(er)
vspec=importlib.util.spec_from_file_location('verify16',HERE/'verify.py'); verify=importlib.util.module_from_spec(vspec);vspec.loader.exec_module(verify)
def p32(x): return struct.pack('<I',x&0xffffffff)
def pack(vddf,active,tempco,vddc): return (vddf&127)|((active&1023)<<7)|((tempco&15)<<17)|((vddc&127)<<21)
def setup_fixture(timer):
    i=3; prof=[pack((13+7*i+11*j)&127,(31+43*i+71*j)&1023,(i+3*j)&15,(17+9*i+13*j)&127) for j in range(21)]
    low=[(i*31+j*41)&127 for j in range(4)]
    return {'name':'current6-target5-selector16','walker_args':[5,6,3,1],'handler_args':[5,6,3,1], 'profiles':prof,'low_voltage':low,'timer_control':0x80001235 if timer else 0,'timer_status':0x40000000 if timer else 0,'timer_state':26 if timer else 0,'clock_user':bool(timer),'mode':0}
def seed(u,f):
    info=bytearray(0x6c);struct.pack_into('<I',info,0,0x1f01600d)
    for i,w in enumerate(f['profiles']):struct.pack_into('<I',info,4+4*i,w)
    info[0x64:0x68]=bytes(f['low_voltage']);u.mem_write(0x20026ba0,bytes(info))
    for addr in [0x200270b0,0x200270b4,0x200270b8,0x200270bc,0x200270c0,0x200270c4,0x40020044,0x40020048,0x4002004c,0x40020080]:u.mem_write(addr,p32(0x5a5a0000|(addr&0xffff)))
    for addr,val in [(0x40021000,f['mode']),(0x400083e0,f['timer_control']),(0x40008064,f['timer_status']),(0x400083e8,0x1234),(0x40008010,0x8000),(0x40008068,0x76543210),(0x4002037c,0xa5123456),(0x40004030,0x01000000),(0x40004044,0x20),(0x20027030,0),(0x20027044,0),(0x47ff0000,0x12345678)]:u.mem_write(addr,p32(val))
    u.mem_write(0x20000550,b'\x01');u.mem_write(0x2000055a,bytes([f['timer_state']]));u.mem_write(0x20026e74,bytes(56));u.mem_write(0x2002719c,b'\0');u.mem_write(0x2002719e,b'\0')
    if f['clock_user']:u.mem_write(0x20026ea8,p32(1<<17))
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1);u.reg_write(a.UC_ARM_REG_PRIMASK,0)
    for i,v in enumerate(f['walker_args']):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),v)
def main():
 global _stock_raw
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 blob=IMAGE.read_bytes();assert hashlib.sha256(blob).hexdigest()==IMAGE_SHA
 receipt=json.loads(SELECTORS.read_text());assert receipt['status']=='PASS' and receipt['original_sha256']==IMAGE_SHA and receipt['callback_table_address']==hex(TABLE) and receipt['output_bytes']==1371 and receipt['output_sha256']=='e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843'
 targets=[int(x['thumb_target'],16) for x in receipt['selectors']];assert len(targets)==27 and [x['selector'] for x in receipt['selectors']]==list(range(27))
 funcs={int((d:=json.loads(l))['entry'],16):d for l in (ROOT/'g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines()}
 for entry,end,digest in (WALKER,SEQUENCER):
  body=blob[entry-0x410000:end-0x410000];assert int(funcs[entry]['body_end_inclusive'],16)+1==end and len(body)==end-entry and hashlib.sha256(body).hexdigest()==digest
 assert hashlib.sha256(blob[MATRIX[0]-0x410000:MATRIX[0]-0x410000+MATRIX[1]]).hexdigest()==MATRIX[2]
 assert hashlib.sha256(blob[HANDLER[0]-0x410000:HANDLER[1]-0x410000]).hexdigest()==HANDLER[2]
 _,segments,symbols=er.elf_info(args.elf)
 for sym in ('event_a_temperature_transition_separate','event_a_state_transition_sequence','opencfw_spot_pcm22_transition16','opencfw_boot_install_initialized_data'):assert sym in symbols,sym
 source_walker=symbols['event_a_temperature_transition_separate']&~1; source_handler=symbols['opencfw_spot_pcm22_transition16']&~1
 def run(stock,f):
  global _stock_raw
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
  for lo,sz in [(0,0x1000),(0x08000000,0x1000),(0x10000,0x40000),(0x20000000,0x40000),(0x40000000,0x100000),(0x410000,0x25000),(0xe0000000,0x200000),(0x47ff0000,0x1000)]:u.mem_map(lo,sz)
  if stock:u.mem_write(0x410000,blob);start=WALKER[0]
  else:
   for seg in segments:u.mem_write(seg['address'],seg['data'])
   start=source_walker
  # Install authentic decoded stock table or execute the source-owned initializer before fixture state.
  u.mem_write(0x20000000,b'\xa5'*1372);u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
  u.reg_write(a.UC_ARM_REG_R0,0x433104 if stock else 0);u.reg_write(a.UC_ARM_REG_R1,0);u.reg_write(a.UC_ARM_REG_R9,0)
  init=ENTRY if stock else (symbols['opencfw_boot_install_initialized_data']&~1);doneinit=[False]
  def init_hook(cpu,pc,size,_):
   if pc==STOP:doneinit[0]=True;cpu.emu_stop();return
   if not stock and 0x410000<=pc<0x435000:raise AssertionError(f'source installer executed locked code {pc:#x}')
  ih=u.hook_add(UC_HOOK_CODE,init_hook);u.emu_start(init|1,0,count=200000);u.hook_del(ih);assert doneinit[0]
  raw=bytes(u.mem_read(0x20000000,1371));assert u.mem_read(0x20000000+1371,1)==b'\xa5'
  bindings=json.loads(NATIVE_BINDINGS.read_text())['slots'];normalized=bytearray(raw)
  if stock:
   assert hashlib.sha256(raw).hexdigest()==receipt['output_sha256'];_stock_raw=raw
  else:
   for slot,name in bindings.items():
    off=0x158+int(slot)*4;actual=struct.unpack_from('<I',raw,off)[0];assert actual==(symbols[name]|1),(slot,hex(actual),name,hex(symbols.get(name,0)))
    normalized[off:off+4]=p32(targets[int(slot)])
   assert bytes(normalized)==_stock_raw
   assert struct.unpack_from('<I',raw,0x158+16*4)[0]==(source_handler|1)
  table_data=bytes(u.mem_read(TABLE,108));seed(u,f);writes=[];waits=[];calls=[];cv={'walker':set(),'selector':set(),'handler':set()};done=[False]
  def code(cpu,pc,size,_):
   if pc==STOP:done[0]=True;cpu.emu_stop();return
   if pc==0x40:waits.append(cpu.reg_read(a.UC_ARM_REG_R0));cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
   if stock:
    if WALKER[0]<=pc<WALKER[1]:cv['walker'].update(range(pc,pc+size))
    if SEQUENCER[0]<=pc<SEQUENCER[1]:cv['selector'].update(range(pc,pc+size))
    if HANDLER[0]<=pc<HANDLER[1]:cv['handler'].update(range(pc,pc+size))
   elif 0x410000<=pc<0x435000:raise AssertionError(f'source executed locked code at {pc:#x}')
   if pc==(HANDLER[0] if stock else source_handler):calls.append([cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)])
  def wr(cpu,access,addr,size,value,_):
   if 0x40000000<=addr<0x40100000 or 0xe0000000<=addr<0xe0020000:writes.append([addr,size,value&((1<<(8*size))-1)])
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40000000,end=0x400fffff)
  try:u.emu_start(start|1,0,count=1000000)
  except Exception as exc:raise RuntimeError((f['name'],stock,hex(u.reg_read(a.UC_ARM_REG_PC)))) from exc
  assert done[0],(f['name'],'did not return',hex(u.reg_read(a.UC_ARM_REG_PC)))
  out={'calls':calls,'return_regs':[u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)],'state':{f'{p:08x}':bytes(u.mem_read(p,4)).hex() for p in [0x200270b0,0x200270b4,0x200270b8,0x200270bc,0x200270c0,0x200270c4,0x40020044,0x40020048,0x40020080,0x400083e0,0x40008064,0x2000055a]},'writes':writes,'wait_cycles':waits,'callee_saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],'sp':u.reg_read(a.UC_ARM_REG_SP),'primask':u.reg_read(a.UC_ARM_REG_PRIMASK)}
  return out,cv,{'raw_sha256':hashlib.sha256(raw).hexdigest(),'normalized_sha256':hashlib.sha256(normalized).hexdigest(),'slot16':hex(struct.unpack_from('<I',raw,0x158+64)[0]),'table_sha256':hashlib.sha256(table_data).hexdigest()}
 fixtures=[setup_fixture(False),setup_fixture(True)];rows=[];coverage={k:set() for k in ('walker','selector','handler')}
 for f in fixtures:
  stock,cv,st=run(True,f);source,_,so=run(False,f);assert stock==source,(f['name'],stock,source);assert stock['calls']==[[5,6,3,1]],stock['calls']
  rows.append({'fixture':f,'selector_matrix_cell':{'current_group':1,'target_group':1,'base_sequence':25,'temperature_class':'le0(current)->gt0(target)','resolved_selector':16},'result':stock,'initialized_table':{'stock_sha256':st['raw_sha256'],'source_sha256':so['raw_sha256'],'normalized_sha256':so['normalized_sha256'],'source_slot16':so['slot16']}})
  for k,v in cv.items():coverage[k]|=v
 out={'status':'PASS','image_sha256':IMAGE_SHA,'candidate_elf':str(args.elf),'candidate_elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),'initialized_data_bytes':1371,'initialized_data_sha256':receipt['output_sha256'],'source_table_normalized_sha256':hashlib.sha256(_stock_raw).hexdigest(),'selector_table_address':hex(TABLE),'selector_table_bytes':108,'selector_table_sha256':receipt['callback_table_sha256'],'source_selector16_target':hex(source_handler|1),'temperature_matrix_address':hex(MATRIX[0]),'temperature_matrix_sha256':MATRIX[2],'walker_range':[hex(WALKER[0]),hex(WALKER[1])],'selector_range':[hex(SEQUENCER[0]),hex(SEQUENCER[1])],'handler_range':[hex(HANDLER[0]),hex(HANDLER[1])],'coverage':{k:len(v) for k,v in coverage.items()},'fixtures':rows,'limits':['The candidate executes its source-owned initialized-data installer before fixture state is applied; no callback-table slot is manually rebound. Authenticated source pointer relocations are normalized only for comparison to the locked initialized table.','Source execution traps if PC enters locked image range. ROM cycle-wait service at 0x40 is the only controlled peripheral boundary; timer, delay, clock, walker, selector, and handler source execute from the candidate.','Offline emulation only; no hardware or whole-firmware equivalence claim.']}
 args.output.write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(rows),'walker-selector-handler cases',out['coverage'])
if __name__=='__main__':main()
