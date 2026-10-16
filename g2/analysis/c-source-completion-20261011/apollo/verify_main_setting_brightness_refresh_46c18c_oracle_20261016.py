#!/usr/bin/env python3
"""Compare stock and C settings brightness refresh and callback dispatch."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_brightness_refresh_46c18c.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x46c18c-0x438000:0x46c1bc-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-setting-brightness-refresh-46c18c"
CALLS={"audio_log_wake_allowed":0x443484,"audio_uart_device_role_get":0x45a568,
       "audio_setting_display_start_466890":0x466890,
       "audio_als_callback_context_47394c":0x47394c}
CALLBACK=0x20050000
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  shim=Path(temp)/"shim.c"
  shim.write_text("#include <stdint.h>\nuint8_t audio_settings_config_live[0x50];\n"+
   "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}' for s in CALLS))
  elf=Path(temp)/"candidate.elf"
  subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                  "-std=c11","-ffreestanding","-fno-builtin","-O2","-w","-nostdlib",
                  "-Wl,-Ttext=0x100000","-Wl,-e,audio_setting_brightness_refresh_46c18c",
                  str(SOURCE),str(shim),"-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def run(compiled,wake,role,brightness):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   cell=symbols["audio_settings_config_live"] if compiled else 0x20072da8
   uc.mem_write(cell,b"\xa5"*0x50);uc.mem_write(cell+1,bytes([brightness]))
   context=0x20040000
   uc.mem_write(context+0x14,(CALLBACK|1).to_bytes(4,"little"))
   uc.mem_write(CALLBACK,b"\x70\x47")
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
   trace=[]
   def observe(cpu,address,insn_size,_):
    name=hooks.get(address)
    if name is None and address!=CALLBACK:return
    r=cpu.reg_read(A.UC_ARM_REG_R0)
    result=0
    if address==CALLBACK:trace.append(("callback",r))
    elif name=="audio_log_wake_allowed":trace.append(("wake",));result=wake
    elif name=="audio_uart_device_role_get":trace.append(("role",));result=role
    elif name=="audio_setting_display_start_466890":trace.append(("display_start",))
    else:trace.append(("context",));result=context
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols["audio_setting_brightness_refresh_46c18c"] if compiled else 0x46c18c
   uc.emu_start(start|1,0x600000,count=200)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:
    raise RuntimeError(("brightness refresh did not return",compiled,wake,role,brightness))
   return uc.reg_read(A.UC_ARM_REG_R0),trace
  cases=0
  for wake in (0,1,2):
   for role in (0,1,2):
    for brightness in (0,1,255):
     values=(wake,role,brightness)
     native=run(False,*values);compiled=run(True,*values)
     if native!=compiled:raise AssertionError((values,native,compiled))
     cases+=1
  receipt={"status":"PASS_NATIVE_MAIN_SETTING_BRIGHTNESS_REFRESH_46C18C",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "source_owned_symbols":["audio_setting_brightness_refresh_46c18c"],
           "cases":cases,"limits":["Wake, role, context, display-start and callback calls are controlled hooks; final placement and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
