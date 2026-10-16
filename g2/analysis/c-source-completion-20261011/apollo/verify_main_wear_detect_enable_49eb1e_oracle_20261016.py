#!/usr/bin/env python3
"""Controlled native/C comparison for wear-detect enable and getter."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/wear_detect_enable_49eb1e.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x49eb1e-0x438000:0x49eb8e-0x438000]).hexdigest()
GETTER_SHA=hashlib.sha256(IMAGE[0x49ead8-0x438000:0x49eae2-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-wear-detect-enable-49eb1e"
CALLS={"audio_settings_get_config_46b44c":0x46b44c,
       "audio_wear_detect_handle_status_change_49ebb6":0x49ebb6,
       "audio_log_flags":0x43d0ce,"audio_log_extended":0x43d574,
       "compressed_log_output":0x43ce9e}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  shim=Path(temp)/"shim.c"
  shim.write_text("#include <stdint.h>\nvolatile uint32_t audio_uart_lcd_status_cell;\n"+
   "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}' for s in CALLS))
  elf=Path(temp)/"candidate.elf"
  subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                  "-std=c11","-ffreestanding","-fno-builtin","-O2","-w","-nostdlib",
                  "-Wl,-Ttext=0x100000","-Wl,-e,audio_wear_detect_set_enable_49eb1e",
                  str(SOURCE),str(shim),"-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def u32(v):return (v&0xffffffff).to_bytes(4,"little")
  def run(compiled,enable,current,flags,status):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   config=0x20040000
   cell=symbols["audio_uart_lcd_status_cell"] if compiled else 0x20074edc
   uc.mem_write(config,b"\xa5"*128)
   uc.mem_write(config+20,bytes([current]))
   uc.mem_write(cell,u32(status))
   for reg,value in ((A.UC_ARM_REG_R0,enable),(A.UC_ARM_REG_SP,0x200ff000),
                     (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,value)
   hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
   trace=[]
   def cstr(address):return bytes(uc.mem_read(address,160)).split(b"\0",1)[0].decode("ascii")
   def observe(cpu,address,insn_size,_):
    name=hooks.get(address)
    if name is None:return
    r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
    result=0
    if name=="audio_settings_get_config_46b44c":trace.append(("config",));result=config
    elif name=="audio_wear_detect_handle_status_change_49ebb6":trace.append(("change",r[0]))
    elif name=="audio_log_flags":trace.append(("flags",));result=flags
    elif name=="audio_log_extended":
     sp=cpu.reg_read(A.UC_ARM_REG_SP)
     trace.append(("extended",r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),
                   int.from_bytes(cpu.mem_read(sp,4),"little"),
                   cstr(int.from_bytes(cpu.mem_read(sp+4,4),"little")),
                   int.from_bytes(cpu.mem_read(sp+8,4),"little")))
    elif name=="compressed_log_output":trace.append(("compressed",r[0],cstr(r[1]),cstr(r[2]),r[3]))
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols["audio_wear_detect_set_enable_49eb1e"] if compiled else 0x49eb1e
   uc.emu_start(start|1,0x600000,count=700)
   return (trace,bytes(uc.mem_read(config+20,1)))
  cases=0
  for enable in (0,1,2,0x12345678,0xffffffff):
   for current in (0,1,2,255):
    for flags in (0,1,2,4,7):
     for status in (0,0x12345678):
      n=run(False,enable,current,flags,status);c=run(True,enable,current,flags,status)
      if n!=c:raise AssertionError((enable,current,flags,status,n,c))
      cases+=1
  receipt={"status":"PASS_NATIVE_MAIN_WEAR_DETECT_ENABLE_49EB1E",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "native_getter_body_sha256":GETTER_SHA,
           "source_owned_symbols":["audio_wear_detect_get_enable_49ead8",
                                   "audio_wear_detect_set_enable_49eb1e"],
           "cases":cases,"limits":["Config accessor, status-change and log calls are controlled hooks; status-change body and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
