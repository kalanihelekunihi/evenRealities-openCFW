from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-bmp-round153';S=D/'candidate.c';W=lambda *v:struct.pack('<'+'I'*len(v),*v);P=0x20001000;H=0x20002000
if '--selected' in sys.argv:S=R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c'
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf'
 if '--selected' in sys.argv:
  selected=S.read_text();prefix=(D/'candidate.c').read_text().split('/* Native4c91e0')[0];fixture=Path(t)/'selected-info.c';fixture.write_text(prefix+selected[selected.index('/* Native4c91e0'):]);S=fixture
 names=['audio_uart_lv_fs_extension_4c70e4','audio_uart_lv_string_compare_4547be','audio_uart_lv_fs_file_read_4c6f46','audio_uart_lv_grid_copy_454738','audio_uart_lvgl_log'];defs={n:0x101011+i*16 for i,n in enumerate(names)}
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_bmp_info_4c91e0',*[f'-Wl,--defsym={k}={v}' for k,v in defs.items()],str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,typ,ext,bpp,width,height,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,W(*[seed]*32));u.mem_write(P+12,W(0x20003000));u.mem_write(P+16,bytes([typ]));u.mem_write(H,W(*[seed]*8));u.mem_write(0x20003000,b'image.bmp\0');u.mem_write(0x20003100,b'bmp\0');events=[]
  ops=['ext','compare','read','copy','log'];cuts=dict(zip([0x101010+i*16 for i in range(5)] if isc else [0x4c70e4,0x4547be,0x4c6f46,0x454738,0x44d25c],ops))
  def string(a):return bytes(u.mem_read(a,220)).split(b'\0',1)[0].decode('ascii')
  def hook(uc,a,n,user):
   if a not in cuts:return
   op=cuts[a];r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0
   if op=='ext':events.append((op,string(r[0])));ret=0x20003100
   elif op=='compare':events.append((op,string(r[0]),string(r[1])));ret=ext
   elif op=='read':
    events.append((op,r[0],r[2],r[3]));data=bytearray(54);struct.pack_into('<II',data,18,width,height);struct.pack_into('<H',data,28,bpp);uc.mem_write(r[1],bytes(data));ret=7
   elif op=='copy':
    data=bytes(uc.mem_read(r[1],r[2]));events.append((op,data.hex(),bytes(uc.mem_read(H,32)).hex()));uc.mem_write(r[0],data);ret=r[0]
   else:
    stack=struct.unpack('<II',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8));events.append((op,r[0],string(r[1]),r[2],string(r[3]),string(stack[0]),stack[1]))
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33)
  for reg,v in [(UC_ARM_REG_R0,0),(UC_ARM_REG_R1,P),(UC_ARM_REG_R2,H),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(reg,v)
  u.emu_start((sym['audio_uart_lv_bmp_info_4c91e0'] if isc else 0x4c91e0)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(H,32)),bytes(u.mem_read(P,128))
 count=0
 for typ,ext,bpp,dimensions,seed in itertools.product([0,1,2,255],[0,1],[0,16,24,32,65535],[(0,0),(1,2),(0x12345678,0xfedcba98),(0xffffffff,0xffffffff)],[0,0xa5a5a5a5,0xffffffff]):
  a=run(False,typ,ext,bpp,*dimensions,seed);b=run(True,typ,ext,bpp,*dimensions,seed);assert a==b,(typ,ext,bpp,dimensions,seed,a,b);count+=1
 receipt={'status':'PASS_NATIVE_BMP_INFO','cases':count,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Extension/compare/read/copy/logger controlled cuts; source type,packed dimensions,colorformat,unsupported depth logging,copy-entry header snapshots and return/SP compared.','Full54-byte read supplied despite controlled nonzero read status; partial/failed read contents unproved. Open/get-area and fullimage gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
