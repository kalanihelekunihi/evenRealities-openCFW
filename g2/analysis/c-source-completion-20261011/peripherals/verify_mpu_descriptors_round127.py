from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-mpu-descriptors-round127';S=D/'mpu_descriptors_candidate.c';blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';P=0x20004000;C=0xe000ed94;W=lambda *v:struct.pack('<'+'I'*len(v),*v);providers=[('audio_uart_mpu_attributes_4d450c',0x4d450c),('audio_uart_mpu_region_4d4596',0x4d4596)]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);shim=t/'shim.c';shim.write_text('void audio_uart_mpu_attribute_write_4d4434(unsigned a,unsigned b){} void audio_uart_mpu_regions_write_4d44d2(unsigned a,const unsigned*b,unsigned c){}');e=t/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0],'-Wl,-u,'+providers[1][0],str(S),str(shim),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,4096)
  for a,b in segs:u.mem_write(a,b)
  cuts={(syms[s] if isc else a)&~1:op for op,s,a in [('attribute','audio_uart_mpu_attribute_write_4d4434',0x4d4434),('region','audio_uart_mpu_regions_write_4d44d2',0x4d44d2)]};engines.append((u,cuts,isc))
 counts={n:0 for n,a in providers}
 def check(idx,count,id=0,seed=0,control=0,mutation=0,ptr=P):
  outs=[];name,address=providers[idx]
  for u,cuts,isc in engines:
   u.mem_write(P,bytes(1024));u.mem_write(C,W(control))
   for i in range(16):
    if idx==0:u.mem_write(P+i*11,bytes([(id+i)&255]+[(seed+j*17+i)&255 for j in range(1,11)]))
    else:u.mem_write(P+i*24,W(id if i==0 else i,(seed*0x1234567+i)&0xffffffff,seed|(seed<<8)|(seed<<16),(0x23456789+seed+i)&0xffffffff,seed*0x1020304&0xffffffff,seed))
   calls=[];faults=[]
   def hook(uc,a,n,user):
    if a not in cuts:return
    op=cuts[a];r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
    if op=='attribute':
     calls.append((op,*r[:2]))
     if mutation:u.mem_write(P+11,bytes([8 if mutation==2 else 1]));u.mem_write(P+12,bytes([0]))
    else:calls.append((op,r[0],bytes(uc.mem_read(r[1],r[2]*8)).hex(),r[2]))
    uc.reg_write(UC_ARM_REG_R0,0x12345678);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,a,n,value,user):faults.append((access,a,n));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_INVALID,fault);u.reg_write(UC_ARM_REG_R0,ptr);u.reg_write(UC_ARM_REG_R1,count);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   try:u.emu_start((syms[name] if isc else address)|1,0x600000,count=10000)
   except UcError:assert faults
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P,1024))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(name,count,id,seed,control,mutation,ptr,outs);counts[name]+=1
 for count,id,seed,control,mutation in itertools.product([0,1,2,3],[0,6,7,8,255],[0,1,2,3,128,255],[0,1],[0,1,2]):check(0,count,id,seed,control,mutation)
 for count,id,seed,control in itertools.product([0,1,2,8,16],[0,1,8,15,16,17,0xffffffff],[0,1,128,255],[0,1]):check(1,count,id,seed,control)
 for idx,count,control in itertools.product(range(2),[0,1],[0,1]):check(idx,count,control=control,ptr=0)
 receipt={'status':'PASS_COMPILED_ARM_MPU_DESCRIPTORS_NATIVE','cases':sum(counts.values()),'by_provider':counts,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual attribute/region parsing executes; attribute and packed-region writers are controlled cuts.','11/24 byte strides,low-byte packing,word wrap,validation/NULL ordering,next descriptor mutation and partial writes compared. Pathological overflowing counts beyond local native stack and physical MPU effects remain unproved.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
