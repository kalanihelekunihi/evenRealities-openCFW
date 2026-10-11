from pathlib import Path
import hashlib,json,struct
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();raw=blob[32:];elf=Path('/tmp/audio-aux-command/aux.elf');segs=[]
with elf.open('rb') as f:
 e=ELFFile(f);entry=e.get_section_by_name('.symtab').get_symbol_by_name('audio_aux_command')[0]['st_value']
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segs.append((s['p_vaddr'],s.data()))
rows=[]
for queue in [0,0x20006000]:
 out=[]
 for target in [0x47e7b0,entry]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000)
  for a,b in segs:u.mem_write(a,b)
  u.mem_write(0x20074ab0,struct.pack('<I',queue));u.mem_write(0x20006000,b'\xa5'*64)
  u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,5);u.reg_write(UC_ARM_REG_R2,0x12345678);u.reg_write(UC_ARM_REG_R3,0);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.mem_write(0x2007e000,struct.pack('<I',2))
  calls=[];writes=[]
  def hook(u,a,n,d):
   if a==0x5fa0a4:calls.append(hex(a))
  def invalid_write(u,access,a,n,value,d):
   writes.append((hex(a),n,value));u.emu_stop();return True
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,invalid_write)
  try:u.emu_start(target|1,0,count=1000)
  except UcError:
   if not writes:raise
  out.append((calls,writes,u.reg_read(UC_ARM_REG_BASEPRI),bytes(u.mem_read(0x20006000,64)),bytes(u.mem_read(0x20074ab0,4))))
 assert out[0]==out[1],(queue,out);assert out[0][0]==['0x5fa0a4'] and out[0][1]==[('0xffffffff',4,0)]
 rows.append({'queue':hex(queue),'mask_helper':out[0][0][0],'invalid_write':out[0][1][0],'basepri_after':out[0][2],'queue_unchanged':True})
p={'status':'PASS','cases':2,'entry':'0x47e7b0','source_elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'rows':rows,'limit':'Executes original BASEPRI mask helper 0x5fa0a4 and stops on attempted unmapped write to 0xffffffff. Exception delivery and subsequent loop are not executed.'}
(D/'timer-aux-null-prefix.json').write_text(json.dumps(p,indent=2)+'\n');print('PASS',len(rows))
