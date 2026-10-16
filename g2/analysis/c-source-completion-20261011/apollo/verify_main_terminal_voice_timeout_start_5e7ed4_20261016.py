#!/usr/bin/env python3
"""Compare voice timeout start with stock state and logger calls."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_voice_timeout_start_5e7ed4.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-voice-timeout-start-5e7ed4'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
TIMER=0x20073c38;CALLS={'g2_flashdb_candidate_tick':0x4490cc,'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_terminal_ui_timer_state_20073c38=0x20073c38',*[f'--defsym={k}=0x{v|1:x}' for k,v in CALLS.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,tick,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(TIMER,bytes((i*17+3)&255 for i in range(0x18)))
  u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  trace=[];fi=0
  def cstr(cpu,p):return bytes(cpu.mem_read(p,140)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   nonlocal fi
   if pc not in CALLS.values():return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   sp=cpu.reg_read(A.UC_ARM_REG_SP);ret=0
   if pc==0x4490cc:trace.append(('tick',));ret=tick
   elif pc==0x43d0ce:trace.append(('flags',fi));ret=flags[min(fi,len(flags)-1)];fi+=1
   elif pc==0x43d574:
    line,msg,interval=struct.unpack('<III',cpu.mem_read(sp,12))
    trace.append(('extended',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),cstr(cpu,r[3]),line,cstr(cpu,msg),interval))
   else:trace.append(('compact',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),r[3]))
   cpu.reg_write(A.UC_ARM_REG_R0,ret);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_voice_timeout_start_5e7ed4'] if compiled else 0x5e7ed4)|1,0x600000,count=250)
  return trace,bytes(u.mem_read(TIMER,0x18))
 cases=list(itertools.product((0,1,0xfffffff0,0xffffffff),((0,0,0),(2,0,0),(0,1,0),(0,0,4),(0,0,0),(2,1,4))))
 for i,args in enumerate(cases):
  a,b=run(False,*args),run(True,*args)
  if a!=b:raise RuntimeError(f'case {i} {args}: stock={a} rebuilt={b}')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_TIMEOUT_START_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Timer flag, wrapping deadline, extended and compact logging decisions','limits':['Clock and logger lower effects isolated; timer state final RAM placement and runtime timing remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(path))
if __name__=='__main__':main()
