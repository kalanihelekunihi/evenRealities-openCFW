#!/usr/bin/env python3
"""Compare stock and C coordinate-setting handlers and config writes."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_dispatch_coordinates_466e1c_466ea2.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA={"y":hashlib.sha256(IMAGE[0x466e1c-0x438000:0x466ea2-0x438000]).hexdigest(),
          "x":hashlib.sha256(IMAGE[0x466ea2-0x438000:0x466f28-0x438000]).hexdigest()}
OUT=G2/"build/c-firmware/20261016/main-setting-coordinates-466e1c-466ea2"
CALLS={"audio_settings_get_config_46b44c":0x46b44c,
       "audio_log_flags":0x43d0ce,"audio_log_extended":0x43d574,
       "compressed_log_output":0x43ce9e,"audio_log_wake_allowed":0x443484,
       "audio_uart_service_mode":0x45a570,
       "audio_setting_display_start_466890":0x466890,
       "audio_dashboard_auto_close_reset_49c0dc":0x49c0dc,
       "audio_uart_master_input_event":0x465748}
START={"y":("audio_setting_dispatch_type2_466e1c",0x466e1c),
       "x":("audio_setting_dispatch_type3_466ea2",0x466ea2)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  shim=Path(temp)/"shim.c"
  shim.write_text("#include <stdint.h>\n"+"\n".join(
   f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}' for s in CALLS))
  elf=Path(temp)/"candidate.elf"
  subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                  "-std=c11","-ffreestanding","-fno-builtin","-O2","-w","-nostdlib",
                  "-Wl,-Ttext=0x100000","-Wl,-e,audio_setting_dispatch_type2_466e1c",
                  str(SOURCE),str(shim),"-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def run(compiled,axis,value,flags,wake,mode):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   config=0x20040000;uc.mem_write(config,b"\xa5"*128)
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.reg_write(A.UC_ARM_REG_R0,value)
   hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
   trace=[]
   def cstr(address):return bytes(uc.mem_read(address,175)).split(b"\0",1)[0].decode("ascii")
   def observe(cpu,address,insn_size,_):
    name=hooks.get(address)
    if name is None:return
    r=tuple(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
    result=0
    if name=="audio_settings_get_config_46b44c":trace.append(("config",));result=config
    elif name=="audio_log_flags":trace.append(("flags",));result=flags
    elif name=="audio_log_extended":
     sp=cpu.reg_read(A.UC_ARM_REG_SP)
     trace.append(("extended",r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),
                   int.from_bytes(cpu.mem_read(sp,4),"little"),
                   cstr(int.from_bytes(cpu.mem_read(sp+4,4),"little")),
                   int.from_bytes(cpu.mem_read(sp+8,4),"little")))
    elif name=="compressed_log_output":trace.append(("compressed",r[0],cstr(r[1]),cstr(r[2]),r[3]))
    elif name=="audio_log_wake_allowed":trace.append(("wake",));result=wake
    elif name=="audio_uart_service_mode":trace.append(("mode",));result=mode
    elif name=="audio_setting_display_start_466890":trace.append(("display_start",))
    elif name=="audio_dashboard_auto_close_reset_49c0dc":trace.append(("reset",))
    else:trace.append(("input",*r))
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   symbol,native=START[axis]
   uc.emu_start((symbols[symbol] if compiled else native)|1,0x600000,count=500)
   return bytes(uc.mem_read(config,128)),trace
  cases=0
  for axis in ("y","x"):
   for value in (0,1,0x100,0xffffffff):
    for flags in (0,1,2,4,7):
     for wake in (0,1,2):
      for mode in (0,1,2,0x101):
       values=(axis,value,flags,wake,mode)
       native=run(False,*values);compiled=run(True,*values)
       if native!=compiled:raise AssertionError((values,native,compiled))
       cases+=1
  receipt={"status":"PASS_NATIVE_MAIN_SETTING_COORDINATES_466E1C_466EA2",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "source_owned_symbols":["audio_setting_dispatch_type2_466e1c","audio_setting_dispatch_type3_466ea2"],
           "cases":cases,"limits":["Config getter, logging, wake, mode, display and peer calls are controlled hooks; final placement and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
