#!/usr/bin/env python3
"""Compare stock and C manual brightness and ALS scale getter."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_manual_brightness_46c1c8.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x46c1c8-0x438000:0x46c212-0x438000]).hexdigest()
GETTER_SHA=hashlib.sha256(IMAGE[0x4ae946-0x438000:0x4ae94c-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-setting-manual-brightness-46c1c8"
CALLS={"audio_quicklist_tick_now":0x44a1c6,
       "audio_als_manual_set_brightness_4ae81c":0x4ae81c,
       "audio_setting_als_scale_get_4ae946":0x4ae946,
       "audio_uart_hand_mismatch_448e34":0x448e34,
       "audio_setting_brightness_refresh_46c18c":0x46c18c}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  shim=Path(temp)/"shim.c"
  shim.write_text("#include <stdint.h>\nuint8_t audio_settings_config_live[0x50];\nuint32_t audio_als_scale_active;\n"+
   "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}' for s in CALLS if s!="audio_setting_als_scale_get_4ae946"))
  elf=Path(temp)/"candidate.elf"
  subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                  "-std=c11","-ffreestanding","-fno-builtin","-O2","-w","-nostdlib",
                  "-Wl,-Ttext=0x100000","-Wl,-e,audio_setting_manual_brightness_46c1c8",
                  str(SOURCE),str(shim),"-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def u32(v):return (v&0xffffffff).to_bytes(4,"little")
  def run(compiled,value,active,manual_result,tick,scale,getter_only=False):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   config=symbols["audio_settings_config_live"] if compiled else 0x20072da8
   scale_cell=symbols["audio_als_scale_active"] if compiled else 0x20000064
   uc.mem_write(config,b"\xa5"*0x50);uc.mem_write(config+2,bytes([active]))
   uc.mem_write(scale_cell,u32(scale))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.reg_write(A.UC_ARM_REG_R0,value)
   hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
   trace=[]
   def observe(cpu,address,insn_size,_):
    name=hooks.get(address)
    if name is None or getter_only:return
    arg=cpu.reg_read(A.UC_ARM_REG_R0)
    result=0
    if name=="audio_quicklist_tick_now":trace.append(("tick",));result=tick
    elif name=="audio_als_manual_set_brightness_4ae81c":trace.append(("manual",arg));result=manual_result
    elif name=="audio_setting_als_scale_get_4ae946":trace.append(("scale",));result=scale
    elif name=="audio_uart_hand_mismatch_448e34":trace.append(("signal",))
    else:trace.append(("refresh",))
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=(symbols["audio_setting_als_scale_get_4ae946"] if compiled else 0x4ae946) if getter_only else (symbols["audio_setting_manual_brightness_46c1c8"] if compiled else 0x46c1c8)
   uc.emu_start(start|1,0x600000,count=350)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:
    raise RuntimeError(("manual brightness did not return",compiled,getter_only,value,active))
   return (uc.reg_read(A.UC_ARM_REG_R0),trace) if getter_only else (uc.reg_read(A.UC_ARM_REG_R0),bytes(uc.mem_read(config,0x50)),trace)
  cases=0
  for scale in (0,0x400,0xffffffff):
   native=run(False,0,0,0,0,scale,True);compiled=run(True,0,0,0,0,scale,True)
   if native!=compiled:raise AssertionError(("getter",scale,native,compiled))
   cases+=1
  for value in (0,1,2,3,99,100,101,0xffffffff):
   for active in (0,1):
    for manual_result in (0,1,0xffffffff):
     for scale in (0,0x400,0xffffffff):
      args=(value,active,manual_result,0x12345678,scale)
      native=run(False,*args);compiled=run(True,*args)
      if native!=compiled:raise AssertionError((args,native,compiled))
      cases+=1
  receipt={"status":"PASS_NATIVE_MAIN_SETTING_MANUAL_BRIGHTNESS_46C1C8",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "native_getter_sha256":GETTER_SHA,
           "source_owned_symbols":["audio_setting_als_scale_get_4ae946","audio_setting_manual_brightness_46c1c8"],
           "cases":cases,"limits":["Tick, ALS learning, scale getter, signal and refresh calls are controlled hooks; ALS learning, final placement and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
