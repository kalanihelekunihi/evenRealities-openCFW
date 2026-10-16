#!/usr/bin/env python3
"""Compare the query-permission dialog's C call and state contract with stock."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_query_visibility_5ec82a.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-query-visibility-5ec82a'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STATE=0x2006e0d0;QUEUE=0x20074a90;FONT=0x200746e0
ROOT_OBJ=0x20082000;IMAGE=0x20083000;LABEL=0x20084000;PARENT=0x20085000;NAME=0x20086000
CALLS={
 'audio_uart_device_role_get':0x45a568,
 'audio_terminal_query_root_5e4f54':0x5e4f54,
 'audio_uart_page_43f4c0':0x43f4c0,
 'audio_uart_page_44119c':0x44119c,
 'audio_uart_page_44120e':0x44120e,
 'audio_uart_page_44121c':0x44121c,
 'audio_uart_page_44122a':0x44122a,
 'audio_uart_page_441238':0x441238,
 'audio_uart_page_43dfa4':0x43dfa4,
 'audio_uart_page_498668':0x498668,
 'audio_uart_page_498680':0x498680,
 'audio_uart_page_43f6b8':0x43f6b8,
 'audio_uart_page_44104c':0x44104c,
 'audio_uart_page_44127e':0x44127e,
 'audio_uart_page_44129e':0x44129e,
 'audio_uart_page_4413ce':0x4413ce,
 'audio_terminal_query_session_name_5ec7f0':0x5ec7f0,
 'audio_uart_page_499416':0x499416,
 'audio_uart_page_441180':0x441180,
 'audio_uart_page_layout_499678':0x499678,
 'audio_lv_label_set_text_fmt_49954c':0x49954c,
 'audio_uart_page_44140e':0x44140e,
 'audio_uart_page_44143e':0x44143e,
 'audio_uart_page_43f6d6':0x43f6d6,
 'audio_uart_page_43f66c':0x43f66c,
 'audio_uart_page_overlay_44dca2':0x44dca2,
 'audio_uart_lv_obj_width_43fd9e':0x43fd9e,
 'audio_uart_page_43f506':0x43f506,
}
BY_ADDR={v:k for k,v in CALLS.items()}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_terminal_ui_state_base':STATE,'audio_terminal_display_queue_handle':QUEUE,'audio_uart_ring_secondary_head_cell':FONT,'audio_terminal_query_image_770890':0x770890}
 defs.update({k:v|1 for k,v in CALLS.items()})
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];symbols={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,role,queue,prior,name,parent):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  u.mem_write(STATE,bytes((i*13+7)&255 for i in range(0x2a0)))
  u.mem_write(STATE+0x224,struct.pack('<III',prior,0x88888888,0x77777777))
  u.mem_write(STATE+0x288,struct.pack('<I',0x1357))
  u.mem_write(QUEUE,struct.pack('<I',0x20070000 if queue else 0))
  u.mem_write(FONT,struct.pack('<I',0x20077700))
  u.mem_write(NAME,b'Ada\0')
  trace=[]
  def cstr(cpu,p):return bytes(cpu.mem_read(p,80)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   if pc not in BY_ADDR:return
   n=BY_ADDR[pc];r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if pc==0x49954c:args=(r[0],cstr(cpu,r[1]),r[2])
   elif pc==0x43f6d6:args=(*r,struct.unpack('<I',cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_SP),4))[0])
   else:args=tuple(r[:{0x45a568:0,0x5ec7f0:0,0x498668:1,0x499416:1,0x43f66c:1,0x44dca2:1,0x43fd9e:1,0x44104c:1,0x43dfa4:2,0x498680:2,0x499678:2,0x43f506:2,0x5e4f54:2}.get(pc,3)])
   trace.append((n,args))
   value={0x45a568:role,0x5e4f54:ROOT_OBJ,0x498668:IMAGE,0x499416:LABEL,0x5ec7f0:NAME if name else 0,0x44dca2:PARENT if parent else 0,0x43fd9e:0x130}.get(pc,0)
   if pc==0x44104c:value=r[0]^0x12345678
   cpu.reg_write(A.UC_ARM_REG_R0,value);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  u.emu_start((symbols['audio_terminal_query_visibility_5ec82a'] if compiled else 0x5ec82a)|1,0x600000,count=1200)
  return trace,bytes(u.mem_read(STATE,0x2a0))
 cases=list(itertools.product((1,2),(0,1),(0,0x12345678),(0,1),(0,1)))
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock!=source:
   print('mismatch',i,args,'stock trace',stock[0],'source trace',source[0]);print('state diff',[(j,a,b) for j,(a,b) in enumerate(zip(stock[1],source[1])) if a!=b][:16]);raise RuntimeError('query visibility mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_VISIBILITY_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Early returns, device-role offset, dialog construction and formatted label branches, parent width/position branch, state writes','limits':['Lower LVGL and root-creation effects isolated; stock image descriptor remains absolute pending source ownership; state and display queue final placement open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(path))
if __name__=='__main__':main()
