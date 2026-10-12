from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
BASE=Path(__file__).parent;SRC=BASE/'root-draw-duplicate-round91/duplicate_candidate.c';ROOT=BASE.parents[2]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
A,B,P,Q=0x20001000,0x20002000,0x20003000,0x20004000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void *audio_uart_lv_draw_buf_create_ex_48b010(void*a,unsigned b,unsigned c,unsigned d,unsigned e){return 0;} void *audio_uart_lv_grid_copy_454738(void*a,const void*b,unsigned c){return a;}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_draw_buf_duplicate_ex_48b134',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for flags,srcsize,dstsize,mode,mutate in itertools.product([0,1,16,32,65535],[0,1,16,31],[0,1,16,31],[0,1,2],[False,True]):
  outs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(A,W((flags<<16)|(16<<8)|0xaa,0xffff000b,0xabcd0011,srcsize,P));u.mem_write(B,W(0xaaaa1357,0,0,dstsize,Q));u.mem_write(P,bytes(range(64)));u.mem_write(Q,bytes([0xaa])*64);calls=[]
   create=(syms['audio_uart_lv_draw_buf_create_ex_48b010'] if isc else 0x48b010)&~1;copy=(syms['audio_uart_lv_grid_copy_454738'] if isc else 0x454738)&~1
   def hook(uc,addr,size,user):
    if addr not in [create,copy]:return
    r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
    if addr==create:
     calls.append(('create',*r,struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0]));ret=[0,B,A][mode]
     if mutate:uc.mem_write(A,W(0x123419ab,13|(9<<16),23,7,Q))
    else:
     calls.append(('copy',*r[:3]));uc.mem_write(r[0],bytes(uc.mem_read(r[1],r[2])));ret=0xdeadbeef
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0xabcdef00);u.reg_write(UC_ARM_REG_R1,A);u.emu_start((syms['audio_uart_lv_draw_buf_duplicate_ex_48b134'] if isc else 0x48b134)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),*[bytes(u.mem_read(p,n)) for p,n in [(A,20),(B,20),(P,64),(Q,64)]]))
  assert outs[0]==outs[1],(flags,srcsize,dstsize,mode,mutate,outs);count+=1
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_DRAW_DUPLICATE','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_range':'48b134..48b196','limits':['Allocation and memcpy child cuts; memcpy performs actual byte writes. Alias and allocation-side source mutation covered.','Full image/layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
