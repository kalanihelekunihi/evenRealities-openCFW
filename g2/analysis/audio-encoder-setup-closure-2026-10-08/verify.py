from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-encoder-setup/setup.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
A=0x20106000;M=A+28;span=0x8000;ret=0x2007f000

def run(native,hr,dt,sr,pcm,kind='setup',null=False,address=A,config=None):
 A=address;M=A+28
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x20100000,0x20000);u.mem_map(0x100000,0x10000)
 for a,b in segments:u.mem_write(a,b)
 u.mem_write(A,bytes([0xa5])*span);u.mem_write(A,struct.pack('<7I',*(config or [0,dt&0xffffffff,sr&0xffffffff,1,0,32000,0xdeadbeef])));calls=[]
 def hook(u,a,n,d):
  if a in [0x48949c,0x439c04,0x4d4ccc]:calls.append(dict(entry=hex(a),r0=hex(u.reg_read(UC_ARM_REG_R0)),r1=u.reg_read(UC_ARM_REG_R1),r2=u.reg_read(UC_ARM_REG_R2)))
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,ret|1)
 if kind=='reset':args=[0 if null else A];entry=sym['audio_encoder_reset_config'] if native else 0x57a926
 elif kind=='standard':args=[dt,sr,pcm,0 if null else M];entry=sym['audio_encoder_setup_standard'] if native else 0x591374
 else:
  args=[hr,dt,sr,pcm];entry=sym['audio_encoder_setup_selected'] if native else 0x59123a;u.mem_write(0x2007e000,struct.pack('<I',0 if null else M))
 for i,v in enumerate(args):u.reg_write([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3][i],v&0xffffffff)
 u.emu_start(entry|1,ret,count=300000);assert u.reg_read(UC_ARM_REG_PC)==ret,(native,hr,dt,sr,pcm,kind,hex(u.reg_read(UC_ARM_REG_PC)))
 mem=bytes(u.mem_read(A,span));result=u.reg_read(UC_ARM_REG_R0) if kind!='reset' else None
 return mem,result,calls
cases=[(0,d,s,p,'setup',False) for d,s,p in itertools.product([2500,5000,7500,10000],[8000,16000,24000,32000,48000],[0,8000,16000,24000,32000,48000,96000])]
cases += [(1,d,s,p,'setup',False) for d,s,p in itertools.product([2500,5000,7500,10000],[48000,96000],[0,48000,96000])]
cases += [(0,d,s,p,'setup',n) for d,s,p,n in [(0,16000,0,False),(-1,16000,0,False),(10001,16000,0,False),(10000,0,0,False),(10000,12345,0,False),(10000,16000,-1,False),(10000,16000,12345,False),(10000,16000,0,True)]]
cases += [(0,10000,s,0,k,n) for s,k,n in [(16000,'standard',False),(16000,'standard',True),(16000,'reset',False),(16000,'reset',True),(12345,'reset',False),(48000,'reset',False)]]
rows=[]
for hr,dt,sr,pcm,kind,null in cases:
 original,rv,calls=run(False,hr,dt,sr,pcm,kind,null);independent,nrv,ncalls=run(True,hr,dt,sr,pcm,kind,null);assert original==independent and rv==nrv,(hr,dt,sr,pcm,kind,null,'mismatch');assert not ncalls
 changed=[i for i,(a,b) in enumerate(zip(original,struct.pack('<7I',0,dt&0xffffffff,sr&0xffffffff,1,0,32000,0xdeadbeef)+bytes([0xa5])*(span-28))) if a!=b]
 rows.append(dict(hr=hr,dt=dt,sample_rate=sr,pcm_sample_rate=pcm,kind=kind,null_memory=null,return_value=None if rv is None else hex(rv),config_encoder_pointer=hex(struct.unpack_from('<I',original,24)[0]),geometry=list(struct.unpack_from('<3I',original,28+0x4a0)),last_changed_offset=max(changed) if changed else None,original_memory_provider_calls=calls,workspace_sha256=hashlib.sha256(original).hexdigest()))
stock_path=root/'g2/analysis/audio-diagnostic-deinit-closure-2026-10-08/startup-config-results.json';stock=json.loads(stock_path.read_text());stock_rows=[]
for address,words in stock['configs'].items():
 config=[int(v,16) for v in words];a=int(address,16);original,rv,calls=run(False,0,config[1],config[2],0,'reset',False,a,config);independent,nrv,ncalls=run(True,0,config[1],config[2],0,'reset',False,a,config);assert original==independent and rv==nrv
 assert struct.unpack_from('<I',original,24)[0]==a+28
 stock_rows.append(dict(config_address=address,authenticated_initial_words=words,encoder_pointer=hex(a+28),original_memory_provider_calls=calls,workspace_sha256=hashlib.sha256(original).hexdigest()))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows)+len(stock_rows),comparisons=rows,authenticated_config_comparisons=stock_rows,authenticated_config_input=str(stock_path.relative_to(root)),authenticated_config_input_sha256=hashlib.sha256(stock_path.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Complete selected setup bytes and copy/zero providers execute; no provider stubs.','Constructed caller-supplied mapped workspace; no allocator, mutex, scheduler, encode body or hardware execution.','Independent C uses mathematical selectors/geometry and own byte stores; full workspace compared including unchanged sentinel bytes.','Reset wrapper has void ABI; compare config encoder pointer and workspace, not undefined r0.']),indent=2)+'\n');print('PASS',len(rows)+len(stock_rows),'encoder setup comparisons')
