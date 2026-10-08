from pathlib import Path
import json,struct,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import *
import unicorn.arm_const as a
HERE=Path(__file__).resolve().parent;ROOT=next(p for p in HERE.parents if (p/'AGENTS.md').exists());c=json.loads((HERE/'base-candidate.json').read_text());base=ROOT/c['directory']/'candidate.elf';addon=Path('/tmp/opencfw-pcm21-boost.elf');blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
segments=[];sy={}
for f in [base,addon]:
 with f.open('rb') as handle:
  e=ELFFile(handle)
  for s in e.iter_segments():
   if s['p_type']=='PT_LOAD':segments.append((int(s['p_vaddr']),s.data()))
  sy.update({s.name:int(s['st_value']) for s in e.get_section_by_name('.symtab').iter_symbols()})
visited=set()
def run(stock,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for addr,size in [(0x10000,0x10000),(0x30000,0x10000),(0x50000,0x10000),(0x410000,0x30000),(0x20000000,0x40000),(0x40000000,0x300000),(0x47ff0000,0x1000),(0xe000e000,0x2000),(0x8000000,0x20000)]:u.mem_map(addr,size)
 if stock:u.mem_write(0x410000,blob)
 else:
  for addr,data in segments:u.mem_write(addr,data)
 def w(addr,value):u.mem_write(addr,struct.pack('<I',value&0xffffffff))
 for addr,value in [(0x20000144,f['mode']),(0x4002037c,0x12340000),(0x40020044,0xabcdef00),(0x4002004c,0x11223300),(0x200270a8,0x79),(0x200270ac,0x6a),(0x40020080,f['trim']),(0x200270a4,f['delta']),(0x20026c08,0x12345678),(0x40020088,0xffffff00),(0x400201b0,0xfedcba98),(0x400083e0,0xffffffff),(0x40008010,0xffffffff)]:w(addr,value)
 u.mem_write(0x200271b2,bytes([f['switching']]));u.mem_write(0x200271ae,bytes([f['skip_restore']]));u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x8000001);u.reg_write(a.UC_ARM_REG_PRIMASK,f['mask']);writes=[];done=[False]
 def code(cpu,pc,size,data):
  if pc==0x8000000:done[0]=True;cpu.emu_stop();return
  if not stock and 0x410000<=pc<0x435000:raise AssertionError(('locked code on source',hex(pc)))
  if stock and 0x42ae9c<=pc<0x42aeec:visited.update(range(pc,pc+size))
 def write(cpu,access,addr,size,value,data):
  if 0x40000000<=addr<0x40300000 or 0xe000e000<=addr<0xe0020000 or 0x20027000<=addr<0x20027200:writes.append([addr,size,value&((1<<(size*8))-1)])
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((0x42ae9c if stock else sy['pcm21_boost_service'])|1,0,count=200000);assert done[0],hex(u.reg_read(a.UC_ARM_REG_PC))
 return dict(result=u.reg_read(a.UC_ARM_REG_R0),mask=u.reg_read(a.UC_ARM_REG_PRIMASK),sp=u.reg_read(a.UC_ARM_REG_SP),writes=writes,switching=bytes(u.mem_read(0x200271b2,1)).hex())
rows=[]
for switching,skip,mode,mask,trim,delta in itertools.product([0,1],[0,1],[0,8,12,9],[0,1],[0xabc00000,0xabc003ff],[0,17]):
 f=dict(switching=switching,skip_restore=skip,mode=mode,mask=mask,trim=trim,delta=delta);x=run(True,f);y=run(False,f)
 if x!=y:(HERE/'failure.json').write_text(json.dumps(dict(fixture=f,stock=x,source=y),indent=2));raise AssertionError((f,x,y))
 rows.append(dict(fixture=f,result=x))
out=dict(status='PASS',cases=len(rows),base_elf_sha256=c['sha256'],addon_elf_sha256=hashlib.sha256(addon.read_bytes()).hexdigest(),original_body_sha256=hashlib.sha256(blob[0x1ae9c:0x1aeec]).hexdigest(),covered_body_bytes=len(visited),results=rows,limits=['Clock/timer/SCS accesses are synthetic registers; no peripheral W1C or concurrency proof.','Addon executes native critical-save, trim-restore, timer-stop and profile-trim providers from215object base; no external call stubs and no source-side locked instruction execution.','Shared helper namePCM22 timer stop refers to common stock41ccd6, not a PCM-specific behavior assumption.'])
(HERE/'comparison.json').write_text(json.dumps(out,indent=2));print('PASS',len(rows),len(visited),'original body bytes')
