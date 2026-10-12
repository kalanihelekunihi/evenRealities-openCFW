from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;SRC=BASE/'root-premultiply-round94/premultiply_candidate.c';ROOT=BASE.parents[2];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
A,P=0x20001000,0x20010000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void audio_uart_lv_basic_box_clear_454746(void*a,unsigned b,unsigned c){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_draw_buf_premultiply_48b540',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={(syms['audio_uart_lv_basic_box_clear_454746'] if isc else 0x454746)&~1:'clear',(syms['audio_uart_lvgl_log'] if isc else 0x44d25c)&~1:'log'};engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 def compare(name,native,initial,args,mutate=False,void=False):
  outs=[]
  for u,cuts,isc in engines:
   u.mem_write(A,W(0,0,0,4096,P));u.mem_write(P,bytes(range(256))*16)
   for address,data in initial:u.mem_write(address,data)
   calls=[];faults=[]
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP)
    if op=='clear':
     calls.append((op,*r[:3]));uc.mem_write(r[0],bytes([r[1]&255])*r[2])
     if mutate:uc.mem_write(A,W(0x004011aa,0xffffeeee,0xabcdffff,0,P))
    else:
     fmt=string(uc,struct.unpack('<I',uc.mem_read(sp,4))[0]);item=(op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),fmt)
     if r[2]==520:item+=tuple(string(uc,v) for v in struct.unpack('<II',uc.mem_read(sp+4,8)))
     else:item+=(struct.unpack('<I',uc.mem_read(sp+4,4))[0],)
     calls.append(item)
     if mutate and r[2]==589:uc.mem_write(A,W(0x004011aa))
    uc.reg_write(UC_ARM_REG_R0,0xdeadbeef);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,address,size,value,user):faults.append((address,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1],args):u.reg_write(reg,value)
   try:u.emu_start((syms[name] if isc else native)|1,0x600000,count=50000)
   except UcError:assert faults==[(0xffffffff,4,0)],faults
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,None if void or faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(A,20)),bytes(u.mem_read(P,4096))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(name,initial,args,mutate,outs[0][:4],outs[1][:4]);return 1
 count=0
 for alpha,offset in itertools.product(range(256),[0,1]):
  count+=compare('audio_uart_lv_color_premultiply_4410b8',0x4410b8,[(P+offset,bytes([253,127,61,alpha]))],[P+offset,0],void=True)
 for color,alpha,offset in itertools.product([0,1,0x1f,0x7e0,0xf800,0xffff],range(256),[0,1]):
  count+=compare('audio_uart_lv_color16_premultiply_4410ee',0x4410ee,[(P+offset,struct.pack('<H',color))],[P+offset,alpha|0x10000],void=True)
 leaf_count=count
 for cf,flags,width,height,stride,mode in itertools.product([7,8,9,10,11,14,16,19,20,24,255],[0,1,32,33],[0,1,3],[0,1,3],[0,12,21],[0,1,2]):
  initial=[(A,W((flags<<16)|(cf<<8),width|(height<<16),0xabcd0000|stride,4096,P))]
  if mode==2:initial.append((P,bytes(4096)))
  count+=compare('audio_uart_lv_draw_buf_premultiply_48b540',0x48b540,initial,[A,0],mutate=mode!=0)
 count+=compare('audio_uart_lv_draw_buf_premultiply_48b540',0x48b540,[],[0,0])
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_PREMULTIPLY_AND_COLOR_LEAVES','cases':count,'leaf_cases':leaf_count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_ranges':['440f38..440f44','4410b8..4410ee','4410ee..441164','48b540..48b722'],'limits':['Actual color leaves execute in full draw-buffer body. Clear/logger child cuts; clear performs actual byte writes and selected header mutations.','Exhaustive low-byte alpha values with bounded colors, odd addresses, formats/stride/dimensions; exact logs, flags and first assertion store. Full-image and hardware gates open.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
