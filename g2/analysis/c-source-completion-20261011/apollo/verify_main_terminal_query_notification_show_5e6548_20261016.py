#!/usr/bin/env python3
"""Compare Terminal query-notification-show FSM action with pinned stock."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_query_notification_show_5e6548.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-query-notification-show-5e6548'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STATE=0x2006e0d0;OBJ=0x20001000
CALLS=[('audio_terminal_counter_b_get_5973dc',0x5973dc),('audio_uart_page_43ded4',0x43ded4),('audio_terminal_query_visibility_5ec82a',0x5ec82a),('audio_log_flags',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=audio_terminal_ui_state_base=0x2006e0d0',*[f'--defsym={n}=0x{a|1:x}' for n,a in CALLS],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 return elf,seg,sym

def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 elf,seg,sym=build()
 def run(compiled,state,session,prior,object,flags,counter):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(STATE,bytes((i*7+31)&255 for i in range(0x2a0)));u.mem_write(OBJ,bytes(128))
  u.mem_write(STATE,struct.pack('<I',OBJ if object else 0));u.mem_write(STATE+0x288,struct.pack('<I',prior))
  trace=[];flag_i=0
  def cstr(cpu,p):return bytes(cpu.mem_read(p,180)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   nonlocal flag_i
   if pc not in (0x5973dc,0x43ded4,0x5ec82a,0x43d0ce,0x43d574,0x43ce9e):return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)];sp=cpu.reg_read(A.UC_ARM_REG_SP);value=0
   if pc==0x5973dc:trace.append(('counter',));value=counter
   elif pc==0x43ded4:trace.append(('flag',r[0],r[1]))
   elif pc==0x5ec82a:trace.append(('visibility',))
   elif pc==0x43d0ce:
    trace.append(('log_flags',flag_i));value=flags[min(flag_i,len(flags)-1)];flag_i+=1
   elif pc==0x43d574:
    line,fmt,sess,status=struct.unpack('<IIII',cpu.mem_read(sp,16))
    trace.append(('extended',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),cstr(cpu,r[3]),line,cstr(cpu,fmt),sess,status))
   elif pc==0x43ce9e:
    status=struct.unpack('<I',cpu.mem_read(sp,4))[0]
    trace.append(('compact',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),r[3],status))
   cpu.reg_write(A.UC_ARM_REG_R0,value);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  for reg,v in ((A.UC_ARM_REG_R0,state),(A.UC_ARM_REG_R1,session),(A.UC_ARM_REG_R2,0x12345678),(A.UC_ARM_REG_R3,0x87654321)):u.reg_write(reg,v)
  entry=sym['audio_terminal_ui_action_5e6548'] if compiled else 0x5e6548
  u.emu_start(entry|1,0x600000,count=400)
  return trace,bytes(u.mem_read(STATE,0x2a0)),u.reg_read(A.UC_ARM_REG_R0)
 cases=[]
 for state,session,prior,object,flags in itertools.product((0,1,2,0x101,0xffffffff),(0,7),(0,9),(0,1),((0,0,0),(2,0,0),(2,1,0),(0,0,4),(0,1,0))):
  cases.append((state,session,prior,object,flags,0x1357))
 for idx,args in enumerate(cases):
  a,b=run(False,*args),run(True,*args)
  if a!=b:
   print('case',idx,args,'stock trace',a[0],'compiled trace',b[0]);print('bytes',[(i,x,y) for i,(x,y) in enumerate(zip(a[1],b[1])) if x!=y][:20],a[2],b[2]);raise RuntimeError('query notification show mismatch')
 result={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_NOTIFICATION_SHOW_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Session fallback, state normalization, object flag, query visibility, enabled extended/compact logging and return','limits':['Counter, query-visibility and logger lower effects isolated; state final placement open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],len(cases),sha(path))
if __name__=='__main__':main()
