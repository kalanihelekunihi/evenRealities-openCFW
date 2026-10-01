from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-row-calibration-independent-review-1500/001');o.mkdir(parents=True,exist_ok=True);src=o/'touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for flag,index,value,status in itertools.product([0,1,7,8,255],[0,1,2],[0,65535,65536,0xffffffff],[0,3,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;T=0x20002100;R=0x20002400;rec=T+144*index;sp=0x2000f000
 u.mem_write(D+12,T.to_bytes(4,'little'));u.mem_write(rec,R.to_bytes(4,'little'));u.mem_write(rec+128,(1234).to_bytes(2,'little'));u.mem_write(R+35,bytes([flag]));u.mem_write(R+4,(0xa5a5).to_bytes(2,'little'));u.reg_write(UC_ARM_REG_R0,index);u.reg_write(UC_ARM_REG_R1,D);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0x7bc0:
   args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];calls.append(args+[int.from_bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4),'little')]);u.mem_write(args[0],value.to_bytes(4,'little'));u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x5cad,0,count=100)
 active=bool(flag&8);expected=min(value,65535) if active else 0xa5a5
 assert calls==([[sp-12,index,1234,0,D]] if active else []) and int.from_bytes(u.mem_read(R+4,2),'little')==expected and u.reg_read(UC_ARM_REG_R0)==(status if active else 0) and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(flag=flag,index=index,value=value,status=status,stored=expected,calls=calls))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Row calibration at 5CAC\n\nThe72-byte body[5CAC,5CF4) isfollowed by65535literal. Selectstride144record throughdescriptorword12 andreadrecordword0 rowpointer. Initialize stackresultwordzero. Ifrowbyte35bit3clear,return0withoutchangingrowhalfword4. Otherwisecall7BC0(resultPointer,index,recordhalfword128,0,descriptor asfifthstackargument). Clampreturnedresultwordto65535 andstoreitslowhalfwordatrow+4. ReturnhelperR0status unchanged,independentofresultword. Restore24-byteframe.\n\nThe180original-instructionfixtures checkbitgate,threeindices,clampboundary,independentstatus/result,exactfivearguments andframe.7BC0remainscontrolled.Pointervalidity andphysicalmeaningremainunresolved.No canonicaladmission orCimplementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
