#!/usr/bin/env python3
"""Controlled native/C comparison for settings input-event policy."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/settings_input_event_check_46b0ec.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x46b0ec-0x438000:0x46b238-0x438000]).hexdigest()
HELPER_SHA=hashlib.sha256(IMAGE[0x49eb96-0x438000:0x49ebb6-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-settings-input-check-46b0ec"
CALLS={"audio_uart_command_pending":0x4abe60,"audio_ota_transfer_active":0x4487ac,
       "audio_wear_input_enabled_49eb96":0x49eb96,
       "audio_wear_detect_get_enable_49ead8":0x49ead8,
       "audio_uart_case_status":0x4acad0,"audio_settings_get_config_46b44c":0x46b44c,
       "audio_log_flags":0x43d0ce,"audio_log_extended":0x43d574,
       "compressed_log_output":0x43ce9e}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  shim=Path(temp)/"shim.c"
  shim.write_text("#include <stdint.h>\nvolatile uint32_t audio_uart_lcd_status_cell;\n"+
   "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}' for s in CALLS if s!="audio_wear_input_enabled_49eb96"))
  elf=Path(temp)/"candidate.elf"
  subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                  "-std=c11","-ffreestanding","-fno-builtin","-O2","-w","-nostdlib",
                  "-Wl,-Ttext=0x100000","-Wl,-e,audio_wear_child_46b0ec",
                  str(SOURCE),str(shim),"-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def u32(v):return (v&0xffffffff).to_bytes(4,"little")
  def run(compiled,pending,ota,wear,box,silent,flags,helper_only=False,enable=0,lcd=0):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   config=0x20040000
   uc.mem_write(config,b"\xa5"*128);uc.mem_write(config+0x15,bytes([silent]))
   cell=symbols["audio_uart_lcd_status_cell"] if compiled else 0x20074edc
   uc.mem_write(cell,u32(lcd))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
   trace=[]
   def cstr(address):return bytes(uc.mem_read(address,160)).split(b"\0",1)[0].decode("ascii")
   def observe(cpu,address,insn_size,_):
    name=hooks.get(address)
    if name is None or (helper_only and name!="audio_wear_detect_get_enable_49ead8"):return
    r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
    result=0
    if name=="audio_uart_command_pending":trace.append(("pending",));result=pending
    elif name=="audio_ota_transfer_active":trace.append(("ota",));result=ota
    elif name=="audio_wear_input_enabled_49eb96":trace.append(("wear",));result=wear
    elif name=="audio_wear_detect_get_enable_49ead8":trace.append(("enable",));result=enable
    elif name=="audio_uart_case_status":trace.append(("box",));result=box
    elif name=="audio_settings_get_config_46b44c":trace.append(("config",));result=config
    elif name=="audio_log_flags":trace.append(("flags",));result=flags
    elif name=="audio_log_extended":
     sp=cpu.reg_read(A.UC_ARM_REG_SP)
     trace.append(("extended",r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),
                   int.from_bytes(cpu.mem_read(sp,4),"little"),
                   cstr(int.from_bytes(cpu.mem_read(sp+4,4),"little"))))
    elif name=="compressed_log_output":trace.append(("compressed",r[0],cstr(r[1]),cstr(r[2])))
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=(symbols["audio_wear_input_enabled_49eb96"] if compiled else 0x49eb96) if helper_only else (symbols["audio_wear_child_46b0ec"] if compiled else 0x46b0ec)
   uc.emu_start(start|1,0x600000,count=1300)
   return (uc.reg_read(A.UC_ARM_REG_R0),trace)
  cases=0
  for enable in (0,1,2):
   for lcd in (0,1,2,0x102):
    n=run(False,0,0,0,0,0,0,True,enable,lcd)
    c=run(True,0,0,0,0,0,0,True,enable,lcd)
    if n!=c:raise AssertionError(("helper",enable,lcd,n,c))
    cases+=1
  for pending in (0,1,2):
   for ota in (0,1):
    for wear in (0,1):
     for box in (0,1):
      for silent in (0,1):
       for flags in (0,1,2,4,7):
        values=(pending,ota,wear,box,silent,flags)
        n=run(False,*values);c=run(True,*values)
        if n!=c:raise AssertionError((values,n,c))
        cases+=1
  receipt={"status":"PASS_NATIVE_MAIN_SETTINGS_INPUT_CHECK_46B0EC",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "native_helper_body_sha256":HELPER_SHA,
           "source_owned_symbols":["audio_wear_child_46b0ec","audio_wear_input_enabled_49eb96"],
           "cases":cases,"limits":["State getters and logger calls are controlled hooks; final placement and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
