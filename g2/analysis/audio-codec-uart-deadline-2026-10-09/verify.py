from pathlib import Path
import json,struct,subprocess,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3}
with elf.open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_size']]
Q=0x20073ed4;BUF=0x200731b0;DST=0x20040000

def run(f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_write(Q,struct.pack('<4I',BUF,63,0,1 if f['arrival']==0 else 0));u.mem_write(BUF,b'\xA3');u.mem_write(DST,b'\xee');u.reg_write(UC_ARM_REG_R0,DST);u.reg_write(UC_ARM_REG_R1,f['timeout']);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);tick=[f['start']];reads=[];delays=[];stop=[]
 def hook(uc,pc,size,user):
  if pc==0x4490cc:
   reads.append(tick[0]);uc.reg_write(UC_ARM_REG_R0,tick[0]);uc.reg_write(UC_ARM_REG_R1,0xbadbad);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc==0x449376:
   delays.append(uc.reg_read(UC_ARM_REG_R0));assert delays[-1]==1
   if len(delays)>=8:stop.append('before-delay-budget-cut');uc.emu_stop();return
   tick[0]=(tick[0]+1)&0xffffffff
   if len(delays)==f['arrival']:uc.mem_write(Q+12,struct.pack('<I',1))
   uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  if native:assert 0x100000<=pc<0x104000 or 0x58fac8<=pc<0x58fad2,hex(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PC,(syms['codec_read_byte_deadline'] if native else 0x58fad2)|1)
 for _ in range(10000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stop
 return {'stop':stop,'return':u.reg_read(UC_ARM_REG_R0) if stop==['return'] else None,'tick_reads':reads,'delay_arguments':delays,'ring':bytes(u.mem_read(Q,16)).hex(),'destination':bytes(u.mem_read(DST,1)).hex()}
rows=[]
for start,timeout,arrival in itertools.product([0,100,0xfffffffe,0xffffffff],[0,1,2,5,0x7fffffff,0x80000000,0xffffffff],[-1,0,1,3]):
 f=dict(start=start,timeout=timeout,arrival=arrival);a=run(f,False);b=run(f,True);assert a==b,(f,a,b);rows.append({'fixture':f,'observed':a})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'comparisons':rows,'limits':'Actual original/source deadline arithmetic and drain. Tick/delay/arrival are explicit synthetic providers; eight-delay cut is not hardware hang evidence.'},indent=2)+'\n');print('PASS',len(rows))
