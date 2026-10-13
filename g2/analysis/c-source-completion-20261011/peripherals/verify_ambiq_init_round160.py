from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-init-round160';S=D/'candidate.c';W=lambda *v:struct.pack('<'+'I'*len(v),*v);CELL=0x200746c0;UNIT=0x20001000;ALT=0x20002000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
names=['audio_uart_ambiq_buffer_handlers_53d5da','audio_uart_lv_draw_unit_create_484398','audio_uart_display_surface_alloc','audio_uart_nema_vg_path_create_514ebc','audio_uart_nema_vg_paint_create_515096','audio_uart_nema_vg_grad_create_51510e','audio_uart_lv_basic_box_clear_454746','audio_uart_nema_cl_create_sized_514278','audio_uart_checksum_copy','audio_uart_lvgl_log','audio_uart_ambiq_vector_font_init_53d6da','audio_uart_lv_async_init_4d465c','audio_uart_lv_thread_init_4d4610']
ops=['handlers','unit','texture','path','paint','grad','clear','cl','copy','log','vector','mutex','thread'];native=[0x53d5da,0x484398,0x48affa,0x514ebc,0x515096,0x51510e,0x454746,0x514278,0x439c04,0x44d25c,0x53d6da,0x4d465c,0x4d4610]
with tempfile.TemporaryDirectory() as t:
 e=Path(t)/'test.elf'
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('static volatile uint32_t *ambiq_unit(void)');prefix=S.read_text().split('static volatile uint32_t *ambiq_unit(void)')[0];fixture=Path(t)/'selected-init.c';fixture.write_text(prefix+selected[a:]);S=fixture
 defs={n:0x101011+i*16 for i,n in enumerate(names)};defs.update({'audio_uart_ambiq_unit_cell':CELL,'audio_uart_ambiq_dispatch_4c76a8':0x4c76a9,'audio_uart_ambiq_evaluate_4c7548':0x4c7549,'audio_uart_ambiq_delete_4c74f0':0x4c74f1,'audio_uart_ambiq_render_thread_4c7700':0x4c7701})
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_init_group_4c73d6',*[f'-Wl,--defsym={k}={v}' for k,v in defs.items()],str(S),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,allocated,good,mutation,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  for a in [UNIT,ALT]:u.mem_write(a,W(*[seed]*64))
  u.mem_write(CELL,W(ALT));events=[];cuts=dict(zip([0x101010+i*16 for i in range(len(ops))] if isc else native,ops))
  def string(a):return bytes(u.mem_read(a,220)).split(b'\0',1)[0].decode('ascii')
  def dump(a):
   data=bytearray(u.mem_read(a,256));ptr=struct.unpack_from('<I',data,4)[0]
   if ptr==(sym['ambiq_name'] if isc else 0x78d8e4):assert string(ptr)=='AMBIQ';struct.pack_into('<I',data,4,0)
   return data.hex()
  def hook(uc,a,n,user):
   if a not in cuts:return
   op=cuts[a];r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0x12345678
   snap=(dump(UNIT),dump(ALT))
   if op=='unit':events.append((op,r[0],snap));ret=UNIT if allocated else 0
   elif op in ['texture','path','paint','grad']:events.append((op,tuple(r) if op=='texture' else (),snap));ret=0x20008000+ops.index(op)*16
   elif op=='clear':events.append((op,*r[:3],snap));uc.mem_write(r[0],bytes([r[1]&255])*r[2])
   elif op=='cl':
    events.append((op,r[1],snap));data=[0x100+i for i in range(15)];data[2]=0x20009000 if good else 0;uc.mem_write(r[0],W(*data))
   elif op=='copy':events.append((op,r[0],r[2],snap));uc.mem_write(r[0],bytes(uc.mem_read(r[1],r[2])))
   elif op=='log':
    stack=struct.unpack('<III',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),12));events.append((op,r[0],string(r[1]),r[2],string(r[3]),*[string(v) for v in stack],snap))
   elif op=='thread':
    stack=struct.unpack('<II',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8));events.append((op,r[0],string(r[1]),r[2],r[3],*stack,snap))
   else:events.append((op,r[0] if op in ['vector','mutex'] else None,snap))
   if op=={1:'texture',2:'path',3:'clear',4:'cl',5:'vector',6:'mutex'}.get(mutation):uc.mem_write(CELL,W(ALT))
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);fault=None
  try:u.emu_start((sym['audio_uart_lv_init_group_4c73d6'] if isc else 0x4c73d6)|1,0x600000,count=2000)
  except UcError as ex:fault=ex.errno
  if fault is None:assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,fault,u.reg_read(UC_ARM_REG_SP) if fault is None else None,dump(UNIT),dump(ALT),bytes(u.mem_read(CELL,4))
 count=0
 for allocated,good,mutation,seed in itertools.product([0,1],[0,1],range(7),[0,0xa5a5a5a5,0xffffffff]):
  a=run(False,allocated,good,mutation,seed);b=run(True,allocated,good,mutation,seed);
  if a!=b:
   diff=[(i,x,y) for i,(x,y) in enumerate(zip(a[0],b[0])) if x!=y];(D/'mismatch.json').write_text(json.dumps({'case':[allocated,good,mutation,seed],'events':diff,'tail_native':a[1:],'tail_source':b[1:]},default=lambda x:x.hex() if isinstance(x,bytes) else x,indent=2));raise AssertionError((allocated,good,mutation,seed,[(i,x[:-1],y[:-1]) for i,x,y in diff],a[1:3],b[1:3]))
  count+=1
 receipt={'status':'PASS_NATIVE_AMBIQ_INIT','cases':count,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['All child providers controlled cuts; unit cell reload mutation,228-byte construction,60-byte commandlist,callback bindings,texture/VG fields,clear ordering,thread/mutex params,assert/NULLfault and two256-byte unit regions compared.','AMBIQ name relocated and compared by bytes; GPU/Nema hardware,real child graphs and full-image gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
