from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-font-select-metrics-full-graph-round261';F=0x20001000;M=0x20002000;Q=0x20003000
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_font_divide_metric','audio_uart_font_mul_div','audio_uart_font_scale_metric','audio_uart_font_prepare_metrics','audio_uart_buffer_zero'];native=[0x524754,0x524606,0x5246f8,0x526a4e,0x43c0e4];cuts=[0x180000+i*16 for i in range(5)]
source=B/'root-font-select-metrics-round257/candidate.c'
D.mkdir(exist_ok=True)
selected=R/'components/audio/uart_thread_source_candidate/display_font_face_metrics.c'
text=selected.read_text();prep=text[text.index('void audio_uart_font_prepare_metrics(void *face,void *metrics) {'):text.index('void audio_uart_font_request_size_metrics')]
helper=D/'prepare-fixture.c';helper.write_text('#include <stdint.h>\nextern int32_t audio_uart_font_scale_metric(uint32_t,int32_t);\nstatic uint32_t word(const void *p,uint32_t o){return *(const uint32_t*)((const uint8_t*)p+o); }\n'+prep)
scale=R/'components/audio/uart_thread_source_candidate/display_font_metric_scale.c'
math=R/'components/audio/uart_thread_source_candidate/display_font_math.c'
division=R/'components/audio/uart_power_config_offline/division_support.c'
if '--selected' in sys.argv:
 t=(R/'components/audio/uart_thread_source_candidate/display_font_face_metrics.c').read_text();assert t[t.index('void audio_uart_font_select_size_metrics'):t.index('void audio_uart_font_prepare_metrics(void *face,void *metrics) {')].strip() in source.read_text()
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_font_select_size_metrics']+[str(source),str(helper),str(scale),str(math),str(division),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,typ,flag,upm,x,y,dpi,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(F,bytes(128));u.mem_write(M,bytes([0x5a])*64);u.mem_write(F+8,bytes([flag]));u.mem_write(F+88,W(M-12));u.mem_write(F+52,W(0x80000000));u.mem_write(F+56,W(0xffffffff));u.mem_write(F+60,W(0));u.mem_write(F+64,W(0x7fffffff));u.mem_write(F+68,struct.pack('<HHHHH',upm,0x7fff,0x8000,0xffff,0x8000));u.mem_write(F+32,W(Q));u.mem_write(Q,bytes(64));u.mem_write(Q+typ*16,struct.pack('<H',dpi&65535));u.mem_write(Q+typ*16+8,W(x));u.mem_write(Q+typ*16+12,W(y));events=[]
  u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,F);u.reg_write(UC_ARM_REG_R1,typ);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_font_select_size_metrics'] if isc else 0x526a9c)|1,0x600000,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,bytes(u.mem_read(F,128)).hex(),bytes(u.mem_read(M,64)).hex(),bytes(u.mem_read(Q,64)).hex(),u.reg_read(UC_ARM_REG_SP)
 cases=itertools.product([0,1,2],[0,1],[0,0x7fff,0x8000,0xffff],[0,64,0x40000000,0x80000000],[0,64,0x80000000,0xffffffff],[0,0x8000,0xffff],[0]);count=0
 for c in cases:
  n=run(False,*c);a=run(True,*c)
  if n!=a:
   (D/('original-mismatch.json' if '--original' in sys.argv else 'candidate-mismatch.json')).write_text(json.dumps({'case':c,'native':n,'candidate':a},indent=2)+'\n')
   assert '--original' in sys.argv, c
   print('EXPECTED_ORIGINAL_MISMATCH',c);sys.exit(0)
  count+=1
 assert '--original' not in sys.argv
 receipt={'status':'PASS_NATIVE_SELECT_METRICS_FULL_ARITHMETIC_GRAPH','cases':count,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'child_cuts':0,'selected_helper_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [selected,scale,math,division]},'limits':['Full native/C select/preparation/scale/divide graph with selected complete unsigned division ABI and no child cuts; full face/metrics/three-strike state/SP matched. Ordered bus,pointerfault,concurrency/ownership/layout/hardware remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
