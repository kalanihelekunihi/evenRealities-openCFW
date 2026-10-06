from pathlib import Path
import hashlib,json,random,struct,itertools,math
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');src=b/'attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();assert h(d)=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,(len(d)+4095)&~4095);u.mem_write(0x438000,d);base=0x21000000;u.mem_map(base,4096);sp=base+4000;ptr=base+128;rng=random.Random(16362);regs=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,UC_ARM_REG_R12];perms=list(itertools.permutations(range(3)))
bits=lambda f:struct.unpack('<I',struct.pack('<f',f))[0]
cohorts={'copy':0,'identity':0,'translation':0,'inverse_success':0,'inverse_reject':0}
for mode in range(4):
 for i in range(1024):
  ram=bytearray(rng.randbytes(4096));expected=bytearray(ram);vals=[rng.getrandbits(32) for _ in regs];vals[0]=ptr;fps=[rng.getrandbits(32) for _ in range(16)];r0expected=ptr;dirty=(128,164);schecks={};expectedmatrix=None
  if mode==0:
   entry=0x540024;delta=[-12,-8,-4,0,4,8,12,32][i%8];source=128;dest=source+delta;vals[0]=base+dest;vals[1]=base+source;r0expected=vals[0];dirty=(dest,dest+16)
   for off in range(0,16,4):
    v=struct.unpack_from('<I',expected,source+off)[0];struct.pack_into('<I',expected,dest+off,v)
    if off==8:vals[2]=v
    if off==12:vals[1]=v
   cohorts['copy']+=1
  elif mode==1:
   entry=0x561810
   for k in range(9):struct.pack_into('<I',expected,128+k*4,0x3f800000 if k in [0,4,8] else 0)
   vals[1]=0;schecks={0:0x3f800000};cohorts['identity']+=1
  elif mode==2:
   entry=0x561856;matrix=[float(rng.randrange(-64,65)) for _ in range(9)];x=float(rng.randrange(-16,17));y=float(rng.randrange(-16,17));struct.pack_into('<9f',ram,128,*matrix);expected=bytearray(ram);fps[0]=bits(x);fps[1]=bits(y)
   wanted=matrix[:]
   for col in range(3):wanted[col]=matrix[col]+x*matrix[6+col];wanted[3+col]=matrix[3+col]+y*matrix[6+col]
   struct.pack_into('<9f',expected,128,*wanted);schecks={0:bits(matrix[8]),1:bits(y),2:bits(wanted[5]),3:bits(matrix[8]),4:bits(matrix[7])};cohorts['translation']+=1
  else:
   entry=0x561b38;p=perms[i%6];exps=[rng.randrange(-8,9) for _ in range(3)];scale=[(-1 if rng.randrange(2) else 1)*2.0**e for e in exps];matrix=[0.0]*9
   for row,col in enumerate(p):matrix[3*row+col]=scale[row]
   if i%8==0:matrix[3*p.index(0)]=0.0;scale[p.index(0)]=0.0
   struct.pack_into('<9f',ram,128,*matrix);expected=bytearray(ram);detabs=abs(math.prod(scale));reject=detabs<struct.unpack('<f',bytes.fromhex('adc52737'))[0]
   if reject:r0expected=0xffffffff;cohorts['inverse_reject']+=1
   else:
    r0expected=0;expectedmatrix=[0.0]*9
    for row,col in enumerate(p):expectedmatrix[3*col+row]=1.0/scale[row]
    cohorts['inverse_success']+=1
  u.mem_write(base,bytes(ram));initialvals=[rng.getrandbits(32) for _ in regs]
  # Inputs distinct from expected post-state for copy and identity clobbers.
  initialvals[:]=vals
  if mode==0:initialvals[1]=base+128;initialvals[2]=rng.getrandbits(32)
  if mode==1:initialvals[1]=rng.getrandbits(32)
  for reg,v in zip(regs,initialvals):u.reg_write(reg,v)
  for k,v in enumerate(fps):u.reg_write(UC_ARM_REG_S0+k,v)
  for reg,v in [(UC_ARM_REG_SP,sp),(UC_ARM_REG_LR,0x438101),(UC_ARM_REG_XPSR,0xA1000000),(UC_ARM_REG_PRIMASK,i%2),(UC_ARM_REG_FPSCR,0),(UC_ARM_REG_FPEXC,1<<30)]:u.reg_write(reg,v)
  u.emu_start(entry|1,0x438100,count=200)
  actual=bytes(u.mem_read(base,4096))
  if expectedmatrix is not None:
   got=struct.unpack_from('<9f',actual,128);assert all(x==y for x,y in zip(got,expectedmatrix)),(mode,i,got,expectedmatrix)
   assert actual[:128]==expected[:128] and actual[164:]==expected[164:]
  else:assert actual==expected,(mode,i,'RAM')
  assert u.reg_read(UC_ARM_REG_R0)==r0expected and all(u.reg_read(reg)==v for reg,v in zip(regs[1:],vals[1:])),(mode,i,'integer registers')
  assert all(u.reg_read(UC_ARM_REG_S0+k)==v for k,v in schecks.items()),(mode,i,'S registers')
  assert u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PC)==0x438100 and u.reg_read(UC_ARM_REG_LR)==0x438101 and u.reg_read(UC_ARM_REG_PRIMASK)==i%2
assert bytes(u.mem_read(0x438000,len(d)))==d
o=Path('/tmp/review2-rectangle-matrix-fixture-16362');o.mkdir(parents=True,exist_ok=False);(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'results.json').write_text(json.dumps(dict(status='partial',accepted=False,cases=4096,cohorts=cohorts,input_sha256=h(d),executed_spans=[[0x540024,0x540036],[0x561810,0x561830],[0x561856,0x5618b8],[0x561b38,0x561c64]],checks=['No hooks, complete original leaf execution','Forward/backward/self/disjoint ordered wordcopy overlap exactfullRAM and registerclobbers','Identity exactfullRAM and S0,R1','Finite integertranslation exactbinary32 outputs and S0..S4','Signed power-of-two permutationmatrix inverse independently calculated transpose reciprocal; nearthreshold and singular rejection; rejection exactfullRAM, success matrixnumeric and exactoutsideRAM','SP LR PC PRIMASK integerregisters immutableflash'],limitations=['FPSCR0 FP enabled only; no alternate rounding/traps/NaN/subnormal/infinity qualification','Inverse success compares +/-zero numerically; zero-sign bits not checked','No FPstatus/APSR verification','Ordinary alignedRAM only, no physicalfaults/concurrency','No admission C freeze gates']),indent=2)+'\n');print('PASS4096',cohorts)
