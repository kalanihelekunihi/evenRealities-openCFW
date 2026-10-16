#!/usr/bin/env python3
"""Compare stock and C gesture-list setting routing under controlled hooks."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_dispatch_type10_467308.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x467308-0x438000:0x4674a6-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-setting-type10-467308"
CALLS={"audio_log_flags":0x43d0ce,"audio_log_extended":0x43d574,
       "compressed_log_output":0x43ce9e,"audio_setting_gesture_apptype_46658e":0x46658e,
       "audio_setting_unit_record_get_466010":0x466010,
       "audio_uart_ring_unpair_publish_hand_4661a6":0x4661a6}
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
                  "-Wl,-Ttext=0x100000","-Wl,-e,audio_setting_dispatch_type10_467308",
                  str(SOURCE),str(shim),"-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def u32(v):return (v&0xffffffff).to_bytes(4,"little")
  def run(compiled,count,flags):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   data=0x20040000;record=0x20041000
   body=bytearray(4+12*255)
   if count is not None:
    body[:2]=count.to_bytes(2,"little")
    for i in range(255):
     off=4+12*i
     body[off:off+4]=u32(0x100+i)
     body[off+4:off+8]=u32(0x200+i)
     body[off+8]=(0x30+i)&0xff
   uc.mem_write(data,bytes(body))
   uc.mem_write(record,bytes(range(0x30)))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   uc.reg_write(A.UC_ARM_REG_R0,0 if count is None else data)
   hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
   trace=[]
   def cstr(address):return bytes(uc.mem_read(address,190)).split(b"\0",1)[0].decode("ascii")
   def observe(cpu,address,insn_size,_):
    name=hooks.get(address)
    if name is None:return
    r=tuple(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
    sp=cpu.reg_read(A.UC_ARM_REG_SP)
    word=lambda n:int.from_bytes(cpu.mem_read(sp+4*n,4),"little")
    result=0
    if name=="audio_log_flags":trace.append(("flags",));result=flags
    elif name=="audio_log_extended":
     line=word(0);n=6 if line==0x227 else (1 if line==0x213 else 0)
     trace.append(("extended",r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),line,
                   cstr(word(1)),tuple(word(i) for i in range(2,2+n))))
    elif name=="compressed_log_output":
     n=6 if r[0]==0x0d800000 else (1 if r[0]==0x0c400000 else 0)
     extras=(r[3],)+tuple(word(i) for i in range(n-1)) if n else ()
     trace.append(("compressed",r[0],cstr(r[1]),cstr(r[2]),extras))
    elif name=="audio_setting_gesture_apptype_46658e":trace.append(("set",*r[:3]))
    elif name=="audio_setting_unit_record_get_466010":trace.append(("record_get",));result=record
    else:trace.append(("publish",))
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols["audio_setting_dispatch_type10_467308"] if compiled else 0x467308
   uc.emu_start(start|1,0x600000,count=20000)
   if (uc.reg_read(A.UC_ARM_REG_PC)&~1)!=0x600000:
    raise RuntimeError(("gesture list did not return",compiled,count,hex(uc.reg_read(A.UC_ARM_REG_PC))))
   return trace
  cases=0
  for count in (None,0,1,2,3,0x100,0x101,255,0x1ff):
   for flags in (0,1,2,4,7):
    native=run(False,count,flags);compiled=run(True,count,flags)
    if native!=compiled:raise AssertionError((count,flags,native,compiled))
    cases+=1
  receipt={"status":"PASS_NATIVE_MAIN_SETTING_TYPE10_467308",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "source_owned_symbols":["audio_setting_dispatch_type10_467308"],
           "cases":cases,"limits":["Logger, setter, record getter and publish calls are controlled hooks; final placement and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
