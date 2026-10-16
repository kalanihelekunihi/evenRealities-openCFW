#!/usr/bin/env python3
"""Controlled native/C comparison for the local-data response encoder."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_local_response_encode_49b7c4.c"
RAM=G2/"components/audio/uart_thread_source_candidate/settings_response_magic_ram.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x49b7c4-0x438000:0x49b900-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-setting-local-response-encode-49b7c4"
CALLS={"audio_settings_build_full_status":0x49b4da,"audio_uart_checksum_copy":0x439c04,
       "audio_log_flags":0x43d0ce,"audio_log_extended":0x43d574,
       "compressed_log_output":0x43ce9e,"audio_pb_ostream_from_buffer":0x4905f4,
       "audio_pb_encode":0x490c32}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  shim=Path(temp)/"shim.c"
  shim.write_text("#include <stdint.h>\nuint8_t audio_settings_notify_staging[104];\n"
   "const uint8_t audio_settings_status_pb_descriptor[32]={0};\n"+
   "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}' for s in CALLS))
  elf=Path(temp)/"candidate.elf"
  subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                  "-std=c11","-ffreestanding","-fno-builtin","-O2","-w","-nostdlib",
                  "-Wl,-Ttext=0x100000","-Wl,-e,audio_setting_local_response_encode_49b7c4",
                  str(SOURCE),str(RAM),str(shim),"-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def u32(v):return (v&0xffffffff).to_bytes(4,"little")
  def run(compiled,pointer,length_pointer,length,magic,flags,build_ok,encode_ok,encoded_len):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,data in segments:uc.mem_write(address,data)
   uc.mem_map(0x20000000,0x100000)
   stage=symbols["audio_settings_notify_staging"] if compiled else 0x200725a0
   magic_cell=symbols["audio_settings_response_magic_20074864"] if compiled else 0x20074864
   desc=symbols["audio_settings_status_pb_descriptor"] if compiled else 0x77772c
   output=0x20040000 if pointer else 0
   length_addr=0x20030000 if length_pointer else 0
   uc.mem_write(stage,b"\xa5"*104)
   uc.mem_write(magic_cell,u32(magic))
   uc.mem_write(0x20040000,b"\x5a"*256)
   uc.mem_write(0x20030000,u32(length))
   for reg,value in ((A.UC_ARM_REG_R0,output),(A.UC_ARM_REG_R1,length_addr),
                     (A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):
    uc.reg_write(reg,value)
   hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
   trace=[]
   def cstr(address):
    data=bytes(uc.mem_read(address,160));return data.split(b"\0",1)[0].decode("ascii")
   def observe(cpu,address,insn_size,_):
    name=hooks.get(address)
    if name is None:return
    r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
    result=0
    if name=="audio_settings_build_full_status":
     trace.append(("build",r[0]==stage))
     cpu.mem_write(r[0],bytes(range(104)))
     result=build_ok
    elif name=="audio_uart_checksum_copy":
     trace.append(("copy",r[2]));cpu.mem_write(r[0],bytes(cpu.mem_read(r[1],r[2])))
    elif name=="audio_log_flags":trace.append(("flags",));result=flags
    elif name=="audio_log_extended":
     sp=cpu.reg_read(A.UC_ARM_REG_SP)
     line=int.from_bytes(cpu.mem_read(sp,4),"little")
     msg=cstr(int.from_bytes(cpu.mem_read(sp+4,4),"little"))
     item=("extended",r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),line,msg)
     if "%d" in msg:
      item+=(int.from_bytes(cpu.mem_read(sp+8,4),"little"),
             int.from_bytes(cpu.mem_read(sp+12,4),"little"))
     trace.append(item)
    elif name=="compressed_log_output":
     item=("compressed",r[0],cstr(r[1]),cstr(r[2]))
     if "%d" in item[-1]:item+=(r[3],int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4),"little"))
     trace.append(item)
    elif name=="audio_pb_ostream_from_buffer":
     trace.append(("stream",r[1]==output,r[2]))
     cpu.mem_write(r[0],u32(0)+u32(output)+u32(r[2])+u32(0)+u32(0))
    elif name=="audio_pb_encode":
     trace.append(("encode",r[1]==desc,r[2]==stage,bytes(cpu.mem_read(stage,12))))
     cpu.mem_write(r[0]+12,u32(encoded_len));result=encode_ok
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols["audio_setting_local_response_encode_49b7c4"] if compiled else 0x49b7c4
   uc.emu_start(start|1,0x600000,count=1600)
   return (uc.reg_read(A.UC_ARM_REG_R0),trace,bytes(uc.mem_read(stage,104)),
           int.from_bytes(uc.mem_read(0x20030000,4),"little"),
           bytes(uc.mem_read(0x20040000,16)))
  cases=0
  for pointer in (False,True):
   for lp in (False,True):
    for length in (0,1,256):
     for magic in (0,0x12345678):
      for flags in (0,1,2,4,7):
       for build_ok in (0,1):
        for encode_ok in (0,1):
         for written in (0,0x12345):
          n=run(False,pointer,lp,length,magic,flags,build_ok,encode_ok,written)
          c=run(True,pointer,lp,length,magic,flags,build_ok,encode_ok,written)
          if n!=c:raise AssertionError((pointer,lp,length,magic,flags,build_ok,encode_ok,written,n,c))
          cases+=1
  receipt={"status":"PASS_NATIVE_MAIN_SETTING_LOCAL_RESPONSE_ENCODE_49B7C4",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "ram_source":str(RAM.relative_to(ROOT)),"ram_source_sha256":sha(RAM),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "source_owned_symbols":["audio_setting_local_response_encode_49b7c4"],
           "cases":cases,"limits":["Status builder, nanopb and logger calls are controlled hooks; final RAM placement and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
