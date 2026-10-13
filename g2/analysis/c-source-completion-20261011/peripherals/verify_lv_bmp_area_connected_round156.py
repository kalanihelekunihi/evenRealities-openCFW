from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-lv-bmp-round156';D.mkdir(exist_ok=True);S=B/'root-lv-bmp-round155/candidate.c';W=lambda *v:struct.pack('<'+'I'*len(v),*v);P=0x20001000;STATE=0x20002000;FULL=0x20003000;AREA=0x20004000;BUF=0x20005000;NEW=0x20006000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as t:
 selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('void *audio_uart_lv_draw_buf_reshape_48b196(void *draw_buffer');z=selected.index('/* Full native4d5104',a);extra=Path(t)/'reshape.c';extra.write_text('#include <stdint.h>\nextern uint32_t audio_uart_font_bitmap_stride(uint32_t,uint8_t);\nextern uint32_t audio_uart_lv_draw_buf_size_48b86c(uint32_t,uint32_t,uint32_t,uint32_t);\n'+selected[a:z])
 e=Path(t)/'test.elf'
 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();prefix=S.read_text().split('/* Native4c93a0')[0];fixture=Path(t)/'selected-area.c';fixture.write_text(prefix+selected[selected.index('/* Native4c93a0'):]);S=fixture
 names=['audio_uart_checksum_copy','audio_uart_lv_area_width_451598','audio_uart_lv_draw_buf_reshape_48b196','audio_uart_lv_draw_buf_create_ex_48b010','audio_uart_font_bitmap_release','audio_uart_lv_fs_file_seek_4c6fba','audio_uart_lv_fs_file_read_4c6f46'];defs={n:0x101011+i*16 for i,n in enumerate(names)};defs.pop('audio_uart_lv_area_width_451598');defs.pop('audio_uart_lv_draw_buf_reshape_48b196');defs['audio_uart_font_bitmap_stride']=0x101081;defs['audio_uart_lv_draw_buf_size_48b86c']=0x101091;defs['audio_uart_display_lv_root']=0x2006f548
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_lv_bmp_get_area_4c93a0',*[f'-Wl,--defsym={k}={v}' for k,v in defs.items()],str(S),str(extra),str(R/'components/audio/uart_thread_source_candidate/display_lv_round_geometry.c'),'-o',str(e)],check=True)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,row,old,reshape,create,bpp,mutation):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  u.mem_write(P,bytes(128));u.mem_write(P+72,W(STATE));u.mem_write(P+44,W(BUF if old else 0));u.mem_write(P+32,W(0x12341000));u.mem_write(STATE,W(0x20009000,0,0,0xfffffff0,17,8,bpp,0x80000000));u.mem_write(FULL,W(0xfffffffd,2,9,4));u.mem_write(AREA,W(3,row,9,row));u.mem_write(BUF,W(0,0,0,1024 if reshape else 0,0x20007000));u.mem_write(NEW,W(*[0]*4,0x20008000));events=[]
  ops=['copy','width','reshape','create','release','seek','read'];cuts=dict(zip([0x101010+i*16 for i in range(7)] if isc else [0x439c04,0x451598,0x48b196,0x48b010,0x48b216,0x4c6fba,0x4c6f46],ops))
  cuts={a:op for a,op in cuts.items() if op not in ['width','reshape']};cuts.update({0x101080 if isc else 0x48aad8:'stride',0x101090 if isc else 0x48b86c:'size'})
  def hook(uc,a,n,user):
   if a not in cuts:return
   op=cuts[a];r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0
   snapshot=bytes(uc.mem_read(AREA,16)).hex()
   if op=='stride':events.append((op,r[0],r[1]));ret=64
   elif op=='size':events.append((op,*r));ret=64
   elif op=='copy':data=bytes(uc.mem_read(r[1],r[2]));events.append((op,r[2],data.hex()));uc.mem_write(r[0],data)
   elif op=='width':
    events.append((op,r[0],snapshot));v=struct.unpack('<IIII',uc.mem_read(r[0],16));ret=(v[2]-v[0]+1)&0xffffffff
   elif op in ['reshape','create']:
    events.append((op,*r,struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0],snapshot));ret=NEW if (reshape if op=='reshape' else create) else 0
    if mutation:uc.mem_write(P+32,W(0xdead1200))
   elif op=='release':events.append((op,r[0],snapshot));uc.mem_write(P+44,W(0x20009000))
   elif op=='seek':
    events.append((op,*r[:3],snapshot));ret=7
    if mutation:uc.mem_write(STATE+24,W(40))
   else:events.append((op,*r,snapshot));ret=9
   uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_CPSR,0x33)
  for reg,v in [(UC_ARM_REG_R0,0),(UC_ARM_REG_R1,P),(UC_ARM_REG_R2,FULL),(UC_ARM_REG_R3,AREA),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)]:u.reg_write(reg,v)
  u.emu_start((sym['audio_uart_lv_bmp_get_area_4c93a0'] if isc else 0x4c93a0)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P,128)),bytes(u.mem_read(STATE,32)),bytes(u.mem_read(AREA,16)),bytes(u.mem_read(BUF,20))
 count=0
 for row,old,reshape,create,bpp,mutation in itertools.product([0xe0000001,1,4,0x7fffffff,0xffffffff],[0,1],[0,1],[0,1],[16,24,32,0xffffffff],[0,1]):
  if row!=0xe0000001 and not old:continue
  a=run(False,row,old,reshape,create,bpp,mutation);b=run(True,row,old,reshape,create,bpp,mutation);assert a==b,(row,old,reshape,create,bpp,mutation,a,b);count+=1
 receipt={'status':'PASS_CONNECTED_BMP_GET_AREA_RESHAPE_WIDTH','cases':count,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['Actual area-width and reshape execute; copy/create/release/seek/read/stride/size controlled cuts; first/subsequent rows,allocation failures,callback mutations,unsigned offsets/signed bounds,descriptor/area/state bytes,call snapshots and return/SP compared.','No actual filesystem pixel transfer or physical rendering; fullimage gates remain open.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
