from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-font-prepare-metrics-round253';F=0x20001000;M=0x20002000;CUT=0x180000
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
source=D/('original.c' if '--original' in sys.argv else 'candidate.c')
if '--selected' in sys.argv:
 t=(R/'components/audio/uart_thread_source_candidate/display_font_face_metrics.c').read_text();body=t[t.index('void audio_uart_font_prepare_metrics(void *face,void *metrics) {'):t.index('\nvoid audio_uart_font_request_size_metrics')];assert body in source.read_text()
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_font_prepare_metrics','-Wl,--defsym=audio_uart_font_scale_metric='+hex(CUT|1),str(source),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,seed,mutate,result):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(F,bytes(128));u.mem_write(M,bytes([0x5a])*64);u.mem_write(M+4,W(seed));u.mem_write(M+8,W(seed^0x80000000))
  for n,v in enumerate([0x7fff,0x8000,0xffff,0]):u.mem_write(F+0x46+n*2,struct.pack('<H',v))
  events=[]
  def hook(u,a,size,data):
   if a==(CUT if isc else 0x5246f8):
    i=len(events);events.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
    if mutate:
     u.mem_write(M+4,W(seed+(i+1)*17));u.mem_write(M+8,W(seed+(i+1)*31));u.mem_write(F+0x46+((i+1)%4)*2,struct.pack('<H',(seed+i)&65535))
    u.reg_write(UC_ARM_REG_R0,(result+i*63)&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,F);u.reg_write(UC_ARM_REG_R1,M);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_font_prepare_metrics'] if isc else 0x526a4e)|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,bytes(u.mem_read(F,128)).hex(),bytes(u.mem_read(M,64)).hex(),u.reg_read(UC_ARM_REG_SP)
 cases=list(itertools.product([0,1,0x80000000,0xffffffff],[0,1],[0,1,31,32,63,64,0x7fffffff,0x80000000,0xffffffff]))
 for c in cases:
  n=run(False,*c);a=run(True,*c)
  if n!=a:
   (D/'original-mismatch.json').write_text(json.dumps({'case':c,'native':n,'original':a},indent=2)+'\n');assert '--original' in sys.argv;print('EXPECTED_ORIGINAL_MISMATCH');sys.exit(0)
 assert '--original' not in sys.argv
 receipt={'status':'PASS_NATIVE_PREPARE_METRICS_CONTROLLED_CHILD','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'child_cuts':1,'limits':['Full face/metrics state, child argument order and SP matched with controlled scale results and child mutations. Real scale graph,ordered memory bus,pointer faults,ownership/full-font/full-image remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
