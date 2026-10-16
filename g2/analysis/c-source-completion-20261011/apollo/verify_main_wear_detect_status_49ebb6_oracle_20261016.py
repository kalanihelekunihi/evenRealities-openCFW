#!/usr/bin/env python3
"""Controlled native/C branch comparison for wear-detect status changes."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/wear_detect_status_change_49ebb6.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x49ebb6-0x438000:0x49ed04-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-wear-detect-status-49ebb6"
CALLS={"audio_wear_detect_get_enable_49ead8":0x49ead8,
       "audio_ble_master_emit_ring_event":0x4ac16c,
       "audio_wear_child_46b0ec":0x46b0ec,"audio_wear_child_502bf0":0x502bf0,
       "audio_wear_child_474100":0x474100,"audio_wear_child_47432c":0x47432c,
       "audio_wear_child_46805a":0x46805a,"audio_wear_child_47e320":0x47e320,
       "audio_uart_device_role_get":0x45a568,"audio_uart_display_housekeep":0x47243a,
       "audio_log_flags":0x43d0ce,"audio_log_extended":0x43d574,
       "compressed_log_output":0x43ce9e}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  shim=Path(temp)/"shim.c"
  shim.write_text("#include <stdint.h>\n"+
   "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}' for s in CALLS))
  elf=Path(temp)/"candidate.elf"
  subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                  "-std=c11","-ffreestanding","-fno-builtin","-O2","-w","-nostdlib",
                  "-Wl,-Ttext=0x100000","-Wl,-e,audio_wear_detect_handle_status_change_49ebb6",
                  str(SOURCE),str(shim),"-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def run(compiled,state,flags,enable,link,role):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   uc.reg_write(A.UC_ARM_REG_R0,state);uc.reg_write(A.UC_ARM_REG_SP,0x200ff000)
   uc.reg_write(A.UC_ARM_REG_LR,0x600001)
   hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
   trace=[]
   def cstr(address):return bytes(uc.mem_read(address,160)).split(b"\0",1)[0].decode("ascii")
   def observe(cpu,address,insn_size,_):
    name=hooks.get(address)
    if name is None:return
    r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
    result=0
    if name=="audio_wear_detect_get_enable_49ead8":trace.append(("enable",));result=enable
    elif name=="audio_wear_child_46b0ec":trace.append(("link",));result=link
    elif name=="audio_uart_device_role_get":trace.append(("role",));result=role
    elif name=="audio_log_flags":trace.append(("flags",));result=flags
    elif name=="audio_log_extended":
     sp=cpu.reg_read(A.UC_ARM_REG_SP)
     msg=cstr(int.from_bytes(cpu.mem_read(sp+4,4),"little"))
     item=("extended",r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),
           int.from_bytes(cpu.mem_read(sp,4),"little"),msg)
     if "%d" in msg:item+=(int.from_bytes(cpu.mem_read(sp+8,4),"little"),)
     trace.append(item)
    elif name=="compressed_log_output":
     item=("compressed",r[0],cstr(r[1]),cstr(r[2]))
     if "%d" in item[-1]:item+=(r[3],)
     trace.append(item)
    else:trace.append((name,r[0] if name in ("audio_ble_master_emit_ring_event","audio_wear_child_502bf0","audio_wear_child_46805a","audio_wear_child_47e320") else None))
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols["audio_wear_detect_handle_status_change_49ebb6"] if compiled else 0x49ebb6
   uc.emu_start(start|1,0x600000,count=1900)
   return (uc.reg_read(A.UC_ARM_REG_R0),trace)
  cases=0
  for state in (0,1,2,3,255,257,258):
   for flags in (0,1,2,4,7):
    for enable in (0,1,2):
     for link in (0,1):
      for role in (0,1):
       n=run(False,state,flags,enable,link,role)
       c=run(True,state,flags,enable,link,role)
       if n!=c:raise AssertionError((state,flags,enable,link,role,n,c))
       cases+=1
  receipt={"status":"PASS_NATIVE_MAIN_WEAR_DETECT_STATUS_49EBB6",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "source_owned_symbols":["audio_wear_detect_handle_status_change_49ebb6"],
           "cases":cases,"limits":["UI, ring, role, wear-getter and logger calls are controlled hooks; child bodies and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
