#!/usr/bin/env python3
"""Compare voice page constructor call/state contract with pinned Apollo Main."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/terminal_ui_voice_prepare_5ebd0e.c'
OUT=G2/'build/c-firmware/20261016/main-terminal-ui-voice-prepare-5ebd0e'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
STATE=0x2006e0d0;QUEUE=0x20074a90;FONT=0x200746e0;STYLE=0x200014e8
CALLS={'audio_lv_style_opa_441488':0x441488,'audio_terminal_query_root_5e4f54':0x5e4f54,'audio_uart_page_43f4c0':0x43f4c0,'audio_uart_page_44119c':0x44119c,'audio_uart_page_4411aa':0x4411aa,'audio_terminal_ui_margins_5ebc5c':0x5ebc5c,'audio_uart_page_48ba78':0x48ba78,'audio_uart_page_48ba92':0x48ba92,'audio_uart_page_44120e':0x44120e,'audio_uart_page_44122a':0x44122a,'audio_uart_page_441238':0x441238,'audio_uart_page_441246':0x441246,'audio_uart_page_43ded4':0x43ded4,'audio_uart_page_44e3ca':0x44e3ca,'audio_uart_page_44e368':0x44e368,'audio_uart_page_43de82':0x43de82,'audio_uart_page_43dfa4':0x43dfa4,'audio_uart_page_44129e':0x44129e,'audio_uart_page_44131c':0x44131c,'audio_uart_page_441254':0x441254,'audio_terminal_voice_anim_create_597e90':0x597e90,'audio_uart_page_4411e4':0x4411e4,'audio_terminal_set_label_style_5e482a':0x5e482a,'audio_uart_page_499416':0x499416,'audio_uart_page_layout_499678':0x499678,'audio_uart_page_49942e':0x49942e,'audio_uart_page_44104c':0x44104c,'audio_uart_page_44140e':0x44140e,'audio_uart_page_44143e':0x44143e,'audio_uart_page_4412ec':0x4412ec,'audio_uart_page_44132a':0x44132a,'audio_uart_page_44146a':0x44146a,'audio_uart_page_441270':0x441270,'audio_uart_page_43f6b8':0x43f6b8,'audio_terminal_counter_b_get_5973dc':0x5973dc,'audio_terminal_ui_event_5e5484':0x5e5484}
BY_ADDR={v:k for k,v in CALLS.items()}
ARGS={0x5e4f54:2,0x48ba78:2,0x48ba92:4,0x43ded4:2,0x44e3ca:2,0x44e368:2,0x43de82:1,0x43dfa4:2,0x597e90:1,0x5e482a:4,0x499416:1,0x499678:2,0x44104c:1,0x43f6b8:4,0x5973dc:0,0x5e5484:3}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 defs={'audio_terminal_ui_state_base':STATE,'audio_terminal_display_queue_handle':QUEUE,'audio_uart_ring_secondary_head_cell':FONT,'audio_terminal_voice_style_200014e8':STYLE};defs.update({k:v|1 for k,v in CALLS.items()})
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={k}=0x{v:x}' for k,v in defs.items()],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,queue,existing,previous,font):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000);u.mem_write(STATE,bytes((i*11+5)&255 for i in range(0x2a0)))
  u.mem_write(STATE,struct.pack('<I',0x20080000 if previous else 0))
  u.mem_write(STATE+0x1f4,struct.pack('<I',0x20088000 if existing else 0))
  u.mem_write(QUEUE,struct.pack('<I',0x20070000 if queue else 0));u.mem_write(FONT,struct.pack('<I',font))
  u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  trace=[];page_idx=0;label_idx=0
  def cstr(cpu,p):return bytes(cpu.mem_read(p,100)).split(b'\0',1)[0]
  def hook(cpu,pc,size,_):
   nonlocal page_idx,label_idx
   if pc not in BY_ADDR:return
   r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
   if pc==0x49942e:args=(r[0],cstr(cpu,r[1]))
   else:args=tuple(r[:ARGS.get(pc,3)])
   trace.append((BY_ADDR[pc],args));value=0
   if pc==0x5e4f54:value=0x20081000
   elif pc==0x43de82:page_idx+=1;value=0x20082000+page_idx*0x1000
   elif pc==0x597e90:value=0x20085000
   elif pc==0x499416:label_idx+=1;value=0x20085000+label_idx*0x1000
   elif pc==0x44104c:value=r[0]^0x12345678
   elif pc==0x5973dc:value=0x1357
   cpu.reg_write(A.UC_ARM_REG_R0,value);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((sym['audio_terminal_ui_voice_prepare_5ebd0e'] if compiled else 0x5ebd0e)|1,0x600000,count=800)
  return trace,bytes(u.mem_read(STATE,0x2a0))
 cases=list(itertools.product((0,1),(0,1),(0,1),(0,0x20077700)))
 for i,args in enumerate(cases):
  stock=run(False,*args);source=run(True,*args)
  if stock!=source:
   print('mismatch',i,args,'stock trace',stock[0],'source trace',source[0]);print('state diff',[(j,a,b) for j,(a,b) in enumerate(zip(stock[1],source[1])) if a!=b][:16]);raise RuntimeError('voice prepare mismatch')
 receipt={'status':'PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_PREPARE_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Queue/existing early exits, prior-object opacity, complete root/panel/animation/labels call sequence, state writes and event','limits':['LVGL, animation and event lower effects isolated; style RAM 0x200014e8 and final object/RAM layout remain open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(receipt['status'],len(cases),sha(path))
if __name__=='__main__':main()
