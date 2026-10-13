from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-nema-texture-bind-round243';S=D/'candidate.c';P=0x20001000;CTX=0x20002000;CELL=0x20074efc
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_nema_cl_get_space_514aec'];native=[0x514aec];cuts=[0x101030]
entries=['audio_uart_nema_bind_tex_4b1298'];orig=[0x4b1298]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  text=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=text.index('static uint32_t bind243_align4');z=text.find('\n#include',a);S=Path(t)/'selected.c';S.write_text((D/'candidate.c').read_text().split('static uint32_t bind243_align4')[0]+text[a:z if z>=0 else len(text)])
 selected_text=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text()
 a=selected_text.index('/* Native52262e');z=selected_text.index('\n#include',a);h=selected_text[a:z]
 a=selected_text.index('/* Native52264e');z=selected_text.find('\n#include',a);h+=selected_text[a:z if z>=0 else len(selected_text)]
 helpers=Path(t)/'helpers.c';helpers.write_text('#include <stdint.h>\nextern volatile uint32_t audio_uart_nema_context_cell[];\n'+h)
 e=Path(t)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_nema_context_cell='+hex(CELL)]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),str(helpers),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,unit,width,fmt,stride,flags,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes([165])*96);u.mem_write(CTX,bytes([165])*2048);u.mem_write(CELL,W(CTX));u.mem_write(CTX+9,bytes([0x81]));events=[]
  def hook(uc,a,n,user):
   addresses=cuts if isc else native
   if a not in addresses:return
   k=2;arg=uc.reg_read(UC_ARM_REG_R0);events.append([k,arg])
   if mutation and k<2:uc.mem_write(CELL,W(CTX+1024))
   if k==2:
    if mutation==2:uc.mem_write(CELL,W(CTX+1024));uc.mem_write(CTX+1024+unit*24+68,W(0x87654321))
    uc.reg_write(UC_ARM_REG_R0,0 if mutation==3 else P)
   else:uc.reg_write(UC_ARM_REG_R0,0xa5a5a5a5)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33)
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[unit,0x20009003,width,0x87654321]):u.reg_write(reg,val)
  sp=0x200ff000;u.mem_write(sp,b''.join(W(v) for v in [fmt,stride,flags]));u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym[entries[0]] if isc else orig[0])|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,bytes(u.mem_read(P,96)).hex(),bytes(u.mem_read(CTX,2048)).hex(),bytes(u.mem_read(CELL,4)).hex(),u.reg_read(UC_ARM_REG_SP)
 cases=list(itertools.product([0,1],[0,7,0x80000000,0xffffffff],range(128),[0xffffffff,17],[0,16],[0,2]))
 cases += list(itertools.product([0,1,7,0xffffffff],[0x7fffffff],[0,18,22,76,77,78,255,0xffffffff],[0xffffffff,0x80000000],[0xffffffff],range(4)))
 for c in cases:
  a=run(False,*c);z=run(True,*c)
  if a!=z:(D/'tiling-connected-mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':z},indent=2));raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_TEXTURE_BIND_REAL_TILING_HELPERS','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'selected_helpers_sha256':hashlib.sha256(helpers.read_bytes()).hexdigest(),'limits':['All128 masked formats/default andexplicit stride,wrapped signed widths/flags,context reload mutations,packet NULL/fullstate/events/SP matched. Both tiling providers are actual native/selected C; command-space contract controlled; exact bus,pointer faults/ownership/physical GPU/full-image remain.']};(D/'tiling-connected-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
