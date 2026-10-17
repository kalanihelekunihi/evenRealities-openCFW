#!/usr/bin/env python3
"""Compare Terminal session-list-show FSM action with stock call/state behavior."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_ui_action_session_list_show_5ed208.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-session-list-show-5ed208'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';STATE=0x2006e0d0
SPECS={'audio_terminal_session_index_i16_5eca44':(0x5eca44,1),'audio_td_flag_b_get':(0x59758e,0),'audio_terminal_cancel_pending_5cef8c':(0x5cef8c,0),'audio_td_flag_b_set_597572':(0x597572,1),'audio_terminal_ui_stop_service_b_5ec268':(0x5ec268,0),'audio_terminal_ui_stop_service_c_5ebbc6':(0x5ebbc6,0),'audio_terminal_ui_stop_service_e_5ec9c0':(0x5ec9c0,0),'audio_terminal_ui_stop_service_d_5ec770':(0x5ec770,0),'audio_uart_page_43ded4':(0x43ded4,2),'audio_terminal_session_list_event_5ed1fa':(0x5ed1fa,0),'audio_terminal_session_list_rebuild_5ecef6':(0x5ecef6,1),'audio_log_flags':(0x43d0ce,0),'audio_log_extended':(0x43d574,6),'compressed_log_output':(0x43ce9e,3)}
BY_ADDR={v[0]:(k,v[1]) for k,v in SPECS.items()}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_terminal_ui_state_base':STATE};defs.update({k:v[0]|1 for k,v in SPECS.items()})
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,old,payload,flag,root,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(STATE,bytes((i*7+11)&255 for i in range(0x2a0)));u.mem_write(STATE,struct.pack('<I',root))
  u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001);u.reg_write(A.UC_ARM_REG_R0,old);u.reg_write(A.UC_ARM_REG_R1,payload)
  trace=[];fi=0
  def cstr(cpu,p):return bytes(cpu.mem_read(p,160)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   nonlocal fi
   if pc not in BY_ADDR:return
   name,n=BY_ADDR[pc];r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)];sp=cpu.reg_read(A.UC_ARM_REG_SP);v=0
   if pc==0x43d0ce:trace.append(('flags',fi));v=flags[min(fi,len(flags)-1)];fi+=1
   elif pc==0x43d574:
    line,msg,old_arg,selected=struct.unpack('<IIII',cpu.mem_read(sp,16));trace.append(('extended',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),cstr(cpu,r[3]),line,cstr(cpu,msg),old_arg if line==0x1d0 else None,selected if line==0x1d0 else None))
   elif pc==0x43ce9e:
    selected=struct.unpack('<I',cpu.mem_read(sp,4))[0];trace.append(('compact',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),r[3] if r[0]==0x0c800000 else None,selected if r[0]==0x0c800000 else None))
   else:trace.append((name,tuple(r[:n])))
   if pc==0x5eca44:v=(r[0]&0xffff);v=v-65536 if v&0x8000 else v
   elif pc==0x59758e:v=flag
   cpu.reg_write(A.UC_ARM_REG_R0,v&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_ui_action_5ed208'] if compiled else 0x5ed208)|1,0x600000,count=550)
  return trace,bytes(u.mem_read(STATE,0x2a0)),u.reg_read(A.UC_ARM_REG_R0)
 cases=list(itertools.product((0,8,12,0x10c),(0,1,0x8001,0x12345678),(0,1),(0,0x20090000),((0,)*12,(2,0,0,2,0,0,2,0,0,2,0,0),(0,1,0,0,1,0,0,1,0,0,1,0),(0,0,4,0,0,4,0,0,4,0,0,4))))
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock!=source:
   for j,(a,b) in enumerate(itertools.zip_longest(stock[0],source[0])):
    if a!=b:print('trace diff',j,a,b);break
   print('mismatch',i,args,'return',stock[2],source[2],'state',stock[1]==source[1]);raise RuntimeError('session-list-show mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_LIST_SHOW_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Pending cancellation gate, services, selector rebuild call, UI state byte, enabled logs and return','limits':['Cancellation sender, selector rebuild and lower service/logger effects isolated; final image/hardware remain open.']}
 p=OUT/'oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(p))
if __name__=='__main__':main()
