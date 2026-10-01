from pathlib import Path
import json,hashlib
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-bit-scale-independent-review-1430/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x09000000,0x1000);u.hook_add(UC_HOOK_CODE,lambda u,p,s,x:u.emu_stop() if p==0x09000000 else None);results=[]
for value in range(65536):
 u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_LR,0x09000001);u.emu_start(0x6221,0,count=100)
 expected=(1<<max(1,value.bit_length()))-1
 assert u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_PC)==0x09000000
 results.append(expected)
raw=b''.join(x.to_bytes(2,'little') for x in results);(o/'results.bin').write_bytes(raw);(o/'pseudocode.md').write_text('# Highest-bit scale helper at 6220\n\nStart result at 65535 and mask at 32768. While result is greater than 1 and input does not contain the current mask bit, shift result and mask right once. Return result. For a halfword input with highest set bit k, return (1 << (k+1)) - 1; zero and one both return 1. Higher input bits are ignored because the tested mask begins at bit 15.\n\nThe code span is [6220,6238), 24 bytes, followed by the 65535 literal at 6238. All 65536 halfword inputs execute the original instructions and agree with an independent bit-length model. The compact result vector is retained with its hash. This helper has no calls, stores or stack operations. Physical meaning remains unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(results),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(results))
