from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-memory-config-round125';S=D/'memory_config_candidate.c';blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';W=lambda *v:struct.pack('<'+'I'*len(v),*v);ram=[0x200007bc,0x200007d4,0x20000630,0x20000c20]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);shim=t/'shim.c';shim.write_text('unsigned audio_uart_mpu_reset_4d44e2(void){return 0;} unsigned audio_uart_mpu_attributes_4d450c(const void*a,unsigned b){return 0;} unsigned audio_uart_mpu_region_4d4596(const void*a,unsigned b){return 0;} unsigned audio_uart_mpu_enable_4d44ec(unsigned a,unsigned b){return 0;} void audio_uart_checksum_copy(void*a,const void*b,unsigned c){} void audio_ble_privacy_cache_maintenance(const void*a,unsigned char b){}');e=t/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_heap_memory_configure_4840c8',str(S),str(shim),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,b in segs:u.mem_write(a,b)
  cuts={(syms[s] if isc else a)&~1:op for op,s,a in [('reset','audio_uart_mpu_reset_4d44e2',0x4d44e2),('attributes','audio_uart_mpu_attributes_4d450c',0x4d450c),('region','audio_uart_mpu_region_4d4596',0x4d4596),('enable','audio_uart_mpu_enable_4d44ec',0x4d44ec),('copy','audio_uart_checksum_copy',0x439c04),('cache','audio_ble_privacy_cache_maintenance',0x475014)]};engines.append((u,cuts,isc))
 count=0
 for mutation,ret,seed in itertools.product([0,1,2],[0,1,3,0xffffffff],[0,0xa5a5a5a5]):
  outs=[]
  for u,cuts,isc in engines:
   for i,a in enumerate(ram):u.mem_write(a,W(*[(seed+i+j)&0xffffffff for j in range(6)]))
   calls=[]
   def hook(uc,a,n,user):
    if a not in cuts:return
    op=cuts[a];r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]
    if op=='copy':
     data=bytes(uc.mem_read(r[1],r[2]));calls.append((op,data.hex(),r[2]));uc.mem_write(r[0],data)
     if mutation:uc.mem_write(r[0]+4,W(0x12345678))
    elif op in ['region','attributes']:
     calls.append((op,r[0] if r[0] in ram else 'stack',bytes(uc.mem_read(r[0],24 if op=='region' else 12)).hex(),r[1]))
     if mutation:uc.mem_write(ram[0],W(1,2,3,4,5,6))
     if mutation==2:uc.mem_write(r[0],W(0x87654321))
    elif op in ['enable','cache']:calls.append((op,*r[:2]))
    else:calls.append((op,))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   h=u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((syms['audio_uart_heap_memory_configure_4840c8'] if isc else 0x4840c8)|1,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,u.reg_read(UC_ARM_REG_SP),[bytes(u.mem_read(a,24)) for a in ram]));u.hook_del(h)
  assert outs[0]==outs[1],(mutation,ret,seed,outs);count+=1
 receipt={'status':'PASS_COMPILED_ARM_MEMORY_CONFIGURATION_NATIVE','cases':count,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Root configuration body and source-owned non-executable ROM descriptor words execute; MPU/copy/cache children controlled cuts.','Call order,descriptor contents,copy-output/global/stack mutation and ignored child statuses compared. MPU register/barrier/cache effects and physical hardware remain unproved.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
