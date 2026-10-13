from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-ambiq-drawing-round174';S=D/'candidate.c';W=lambda *v:struct.pack('<'+'I'*len(v),*[x&0xffffffff for x in v]);T=0x20001000;L=0x20002000;BF=0x20003000;DS=0x20004000;ALT=0x20005000
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native=[0x4c73c4,0x450bb2,0x451598,0x4515a4,0x488cda,0x450bcc,0x48abb8,0x4b092a,0x53dc38,0x53df00,0x53e728,0x53ecfc,0x53f09c,0x53f42a,0x53f400,0x4b0bea,0x53faa6,0x540036,0x5409f0,0x4b0c8a,0x48ab30]
names=['audio_uart_ambiq_area_copy_4c73c4','audio_uart_ambiq_area_move_450bb2','audio_uart_lv_area_width_451598','audio_uart_lv_area_height_4515a4','audio_uart_ambiq_transform_area_488cda','audio_uart_lv_area_intersect_450bcc','audio_uart_ambiq_buffer_invalidate_48abb8','audio_uart_ambiq_bind_buffer_4b092a','audio_uart_ambiq_draw_fill_53dc38','audio_uart_ambiq_draw_border_53df00','audio_uart_ambiq_draw_triangle_53e728','audio_uart_ambiq_draw_line_53ecfc','audio_uart_ambiq_draw_arc_53f09c','audio_uart_ambiq_draw_image_53f42a','audio_uart_ambiq_draw_layer_53f400','audio_uart_ambiq_set_resolution_4b0bea','audio_uart_ambiq_draw_label_53faa6','audio_uart_ambiq_draw_box_shadow_540036','audio_uart_ambiq_draw_mask_5409f0','audio_uart_ambiq_submit_4b0c8a','audio_uart_ambiq_buffer_flush_48ab30']
with tempfile.TemporaryDirectory() as tmp:

 if '--selected' in sys.argv:
  selected=(R/'components/audio/uart_thread_source_candidate/display_lv_init_children.c').read_text();a=selected.index('/* Native4c7752..4c791a.');fixture=Path(tmp)/'selected.c';fixture.write_text(S.read_text().split('/* Native4c7752')[0]+selected[a:]);S=fixture
 e=Path(tmp)/'test.elf';cuts=[0x101010+i*16 for i in range(len(names))]
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mrestrict-it','-O2','-nostdlib','-Wl,-Ttext=0x110000','-Wl,-e,audio_uart_ambiq_execute_drawing_4c7752']+['-Wl,--defsym='+n+'='+hex(a|1) for n,a in zip(names,cuts)]+[str(S),'-o',str(e)],check=True,stderr=subprocess.DEVNULL)
 with e.open('rb') as f:
  elf=ELFFile(f);segs=[(p['p_vaddr'],p.data()) for p in elf.iter_segments() if p['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(isc,typ,transform,intersect,bind,mutation,seed):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,data in segs:u.mem_write(a,data)
  for a in [T,L,BF,DS,ALT]:u.mem_write(a,bytes([seed])*128)
  u.mem_write(T+4,bytes([typ]));u.mem_write(T+8,W(0x80000000,17,23,0x7fffffff));u.mem_write(T+56,W(3,5,43,65));u.mem_write(T+72,W(L,BF));u.mem_write(T+84,W(DS));u.mem_write(L,W(BF,0x80000000,0xffffffff));u.mem_write(BF+4,W(0x43211234));vals=[0,256,256,0,0]
  if transform:vals[[0,1,2,4,3][transform-1]]=123
  u.mem_write(DS+48,W(*vals));events=[];trace=[];mc=0
  def area(a):return struct.unpack('<4I',u.mem_read(a,16))
  def hook(uc,a,n,user):
   nonlocal mc
   addresses=cuts if isc else native
   if a not in addresses:return
   i=addresses.index(a);r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0xabcdef01
   if i==0:events.append((i,r[1],area(r[1])));uc.mem_write(r[0],bytes(uc.mem_read(r[1],16)))
   elif i==1:
    events.append((i,area(r[0]),r[1],r[2]));v=area(r[0]);uc.mem_write(r[0],W(v[0]+r[1],v[1]+r[2],v[2]+r[1],v[3]+r[2]));mc+=1
   elif i in [2,3]:
    v=area(r[0]);events.append((i,v));ret=(v[2]-v[0]+1 if i==2 else v[3]-v[1]+1)&0xffffffff
    if mutation==1:uc.mem_write(DS+48,W(7,9,11,13,15))
   elif i==4:
    stk=struct.unpack('<3I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),12));events.append((i,area(r[0]),tuple(r[1:]),stk));uc.mem_write(r[0],W(0xffffffff,0x80000000,9,11))
    if mutation==2:uc.mem_write(T+8,W(7,13,17,23));uc.mem_write(L+4,W(19,29))
   elif i==5:events.append((i,area(r[0]),area(r[1]),area(r[2]),r[0]==r[1]));uc.mem_write(r[0],W(101,103,107,109));ret=intersect
   elif i in [6,20]:events.append((i,r[0],area(r[1])))
   elif i==7:
    events.append((i,r[0],area(r[1]),r[2]));ret=bind
    if mutation==3:uc.mem_write(T+4,bytes([5]));uc.mem_write(T+84,W(ALT))
   elif i==15:
    events.append((i,r[0],r[1]))
    if mutation==4:uc.mem_write(T+84,W(ALT))
   elif i==19:events.append((i,r[0]))
   else:events.append((i,tuple(r[:2 if i in [10,11] else 3])))
   uc.reg_write(UC_ARM_REG_R0,ret&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  def mem(uc,access,a,n,value,user):
   if any(x<=a<x+128 for x in [T,L,BF,DS,ALT]):trace.append((access,a,n,value if access==17 else bytes(uc.mem_read(a,n)).hex()))
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,mem);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_R0,T);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((sym['audio_uart_ambiq_execute_drawing_4c7752'] if isc else 0x4c7752)|1,0x600000,count=3000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
  return events,trace,u.reg_read(UC_ARM_REG_SP),tuple(bytes(u.mem_read(a,128)) for a in [T,L,BF,DS,ALT])
 cases=[(typ,0,1,1,0,seed) for typ,seed in itertools.product(range(256),[0,165])]
 cases += [(typ,trans,inter,bind,mutation,165) for typ,trans,inter,bind,mutation in itertools.product([5,6,13],range(6),[0,1],[0,1,257,255],range(5))]
 for case in cases:
  a=run(False,*case);b=run(True,*case)
  if a!=b:
   (D/'mismatch.json').write_text(json.dumps({'case':case,'native_events':a[0],'source_events':b[0],'native_trace':a[1],'source_trace':b[1]},indent=2)+'\n');raise AssertionError(case)
 receipt={'status':'PASS_NATIVE_AMBIQ_DRAWING_CONTROLLED_CHILDREN','cases':len(cases),'selected':'--selected' in sys.argv,'candidate_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'limits':['21 controlled child entries; all task types, each transform predicate, clipping/bind low-byte outcomes, child mutations, wrapped coordinates, ordered input field accesses, five128byte regions, normalized stack area snapshots/SP compared.','Actual area/buffer/transform/drawing children and physical GPU behavior remain unqualified.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
