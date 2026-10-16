#!/usr/bin/env python3
"""Controlled native/C comparison for the settings nanopb parser."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_parse_data_package_49b1f8.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x49b1f8-0x438000:0x49b3d4-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-setting-parse-49b1f8"
CALLS={"audio_uart_pb_stream_init":0x48f49c,"audio_uart_checksum_copy":0x439c04,
       "audio_uart_pb_decode":0x490120,"audio_setting_is_duplicate_message_49b198":0x49b198,
       "audio_log_flags":0x43d0ce,"audio_log_extended":0x43d574,
       "compressed_log_output":0x43ce9e}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  shim=Path(temp)/"shim.c"
  shim.write_text("#include <stdint.h>\nuint32_t audio_settings_response_command_id_20074860;\n"
   "uint32_t audio_settings_response_magic_20074864;\n"
   "const uint8_t audio_settings_status_pb_descriptor[32]={0};\n"+
   "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}' for s in CALLS))
  elf=Path(temp)/"candidate.elf"
  subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                  "-std=c11","-ffreestanding","-fno-builtin","-O2","-w","-nostdlib",
                  "-Wl,-Ttext=0x100000","-Wl,-e,audio_setting_parse_data_package_49b1f8",
                  str(SOURCE),str(shim),"-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def u32(v):return (v&0xffffffff).to_bytes(4,"little")
  def run(compiled,data_ok,msg_ok,flags,decode_ok,error_ok,duplicate,command,magic,which):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   data=0x20040000 if data_ok else 0
   msg=0x20050000 if msg_ok else 0
   command_cell=symbols["audio_settings_response_command_id_20074860"] if compiled else 0x20074860
   magic_cell=symbols["audio_settings_response_magic_20074864"] if compiled else 0x20074864
   desc=symbols["audio_settings_status_pb_descriptor"] if compiled else 0x77772c
   uc.mem_write(0x20040000,b"\x6a"*256)
   uc.mem_write(0x20050000,b"\xa5"*104)
   uc.mem_write(0x20060000,b"hook decode error\0")
   uc.mem_write(command_cell,u32(0xdeadbeef));uc.mem_write(magic_cell,u32(0xcafebabe))
   for reg,value in ((A.UC_ARM_REG_R0,data),(A.UC_ARM_REG_R1,59),
                     (A.UC_ARM_REG_R2,msg),(A.UC_ARM_REG_SP,0x200ff000),
                     (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,value)
   hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
   trace=[]
   def cstr(address):
    return bytes(uc.mem_read(address,160)).split(b"\0",1)[0].decode("ascii")
   def observe(cpu,address,insn_size,_):
    name=hooks.get(address)
    if name is None:return
    r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
    result=0
    if name=="audio_uart_pb_stream_init":
     trace.append(("stream",r[1]==data,r[2]));cpu.mem_write(r[0],u32(0)+u32(data)+u32(r[2])+u32(0))
    elif name=="audio_uart_checksum_copy":
     trace.append(("copy",r[2]));cpu.mem_write(r[0],bytes(cpu.mem_read(r[1],r[2])))
    elif name=="audio_uart_pb_decode":
     trace.append(("decode",r[1]==desc,r[2]==msg))
     if decode_ok:
      body=bytes([command])+u32(magic)+b"\0\0"+which.to_bytes(2,"little")+b"\x33"*94
      cpu.mem_write(r[2],body)
     cpu.mem_write(r[0]+12,u32(0x20060000 if error_ok else 0));result=decode_ok
    elif name=="audio_setting_is_duplicate_message_49b198":
     trace.append(("duplicate",r[0]));result=duplicate
    elif name=="audio_log_flags":trace.append(("flags",));result=flags
    elif name=="audio_log_extended":
     sp=cpu.reg_read(A.UC_ARM_REG_SP)
     line=int.from_bytes(cpu.mem_read(sp,4),"little")
     message=cstr(int.from_bytes(cpu.mem_read(sp+4,4),"little"))
     item=("extended",r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),line,message)
     if "%" in message:
      count=2 if message.count("%d")==2 else 1
      args=tuple(int.from_bytes(cpu.mem_read(sp+8+4*i,4),"little") for i in range(count))
      item+=(cstr(args[0]),) if "%s" in message else args
     trace.append(item)
    elif name=="compressed_log_output":
     item=("compressed",r[0],cstr(r[1]),cstr(r[2]))
     if "%" in item[-1]:
      count=2 if item[-1].count("%d")==2 else 1
      item+=(cstr(r[3]) if "%s" in item[-1] else r[3],)
      if count==2:item+=(int.from_bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4),"little"),)
     trace.append(item)
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols["audio_setting_parse_data_package_49b1f8"] if compiled else 0x49b1f8
   uc.emu_start(start|1,0x600000,count=2200)
   return (uc.reg_read(A.UC_ARM_REG_R0),trace,
           int.from_bytes(uc.mem_read(command_cell,4),"little"),
           int.from_bytes(uc.mem_read(magic_cell,4),"little"),
           bytes(uc.mem_read(0x20050000,16)))
  cases=0
  for data_ok in (False,True):
   for msg_ok in (False,True):
    for flags in (0,1,2,4,7):
     for decode_ok in (0,1):
      for error_ok in (0,1):
       for duplicate in (0,1):
        for command,magic,which in ((0,0,0),(5,0x12345678,9)):
         values=(data_ok,msg_ok,flags,decode_ok,error_ok,duplicate,command,magic,which)
         n=run(False,*values);c=run(True,*values)
         if n!=c:raise AssertionError((values,n,c))
         cases+=1
  receipt={"status":"PASS_NATIVE_MAIN_SETTING_PARSE_49B1F8",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "source_owned_symbols":["audio_setting_parse_data_package_49b1f8"],
           "cases":cases,"limits":["Nanopb stream/decode, duplicate and logger calls are controlled hooks; final placement and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
