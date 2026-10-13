from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-font-size-arithmetic-round251';S=D/'candidate.c';P=0x20001000;CTX=0x20002000;CELL=0x20074efc
W=lambda x:struct.pack('<I',x&0xffffffff)
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['__aeabi_ldivmod'];native=[];cuts=[0x101010]
entries=['audio_uart_font_request_size_internal'];orig=[0x526944]
with tempfile.TemporaryDirectory() as t:
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_font_face_size.c').read_text();marker='int32_t audio_uart_font_request_size_internal(void *face';body=marker+selected.split(marker,1)[1];assert body==marker+(D/'candidate.c').read_text().split(marker,1)[1];S=Path(t)/'candidate.c';S.write_text((D/'candidate.c').read_text().split(marker,1)[0]+body)
 compiled={}
 for source in [D/'original.c',S]:
  e=Path(t)/(source.name+'.elf');subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,'+entries[0],'-Wl,--defsym=audio_uart_nema_context_cell='+hex(CELL)]+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(source),'-o',str(e)],check=True)
  with e.open('rb') as f:
   elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
  compiled[source.name]=(segs,sym)
 def run(kind,x,y,dx,dy,count,ignore,index,face_flags=2,request_type=0):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  if kind!='native':
   segs,sym=compiled[kind]
   for a,data in segs:u.mem_write(a,data)
  request=CTX;strikes=CTX+512;idx=CTX+1024
  u.mem_write(P,bytes(96));u.mem_write(P+8,W(face_flags));u.mem_write(P+28,W(count));u.mem_write(P+32,W(strikes));u.mem_write(request,b''.join(W(v) for v in [request_type,x,y,dx,dy]));u.mem_write(strikes,b''.join(W(v) for v in [0,0,x,y,0,0,64,64]));u.mem_write(idx,W(0xa5a5a5a5))
  def hook(uc,a,n,user):
   if a!=cuts[0]:return
   vals=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];n=vals[0]|vals[1]<<32;d=vals[2]|vals[3]<<32
   n=n-(1<<64) if n>>63 else n;d=d-(1<<64) if d>>63 else d;assert d==72
   q=abs(n)//abs(d);q=-q if (n<0)!=(d<0) else q;r=n-q*d
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[q&0xffffffff,(q>>32)&0xffffffff,r&0xffffffff,(r>>32)&0xffffffff]):uc.reg_write(reg,value)
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33)
  for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[P,request,ignore,idx if index else 0]):u.reg_write(reg,val)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((orig[0] if kind=='native' else sym[entries[0]])|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(idx,4)).hex(),u.reg_read(UC_ARM_REG_SP)
 baseline=(0x40000000,64,72,0,1,0,1);a=run('native',*baseline);z=run('original.c',*baseline);assert a!=z;(D/'original-mismatch.json').write_text(json.dumps({'case':baseline,'native':a,'original':z},indent=2)+'\n')
 cases=list(itertools.product([0,64,1024,0x40000000,0xffffffff],[0,64,1024,0x40000000,0xffffffff],[0,72,96,0x80000000,0xffffffff],[0,72,96,0x80000000,0xffffffff],[0,1,2,0xffffffff],[0,1,256],range(2)))
 if '--gates-only' in sys.argv:cases=[(64,64,72,72,c,0,i,f,t) for c,i,f,t in itertools.product([0,1,0xffffffff],range(2),[0,1,2,255],[0,1,4,255])]
 for c in cases:
  a=run('native',*c);z=run('candidate.c',*c)
  if a!=z:(D/'mismatch.json').write_text(json.dumps({'case':c,'native':a,'source':z},indent=2));raise AssertionError(c)
 receipt={'status':'PASS_NATIVE_FONT_SIZE_ARITHMETIC_CORRECTION','cases':len(cases),'gates_only':'--gates-only' in sys.argv,'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Native wrapped32bit DPI product/signedcount/lowbyteignore,return/index/SP match. Original wide source mismatch retained; ABI helper hook used only original-baseline quotient/remainder fixture. Flags/type gates,ordered bus,concurrency,pointerfaults/full-image remain.']};(D/('gates-receipt.json' if '--gates-only' in sys.argv else 'receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
