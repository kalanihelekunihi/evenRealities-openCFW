from pathlib import Path
import subprocess,tempfile,json,hashlib,re
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED,UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-area-round66/area_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);names=re.findall(r'extern[^;]*?\b(audio_\w+)\(',SRC.read_text());shim=td/'shim.c';shim.write_text('unsigned char audio_uart_display_lv_root[512];\n'+'\n'.join('unsigned '+n+'(void){return 0;}' for n in names));elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_bin_decoder_get_area_4c7e4c',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']


 count=0
 native_extra={'audio_uart_font_bitmap_release':0x48b216,'audio_uart_checksum_copy':0x439c04,'audio_uart_lv_malloc':0x44f718,'audio_uart_lv_heap_free':0x44f758,'audio_uart_lvgl_log':0x44d25c}
 import itertools
 for cf,typ,reshape,create,old,alloc,mutate in itertools.product([7,20],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]):
  x=0;y=0xe0000001;status=0
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   dsc=0x20003000;data=0x20004000;decoded=0x20005000;full=0x20006000;area=0x20007000;image=0x20008000;pixels=0x20009000;file=0x2000a000;buffer=0x2000b000
   def put(a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
   def word(a):return int.from_bytes(u.mem_read(a,4),'little')
   bpp={7:1,8:2,9:4,10:8,15:8,16:32,17:32,18:16,19:24,20:24}[cf]
   put(dsc+32,cf<<8);put(dsc+36,12<<16);put(dsc+40,32);put(dsc+48,0x2000c000);put(dsc+52,16);put(dsc+72,data);put(dsc+12,image);u.mem_write(dsc+16,bytes([typ]));put(data,file);put(data+64,decoded if old else 0);put(decoded+8,24);put(decoded+16,pixels);put(image+16,pixels)
   for off,v in [(0,0),(4,0),(8,4),(12,8)]:put(full+off,v)
   for off,v in [(0,x),(4,y),(8,4),(12,y)]:put(area+off,v)
   calls=[];faults=[];cuts={}
   for name in names:
    native=native_extra[name] if name in native_extra else int(name.rsplit('_',1)[1],16)
    cuts[(syms[name] if isc else native)&~1]=name
   def hook(uc,a,size,user):
    if a not in cuts:return
    name=cuts[a];args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0
    if name=='audio_uart_lv_draw_buf_reshape_48b196':calls.append(('reshape',*args,word(uc.reg_read(UC_ARM_REG_SP))));ret=decoded if reshape else 0
    elif name=='audio_uart_lv_draw_buf_create_ex_48b010':
     assert args[0]==((syms['audio_uart_display_lv_root']+0x108) if isc else 0x2006f650)
     calls.append(('create',*args[1:],word(uc.reg_read(UC_ARM_REG_SP))));ret=decoded if create else 0
    elif name=='audio_uart_font_bitmap_release':
     calls.append(('destroy',args[0]))
     if mutate:put(data+64,0x2000d000)
    elif name=='audio_uart_checksum_copy':
     calls.append(('copy',args[1],args[2]));u.mem_write(args[0],bytes(u.mem_read(args[1],args[2])))
     if mutate:put(area+4,3)
    elif name=='audio_uart_lvgl_log':
     sp=uc.reg_read(UC_ARM_REG_SP)
     def string(a):
      data=bytearray()
      while (v:=bytes(u.mem_read(a+len(data),1)))!=b'\0':data.extend(v)
      return data.decode()
     calls.append(('log',args[0],string(args[1]),args[2],string(args[3]),*[string(word(sp+i)) for i in [0,4,8]]))
    elif name=='audio_uart_lv_color_bpp_440f44':calls.append(('bpp',args[0]));ret=bpp
    elif name=='audio_uart_lv_area_width_451598':calls.append(('width',args[0]));ret=5
    elif name=='audio_uart_lv_malloc':calls.append(('malloc',args[0]));ret=buffer if alloc else 0
    elif name=='audio_uart_lv_heap_free':calls.append(('free',args[0]))
    elif name=='audio_uart_lv_fs_read_at_4c8d3c':calls.append(('read',*args,word(uc.reg_read(UC_ARM_REG_SP))));ret=status
    elif name=='audio_uart_lv_bin_decode_indexed_line_4c8c94':
     sp=uc.reg_read(UC_ARM_REG_SP);calls.append(('indexed',*args,word(sp),word(sp+4)))
    else:raise AssertionError(('unexpected',name,args))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,a,size,value,user):faults.append((a,size,value));return False
   u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,v in [(UC_ARM_REG_R0,0),(UC_ARM_REG_R1,dsc),(UC_ARM_REG_R2,full),(UC_ARM_REG_R3,area)]:u.reg_write(reg,v)
   try:u.emu_start((syms['audio_uart_lv_bin_decoder_get_area_4c7e4c'] if isc else 0x4c7e4c)|1,0x600000,count=10000)
   except UcError:assert faults and faults[0][0]==0xffffffff
   outputs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(dsc,80)),bytes(u.mem_read(area,16)),bytes(u.mem_read(data,68)),None if faults else u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(cf,typ,reshape,create,old,alloc,outputs);count+=1
 r={'status':'PASS_INITIAL_SCANLINE_ALLOCATION_PATHS_ONLY','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['BPP/width, malloc/free, read-at and indexed-line children controlled cuts.','Initial indexed and RGB565/A8 scanlines with reshape/create permutations, exact root-relative handlers identity and controlled destroy/copy mutation.','Allocation assertion stops at first fault store; missing production providers, full layout/byte equality and hardware remain unproven.']};(SRC.parent/'area-initial-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
