#!/usr/bin/env python3
"""Compare Terminal query constructor's stock/C call and state contract."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_query_construct_5eb8da.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-query-construct-5eb8da'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';STATE=0x2006e0d0
SPECS={'audio_td_session_struct_ptr':(0x59731e,0),'audio_lv_style_opa_441488':(0x441488,3),'audio_terminal_query_root_5e4f54':(0x5e4f54,2),'audio_uart_page_43f4c0':(0x43f4c0,3),'audio_uart_page_44119c':(0x44119c,3),'audio_uart_page_4411aa':(0x4411aa,3),'audio_uart_page_44120e':(0x44120e,3),'audio_uart_page_44122a':(0x44122a,3),'audio_uart_page_441238':(0x441238,3),'audio_uart_page_44121c':(0x44121c,3),'audio_uart_page_441246':(0x441246,3),'audio_uart_page_48ba78':(0x48ba78,2),'audio_uart_page_48ba92':(0x48ba92,4),'audio_uart_page_44e3ca':(0x44e3ca,2),'audio_uart_page_44e368':(0x44e368,2),'audio_uart_page_43de82':(0x43de82,1),'audio_uart_page_43dfa4':(0x43dfa4,2),'audio_uart_page_44129e':(0x44129e,3),'audio_uart_page_44131c':(0x44131c,3),'audio_terminal_query_four_margins_5eb2bc':(0x5eb2bc,3),'audio_uart_page_441262':(0x441262,3),'audio_uart_page_499416':(0x499416,1),'audio_uart_page_43f506':(0x43f506,2),'audio_uart_page_49942e':(0x49942e,2),'audio_uart_page_layout_499678':(0x499678,2),'audio_uart_page_44104c':(0x44104c,1),'audio_uart_page_44140e':(0x44140e,3),'audio_uart_page_44145a':(0x44145a,3),'audio_uart_page_44143e':(0x44143e,3),'audio_uart_page_441270':(0x441270,3),'audio_uart_page_498668':(0x498668,1),'audio_uart_page_498680':(0x498680,2),'audio_uart_page_43ded4':(0x43ded4,2),'audio_uart_page_43f66c':(0x43f66c,1),'audio_terminal_display_status_44ea04':(0x44ea04,3),'audio_terminal_query_items_style_5eb3c6':(0x5eb3c6,1),'audio_terminal_counter_b_get_5973dc':(0x5973dc,0),'audio_terminal_ui_event_5e5484':(0x5e5484,3)}
BY_ADDR={v[0]:(k,v[1]) for k,v in SPECS.items()}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_terminal_ui_state_base':STATE,'audio_terminal_display_queue_handle':0x20074a90,'audio_uart_ring_secondary_head_cell':0x200746e0,'audio_terminal_result_icon_773258':0x773258};defs.update({k:v[0]|1 for k,v in SPECS.items()})
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,queue,existing,count,td_present,prev):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x110000);u.mem_write(0x20074a90,struct.pack('<I',queue));u.mem_write(0x200746e0,struct.pack('<I',0x200b0000))
  u.mem_write(STATE,bytes((i*7+11)&255 for i in range(0x2a0)));u.mem_write(STATE,struct.pack('<I',prev));u.mem_write(STATE+0x214,struct.pack('<I',existing))
  td=0x20090000;u.mem_write(td+0x406,struct.pack('<H',count));u.mem_write(td+6,b'Question?\0');
  for i in range(count):u.mem_write(td+0x40e+i*0x88,(f'Option {i}'.encode()+b'\0'))
  u.reg_write(A.UC_ARM_REG_SP,0x2010f000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  trace=[];panel_n=0;label_n=0
  def cstr(cpu,p):return bytes(cpu.mem_read(p,160)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   nonlocal panel_n,label_n
   if pc not in BY_ADDR:return
   name,n=BY_ADDR[pc];r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)];args=tuple(r[:n]);v=0
   if pc==0x49942e:args=(r[0],cstr(cpu,r[1]))
   trace.append((name,args))
   if pc==0x59731e:v=td if td_present else 0
   elif pc==0x5e4f54:v=0x200a0000
   elif pc==0x43de82:v=0x200a1000+panel_n*0x1000;panel_n+=1
   elif pc==0x499416:v=0x200a4000+label_n*0x100;label_n+=1
   elif pc==0x498668:v=0x200a3000
   elif pc==0x44104c:v=r[0]^0x1234
   elif pc==0x5973dc:v=0x1357
   cpu.reg_write(A.UC_ARM_REG_R0,v);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_query_construct_5eb8da'] if compiled else 0x5eb8da)|1,0x600000,count=1200)
  return trace,bytes(u.mem_read(STATE,0x2a0)),u.reg_read(A.UC_ARM_REG_R0)
 cases=list(itertools.product((0,0x200b0000),(0,0x200a0000),(0,1,2),(False,True),(0,0x200c0000)))
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock[:2]!=source[:2]:
   for j,(a,b) in enumerate(itertools.zip_longest(stock[0],source[0])):
    if a!=b:print('first trace difference',j,a,b);break
   print('mismatch',i,args,'lengths',len(stock[0]),len(source[0]),'return',stock[2],source[2],'state_equal',stock[1]==source[1]);raise RuntimeError('query-constructor mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_CONSTRUCT_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Precondition gates, object creation order, style calls, title/option row text, RAM state writes and event','limits':['LVGL/nanopb/TD provider effects are isolated; mutable tree behavior, final RAM placement and hardware remain open.']}
 p=OUT/'oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(p))
if __name__=='__main__':main()
