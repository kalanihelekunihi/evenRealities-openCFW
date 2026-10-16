#!/usr/bin/env python3
"""Compare result-area constructor calls and state writes with stock Thumb."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_ui_result_area_prepare_5ebff8.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-result-area-5ebff8'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';STATE=0x2006e0d0;FONT=0x200746e0;ICON=0x773258
CALLS={'audio_uart_page_44122a':0x44122a,'audio_uart_page_441238':0x441238,'audio_uart_page_44120e':0x44120e,'audio_uart_page_441246':0x441246,'audio_uart_page_43f506':0x43f506,'audio_uart_page_44d878':0x44d878,'audio_uart_page_441270':0x441270,'audio_uart_page_43f568':0x43f568,'audio_uart_page_498668':0x498668,'audio_uart_page_498680':0x498680,'audio_uart_page_43ded4':0x43ded4,'audio_uart_page_4411e4':0x4411e4,'audio_uart_page_499416':0x499416,'audio_uart_page_43f09a':0x43f09a,'audio_uart_page_49942e':0x49942e,'audio_uart_page_44104c':0x44104c,'audio_uart_page_44140e':0x44140e,'audio_uart_page_44143e':0x44143e,'audio_uart_page_44e3ca':0x44e3ca,'audio_uart_page_44e368':0x44e368,'audio_uart_page_43f66c':0x43f66c,'audio_terminal_status_apply_layout_5ebc9e':0x5ebc9e,'audio_uart_lv_scroll_bottom_44e4bc':0x44e4bc,'audio_uart_lv_scroll_dispatch_44e884':0x44e884}
BY_ADDR={v:k for k,v in CALLS.items()};ARGS={0x44d878:1,0x498668:1,0x498680:2,0x43ded4:2,0x499416:1,0x44104c:1,0x44e3ca:2,0x44e368:2,0x43f66c:1,0x5ebc9e:2,0x44e4bc:1,0x44e884:4,0x43f506:2,0x43f568:2}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:]
 if hashlib.sha256(blob).hexdigest()!=PIN:raise RuntimeError('payload changed')
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_terminal_ui_state_base':STATE,'audio_uart_ring_secondary_head_cell':FONT,'audio_terminal_result_icon_773258':ICON};defs.update({k:v|1 for k,v in CALLS.items()})
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,missing,font_height,bottom):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in segments:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(STATE,bytes((i*13+7)&255 for i in range(0x2a0)))
  for i,off in enumerate((0x1f4,0x1fc,0x200)):
   u.mem_write(STATE+off,struct.pack('<I',0 if i==missing else 0x20081000+i*0x1000))
  u.mem_write(FONT,struct.pack('<I',0x20075000));u.mem_write(0x2007500c,struct.pack('<I',font_height))
  u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  trace=[];label_index=0
  def cstr(cpu,p):return bytes(cpu.mem_read(p,100)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   nonlocal label_index
   if pc not in BY_ADDR:return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   args=(r[0],cstr(cpu,r[1])) if pc==0x49942e else tuple(r[:ARGS.get(pc,3)])
   trace.append((BY_ADDR[pc],args));value=0
   if pc==0x498668:value=0x20085000
   elif pc==0x499416:label_index+=1;value=0x20086000+label_index*0x1000
   elif pc==0x44104c:value=r[0]^0x12345678
   elif pc==0x44e4bc:value=bottom&0xffffffff
   cpu.reg_write(A.UC_ARM_REG_R0,value);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_ui_result_area_prepare_5ebff8'] if compiled else 0x5ebff8)|1,0x600000,count=650)
  return trace,bytes(u.mem_read(STATE,0x2a0))
 cases=list(itertools.product((-1,0,1,2),(0,16,20,255),(0,10,-3)))
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock!=source:
   print('mismatch',i,args,'stock',stock[0],'source',source[0]);print('state diff',[(j,a,b) for j,(a,b) in enumerate(zip(stock[1],source[1])) if a!=b][:16]);raise RuntimeError('result area mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_RESULT_AREA_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Three-object gate, font-derived height, icon/two-label call order, state writes and scroll-bottom branch','limits':['Lower LVGL effects isolated; result icon exact bytes checked separately; final RAM/layout and hardware remain open.']}
 p=OUT/'oracle-receipt.json';p.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(p))
if __name__=='__main__':main()
