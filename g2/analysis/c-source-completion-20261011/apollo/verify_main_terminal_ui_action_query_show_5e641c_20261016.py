#!/usr/bin/env python3
"""Compare Terminal query-show action's stock/C call, state and return contract."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_ui_action_query_show_5e641c.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-action-query-show-5e641c'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';STATE=0x2006e0d0
CALLS={'audio_terminal_reset_display_5e4c84':0x5e4c84,'audio_terminal_ui_stop_service_e_5ec9c0':0x5ec9c0,'audio_terminal_reset_ancillary_5e65f8':0x5e65f8,'audio_uart_page_43dfa4':0x43dfa4,'audio_terminal_reset_mode_5eae2c':0x5eae2c,'audio_terminal_query_construct_5eb8da':0x5eb8da,'audio_terminal_query_hit_test_5eb61e':0x5eb61e,'audio_terminal_query_layout_5ebb96':0x5ebb96,'audio_terminal_processing_prepare_5ea30c':0x5ea30c,'audio_terminal_image_set_5e47fe':0x5e47fe,'audio_uart_page_49942e':0x49942e,'audio_terminal_elapsed_clear_5e4894':0x5e4894,'audio_log_flags':0x43d0ce,'audio_log_extended':0x43d574,'compressed_log_output':0x43ce9e}
BY_ADDR={v:k for k,v in CALLS.items()};ARGS={0x5e4c84:1,0x43dfa4:2,0x5eae2c:1,0x5eb61e:1}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_terminal_ui_state_base':STATE,'audio_terminal_asset_7733a8':0x7733a8};defs.update({k:v|1 for k,v in CALLS.items()})
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,old,refresh,hit,missing,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(STATE,bytes((i*7+11)&255 for i in range(0x2a0)))
  for j,off in enumerate((0,0x214,0x1cc,0x1d0,0x1d4,0x1dc)):
   u.mem_write(STATE+off,struct.pack('<I',0 if j==missing else 0x20090000+j*0x1000))
  u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001);u.reg_write(A.UC_ARM_REG_R0,old);u.reg_write(A.UC_ARM_REG_R1,refresh)
  trace=[];fi=0
  def cstr(cpu,p):return bytes(cpu.mem_read(p,180)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   nonlocal fi
   if pc not in BY_ADDR:return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)];sp=cpu.reg_read(A.UC_ARM_REG_SP);v=0
   if pc==0x43d0ce:trace.append(('flags',fi));v=flags[min(fi,len(flags)-1)];fi+=1
   elif pc==0x43d574:
    line,msg,old_arg,refresh_arg=struct.unpack('<IIII',cpu.mem_read(sp,16));trace.append(('extended',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),cstr(cpu,r[3]),line,cstr(cpu,msg),old_arg,refresh_arg))
   elif pc==0x43ce9e:
    refresh_arg=struct.unpack('<I',cpu.mem_read(sp,4))[0];trace.append(('compact',r[0],cstr(cpu,r[1]),cstr(cpu,r[2]),r[3],refresh_arg))
   elif pc==0x49942e:trace.append(('label',r[0],cstr(cpu,r[1])))
   elif pc==0x5e47fe:trace.append(('image',r[0],r[1]))
   else:trace.append((BY_ADDR[pc],tuple(r[:ARGS.get(pc,0)])))
   if pc==0x5eb61e:v=hit
   cpu.reg_write(A.UC_ARM_REG_R0,v);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_ui_action_5e641c'] if compiled else 0x5e641c)|1,0x600000,count=700)
  return trace,bytes(u.mem_read(STATE,0x2a0)),u.reg_read(A.UC_ARM_REG_R0)
 cases=list(itertools.product((0,3,0x103),(0,1,0x101,0x12345678),(0,1),(-1,0,1,2,3,4,5),((0,0,0),(2,0,0),(0,1,0),(0,0,4),(2,1,4))))
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock!=source:print('mismatch',i,args,'stock',stock[0],stock[2],'source',source[0],source[2]);raise RuntimeError('query-show mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_SHOW_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Cleanup and constructor call order, refresh mode, hit-test state byte, widget gate, enabled logging and return','limits':['Query constructor and hit-test children, lower LVGL/logger effects, final image/RAM and hardware remain open.']}
 p=OUT/'oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(p))
if __name__=='__main__':main()
