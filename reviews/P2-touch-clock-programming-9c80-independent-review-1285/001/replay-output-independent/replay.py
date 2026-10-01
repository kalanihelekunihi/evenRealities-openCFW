from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-clock-programming-9c80-independent-review-1285/001/replay-output-independent');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for requested,trim,mask,enabled in itertools.product([24000000,28000000,32000000,36000000,40000000,44000000,48000000,0,25000000],range(8),[0,1],[0,1]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x40030000,0x1000);u.mem_write(0x40030030,(enabled<<31).to_bytes(4,'little'));u.mem_write(0x40030f08,trim.to_bytes(4,'little'));u.mem_write(0x40030f18,(0xa5a5a5a5).to_bytes(4,'little'));u.mem_map(0xffff000,0x1000);table1=bytes((i*3+7)&255 for i in range(32));table2=bytes((i*5+9)&255 for i in range(32));u.mem_write(0xffff1e5,table1);u.mem_write(0xffff1cc,table2);table1=bytes(u.mem_read(0xffff1e5,32));table2=bytes(u.mem_read(0xffff1cc,32));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,requested);u.reg_write(UC_ARM_REG_PRIMASK,mask);writes=[];reads=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a>=0x40000000 else None);u.hook_add(UC_HOOK_MEM_READ,lambda u,t,a,s,v,x:reads.append([a,s]) if 0xffff000<=a<0x10000000 else None);u.emu_start(0x9c81,0,count=1000)
 accepted=requested in range(24000000,48000001,4000000);ret=0x4a0003 if not enabled else (0 if accepted else 0x4a0001);expected=[];expected_reads=[]
 if enabled and accepted and requested!=24000000+4000000*trim:
  index=(requested-24000000)//1000000;expected_reads=[[0xffff1e5+index,1],[0xffff1cc+index,1]];expected=[[0x40030f08,4,0],[0x40030f0c,4,table1[index]],[0x40030f10,4,0],[0x40030f18,4,table2[index]]]
  q=index>>2
  if q:expected += [[0x40030f08,4,(q-1)&7],[0x40030f08,4,q&7]]
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==ret and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PRIMASK)==mask
 assert writes==expected and reads==expected_reads,(requested,trim,writes,expected)
 rows.append(dict(requested=requested,trim=trim,enabled=enabled,initial_primask=mask,return_value=ret,table_reads=reads,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch clock programming 9C80 with explicit external tables

Body 9C80..9D4C is 204 instruction bytes. Require bit 31 of fresh 40030030 or return 004A0003. Accept only seven frequencies 24 through 48 million in steps of four million; other inputs return 004A0001. Actual 9C44 calculates current frequency; equality returns zero without programming.

Otherwise actual A6C0 computes index = unsigned(requested - 24000000) / 1000000. Actual 4492 saves and disables PRIMASK. Store zero to 40030F08, table1[index] to 40030F0C, zero to 40030F10, and table2[index] to 40030F18, using unsigned byte reads. Execute actual 4480 delay input 50. Set q = index >> 2. If q nonzero, freshly replace low three bits at 40030F08 with q-1, delay 50 again, then freshly replace them with q. Actual 449A restores saved PRIMASK; return zero with the six-word frame restored.

Table bases are literal addresses 0FFFF1E5 and 0FFFF1CC, outside this authenticated touch image. Fixtures supply explicit overlapping synthetic byte tables and derive expected bytes from their final supplied memory; original table contents and identity remain external obligations. All helpers execute their original instructions without substitution. Receipt-derived fixture count covers all supported requests, two invalid requests, eight trim values, both enable states and both masks. Exact writes, table read addresses, returns and frame/mask restoration are checked. Physical timing and external table identity remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),external_tables=['0x0FFFF1E5','0x0FFFF1CC'],files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
