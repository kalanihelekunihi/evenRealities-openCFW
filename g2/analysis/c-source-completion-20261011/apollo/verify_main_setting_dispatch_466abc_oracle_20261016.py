#!/usr/bin/env python3
"""Controlled native/C comparison for all setting type dispatch arms."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/setting_dispatch_message_466abc.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x466abc-0x438000:0x466bec-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261016/main-setting-dispatch-466abc"
HANDLERS={1:0x466bec,2:0x466e1c,3:0x466ea2,4:0x466f28,5:0x467134,
          6:0x46713e,8:0x4671a2,9:0x467206,10:0x467308,11:0x467540,12:0x467c34}
CALLS={**{f"audio_setting_dispatch_type{k}_{v:x}":v for k,v in HANDLERS.items()},
       "SVC_Settings_SaveSettingConfigToKVCheck":0x46be7c,
       "audio_uart_ring_unpair_commit_hand_466016":0x466016,
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
                  "-Wl,-Ttext=0x100000","-Wl,-e,audio_setting_dispatch_message_466abc",
                  str(SOURCE),str(shim),"-o",str(elf)],check=True)
  with elf.open("rb") as handle:
   parsed=ELFFile(handle)
   segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments() if s["p_type"]=="PT_LOAD"]
   symbols={s.name:s["st_value"] for s in parsed.get_section_by_name(".symtab").iter_symbols()}
  def u32(v):return (v&0xffffffff).to_bytes(4,"little")
  def run(compiled,present,kind,flags):
   uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
   uc.mem_map(0x400000,0x400000);uc.mem_write(0x438000,IMAGE)
   uc.mem_map(0x100000,0x200000)
   for address,body in segments:uc.mem_write(address,body)
   uc.mem_map(0x20000000,0x100000)
   message=0x20040000 if present else 0
   uc.mem_write(0x20040000,b"\x7e"*128)
   uc.mem_write(0x2004000c,kind.to_bytes(2,"little"))
   uc.mem_write(0x20040010,u32(0x12345678))
   for reg,value in ((A.UC_ARM_REG_R0,message),(A.UC_ARM_REG_SP,0x200ff000),
                     (A.UC_ARM_REG_LR,0x600001)):uc.reg_write(reg,value)
   hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
   trace=[]
   def cstr(address):return bytes(uc.mem_read(address,160)).split(b"\0",1)[0].decode("ascii")
   def observe(cpu,address,insn_size,_):
    name=hooks.get(address)
    if name is None:return
    r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
    result=0
    if name=="audio_log_flags":trace.append(("flags",));result=flags
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
    elif name.startswith("audio_setting_dispatch_type"):
     k=int(name.split("_")[3][4:])
     trace.append(("handler",k,r[0]==message+16 if k in (1,4,9,10,11,12) else r[0]))
    else:trace.append(("post",name))
    cpu.reg_write(A.UC_ARM_REG_R0,result)
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
   uc.hook_add(UC_HOOK_CODE,observe)
   start=symbols["audio_setting_dispatch_message_466abc"] if compiled else 0x466abc
   uc.emu_start(start|1,0x600000,count=1400)
   return trace
  cases=0
  for present in (False,True):
   for kind in (*range(14),65535):
    for flags in (0,1,2,4,7):
     n=run(False,present,kind,flags);c=run(True,present,kind,flags)
     if n!=c:raise AssertionError((present,kind,flags,n,c))
     cases+=1
  receipt={"status":"PASS_NATIVE_MAIN_SETTING_DISPATCH_466ABC",
           "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
           "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
           "source_owned_symbols":["audio_setting_dispatch_message_466abc"],
           "cases":cases,"limits":["Type handlers, save/commit and log calls are controlled hooks; child bodies and hardware behavior remain open."]}
  path=OUT/"oracle-receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
  print(receipt["status"],cases,sha(path))
if __name__=="__main__":main()
