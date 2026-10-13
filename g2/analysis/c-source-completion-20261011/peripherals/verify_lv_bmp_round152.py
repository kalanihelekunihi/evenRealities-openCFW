from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-bmp-round152';S=D/'candidate.c';W=lambda *v:struct.pack('<'+'I'*len(v),*v);P=0x20001000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf'
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native 4c94a8..4c94c6');prefix=(D/'candidate.c').read_text().split('/* Native 4c94a8')[0];body=selected[a:selected.index('#include <stdint.h>',a)];fixture=Path(t)/'selected-registration-close.c';fixture.write_text(prefix+body);S=fixture
 defs={'audio_uart_lv_image_decoder_create_4890c8':0x101011,'audio_uart_lv_bmp_info_4c91e0':0x4c91e1,'audio_uart_lv_bmp_open_4c92a8':0x4c92a9,'audio_uart_lv_bmp_get_area_4c93a0':0x4c93a1,'audio_uart_lv_fs_file_close_4c6ee0':0x101021,'audio_uart_lv_heap_free':0x101031,'audio_uart_font_bitmap_release':0x101041}
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_init_assert_4c91a8',*[f'-Wl,--defsym={k}={v}' for k,v in defs.items()],str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,op,seed,allocated,bitmap,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,W(*[seed]*32));u.mem_write(P+72,W(allocated));u.mem_write(P+44,W(bitmap));events=[]
  cuts=({0x101010:'create',0x101020:'close',0x101030:'free',0x101040:'release'} if isc else {0x4890c8:'create',0x4c6ee0:'close',0x44f758:'free',0x48b216:'release'})
  def hook(uc,a,n,user):
   if a not in cuts:return
   kind=cuts[a];arg=uc.reg_read(UC_ARM_REG_R0);events.append((kind,arg if kind!='create' else None))
   if kind=='close' and mutation:uc.mem_write(P+72,W(0x20008000))
   if kind=='free' and mutation:uc.mem_write(P+44,W(0 if mutation==1 else 0x20009000))
   uc.reg_write(UC_ARM_REG_R0,allocated if kind=='create' else 0x12345678);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33)
  for reg,v in [(UC_ARM_REG_R0,0x12345679),(UC_ARM_REG_R1,P),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(reg,v)
  fault=None
  try:u.emu_start((sym['audio_uart_lv_init_assert_4c91a8' if op=='init' else 'audio_uart_lv_bmp_close_4c94a8'] if isc else 0x4c91a8 if op=='init' else 0x4c94a8)|1,0x600000,count=1000)
  except UcError as ex:fault=ex.errno
  if fault is None:assert u.reg_read(UC_ARM_REG_PC)==0x600000
  data=bytearray(u.mem_read(P,128));name=None
  if op=='init' and allocated:
   ptr=struct.unpack_from('<I',data,20)[0];name=bytes(u.mem_read(ptr,4));assert name==b'BMP\0'
   closeptr=struct.unpack_from('<I',data,12)[0];assert closeptr==(sym['audio_uart_lv_bmp_close_4c94a8'] if isc else 0x4c94a9)
   struct.pack_into('<I',data,12,0x4c94a9);struct.pack_into('<I',data,20,0)
  return events,fault,u.reg_read(UC_ARM_REG_SP) if fault is None else None,bytes(data),name
 count=0
 for op,seed,allocated,bitmap,mutation in itertools.product(['init','close'],[0,0xa5a5a5a5,0xffffffff],[0,P],[0,0x20006000],[0,1,2]):
  a=run(False,op,seed,allocated,bitmap,mutation);b=run(True,op,seed,allocated,bitmap,mutation);assert a==b,(op,seed,allocated,bitmap,mutation,a,b);count+=1
 receipt={'status':'PASS_NATIVE_BMP_REGISTRATION_CLOSE','cases':count,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Create/fs-close/free/bitmap release controlled cuts; full128 descriptor bytes and ordered calls/SP/fault compared.','Function pointer relocation normalized to authenticated native identity; BMP name compared by bytes. Other BMP callbacks and full-image gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
