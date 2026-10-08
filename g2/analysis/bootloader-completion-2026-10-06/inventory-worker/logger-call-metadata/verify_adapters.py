from pathlib import Path
import json,struct,hashlib,re
from elftools.elf.elffile import ELFFile
from unicorn import *
from unicorn import arm_const as a
N=Path(__file__).resolve().parent;R=next(p for p in N.parents if (p/'AGENTS.md').exists());capture=json.loads((N/'captured-calls.json').read_text());elf=Path('/tmp/opencfw-log-adapters.elf');blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
with elf.open('rb') as f:
 e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sy={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for r in capture['calls']:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for p,n in [(0x70000,0x10000),(0x8000000,4096),(0x20000000,0x40000)]:u.mem_map(p,n)
 for p,b in segs:u.mem_write(p,b)
 u.mem_write(0x8000100,b'\x70\x47');u.mem_write(0x20026ef8,struct.pack('<8I',*r['header_words']))
 if 'application_vector' in r:
  u.mem_map(0x438000,4096);u.mem_write(0x438000,struct.pack('<2I',*r['application_vector']))
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x8000001);got=[];done=[False]
 def string(p):
  v=bytearray()
  while u.mem_read(p,1)[0]:v+=u.mem_read(p,1);p+=1
  return v.decode('utf-8',errors='backslashreplace')
 def normalize(fmt,args,readstr):
  out=[]
  for code,v in zip(re.findall(r'%(?:z)?([sdux])',fmt),args):out.append(readstr(v) if code=='s' else v)
  return out
 def stockstr(p):
  off=p-0x410000;return blob[off:blob.index(b'\0',off)].decode('utf-8')
 def code(cpu,pc,size,_):
  if pc==0x8000000:done[0]=True;u.emu_stop();return
  if pc==0x8000100:
   regs=[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)];sp=u.reg_read(a.UC_ARM_REG_SP);w=list(struct.unpack('<8I',u.mem_read(sp,32)));fmt=string(w[1]);got.append(dict(level=regs[0],tag=string(regs[1]),file=string(regs[2]),function=string(regs[3]),line=w[0],format=fmt,arguments=normalize(fmt,w[2:],string)))
 u.hook_add(UC_HOOK_CODE,code)
 if r['family']=='allocator':entry=sy['opencfw_allocator_log_native'];args=[r['line']]
 elif r['family']=='control':entry=sy['opencfw_control_log_native'];args=[r['level'],r['line']]
 else:entry=sy['opencfw_dfu_log_detail_native'];args=[r['level'],r['line'],r['argument_words'][1] if r['line']==532 else 0]
 for i,v in enumerate(args):u.reg_write(getattr(a,f'UC_ARM_REG_R{i}'),v)
 u.emu_start(entry|1,0,count=10000);assert done[0]
 expected={k:r[k] for k in ['level','tag','file','function','line','format']};expected['arguments']=normalize(r['format'],r['argument_words'],stockstr)
 if got!=[expected]:(N/'adapter-failure.json').write_text(json.dumps(dict(original=r,expected=expected,source=got),indent=2));raise AssertionError((r['family'],r['line'],expected,got))
 rows.append(dict(original_return_address=r['return_address'],family=r['family'],result=expected))
result=dict(status='PASS_ADAPTERS_AGAINST_ORIGINAL_CALL_METADATA',cases=len(rows),source_sha256=hashlib.sha256((R/'g2/components/bootloader/log_call_adapters/log_adapters.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),capture_sha256=hashlib.sha256((N/'captured-calls.json').read_bytes()).hexdigest(),comparisons=rows,limits=['Replays captured stock header/vector snapshots and consumes only format-defined variadic words. Actual compiled adapters execute, but logger/transport child is a ThumbBXLR fixture.','Adapters are new source bridges for fixed caller lines, not recovered stock function bodies, no bytes added to ownership ledger. Detail532 must be supplied by revised task caller; source caller coupling remains separate.'])
(N/'adapter-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['cases'])
