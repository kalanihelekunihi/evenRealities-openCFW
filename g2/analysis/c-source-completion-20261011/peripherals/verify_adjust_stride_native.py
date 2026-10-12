from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;SRC=BASE/'root-adjust-stride-round92/adjust_candidate.c';ROOT=BASE.parents[2];PROVIDERS=ROOT/'components/audio/uart_thread_source_candidate/display_lv_init_children.c'
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
A,P=0x20001000,0x20010000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('unsigned audio_uart_font_bitmap_stride(unsigned a,unsigned char b){return 0;} void *audio_uart_lv_grid_move_45475a(void*a,const void*b,unsigned c){return a;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_draw_buf_adjust_stride_48b34e',str(SRC),str(PROVIDERS),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={(syms[s] if isc else n)&~1:op for op,s,n in [('stride','audio_uart_font_bitmap_stride',0x48aad8),('move','audio_uart_lv_grid_move_45475a',0x45475a),('log','audio_uart_lvgl_log',0x44d25c)]};engines.append((u,cuts,(syms['audio_uart_lv_draw_buf_adjust_stride_48b34e'] if isc else 0x48b34e)|1))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 count=0;pattern=bytes(range(256))*32
 cases=list(itertools.product([7,8,9,10,11,16,19,20,255],[0,3,11],[0,1,3],[8,32],[0,4,8,32,0x10020],[0,32],[0,4096],[False,True]))
 cases+= [('null',0,0,0,0,0,0,False),('data-null',0,0,0,0,0,0,False)]
 for cf,width,height,oldstride,stride,flags,capacity,mutate in cases:
  outs=[]
  for u,cuts,entry in engines:
   u.mem_write(A,W((flags<<16)|((cf if isinstance(cf,int) else 16)<<8),width|(height<<16),0xabcd0000|oldstride,capacity,0 if cf=='data-null' else P));u.mem_write(P,pattern);calls=[];faults=[]
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0
    if op=='stride':calls.append((op,*r[:2]));ret=24
    elif op=='move':
     calls.append((op,*r[:3]));uc.mem_write(r[0],bytes(uc.mem_read(r[1],r[2])));ret=0xdeadbeef
     if mutate:uc.mem_write(A+8,W(0xdef00010))
    elif op=='log':
     fmt=string(uc,struct.unpack('<I',uc.mem_read(sp,4))[0]);item=(op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),fmt)
     if r[2] in [449,450]:item+=tuple(string(uc,p) for p in struct.unpack('<II',uc.mem_read(sp+4,8)))
     else:item+=(struct.unpack('<I',uc.mem_read(sp+4,4))[0],)
     calls.append(item)
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0 if cf=='null' else A);u.reg_write(UC_ARM_REG_R1,stride)
   try:u.emu_start(entry,0x600000,count=5000)
   except UcError:assert faults==[(0xffffffff,4,0)],faults
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(A,20)),bytes(u.mem_read(P,8192))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(cf,width,height,oldstride,stride,flags,capacity,mutate,outs[0][:4],outs[1][:4]);count+=1
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_ADJUST_STRIDE','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'providers_sha256':hashlib.sha256(PROVIDERS.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_range':'48b34e..48b51e','limits':['Actual flag/BPP/size providers execute. Stride/memmove/logger child cuts; memmove performs actual overlapping byte writes.','Assertions verify exact logger and first native UINT32_MAX zero-store. Full image/layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
