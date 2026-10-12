from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-mpu-control-round126';S=D/'mpu_control_candidate.c';blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';C=0xe000ed94;H=0xe000ed24;W=lambda *v:struct.pack('<'+'I'*len(v),*v);providers=[('audio_uart_mpu_enable_registers_4d43b4',0x4d43b4),('audio_uart_mpu_disable_registers_4d43d4',0x4d43d4),('audio_uart_mpu_reset_4d44e2',0x4d44e2),('audio_uart_mpu_enable_4d44ec',0x4d44ec)];barriers={bytes.fromhex('bff35f8f'):'dmb',bytes.fromhex('bff34f8f'):'dsb',bytes.fromhex('bff36f8f'):'isb'}
with tempfile.TemporaryDirectory() as t:
 t=Path(t);e=t/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0],*['-Wl,-u,'+n for n,a in providers],str(S),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,4096)
  for a,b in segs:u.mem_write(a,b)
  engines.append((u,isc))
 counts={n:0 for n,a in providers}
 for idx in range(4):
  arguments=([[v] for v in [0,1,2,255,256,0x80000000,0xffffffff]] if idx==0 else [[a,b] for a,b in [(0,0),(1,1),(2,255),(256,257),(0xffffffff,0x80000000)]] if idx==3 else [[]])
  for args,control,handler,mutation in itertools.product(arguments,[0,1,2,3,0x80000000,0xffffffff],[0,0x10000,0xa5a5a5a5,0xffffffff],[0,1]):
   outs=[];name,address=providers[idx]
   for u,isc in engines:
    u.mem_write(C,W(control));u.mem_write(H,W(handler));events=[]
    def code(uc,a,n,user):
     if n==4 and (op:=barriers.get(bytes(uc.mem_read(a,4)))):events.append((op,))
    def memory(uc,access,a,n,value,user):
     if a not in [C,H]:return
     # Unicorn memory access READ=16, WRITE=17.
     if access==16:
      if mutation:uc.mem_write(a,W(struct.unpack('<I',uc.mem_read(a,4))[0]^0x80000000))
      events.append(('read',a,n,struct.unpack('<I',uc.mem_read(a,4))[0]))
     else:events.append(('write',a,n,value))
    h=u.hook_add(UC_HOOK_CODE,code);m=u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1],args):u.reg_write(reg,value)
    u.emu_start((syms[name] if isc else address)|1,0x600000,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
    outs.append((events,u.reg_read(UC_ARM_REG_R0) if idx>=2 else None,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(C,4)),bytes(u.mem_read(H,4))));u.hook_del(h);u.hook_del(m)
   assert outs[0]==outs[1],(name,args,control,handler,mutation,outs);counts[name]+=1
 receipt={'status':'PASS_COMPILED_ARM_MPU_CONTROL_MODELED_MMIO_NATIVE','cases':sum(counts.values()),'by_provider':counts,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual register leaves/reset/enable wrappers execute; modeled MPU_CTRL/SCB_SHCSR reads/writes and DMB/DSB/ISB instruction order compared.','Low-byte argument ABI,already-enabled status3,word preservation and read mutations sampled. Modeled register/barrier trace does not prove physical MPU/cache effects or hardware execution.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
