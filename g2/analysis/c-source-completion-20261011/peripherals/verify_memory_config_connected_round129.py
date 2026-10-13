from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-memory-config-connected-round129';D.mkdir(exist_ok=True);S=R/'components/audio/uart_thread_source_candidate/display_font_alloc.c';blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';W=lambda *v:struct.pack('<'+'I'*len(v),*v);ram=[0x200007bc,0x200007d4,0x20000630,0x20000c20];barriers={bytes.fromhex('bff35f8f'):'dmb',bytes.fromhex('bff34f8f'):'dsb',bytes.fromhex('bff36f8f'):'isb'}
with tempfile.TemporaryDirectory() as t:
 t=Path(t);shim=t/'shim.c';shim.write_text('void audio_uart_checksum_copy(void*a,const void*b,unsigned c){} void audio_ble_privacy_cache_maintenance(const void*a,unsigned char b){}');e=t/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_heap_memory_configure_4840c8',str(S),str(shim),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,4096)
  for a,b in segs:u.mem_write(a,b)
  cuts={(syms[s] if isc else a)&~1:op for op,s,a in [('copy','audio_uart_checksum_copy',0x439c04),('cache','audio_ble_privacy_cache_maintenance',0x475014)]};engines.append((u,cuts,isc))
 count=0
 for mutation,control,seed in itertools.product([0,1,2],[0,1,0xffffffff],[0,0xa5a5a5a5]):
  outs=[]
  for u,cuts,isc in engines:
   for i,a in enumerate(ram):u.mem_write(a,W(i if seed==0 else 17,0x20001001+i*256,0x10101,0x200010ff+i*256,1,1))
   u.mem_write(0xe000ed90,W(*[(seed+i)&0xffffffff for i in range(32)]));u.mem_write(0xe000ed94,W(control));events=[]
   def code(uc,a,n,user):
    if n==4 and (op:=barriers.get(bytes(uc.mem_read(a,4)))):events.append((op,))
    if a not in cuts:return
    op=cuts[a];r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
    if op=='copy':
     data=bytes(uc.mem_read(r[1],r[2]));events.append((op,data.hex(),r[2]));uc.mem_write(r[0],data)
     if mutation==1:uc.mem_write(r[0]+4,W(0x12345678))
     if mutation==2:uc.mem_write(0xe000ed94,W(1))
    else:events.append((op,*r[:2]))
    uc.reg_write(UC_ARM_REG_R0,0x12345678);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def memory(uc,access,a,n,value,user):
    if not 0xe000ed90<=a<0xe000ee10:return
    events.append(('read',a,n,struct.unpack('<I',uc.mem_read(a,4))[0]) if access==16 else ('write',a,n,value))
   h=u.hook_add(UC_HOOK_CODE,code);m=u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((syms['audio_uart_heap_memory_configure_4840c8'] if isc else 0x4840c8)|1,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((events,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(0xe000ed90,128)),[bytes(u.mem_read(a,24)) for a in ram]));u.hook_del(h);u.hook_del(m)
  assert outs[0]==outs[1],(mutation,control,seed,outs);count+=1
 receipt={'status':'PASS_COMPILED_ARM_CONNECTED_MEMORY_CONFIG_MPU_NATIVE','cases':count,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual root/reset/control/attribute/region parsing and writers execute; copy/cache maintenance controlled cuts.','Modeled register/barrier trace,valid/invalid RAM descriptors,copy-output/control mutation compared. Physical MPU alias semantics,cache effects and hardware startup remain unproved.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
