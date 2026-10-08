#!/usr/bin/env python3
"""Verify integrated selector17 scatter install and native 9->10 dispatch."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn import arm_const as a
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
FUNCTIONS=ROOT/'g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl'
SELECTORS=ROOT/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/gx-native/scatter-selector-table.json'
BASE_BINDINGS=HERE/'native-selector-bindings.json'
INPUT_MANIFEST=Path('/tmp/opencfw-root-pcm22-relocated/handler17-integrated/input-manifest.json')
ELF_READER=ROOT/'g2/components/bootloader/update_core/elf_reader.py'
V17_PATH=ROOT/'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/pcm2_2-handler17/verify17.py'
IMAGE_SHA='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
RECORD=0x433104;STOCK_DECODER=0x415326;TABLE=0x20000158;STOP=0x08000000
HANDLER=(0x429718,0x42984e,'1800926f5cd512a3f3b45b77aa8f9edc1969de9c3a658341aa6a23650c6e6480')
WALKER=(0x42a43a,0x42a4bc,'1075e4055c2ef66d985f8938f881a08d43a90791be3dc0b2700ff7e0074ed107')
SEQUENCER=(0x42a2b4,0x42a43a,'c02ca4144181ebe16c3dffc47e1bec89a89fbb832fa8bb134b38dd8bf287444f')
MATRIX=(0x433498,28,'d83c73b1f5370cc6063489aedc4f0701bdec2ca34a492233caa521c0cf2ea5e8')
spec=importlib.util.spec_from_file_location('elf_reader',ELF_READER);er=importlib.util.module_from_spec(spec);spec.loader.exec_module(er)
vspec=importlib.util.spec_from_file_location('verify17',V17_PATH);v17=importlib.util.module_from_spec(vspec);vspec.loader.exec_module(v17)
def p32(x):return struct.pack('<I',x&0xffffffff)
def make_uc():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,sz in [(0,0x1000),(0x08000000,0x20000),(0x10000,0x40000),(0x20000000,0x40000),(0x40000000,0x100000),(0x410000,0x25000),(0xe0000000,0x200000),(0x47ff0000,0x1000)]:u.mem_map(lo,sz)
 return u
def load_source(u,segments):
 for seg in segments:u.mem_write(seg['address'],seg['data'])
def install(u,source,image,segments,symbols,source_adapter_range=None):
 u.mem_write(0x20000000,b'\xa5'*1372);u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
 u.reg_write(a.UC_ARM_REG_R0,RECORD);u.reg_write(a.UC_ARM_REG_R1,0);u.reg_write(a.UC_ARM_REG_R9,0)
 if source:
  entry=symbols['opencfw_boot_expand_adapter']&~1
  assert source_adapter_range==(entry,entry+6)
 else:
  u.mem_write(0x410000,image);entry=STOCK_DECODER
 done=[False];trace=[]
 def code(cpu,pc,size,_):
  if pc==STOP:done[0]=True;cpu.emu_stop();return
  if source:
   if 0x410000<=pc<0x435000:
    assert source_adapter_range[0]<=pc<source_adapter_range[1],f'source executed non-source locked bytes {pc:#x}'
  else:
   if STOCK_DECODER<=pc<0x416000:trace.append([pc,bytes(cpu.mem_read(pc,size)).hex()])
 h=u.hook_add(UC_HOOK_CODE,code);u.emu_start(entry|1,0,count=500000);u.hook_del(h);assert done[0],('scatter adapter did not return',source,hex(u.reg_read(a.UC_ARM_REG_PC)))
 raw=bytes(u.mem_read(0x20000000,1372));ret=u.reg_read(a.UC_ARM_REG_R0)
 assert raw[1371]==0xa5
 return raw,ret,trace
def get_mask(u,symbols):
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1);done=[False]
 def code(cpu,pc,size,_):
  if pc==STOP:done[0]=True;cpu.emu_stop()
  elif 0x410000<=pc<0x435000:raise AssertionError(f'mask source executed locked code {pc:#x}')
 h=u.hook_add(UC_HOOK_CODE,code);u.emu_start((symbols['opencfw_boot_selector_source_mask']&~1)|1,0,count=10000);u.hook_del(h);assert done[0]
 return u.reg_read(a.UC_ARM_REG_R0)
def run_direct(stock,u,symbols,source_range,fixture):
 v17.seed(u,fixture);writes=[];waits=[];visited=set();done=[False]
 entry=HANDLER[0] if stock else symbols['opencfw_spot_pcm22_transition17']&~1
 def code(cpu,pc,size,_):
  if pc==STOP:done[0]=True;cpu.emu_stop();return
  if pc==0x40:waits.append(cpu.reg_read(a.UC_ARM_REG_R0));cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  if stock and HANDLER[0]<=pc<HANDLER[1]:visited.update(range(pc,pc+size))
  if not stock and 0x410000<=pc<0x435000:
   assert source_range[0]<=pc<source_range[1],f'source direct handler executed locked bytes {pc:#x}'
 def wr(cpu,access,addr,size,value,_):
  if 0x40000000<=addr<0x40100000 or 0xe0000000<=addr<0xe0020000:writes.append([addr,size,value&((1<<(8*size))-1)])
 h=u.hook_add(UC_HOOK_CODE,code);wh=u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40000000,end=0x400fffff)
 try:u.emu_start(entry|1,0,count=1000000)
 except Exception as e:raise RuntimeError((fixture['name'],'stock' if stock else 'source',hex(u.reg_read(a.UC_ARM_REG_PC)))) from e
 finally:u.hook_del(h);u.hook_del(wh)
 assert done[0],('direct handler did not return',stock,fixture['name'],hex(u.reg_read(a.UC_ARM_REG_PC)))
 out={'return':[u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)],'state':{f'{x:08x}':bytes(u.mem_read(x,4)).hex() for x in v17.STATE},'writes':writes,'wait_cycles':waits,'callee_saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],'sp':u.reg_read(a.UC_ARM_REG_SP),'primask':u.reg_read(a.UC_ARM_REG_PRIMASK)}
 return out,visited
def run_walker(stock,u,symbols,source_range,fixture):
 v17.seed(u,fixture);writes=[];waits=[];calls=[];coverage={'walker':set(),'selector':set(),'handler':set()};done=[False]
 start=WALKER[0] if stock else symbols['event_a_temperature_transition_separate']&~1
 hentry=HANDLER[0] if stock else symbols['opencfw_spot_pcm22_transition17']&~1
 def code(cpu,pc,size,_):
  if pc==STOP:done[0]=True;cpu.emu_stop();return
  if pc==0x40:waits.append(cpu.reg_read(a.UC_ARM_REG_R0));cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
  if stock:
   for name,(lo,hi,_) in {'walker':WALKER,'selector':SEQUENCER,'handler':HANDLER}.items():
    if lo<=pc<hi:coverage[name].update(range(pc,pc+size))
  elif 0x410000<=pc<0x435000:
   assert source_range[0]<=pc<source_range[1],f'source walker executed locked bytes {pc:#x}'
  if pc==hentry:calls.append([cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)])
 def wr(cpu,access,addr,size,value,_):
  if 0x40000000<=addr<0x40100000 or 0xe0000000<=addr<0xe0020000:writes.append([addr,size,value&((1<<(8*size))-1)])
 h=u.hook_add(UC_HOOK_CODE,code);wh=u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40000000,end=0x400fffff)
 try:u.emu_start(start|1,0,count=2000000)
 except Exception as e:raise RuntimeError(('source' if not stock else 'stock',hex(u.reg_read(a.UC_ARM_REG_PC)))) from e
 finally:u.hook_del(h);u.hook_del(wh)
 assert done[0],('walker did not return',stock,hex(u.reg_read(a.UC_ARM_REG_PC)),calls)
 state={f'{x:08x}':bytes(u.mem_read(x,4)).hex() for x in v17.STATE}
 out={'return':[u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)],'state':state,'writes':writes,'wait_cycles':waits,'callback_args':calls,'callee_saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],'sp':u.reg_read(a.UC_ARM_REG_SP),'primask':u.reg_read(a.UC_ARM_REG_PRIMASK)}
 return out,coverage
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--frozen-base',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 blob=IMAGE.read_bytes();assert hashlib.sha256(blob).hexdigest()==IMAGE_SHA
 basehash=hashlib.sha256(args.frozen_base.read_bytes()).hexdigest()
 global INPUT_MANIFEST
 INPUT_MANIFEST=args.candidate.parent/'input-hashes.json'
 manifest=json.loads(INPUT_MANIFEST.read_text());assert hashlib.sha256(args.candidate.read_bytes()).hexdigest()==manifest['elf_sha256']
 for item in manifest['inputs']:
  staged=args.candidate.parent/item['path'];assert hashlib.sha256(staged.read_bytes()).hexdigest()==item['sha256']
 _,segments,symbols=er.elf_info(args.candidate)
 for n in ('opencfw_boot_expand_adapter','opencfw_boot_expand_locked_data_record','opencfw_boot_install_initialized_data','opencfw_boot_selector_source_mask','event_a_temperature_transition_separate','event_a_state_transition_sequence','opencfw_spot_pcm22_transition17'):assert n in symbols,n
 source_adapter=symbols['opencfw_boot_expand_adapter']&~1;source_range=(source_adapter,source_adapter+6)
 adapter_segment=next(s for s in segments if s['address']<=source_adapter and source_adapter+6<=s['address']+len(s['data']))
 adapter_bytes=adapter_segment['data'][source_adapter-adapter_segment['address']:source_adapter-adapter_segment['address']+6]
 assert adapter_bytes and source_adapter==STOCK_DECODER
 # Verify selector17 locked extent/hash and boundary controls against the pinned image.
 recs={int((d:=json.loads(l))['entry'],16):d for l in FUNCTIONS.read_text().splitlines()}
 for entry,end,digest in (HANDLER,WALKER,SEQUENCER):
  body=blob[entry-0x410000:end-0x410000];assert hashlib.sha256(body).hexdigest()==digest and int(recs[entry]['body_end_inclusive'],16)+1==end
 body=blob[HANDLER[0]-0x410000:HANDLER[1]-0x410000];assert hashlib.sha256(body[:-1]).hexdigest()!=HANDLER[2] and hashlib.sha256(blob[HANDLER[0]-0x410000:HANDLER[1]+1-0x410000]).hexdigest()!=HANDLER[2]
 assert hashlib.sha256(blob[MATRIX[0]-0x410000:MATRIX[0]-0x410000+MATRIX[1]]).hexdigest()==MATRIX[2]
 table=json.loads(SELECTORS.read_text());binding=json.loads(BASE_BINDINGS.read_text());assert table['output_bytes']==1371 and binding['source_mask']=='0x707c10f'
 assert binding['slots'].get('17')=='opencfw_spot_pcm22_transition17'
 # Separate machines: stock receives locked image; source receives candidate ELF segments only.
 stock_uc=make_uc();source_uc=make_uc();load_source(source_uc,segments)
 stock_raw,stock_return,stock_trace=install(stock_uc,False,blob,segments,symbols)
 source_raw,source_return,_=install(source_uc,True,blob,segments,symbols,source_range)
 assert stock_return==source_return==RECORD+12,(hex(stock_return),hex(source_return))
 assert hashlib.sha256(stock_raw[:1371]).hexdigest()==table['output_sha256']=='e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843'
 assert source_raw[1371]==stock_raw[1371]==0xa5
 normalized=bytearray(source_raw)
 for slot,name in binding['slots'].items():
  off=0x158+4*int(slot);actual=struct.unpack_from('<I',source_raw,off)[0]
  assert name in symbols and actual==(symbols[name]|1),(slot,hex(actual),name,hex(symbols.get(name,0)))
  normalized[off:off+4]=stock_raw[off:off+4]
 for off,name in [(0x4d0,'opencfw_boot_dfu_thread_deinit_native'),(0x4f8,'opencfw_boot_manager_thread_deinit')]:
  assert struct.unpack_from('<I',source_raw,off)[0]==symbols[name]|1
  normalized[off:off+4]=stock_raw[off:off+4]
 assert bytes(normalized)==stock_raw
 slot17=struct.unpack_from('<I',source_raw,0x158+17*4)[0];assert slot17==((symbols['opencfw_spot_pcm22_transition17']|1))
 assert hashlib.sha256(bytes(stock_raw[:1371])).hexdigest()==hashlib.sha256(bytes(normalized[:1371])).hexdigest()
 mask=get_mask(source_uc,symbols);assert mask==0x707c10f,hex(mask)
 # Invoke the native slot17 handler only after source DATA has installed its real relocated pointer.
 direct_rows=[];direct_coverage=set()
 for fixture in v17.fixtures():
  stock_out,covered=run_direct(True,stock_uc,{},None,fixture)
  source_out,_=run_direct(False,source_uc,symbols,source_range,fixture)
  assert stock_out==source_out,(fixture['name'],stock_out,source_out)
  direct_rows.append({'fixture':fixture,'result':stock_out});direct_coverage|=covered
 # The source and stock walkers consume the tables just installed above; no pointer is rewritten.
 fx=v17.walker_fixture();stock_out,stock_cov=run_walker(True,stock_uc,{},None,fx);source_out,source_cov=run_walker(False,source_uc,symbols,source_range,fx)
 assert stock_out==source_out,(stock_out,source_out);assert stock_out['callback_args']==[[10,9,3,1]],stock_out['callback_args'];assert stock_out['return']==[17,1],stock_out['return']
 ranges={'walker':WALKER[:2],'selector':SEQUENCER[:2],'handler':HANDLER[:2]}
 unvisited={k:[hex(x) for x in sorted(set(range(lo,hi))-stock_cov[k])] for k,(lo,hi) in ranges.items()}
 out={'status':'PASS','candidate':str(args.candidate),'candidate_sha256':hashlib.sha256(args.candidate.read_bytes()).hexdigest(),'frozen_base':str(args.frozen_base),'frozen_base_sha256':basehash,'input_manifest':str(INPUT_MANIFEST),'input_manifest_sha256':hashlib.sha256(INPUT_MANIFEST.read_bytes()).hexdigest(),'frozen_link_object_copies':manifest['linked_objects'],'original_image_sha256':IMAGE_SHA,'modified_inputs':{'initialized_data_c_sha256':hashlib.sha256((HERE/'initialized_data.c').read_bytes()).hexdigest(),'handler17_c_sha256':hashlib.sha256((HERE.parent/'pcm2_2-handler17-integrated/handler17.c').read_bytes()).hexdigest(),'module_ld_sha256':hashlib.sha256((HERE/'module.ld').read_bytes()).hexdigest(),'native_bindings_sha256':hashlib.sha256((HERE/'native-selector-bindings.json').read_bytes()).hexdigest(),'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},'scatter_adapter':{'address':hex(source_adapter),'source_bytes':adapter_bytes.hex(),'record_address':hex(RECORD),'record_fields':list(struct.unpack_from('<III',source_uc.mem_read(RECORD,12))),'return_stock':hex(stock_return),'return_source':hex(source_return),'normalized_initialized_bytes':1371,'stock_initialized_sha256':hashlib.sha256(stock_raw[:1371]).hexdigest(),'source_initialized_sha256':hashlib.sha256(source_raw[:1371]).hexdigest(),'normalized_source_sha256':hashlib.sha256(bytes(normalized[:1371])).hexdigest(),'padding_stock':stock_raw[1371],'padding_source':source_raw[1371],'selector_table_sha256':hashlib.sha256(stock_raw[0x158:0x158+108]).hexdigest(),'source_selector17':hex(slot17),'source_mask':hex(mask),'stock_decoder_trace_instructions':len(stock_trace)},'direct14':{'count':len(direct_rows),'stock_source_equal':True,'visited_stock_handler_bytes':len(direct_coverage),'unvisited_addresses':[hex(x) for x in sorted(set(range(HANDLER[0],HANDLER[1]))-direct_coverage)],'comparisons':direct_rows},'walker':{'fixture':fx,'matrix_selection':{'current_state':9,'target_state':10,'selector':17,'reason':'special current9->target10 gt0->le0 transition'},'stock_source_equal':stock_out==source_out,'callback_args':stock_out['callback_args'],'return':stock_out['return'],'visited_stock_bytes':{k:len(v) for k,v in stock_cov.items()},'unvisited_addresses':unvisited,'ordered_writes':stock_out['writes']},'limits':['The source machine loads only successor ELF segments. The adapter at 0x415326 is source assembly present in that ELF, verified by address and bytes; no locked image bytes are loaded on the source side.','The source table is installed through its scatter adapter and checked byte-for-byte after normalizing only native callback relocations. Selector17 is not manually rebound; the 14 direct handler fixtures call the pointer after this installation.','Stock decoder/walker execute the pinned official image on a separate machine. Offline differential proves only these initialized records and selector17 paths; no seven-test suite or whole-firmware equivalence claim is made.']}
 args.output.write_text(json.dumps(out,indent=2)+'\n');print('PASS scatter adapter output normalized to 1371 stock bytes; slot17',hex(slot17),'mask',hex(mask),'walker args',stock_out['callback_args'],'return',stock_out['return'])
if __name__=='__main__':main()
