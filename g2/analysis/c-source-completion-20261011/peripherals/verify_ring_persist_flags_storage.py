#!/usr/bin/env python3
"""Verify six byte BSS cells against the original Apollo zero initializer."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SOURCE=ROOT/'g2/components/audio/uart_thread_source_candidate/display_ring_persist_flags.c'
blob=OTA.read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
raw=blob[0x20:];word=lambda a:struct.unpack_from('<I',raw,a-0x438000)[0]
start,length=word(0x75d3d0),word(0x75d3cc)
assert (start,length)==(0x20004558,0x70af0)
displacement=struct.unpack('<i',struct.pack('<I',word(0x75d3c8)))[0]
assert 0x75d3c8+displacement==0x5fa01f
cells={'audio_uart_pool_initialized':0x20075031,
       'audio_uart_ring_persist_initialized':0x20075032,
       'audio_uart_ring_persist_has_tail':0x20075033,
       'audio_uart_ring_persist_early_pending':0x20075034,
       'audio_uart_ring_persist_wake_blocked':0x20075036,
       'audio_uart_ring_persist_wake_pending':0x20075037}
assert len(set(cells.values()))==len(cells)
assert all(start<=a<start+length for a in cells.values())
uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
uc.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
uc.mem_map(0x438000,(len(raw)+4095)&~4095);uc.mem_write(0x438000,raw)
uc.mem_map(0x20000000,0x80000)
uc.mem_write(start-16,b'\xa5'*(length+32))
uc.reg_write(A.UC_ARM_REG_R0,0x75d3cc)
uc.reg_write(A.UC_ARM_REG_SP,0x2007f000)
done=[False]
def hook(cpu,pc,sz,user):
 if pc==0x5fa04a and cpu.reg_read(A.UC_ARM_REG_R0)==0x75d3d4:
  done[0]=True;cpu.emu_stop()
uc.hook_add(UC_HOOK_CODE,hook);uc.emu_start(0x5fa01f,0,count=1200000)
assert done[0]
assert bytes(uc.mem_read(start,length))==b'\0'*length
assert bytes(uc.mem_read(start-16,16))==b'\xa5'*16
assert bytes(uc.mem_read(start+length,16))==b'\xa5'*16
obj=OUT/'ring-persist-flags-storage.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                '-std=c11','-ffreestanding','-O2','-Wall','-Wextra','-Werror',
                '-c',str(SOURCE),'-o',str(obj)],check=True)
with obj.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name in cells:
  s=syms[name];section=elf.get_section(s['st_shndx'])
  assert s['st_size']==1 and section['sh_type']=='SHT_NOBITS'
result={'status':'PASS_RING_PERSIST_FLAGS_STORAGE_BOUNDED',
        'ota_sha256':hashlib.sha256(blob).hexdigest(),
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
        'zero_range':[hex(start),hex(start+length)],
        'cells':{name:hex(addr) for name,addr in cells.items()},
        'limits':'Startup zero ownership only; final absolute placement, later initialization and runtime/hardware remain open.'}
(OUT/'ring-persist-flags-storage-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'],len(cells))
