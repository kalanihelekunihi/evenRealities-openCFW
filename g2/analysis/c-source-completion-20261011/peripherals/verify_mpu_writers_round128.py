from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,shutil
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-mpu-writers-round128';S=D/'mpu_writers_candidate.c';blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';P=0x20004000;T=0x20008000;M=0xe000ed90;W=lambda *v:struct.pack('<'+'I'*len(v),*v);providers=[('audio_uart_mpu_attribute_write_raw_4d43f6',0x4d43f6),('audio_uart_mpu_attribute_write_4d4434',0x4d4434),('audio_uart_mpu_copy_words_4d4446',0x4d4446),('audio_uart_mpu_regions_write_raw_4d445e',0x4d445e),('audio_uart_mpu_regions_write_4d44d2',0x4d44d2)]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);e=t/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0],*['-Wl,-u,'+n for n,a in providers],str(S),'-o',str(e)],check=True)
 shutil.copyfile(e,'/tmp/g2-mpuwriters128-test.elf')
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,4096)
  for a,b in segs:u.mem_write(a,b)
  engines.append((u,isc))
 counts={n:0 for n,a in providers}
 def check(idx,args,seed=0,mutation=0,reset=True):
  outs=[];name,address=providers[idx]
  for u,isc in engines:
   u.mem_write(P-16,W(*[(seed+i*0x1020304)&0xffffffff for i in range(80)]));u.mem_write(T,W(*[(seed+i)&0xffffffff for i in range(32)]));u.mem_write(M,W(*[(seed+i)&0xffffffff for i in range(32)]));events=[]
   def memory(uc,access,a,n,value,user):
    if not (P-16<=a<P+304 or T<=a<T+128 or M<=a<M+128):return
    if access==16:
     if mutation:uc.mem_write(a,W(struct.unpack('<I',uc.mem_read(a,4))[0]^0x80000000))
     events.append(('read',a,n,struct.unpack('<I',uc.mem_read(a,4))[0]))
    else:events.append(('write',a,n,value))
   h=u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory)
   if reset:u.reg_write(UC_ARM_REG_CPSR,0x33)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
   u.emu_start((syms[name] if isc else address)|1,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((events,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P-16,320)),bytes(u.mem_read(T,128)),bytes(u.mem_read(M,128))));u.hook_del(h)
  assert outs[0]==outs[1],(name,args,seed,mutation,[o[:2] for o in outs]);counts[name]+=1
 check(4,[1,P,2],0,1,reset=False) # Fresh-engine reproduction of the former warm-engine mismatch.
 for idx,id,attribute,seed,mutation in itertools.product([0,1],[0,1,3,4,7,8,255,256,257,0xffffffff],[0,1,128,255,256,0xffffffff],[0,0xa5a5a5a5],[0,1]):check(idx,[T,id,attribute] if idx==0 else [id,attribute],seed,mutation)
 for count,destination,seed,mutation in itertools.product([0,1,2,8],[P,P+4,P-4,T],[0,0xa5a5a5a5],[0,1]):check(2,[destination,P,count],seed,mutation)
 for idx,start,count,seed,mutation in itertools.product([3,4],[0,1,2,3,4,7,15,0xffffffff],[0,1,2,3,4,5,8,16],[0,0xa5a5a5a5],[0,1]):check(idx,[T,start,P,count] if idx==3 else [start,P,count],seed,mutation)
 receipt={'status':'PASS_COMPILED_ARM_MPU_WRITERS_MODELED_NATIVE','cases':sum(counts.values()),'fixture_cpu_state':'CPSR initialized per call; original failing case passes first in fresh engines without reset','by_provider':counts,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual five raw/wrapper attribute/word-copy/region writer bodies execute; modeled RAM/MMIO read/write traces and final words compared.','Byte truncation,index bank rejection,zero/single/multiple count,start wrap,bank transitions,overlapping forward copies and read mutations sampled. Flat modeled registers do not establish physical MPU alias behavior or hardware execution.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
