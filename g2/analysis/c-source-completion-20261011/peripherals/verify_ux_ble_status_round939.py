#!/usr/bin/env python3
"""Native/C system BLE status and one-cell aliases at 0x20075043."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ux-ble-status-round939';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/ux_ble_status.c'
obj=out/'ux_ble_status.o'
base=root/'build/c-firmware/terminal-host-status-round938/apollo-main-terminal-host-status.o'
linked=out/'apollo-main-ux-ble-status.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=blob[0x47d8ce-0x438000:0x47d8e4-0x438000]
assert hashlib.sha256(native).hexdigest()=='14b7a1e5024c096f484a51166af9d83986c318c36a775d51437bacc3dbf206fa'
assert int.from_bytes(blob[0x47d900-0x438000:0x47d904-0x438000],'little')==0x20075043
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ux_get_system_ble_status',str(src),'-o',str(elf)],check=True)
 syms={p[2]:int(p[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3}
 assert syms['audio_ota_packed_status']==syms['g2_audio_log_transport_bits']
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[]
 for value in range(256):
  outputs=[]
  for compiled in (False,True):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,blob)
   uc.mem_map(0x100000,0x100000)
   for addr,data in segs:uc.mem_write(addr,data)
   uc.mem_map(0x20000000,0x100000)
   uc.mem_write(syms['audio_ota_packed_status'] if compiled else 0x20075043,bytes([value]))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.emu_start(((syms['audio_ux_get_system_ble_status'] if compiled else 0x47d8ce)|1),0x600000,count=100)
   outputs.append(uc.reg_read(A.UC_ARM_REG_R0))
  assert outputs[0]==outputs[1],(value,outputs)
  cases.append(value)
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_ux_get_system_ble_status','audio_ota_packed_status','g2_audio_log_transport_bits'}
assert after-before==set()
receipt={'round':939,'status':'PASS_NATIVE_UX_BLE_STATUS','component':'Apollo UX_GetSystemBLEStatus 0x47d8ce and shared status byte 0x20075043','source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_image_sha256':hashlib.sha256(blob).hexdigest(),'native_body_sha256':hashlib.sha256(native).hexdigest(),'cases':len(cases),'symbol_aliases':['audio_ota_packed_status','g2_audio_log_transport_bits'],'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),'unresolved_before':len(before),'unresolved_after':len(after),'whole_image_complete':False,'hardware_proof':False,'gates':['Runtime producer and final RAM linker placement for status byte remain open','Runtime-event helper 0x5e873e and 5 terminal callback bodies remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],len(cases),len(before),len(after))
