from pathlib import Path
import subprocess,tempfile,json,hashlib,re
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
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
 for cf,typ,x,y,status in itertools.product([7,8,9,10,15,16,17,18,19,20],[0,1],[0,3,0xffffffff],[0,8],[0,1,256]):
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   dsc=0x20003000;data=0x20004000;decoded=0x20005000;full=0x20006000;area=0x20007000;image=0x20008000;pixels=0x20009000;file=0x2000a000;buffer=0x2000b000
   def put(a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
   def word(a):return int.from_bytes(u.mem_read(a,4),'little')
   bpp={7:1,8:2,9:4,10:8,15:8,16:32,17:32,18:16,19:24,20:24}[cf]
   put(dsc+32,cf<<8);put(dsc+36,12<<16);put(dsc+40,32);put(dsc+48,0x2000c000);put(dsc+52,16);put(dsc+72,data);put(dsc+12,image);u.mem_write(dsc+16,bytes([typ]));put(data,file);put(data+64,decoded);put(decoded+8,24);put(decoded+16,pixels);put(image+16,pixels)
   for off,v in [(0,0),(4,0),(8,4),(12,8)]:put(full+off,v)
   for off,v in [(0,x),(4,y),(8,4),(12,y)]:put(area+off,v)
   calls=[];cuts={}
   for name in names:
    native=native_extra[name] if name in native_extra else int(name.rsplit('_',1)[1],16)
    cuts[(syms[name] if isc else native)&~1]=name
   def hook(uc,a,size,user):
    if a not in cuts:return
    name=cuts[a];args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0
    if name=='audio_uart_lv_color_bpp_440f44':calls.append(('bpp',args[0]));ret=bpp
    elif name=='audio_uart_lv_area_width_451598':calls.append(('width',args[0]));ret=5
    elif name=='audio_uart_lv_malloc':calls.append(('malloc',args[0]));ret=buffer
    elif name=='audio_uart_lv_heap_free':calls.append(('free',args[0]))
    elif name=='audio_uart_lv_fs_read_at_4c8d3c':calls.append(('read',*args,word(uc.reg_read(UC_ARM_REG_SP))));ret=status
    elif name=='audio_uart_lv_bin_decode_indexed_line_4c8c94':
     sp=uc.reg_read(UC_ARM_REG_SP);calls.append(('indexed',*args,word(sp),word(sp+4)))
    else:raise AssertionError(('unexpected',name,args))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,v in [(UC_ARM_REG_R0,0),(UC_ARM_REG_R1,dsc),(UC_ARM_REG_R2,full),(UC_ARM_REG_R3,area)]:u.reg_write(reg,v)
   u.emu_start((syms['audio_uart_lv_bin_decoder_get_area_4c7e4c'] if isc else 0x4c7e4c)|1,0x600000,count=10000);outputs.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(dsc,80)),bytes(u.mem_read(area,16)),u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(cf,typ,x,y,status,outputs);count+=1
 r={'status':'PASS_CONTINUING_SCANLINE_PATHS_ONLY','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['BPP/width, malloc/free, read-at and indexed-line children controlled cuts.','Includes indexed file/variable offsets, signed scanline-end check, negative x bit patterns, RGB reads and RGB565/A8 dual read.','Initial reshape/create and allocation-failure paths remain unverified; candidate unselected.']};(SRC.parent/'area-lines-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
