#!/usr/bin/env python3
"""Controlled native/C comparison for the stock local-data response serializer."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_respond_local_serialize_49ba58.c"
RAM=G2/"components/audio/uart_thread_source_candidate/settings_response_command_id_ram.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x49ba58-0x438000:0x49bbb0-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-setting-local-response-49ba58"
CALLS={"audio_uart_device_role_get":0x45a568,"audio_log_flags":0x43d0ce,
       "audio_log_extended":0x43d574,"compressed_log_output":0x43ce9e,
       "audio_uart_buffer_zero":0x43c0e4,"audio_setting_local_response_encode_49b7c4":0x49b7c4,
       "audio_ring_pb_tx_ble_475b14":0x475b14}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  shim=Path(temp)/"shim.c"
  shim.write_text("#include <stdint.h>\nuint8_t audio_settings_notify_encode_buffer[256];\n"+
   "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}' for s in CALLS))
  elf=Path(temp)/"candidate.elf"
  subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11",
                  "-ffreestanding","-fno-builtin","-O2","-w","-nostdlib","-Wl,-Ttext=0x100000",
                  "-Wl,-e,audio_setting_serialize_local_response_49ba58",str(SOURCE),str(RAM),str(shim),
                  "-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def run(compiled,role,cmd_id,flags,encode_ok,size):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,data in segments:uc.mem_write(address,data)
   uc.mem_map(0x20000000,0x100000)
   buffer=symbols["audio_settings_notify_encode_buffer"] if compiled else 0x200706ec
   cmd=symbols["audio_settings_response_command_id_20074860"] if compiled else 0x20074860
   uc.mem_write(buffer,b"\xa5"*256);uc.mem_write(cmd,cmd_id.to_bytes(4,"little"))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
   trace=[]
   def cstr(address):
    data=bytes(uc.mem_read(address,160));return data.split(b"\0",1)[0].decode("ascii")
   def observe(cpu,address,insn_size,_):
    name=hooks.get(address)
    if name is None:return
    r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
    value=0
    if name=="audio_uart_device_role_get":trace.append(("role",));value=role
    elif name=="audio_log_flags":trace.append(("flags",));value=flags
    elif name=="audio_log_extended":
     sp=cpu.reg_read(A.UC_ARM_REG_SP)
     line=int.from_bytes(cpu.mem_read(sp,4),"little")
     msg=int.from_bytes(cpu.mem_read(sp+4,4),"little")
     trace.append(("extended",r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),line,cstr(msg)))
    elif name=="compressed_log_output":
     trace.append(("compressed",r[0],cstr(r[1]),cstr(r[2])))
    elif name=="audio_uart_buffer_zero":
     trace.append(("zero",r[0]==buffer,r[1],r[2]))
     cpu.mem_write(buffer,b"\0"*256)
    elif name=="audio_setting_local_response_encode_49b7c4":
     trace.append(("encode",r[0]==buffer,int.from_bytes(cpu.mem_read(r[1],4),"little")))
     cpu.mem_write(r[1],size.to_bytes(4,"little"));cpu.mem_write(buffer,b"\x3c"*256)
     value=encode_ok
    elif name=="audio_ring_pb_tx_ble_475b14":
     trace.append(("send",r[0],r[1],r[2]==buffer,r[3]))
    cpu.reg_write(A.UC_ARM_REG_R0,value)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols["audio_setting_serialize_local_response_49ba58"] if compiled else 0x49ba58
   uc.emu_start(start|1,0x600000,count=1300)
   return uc.reg_read(A.UC_ARM_REG_R0),trace,bytes(uc.mem_read(buffer,256))
  cases=0
  for role in (0,1,2):
   for cmd in (0,1,0x12345678):
    for flags in (0,1,2,4,7):
     for ok in (0,1):
      for size in (0,0x12345):
       n=run(False,role,cmd,flags,ok,size)
       c=run(True,role,cmd,flags,ok,size)
       if n!=c:raise AssertionError((role,cmd,flags,ok,size,n,c))
       cases+=1
  receipt={"status":"PASS_NATIVE_MAIN_SETTING_LOCAL_RESPONSE_49BA58",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "ram_source":str(RAM.relative_to(ROOT)),"ram_source_sha256":sha(RAM),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "source_owned_symbols":["audio_setting_serialize_local_response_49ba58",
                                   "audio_settings_response_command_id_20074860"],
           "cases":cases,"limits":["Role, logger, encoder and BLE transport are controlled hooks; command RAM initializer, final layout and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
