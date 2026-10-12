from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];SRC=BASE/'root-draw-copy-round95/copy_candidate.c';GOTO=BASE/'root-goto-xy-round96/goto_candidate.c';PROVIDERS=ROOT/'components/audio/uart_thread_source_candidate/display_lv_init_children.c';AREA=ROOT/'components/audio/uart_thread_source_candidate/display_lv_round_geometry.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
D,S,H,DA,SA,P,Q=0x20001000,0x20002000,0x20003000,0x20004000,0x20005000,0x20010000,0x20020000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void *audio_uart_lv_grid_copy_454738(void*a,const void*b,unsigned c){return a;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){} void custom_copy(void*a,const void*b,const void*c,const void*d){}');elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-u,custom_copy','-Wl,-e,audio_uart_lv_draw_buf_copy_48ad42',str(SRC),str(GOTO),str(PROVIDERS),str(AREA),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  callback=(syms['custom_copy'] if isc else 0x600100)|1;cuts={(syms['audio_uart_lv_grid_copy_454738'] if isc else 0x454738)&~1:'copy',(syms['audio_uart_lvgl_log'] if isc else 0x44d25c)&~1:'log',callback&~1:'custom'};engines.append((u,cuts,callback,(syms['audio_uart_lv_draw_buf_copy_48ad42'] if isc else 0x48ad42)|1))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 count=0;pattern=bytes(range(256))*16
 for cf,mismatch,darea,sarea,height,custom,mutate in itertools.product([7,8,9,10,11,16,19,20,24],[False,True],[0,1,2,3],[0,1,2],[0,1,3],[False,True],[False,True]):
  outs=[]
  for u,cuts,callback,entry in engines:
   u.mem_write(D,W((cf<<8)|0xaa,3|(height<<16),0xabcd0015,4096,P,0,H));u.mem_write(S,W(((cf+1 if mismatch else cf)<<8)|0xbb,3|(3<<16),0xbeef0019,4096,Q,0,H));u.mem_write(H,W(*([0]*7),callback if custom else 0));u.mem_write(DA,W(1,0 if darea!=2 else 0xffffffff,3,0xffffffff if darea==3 else 1));u.mem_write(SA,W(0,1,3 if sarea==2 else 2,2));u.mem_write(P-256,bytes([0xa5])*4352);u.mem_write(Q-256,pattern+bytes(range(256)));calls=[];faults=[]
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP)
    if op=='copy':
     calls.append((op,*r[:3]));uc.mem_write(r[0],bytes(uc.mem_read(r[1],r[2])))
     if mutate:
      uc.mem_write(D,W((16<<8)|0xaa,3|(2<<16),0xcafe0021,4096,P+128));uc.mem_write(S,W((16<<8)|0xbb,3|(3<<16),0xabcd0025,4096,Q+128))
    elif op=='custom':calls.append((op,*r));uc.mem_write(D+12,W(0x13579bdf));uc.mem_write(P,bytes([0x77])*16)
    else:
     fmt=string(uc,struct.unpack('<I',uc.mem_read(sp,4))[0]);item=(op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),fmt)
     if r[2]==235:
      expression,a,b=struct.unpack('<III',uc.mem_read(sp+4,12));item+=(string(uc,expression),a,b)
     elif r[2]==250:item+=tuple(string(uc,v) for v in struct.unpack('<II',uc.mem_read(sp+4,8)))
     else:raise AssertionError(r[2])
     calls.append(item)
    uc.reg_write(UC_ARM_REG_R0,0xdeadbeef);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,address,size,value,user):faults.append((address,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[D,DA if darea else 0,S,SA if sarea else 0]):u.reg_write(reg,v)
   try:u.emu_start(entry,0x600000,count=10000)
   except UcError:assert faults==[(0xffffffff,4,0)],faults
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_SP),*[bytes(u.mem_read(p,n)) for p,n in [(D,28),(S,28),(DA,16),(SA,16),(P-256,4352),(Q-256,4352)]]));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(cf,mismatch,darea,sarea,height,custom,mutate,outs[0][:3],outs[1][:3]);count+=1
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_DRAW_COPY','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'goto_sha256':hashlib.sha256(GOTO.read_bytes()).hexdigest(),'providers_sha256':hashlib.sha256(PROVIDERS.read_bytes()).hexdigest(),'area_sha256':hashlib.sha256(AREA.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_range':'48ad42..48aef8','limits':['Actual goto/BPP/area-width providers execute; memcpy/logger/custom callback child cuts. Memcpy performs real bytes and selected header/data mutations.','Exact CF/width assertion logs and first UINT32_MAX zero-store; full image/layout/byte equality/hardware open.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
