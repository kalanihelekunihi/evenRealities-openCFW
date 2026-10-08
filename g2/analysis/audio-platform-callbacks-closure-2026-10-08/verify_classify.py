from pathlib import Path
exec(Path(__file__).with_name('verify.py').read_text().split('# Independent expected registration model')[0].replace('UC_CPU_ARM_CORTEX_M4','UC_CPU_ARM_CORTEX_M33'))
import math
rows=[];bits={0,0x80000000,0x7f800000,0xff800000,0x7fc00000,0xffc00001}
for value in [-300,-273,-22,-20,-2,-1,0,48,50,999,1000,1001]:
 b=struct.unpack('<I',struct.pack('<f',value))[0]
 bits.update(x&0xffffffff for x in [b-1,b,b+1])
for b in sorted(bits):
 f=struct.unpack('<f',struct.pack('<I',b))[0];want=0 if -273<=f<-20 else 1 if -20<=f<0 else 2 if 0<=f<50 else 3 if 50<=f<1000 else 4;vals=[]
 for entry in [0x5a1e8c,sym['audio_platform_classify']]:
  u=machine();u.mem_map(0xe000e000,0x2000);w(u,0xe000ed88,0xf00000);u.reg_write(UC_ARM_REG_S0,b);u.emu_start(entry|1,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;v=u.reg_read(UC_ARM_REG_R0);assert v==want,(hex(b),f,v,want);vals.append(v)
 assert vals[0]==vals[1];rows.append(dict(float_bits=hex(b),value=str(f),classification=want))
(D/'classify-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['M33-compatible FPU subset; numeric units not independently identified.','NaN, infinities, signed zero and next-representable values around thresholds; no hardware sensor trace.']),indent=2)+'\n');print('PASS',len(rows),'classifier comparisons')
