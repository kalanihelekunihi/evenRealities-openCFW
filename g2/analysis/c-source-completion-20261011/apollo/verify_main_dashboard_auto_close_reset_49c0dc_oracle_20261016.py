#!/usr/bin/env python3
"""Compare stock and C dashboard timeout reset and bounded RAM writes."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/dashboard_auto_close_reset_49c0dc.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x49c0dc-0x438000:0x49c146-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-dashboard-auto-close-reset-49c0dc"
CALLS={"audio_log_wake_allowed":0x443484,
       "audio_quicklist_refresh_enabled_4434d0":0x4434d0,
       "audio_log_flags":0x43d0ce,"audio_log_extended":0x43d574,
       "compressed_log_output":0x43ce9e}
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
                  "-Wl,-Ttext=0x100000","-Wl,-e,audio_dashboard_auto_close_reset_49c0dc",
                  str(SOURCE),str(shim),"-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def u32(v):return (v&0xffffffff).to_bytes(4,"little")
  def run(compiled,wake,member,flags,initial,default):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   current=symbols["audio_dashboard_auto_close_current_200743d0"] if compiled else 0x200743d0
   source=symbols["audio_dashboard_auto_close_default_200743d4"] if compiled else 0x200743d4
   uc.mem_write(current,u32(initial));uc.mem_write(source,u32(default))
   uc.reg_write(A.UC_ARM_REG_SP,0x200ff000);uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
   trace=[]
   def cstr(address):return bytes(uc.mem_read(address,170)).split(b"\0",1)[0].decode("ascii")
   def observe(cpu,address,insn_size,_):
    name=hooks.get(address)
    if name is None:return
    r=tuple(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3))
    if name=="audio_log_wake_allowed":trace.append(("wake",));result=wake
    elif name=="audio_quicklist_refresh_enabled_4434d0":trace.append(("member",r[0]));result=member
    elif name=="audio_log_flags":trace.append(("flags",));result=flags
    elif name=="audio_log_extended":
     sp=cpu.reg_read(A.UC_ARM_REG_SP)
     trace.append(("extended",r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),
                   int.from_bytes(cpu.mem_read(sp,4),"little"),
                   cstr(int.from_bytes(cpu.mem_read(sp+4,4),"little")),
                   int.from_bytes(cpu.mem_read(sp+8,4),"little")))
     result=0
    else:trace.append(("compressed",r[0],cstr(r[1]),cstr(r[2]),r[3]));result=0
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols["audio_dashboard_auto_close_reset_49c0dc"] if compiled else 0x49c0dc
   uc.emu_start(start|1,0x600000,count=300)
   return (int.from_bytes(uc.mem_read(current,4),"little"),
           int.from_bytes(uc.mem_read(source,4),"little"),trace)
  cases=0
  for wake in (0,1,2):
   for member in (0,1,2):
    for flags in (0,1,2,4,7):
     for initial,default in ((0,0),(0x12345678,0xabcdef01)):
      values=(wake,member,flags,initial,default)
      native=run(False,*values);compiled=run(True,*values)
      if native!=compiled:raise AssertionError((values,native,compiled))
      cases+=1
  receipt={"status":"PASS_NATIVE_MAIN_DASHBOARD_AUTO_CLOSE_RESET_49C0DC",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "source_owned_symbols":["audio_dashboard_auto_close_current_200743d0",
                                   "audio_dashboard_auto_close_default_200743d4",
                                   "audio_dashboard_auto_close_reset_49c0dc"],
           "cases":cases,"limits":["Wake, page membership and logger calls are controlled hooks; RAM allocation extent, final placement and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
