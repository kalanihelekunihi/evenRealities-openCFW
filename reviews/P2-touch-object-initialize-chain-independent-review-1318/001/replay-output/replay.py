from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-object-initialize-chain-independent-review-1318/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();word=lambda a:struct.unpack_from('<I',d,a-0x3300)[0];settings=word(0x3670);dest=word(0x3674);rows=[]
for timeout,fill in itertools.product([0,1,7,1000,65535],[0,0xa5,0xff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(settings+6,timeout.to_bytes(2,'little'));u.mem_write(dest-1,bytes([fill])*82);u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.emu_start(0x3659,0x09000000,count=1000)
 expected=(timeout or 1000).to_bytes(2,'little')+bytes(78)
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.mem_read(dest,80)==expected and u.mem_read(dest-1,1)==bytes([fill]) and u.mem_read(dest+80,1)==bytes([fill])
 rows.append(dict(timeout=timeout,initial_fill=fill,destination=dest,result=expected.hex()))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch object initialization chain 3658

3658..366E is a 22-byte caller excluding NOP/pool. Allocate a 16-byte frame, load settings halfword at literal base+6, put it at SP+4 and call 404C with literal destination and pointer to that halfword; restore frame. Actual 404C..406E is 34 instruction bytes excluding adjacent zero seam. If either pointer is null, return without data access. Otherwise actual A9D4 clears 80 bytes at destination, copy source halfword to destination offset zero, call actual 3EE8 and restore saved frame. Actual 3EE8..3EFA is 18 bytes: null pointer returns; nonzero first halfword stays unchanged; zero becomes 1000. Following zero halfword is unassigned.

Fifteen original-instruction chain fixtures cover five timeout values and three initial fills. All helpers execute directly. Verify complete 80-byte object, unchanged neighboring bytes and restored caller SP. Direct null-pointer entry branches are decoded but not executed by these chain fixtures; aliases, invalid pointers and concurrent writes remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=dict(settings=settings,destination=dest),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),hex(settings),hex(dest))
