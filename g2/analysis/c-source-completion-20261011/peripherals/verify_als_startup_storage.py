#!/usr/bin/env python3
"""Hash-bound Apollo ALS storage provenance and C object-section verifier."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_als_state.c'
BLOB=OTA.read_bytes()
assert hashlib.sha256(BLOB).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
raw=BLOB[0x20:]
word=lambda address:struct.unpack_from('<I',raw,address-0x438000)[0]
record=0x75d3f4
start=record+word(record)
end=start+(word(record+4)>>1)
assert word(record+8)==0x20000000
data=bytearray();pointer=start
while pointer<end:
 token=raw[pointer-0x438000];pointer+=1
 literals=token&3;match=token>>4
 if not literals:literals=raw[pointer-0x438000]+3;pointer+=1
 if match==15:match=raw[pointer-0x438000]+15;pointer+=1
 for _ in range(literals-1):data.append(raw[pointer-0x438000]);pointer+=1
 if match:
  distance=raw[pointer-0x438000];pointer+=1
  high=(token>>2)&3
  if high==3:high=raw[pointer-0x438000];pointer+=1
  distance+=high<<8
  assert 0<distance<=len(data)
  for _ in range(match+2):data.append(data[-distance])
assert pointer==end and len(data)==0x4558
expected_hash=json.loads((ROOT/'g2/analysis/audio-dispatch-initializer-closure-2026-10-08/results.json').read_text())['decoded_sha256']
assert hashlib.sha256(data).hexdigest()==expected_hash
initialized={
 'audio_als_scale_clamped':0x20000060,
 'audio_als_scale_active':0x20000064,
 'audio_als_scale_shadow':0x20000068,
}
for name,address in initialized.items():
 assert struct.unpack_from('<I',data,address-0x20000000)[0]==0x400,(name,address)
zero={
 'audio_als_active_previous':0x200741e0,
 'audio_als_default_previous':0x200741dc,
 'audio_als_recompute_pending':0x20074200,
 'audio_als_curve_index':0x200741e4,
 'audio_als_curve_nominal':0x200741e8,
 'audio_als_curve_adjusted':0x200741ec,
}
zero_start=word(0x75d3d0);zero_length=word(0x75d3cc)
assert (zero_start,zero_length)==(0x20004558,0x70af0)
assert all(zero_start<=address<zero_start+zero_length for address in zero.values())
# The record resolves to the stock zeroing callback at 0x5fa01e.
displacement=word(0x75d3c8)
assert (0x75d3c8+struct.unpack('<i',struct.pack('<I',displacement))[0])&0xffffffff==0x5fa01f
uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
uc.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
uc.mem_map(0x438000,(len(raw)+4095)&~4095);uc.mem_write(0x438000,raw)
uc.mem_map(0x20000000,0x80000)
uc.mem_write(zero_start-16,b'\xa5'*(zero_length+32))
uc.reg_write(A.UC_ARM_REG_R0,0x75d3cc)
uc.reg_write(A.UC_ARM_REG_SP,0x2007f000)
uc.reg_write(A.UC_ARM_REG_LR,0x110f01)
done=[False]
def hook(cpu,pc,size,user):
 if pc==0x5fa04a and cpu.reg_read(A.UC_ARM_REG_R0)==0x75d3d4:
  done[0]=True;cpu.emu_stop()
uc.hook_add(UC_HOOK_CODE,hook)
uc.emu_start(0x5fa01f,0,count=1200000)
assert done[0]
assert bytes(uc.mem_read(zero_start,zero_length))==b'\0'*zero_length
assert bytes(uc.mem_read(zero_start-16,16))==b'\xa5'*16
assert bytes(uc.mem_read(zero_start+zero_length,16))==b'\xa5'*16
obj=OUT/'als-startup-storage.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                '-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror',
                '-c',str(SOURCE),'-o',str(obj)],check=True)
with obj.open('rb') as f:
 elf=ELFFile(f)
 symbols={sym.name:sym for sym in elf.get_section_by_name('.symtab').iter_symbols()}
 for name in initialized:
  sym=symbols[name];section=elf.get_section(sym['st_shndx'])
  assert sym['st_size']==4 and section['sh_type']=='SHT_PROGBITS'
  offset=sym['st_value']
  assert int.from_bytes(section.data()[offset:offset+4],'little')==0x400
 for name in zero:
  sym=symbols[name];section=elf.get_section(sym['st_shndx'])
  assert sym['st_size']==4 and section['sh_type']=='SHT_NOBITS'
result={'status':'PASS_ALS_STARTUP_STORAGE_BOUNDED',
        'ota_sha256':hashlib.sha256(BLOB).hexdigest(),
        'decoded_sha256':expected_hash,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
        'zero_range':[hex(zero_start),hex(zero_start+zero_length)],
        'initialized':{name:{'address':hex(address),'value':0x400} for name,address in initialized.items()},
        'zero':{name:hex(address) for name,address in zero.items()},
        'limits':'Original zero callback observed for first range only; final candidate linker placement, later runtime writes, boot and hardware remain unproven.'}
(OUT/'als-startup-storage-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],len(initialized)+len(zero))
