from pathlib import Path
import json,struct,subprocess,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];P=R/'g2/analysis/audio-uart-power-config-2026-10-09';rec=json.loads((P/'reproduction-receipt.json').read_text());elf=Path(rec['elf']);raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(elf.read_bytes()).hexdigest()==rec['elf_sha256'];syms={l.split()[2]:int(l.split()[0],16) for l in subprocess.check_output([str(Path(rec['gcc']).with_name('arm-none-eabi-nm')),str(elf)],text=True).splitlines() if len(l.split())==3}
with elf.open('rb') as f:
 e=ELFFile(f);sections=[(s['sh_addr'],s.data()) for s in e.iter_sections() if s['sh_flags']&2 and s['sh_size']]
def run(native,null=False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw);u.mem_map(0x100000,0x10000)
 for a,b in sections:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000);u.mem_map(0x40039000,0x1000);u.mem_write(0x20040000,struct.pack('<I',0x1ea9e06));u.reg_write(UC_ARM_REG_R0,0 if null else 0x20040000);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x10ff01);trace=[];stop=[]
 def mem(uc,access,a,size,value,user):
  if 0x40039000<=a<0x4003a000:trace.append(['R' if access==UC_MEM_READ else 'W',hex(a),size,int.from_bytes(uc.mem_read(a,size),'little') if access==UC_MEM_READ else value])
 def hook(uc,pc,size,user):
  if pc==0x10ff00:stop.append('return');uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_PC,(syms['am_hal_uart_interrupt_clear'] if native else 0x58e7e4)|1)
 try:
  for _ in range(100):
   if stop:break
   u.emu_start(u.reg_read(UC_ARM_REG_PC)|1,0,count=1)
 except UcError as e:stop.append(str(e))
 return {'stop':stop,'return':u.reg_read(UC_ARM_REG_R0) if stop==['return'] else None,'mmio_trace':trace}
a=run(False);b=run(True);assert a['mmio_trace']==[['W','0x40039044',4,0x12345678],['R','0x40039040',4,0]];assert b['mmio_trace']==a['mmio_trace'];c=run(False,True);d=run(True,True);assert c==d and 'UNMAPPED' in c['stop'][0]
(D/'interrupt-clear-difference.json').write_text(json.dumps({'status':'MATCH_CONFIRMED_PRIOR_DECOMPILER_INFERENCE_CORRECTED','original_valid':a,'source_valid':b,'original_null':c,'source_null':d,'elf_sha256':rec['elf_sha256'],'limits':'Offline fixture establishes access sequence and unmapped NULL read, not physical MIS read effect.'},indent=2)+'\n');print('CONFIRMED matching MIS read and NULL prevalidation fault in BOTH stock/source')
