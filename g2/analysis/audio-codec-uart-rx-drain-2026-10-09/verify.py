from pathlib import Path
import json,subprocess,struct,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];rec=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3}
with elf.open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_size']]
bind={'codec_ring_empty':0x598134,'codec_ring_get':0x5981e0,'codec_ring_read':0x59820a,'codec_uart_read':0x58fb2a};Q=0x20073ed4;BUF=0x200731b0;DST=0x20040000

def run(name,f,native):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_write(Q,struct.pack('<4I',BUF,63,f['read'],(f['read']+f['occupied'])&63));u.mem_write(BUF,bytes(range(64)));u.mem_write(DST,b'\xee'*208);args=[DST,f['capacity']] if name=='codec_uart_read' else [Q,DST,f['capacity']]
 for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(reg,val)
 u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);stop=[]
 def hook(uc,pc,size,user):
  if pc==0x10ff00:stop.append('return');uc.emu_stop();return
  if native:assert 0x100000<=pc<0x104000,hex(pc)
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PC,(syms[name] if native else bind[name])|1)
 for _ in range(10000):
  if stop:break
  u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 assert stop
 before=bytes(u.mem_read(DST,208));u.mem_write(BUF,b'Z'*64);assert before==bytes(u.mem_read(DST,208))
 return {'return':u.reg_read(UC_ARM_REG_R0),'ring_state':bytes(u.mem_read(Q,16)).hex(),'destination':before.hex(),'independent_copy_after_ring_reuse':True}
rows=[]
for name,read,occupied,capacity in itertools.product(bind,[0,1,62,63],[0,1,3,63],[0,1,3,64,205]):
 f=dict(read=read,occupied=occupied,capacity=capacity);a=run(name,f,False);b=run(name,f,True);assert a==b,(name,f,a,b);rows.append({'function':name,'fixture':f,'observed':a})
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'comparisons':rows,'limits':'Synthetic UART3 ring state; unchanged stock/source copy/wrap/drain behavior, not concurrent ISR arrival or live codec bytes.'},indent=2)+'\n');print('PASS',len(rows))
