#!/usr/bin/env python3
"""Compare stock hard-float classify entry to retained C over boundary bits."""
from pathlib import Path
import hashlib,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'g2/components/audio/platform_callbacks_offline/classify.c'
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=OTA.read_bytes()[0x20:]
obj=OUT/'classify-hard-m4.o';elf=OUT/'classify-hard-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-mthumb','-O2','-c',str(SOURCE),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','audio_platform_classify','-o',str(elf),str(obj)],check=True)
from elftools.elf.elffile import ELFFile
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
values=[-1000.,-274.,-273.,-272.999,-21.,-20.,-19.999,-1.,-0.0,0.0,0.0001,49.999,50.,50.001,999.999,1000.,1001.,float('inf'),-float('inf')]
bits=[struct.unpack('<I',struct.pack('<f',v))[0] for v in values]+[0x7fc00000,0x7f800001,0xffc00000,0x00000001,0x80000001]
rows=[]
for word in bits:
 outputs=[]
 for stock in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x438000,(len(blob)+4095)&~4095);u.mem_map(0x100000,0x10000);u.mem_map(0x20000000,0x1000)
  if stock:u.mem_write(0x438000,blob)
  else:
   for base,data in segments:u.mem_write(base,data)
  u.reg_write(A.UC_ARM_REG_S0,word);u.reg_write(A.UC_ARM_REG_SP,0x20000800);u.reg_write(A.UC_ARM_REG_LR,0x100f01)
  done=[False]
  def hook(cpu,pc,size,user):
   if pc==0x100f00:done[0]=True;cpu.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start(0x5a1e8d if stock else 0x100001,0,count=300)
  assert done[0]
  outputs.append(u.reg_read(A.UC_ARM_REG_R0))
 if outputs[0]!=outputs[1]:raise AssertionError((hex(word),outputs))
 rows.append({'bits':hex(word),'result':outputs[0]})
receipt={'status':'PASS_BOUNDED_CLASSIFY','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'limits':'Hard-float original/S0 source body only. Selected caller is soft-float R0 and still needs an ABI adapter and composed callback path.'}
(OUT/'classify-oracle-results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(rows))
