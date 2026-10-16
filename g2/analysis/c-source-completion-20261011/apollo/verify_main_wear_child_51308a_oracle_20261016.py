#!/usr/bin/env python3
"""Controlled native/C comparison for four-word wear request wrapper."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/wear_child_51308a.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x51308a-0x438000:0x5130a6-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-wear-child-51308a"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  shim=Path(temp)/"shim.c"
  shim.write_text('__attribute__((naked)) void audio_input_message_send_record(void){__asm volatile("bx lr");}\n')
  elf=Path(temp)/"candidate.elf"
  subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                  "-std=c11","-ffreestanding","-fno-builtin","-O2","-w","-nostdlib",
                  "-Wl,-Ttext=0x100000","-Wl,-e,audio_wear_child_51308a",
                  str(SOURCE),str(shim),"-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def run(compiled,value):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   uc.reg_write(A.UC_ARM_REG_R0,value);uc.reg_write(A.UC_ARM_REG_SP,0x200ff000)
   uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   hook=(symbols["audio_input_message_send_record"]&~1) if compiled else 0x51301c
   trace=[]
   def observe(cpu,address,insn_size,_):
    if address!=hook:return
    p=cpu.reg_read(A.UC_ARM_REG_R0)
    trace.append(bytes(cpu.mem_read(p,16)))
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols["audio_wear_child_51308a"] if compiled else 0x51308a
   uc.emu_start(start|1,0x600000,count=120)
   return trace
  values=(0,1,2,127,128,255,256,257,0x12345678,0xffffffff)
  for value in values:
   n=run(False,value);c=run(True,value)
   if n!=c:raise AssertionError((value,n,c))
  receipt={"status":"PASS_NATIVE_MAIN_WEAR_CHILD_51308A",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "source_owned_symbols":["audio_wear_child_51308a"],
           "cases":len(values),"limits":["Next callee is a controlled hook; its body and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],len(values),sha(path))
if __name__=="__main__":main()
