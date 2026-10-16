#!/usr/bin/env python3
"""Compare ASR timeout-stop state and logs with the pinned stock payload."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_asr_timeout_stop_5e7fc0.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-asr-timeout-stop-5e7fc0'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';TIMER=0x20073c38
CALLS={'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_terminal_ui_timer_state_20073c38':TIMER};defs.update({k:v|1 for k,v in CALLS.items()})
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,active,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);initial=bytes(range(24));u.mem_write(TIMER,initial[:8]+bytes((active,))+initial[9:])
  u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001);trace=[];fi=0
  def cstr(cpu,p):return bytes(cpu.mem_read(p,160)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   nonlocal fi
   if pc not in CALLS.values():return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)];sp=cpu.reg_read(A.UC_ARM_REG_SP);v=0
   if pc==0x43d0ce:trace.append(('flags',fi));v=flags[min(fi,len(flags)-1)];fi+=1
   elif pc==0x43d574:
    line,msg=struct.unpack('<II',cpu.mem_read(sp,8));trace.append(('extended',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),cstr(cpu,r[3]),line,cstr(cpu,msg)))
   else:trace.append(('compact',r[0],cstr(cpu,r[1]),cstr(cpu,r[2])))
   cpu.reg_write(A.UC_ARM_REG_R0,v);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_asr_timeout_stop_5e7fc0'] if compiled else 0x5e7fc0)|1,0x600000,count=150)
  return trace,bytes(u.mem_read(TIMER,24))
 cases=list(itertools.product((0,1,255),((0,0,0),(2,0,0),(0,1,0),(0,0,4),(2,1,4))))
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock!=source:print('mismatch',i,args,stock,source);raise RuntimeError('ASR timeout-stop mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_ASR_TIMEOUT_STOP_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Timer byte gate/clear and exact extended and compressed logs','limits':['Lower logger effects isolated; complete main image, final timer placement and hardware remain open.']}
 p=OUT/'oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(p))
if __name__=='__main__':main()
