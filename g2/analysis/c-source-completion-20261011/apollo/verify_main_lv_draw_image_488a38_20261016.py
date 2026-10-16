#!/usr/bin/env python3
"""Controlled stock comparison for LVGL image scheduler at 0x488a38."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/'g2'
SOURCE=G2/'components/audio/uart_thread_source_candidate/display_lv_draw_image_488a38.c'
OUT=G2/'build/c-firmware/20261016/main-lv-draw-image-488a38'
PAYLOAD=G2/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
PIN='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CALLS=[('audio_uart_lvgl_log',0x44d25c),('audio_uart_lv_malloc',0x44f718),('audio_uart_lv_heap_free',0x44f758),('audio_uart_lv_grid_copy_454738',0x454738),('audio_uart_display_area_copy_439c04',0x439c04),('audio_uart_lv_image_header_488f6a',0x488f6a),('audio_uart_lv_image_decoder_open_488f9c',0x488f9c),('audio_uart_lv_render_task_alloc_4843ee',0x4843ee),('audio_uart_lv_render_task_queue_484476',0x484476),('audio_uart_lv_area_width_451598',0x451598),('audio_uart_lv_area_height_4515a4',0x4515a4),('audio_uart_ambiq_transform_area_488cda',0x488cda),('audio_uart_ambiq_area_move_450bb2',0x450bb2),('audio_uart_lv_area_intersect_450bcc',0x450bcc)]
LAYER,DSC,COORDS,SRC,HEAP,TASK,DECODER,CALLBACK=0x20001000,0x20002000,0x20003000,0x20004000,0x20005000,0x20006000,0x20007000,0x20008000
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build():
 OUT.mkdir(parents=True,exist_ok=True);obj=OUT/'oracle.o';elf=OUT/'oracle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror','-c',str(SOURCE),'-o',str(obj)],check=True)
 subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={n}=0x{a|1:x}' for n,a in CALLS],str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sym={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
 return elf,seg,sym

def main():
 blob=PAYLOAD.read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()==PIN
 elf,seg,sym=build();cuts={a:i for i,(_,a) in enumerate(CALLS)}
 def run(compiled,source,opa,sx,sy,flags,sentinel,child,info_result,open_result,intersect):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_map(0x20000000,0x100000)
  def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def get(a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def area(a):return struct.unpack('<iiii',u.mem_read(a,16))
  def cstr(a):
   raw=bytes(u.mem_read(a,180));return raw.split(b'\0',1)[0]
  u.mem_write(LAYER,bytes(128));put(LAYER+4,5);put(LAYER+8,7);put(LAYER+12,104);put(LAYER+16,78);put(LAYER+0x48,child)
  u.mem_write(DSC,bytes((i*13+9)&255 for i in range(0x6c)))
  put(DSC,0x20009000);put(DSC+0x1c,SRC if source else 0);put(DSC+0x30,0x15);put(DSC+0x34,sx);put(DSC+0x38,sy);put(DSC+0x60,0xe0000001 if sentinel else 0)
  u.mem_write(DSC+0x50,bytes([opa]));u.mem_write(COORDS,struct.pack('<iiii',10,20,49,59))
  u.mem_write(SRC,b'\x10'+bytes(31));u.mem_write(0x20009000,bytes(128));put(0x20009000+0x14,8);put(0x20009000+0x18,18);put(0x20009000+0x1c,60);put(0x20009000+0x20,70)
  u.mem_write(HEAP,bytes([0xa5])*0x6c);u.mem_write(TASK,bytes(128));u.mem_write(DECODER,bytes(64));put(DECODER+0x10,CALLBACK|1)
  trace=[];intersections=iter(intersect)
  def hook(cpu,pc,size,_):
   if pc==CALLBACK:
    r=[cpu.reg_read(v) for v in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
    fifth=get(cpu.reg_read(A.UC_ARM_REG_SP))
    trace.append(('callback',r[0],bytes(cpu.mem_read(r[1],0x4c))[:8],area(r[2]),r[3],area(fifth)))
    cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
   if pc not in cuts:return
   i=cuts[pc];r=[cpu.reg_read(v) for v in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)];sp=cpu.reg_read(A.UC_ARM_REG_SP)
   value=0
   if i==0:trace.append(('log',r[0],r[2],cstr(r[1]),cstr(r[3]),cstr(get(sp))))
   elif i==1:trace.append(('alloc',r[0]));value=HEAP
   elif i==2:trace.append(('free',r[0]))
   elif i in (3,4):
    trace.append(('copy',i,r[2],bytes(cpu.mem_read(r[1],r[2]))))
    cpu.mem_write(r[0],bytes(cpu.mem_read(r[1],r[2])));value=r[0]
   elif i==5:
    trace.append(('info',r[0],r[1]-HEAP));put(r[1],flags);value=info_result
   elif i==6:
    trace.append(('open',r[1],r[2]));put(r[0],DECODER);value=open_result
   elif i==7:trace.append(('add',r[0],area(r[1])));value=TASK
   elif i==8:trace.append(('finalize',r[0],r[1]))
   elif i in (9,10):
    trace.append(('size',i,area(r[0])));value=(area(r[0])[2]-area(r[0])[0]+1) if i==9 else (area(r[0])[3]-area(r[0])[1]+1)
   elif i==11:
    fifth,sixth,pivot=get(sp),get(sp+4),get(sp+8)
    trace.append(('transform',r[1],r[2],r[3],fifth,sixth,bytes(cpu.mem_read(pivot,8))))
    cpu.mem_write(r[0],struct.pack('<iiii',0,0,r[1]-1,r[2]-1))
   elif i==12:
    trace.append(('move',r[1],r[2],area(r[0])))
    x1,y1,x2,y2=area(r[0]);cpu.mem_write(r[0],struct.pack('<iiii',x1+r[1] if r[1]<0x80000000 else x1+r[1]-0x100000000,y1+r[2] if r[2]<0x80000000 else y1+r[2]-0x100000000,x2+r[1] if r[1]<0x80000000 else x2+r[1]-0x100000000,y2+r[2] if r[2]<0x80000000 else y2+r[2]-0x100000000))
   elif i==13:
    value=next(intersections,1);trace.append(('intersect',value,area(r[1]),area(r[2])))
   cpu.reg_write(A.UC_ARM_REG_R0,value&0xffffffff);cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(A.UC_ARM_REG_SP,0x200ff000);u.reg_write(A.UC_ARM_REG_LR,0x600001)
  for reg,value in ((A.UC_ARM_REG_R0,LAYER),(A.UC_ARM_REG_R1,DSC),(A.UC_ARM_REG_R2,COORDS)):u.reg_write(reg,value)
  entry=sym['audio_uart_lv_draw_image_488a38'] if compiled else 0x488a38
  u.emu_start(entry|1,0x600000,count=1500)
  return trace,bytes(u.mem_read(HEAP,0x6c)),bytes(u.mem_read(TASK,0x60)),bytes(u.mem_read(LAYER+0x18,16))
 cases=[]
 for source,opa,sx,sy in itertools.product((0,1),(0,2,3,255),(0,1,256),(0,1,256)):
  cases.append((source,opa,sx,sy,0,0,0,1,1,(1,1)))
 for flags,sentinel,child,info_result,open_result,intersect in itertools.product((0,0x00400000),(0,1),(0,1),(0,1),(0,1),((0,0),(1,0),(1,1))):
  cases.append((1,255,256,256,flags,sentinel,child,info_result,open_result,intersect))
 for idx,args in enumerate(cases):
  a,b=run(False,*args),run(True,*args)
  if a!=b:
   print('case',idx,args,'stock trace',a[0],'compiled trace',b[0])
   print('heap diffs',[(i,x,y) for i,(x,y) in enumerate(zip(a[1],b[1])) if x!=y][:20]);print('task diffs',[(i,x,y) for i,(x,y) in enumerate(zip(a[2],b[2])) if x!=y][:20]);raise RuntimeError('image scheduler mismatch')
 result={'status':'PASS_EXPERIMENTAL_MAIN_LV_DRAW_IMAGE_C_ORACLE','source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'payload_sha256':PIN,'oracle_elf_sha256':sha(elf),'cases':len(cases),'scope':'Early exits, bitmap task and custom decoder branches under isolated lower calls','limits':['Allocation-failure trap excluded; lower providers and final image placement open.']}
 path=OUT/'oracle-receipt.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(result['status'],len(cases),sha(path))
if __name__=='__main__':main()
