#!/usr/bin/env python3
"""Bounded stock/C oracle for the Terminal session-status FSM action."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_ui_action_session_status_5e6018.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-session-status-5e6018'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';STATE=0x2006e0d0
CALLS={'audio_terminal_counter_b_get_5973dc':0x5973dc,'audio_td_record_status_for_session':0x5973e4,'audio_terminal_ui_stop_service_c_5ebbc6':0x5ebbc6,'audio_td_session_struct_clear':0x597124,'audio_uart_page_43dfa4':0x43dfa4,'audio_terminal_processing_prepare_5ea30c':0x5ea30c,'audio_terminal_set_label_style_5e482a':0x5e482a,'audio_uart_page_49942e':0x49942e,'audio_terminal_elapsed_refresh_5e4902':0x5e4902,'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e}
BY_ADDR={v:k for k,v in CALLS.items()}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_terminal_ui_state_base':STATE,'audio_terminal_output_style_20003f80':0x20003f80};defs.update({k:v|1 for k,v in CALLS.items()})
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,old,session,current,status,missing,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x110000);u.mem_write(STATE,bytes((i*7+11)&255 for i in range(0x2a0)))
  for j,off in enumerate((0x1cc,0x1d0,0x1d4,0x1dc)):
   u.mem_write(STATE+off,struct.pack('<I',0 if j==missing else 0x20090000+j*0x1000))
  u.reg_write(A.UC_ARM_REG_SP,0x2010f000);u.reg_write(A.UC_ARM_REG_LR,0x600001);u.reg_write(A.UC_ARM_REG_R0,old);u.reg_write(A.UC_ARM_REG_R1,session)
  trace=[];fi=0
  def cstr(cpu,p):return bytes(cpu.mem_read(p,180)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   nonlocal fi
   if pc not in BY_ADDR:return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)];sp=cpu.reg_read(A.UC_ARM_REG_SP);v=0
   if pc==0x43d0ce:trace.append(('flags',fi));v=flags[min(fi,len(flags)-1)];fi+=1
   elif pc==0x43d574:
    words=struct.unpack('<IIIII',cpu.mem_read(sp,20));trace.append(('extended',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),cstr(cpu,r[3]),words[0],cstr(cpu,words[1]),tuple(words[2:5]) if words[0]==0x532 else (words[2],)))
   elif pc==0x43ce9e:
    words=struct.unpack('<II',cpu.mem_read(sp,8));trace.append(('compact',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),r[3],words if r[0]==0x08c00000 else ()))
   elif pc==0x49942e:trace.append(('label',r[0],cstr(cpu,r[1])))
   elif pc==0x5e482a:trace.append(('style',tuple(r)))
   elif pc==0x43dfa4:trace.append(('icon',r[0],r[1]))
   elif pc==0x5973e4:trace.append(('status_get',r[0]));v=status
   else:trace.append((BY_ADDR[pc],))
   if pc==0x5973dc:v=current
   cpu.reg_write(A.UC_ARM_REG_R0,v);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_ui_action_5e6018'] if compiled else 0x5e6018)|1,0x600000,count=800)
  return trace,bytes(u.mem_read(STATE,0x2a0)),u.reg_read(A.UC_ARM_REG_R0)
 cases=list(itertools.product((0,9,0x109,255),(0,0x1357,0x2457),(0x1357,0x2457),(0,1,2,0x101),(-1,0,1,2,3),((0,)*20,(2,0,0,2,0,0,2,0,0),(0,1,0,0,1,0,0,1,0),(0,0,4,0,0,4,0,0,4))))
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock!=source:
   print('mismatch',i,args,'stock',stock[0],stock[2],'source',source[0],source[2]);raise RuntimeError('session-status mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_STATUS_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Stale/current session, query-pending status, widget gates, logger branches, call order and return','limits':['Child services, TD and LVGL effects are isolated; final image/RAM integration and hardware remain open.']}
 p=OUT/'oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(p))
if __name__=='__main__':main()
