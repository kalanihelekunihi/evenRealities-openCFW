from pathlib import Path
import json,struct,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-storage-transfer-wrappers-independent-review-1311/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();word=lambda a:struct.unpack_from('<I',d,a-0x3300)[0];flag=word(0x355c);ctx=word(0x3560);accepted=word(0x3564);rows=[]
for entry,offset,length,pointer,ready,status in itertools.product([0x3520,0x3568,0x35b0],[0,255,256,0xffffffff],[0,1,8,0xffffffff],[0,0x20002000],[0,1],[0,accepted,1]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(flag,bytes([ready]));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[offset,pointer,length]):u.reg_write(r,v)
 calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0x8a78,0x8aac,0x8ae0]:calls.append(dict(pc=p,args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]));u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(entry|1,0,count=100)
 invalid=entry!=0x35b0 and (pointer==0 or ((offset+length)&0xffffffff)>256)
 reached=not invalid and bool(ready);ret=4 if invalid else (1 if not ready else (0 if status in [0,accepted] else (2 if entry==0x3520 else 3)))
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==ret and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and len(calls)==int(reached)
 if reached:
  if entry==0x35b0:assert calls[0]['args'][0]==ctx
  else:assert calls[0]['args']==[offset,pointer,length,ctx]
 rows.append(dict(entry=entry,offset=offset,length=length,pointer=pointer,ready=ready,controlled_status=status,return_value=ret,calls=calls))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch storage transfer and erase wrappers

3520..355C and 3568..35A4 are each 60 instruction bytes with separate following literal pools. Both reject null buffer or unsigned modular u32(offset+length) greater than 256 with status four. The modular test permits overflowing sums; no stronger range check is inferred. Then read readiness byte; zero returns one. Otherwise pass incoming offset, buffer and length plus literal context in R3 to 8A78 (read) or 8AAC (write). Deeper status zero or accepted-status literal converts to zero; other statuses convert to two for read and three for write.

35B0..35D6 is a 38-byte erase wrapper excluding adjacent NOP/pool. Check the same readiness byte, return one if zero; otherwise call 8AE0(context). Convert deeper zero or accepted status to zero, others to three. All wrappers restore their two-word frames.

Receipt-derived original-instruction fixtures cover modular overflow, null/nonnull buffer, readiness and three deeper statuses. Deep helper boundaries are controlled without memory effects. Exact reached calls and arguments, return and SP are checked. Pointer validity, real storage and stronger logical bounds remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=dict(flag=flag,context=ctx,accepted_status=accepted),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
