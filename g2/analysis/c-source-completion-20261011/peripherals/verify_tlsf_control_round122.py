from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-tlsf-control-round122';S=D/'tlsf_control_candidate.c';blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';P=0x20004000;W=lambda *v:struct.pack('<'+'I'*len(v),*v);providers=[('g2_tlsf_control_construct_4d0524',0x4d0524),('g2_tlsf_control_create_4d06b4',0x4d06b4)]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);shim=t/'shim.c';shim.write_text('void audio_ble_hci_boot_log_4733ee(const char*p,...){}');e=t/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0],'-Wl,-u,'+providers[1][0],str(S),str(shim),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,b in segs:u.mem_write(a,b)
  engines.append((u,isc))
 counts={n:0 for n,a in providers}
 for idx,ptr,mutation in itertools.product(range(2),[0,*range(P,P+8),P+64],[0,1]):
  outs=[];name,address=providers[idx]
  for u,isc in engines:
   u.mem_write(P,bytes([0xa5])*4096);calls=[];faults=[]
   def hook(uc,a,n,user):
    if a!=((syms['audio_ble_hci_boot_log_4733ee'] if isc else 0x4733ee)&~1):return
    calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
    if mutation:uc.mem_write(P,W(1,2,3,4))
    uc.reg_write(UC_ARM_REG_R0,0x12345678);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,a,n,value,user):faults.append((access,a,n,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_INVALID,fault);u.reg_write(UC_ARM_REG_R0,ptr);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   try:u.emu_start((syms[name] if isc else address)|1,0x600000,count=10000)
   except UcError:assert faults
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,u.reg_read(UC_ARM_REG_R0) if idx==1 and not faults else None,None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P,4096))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(name,ptr,mutation,outs);counts[name]+=1
 receipt={'status':'PASS_COMPILED_ARM_TLSF_CONTROL_NATIVE','cases':sum(counts.values()),'by_provider':counts,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual control construction and create execute; logger is controlled cut. All3188 control bytes plus surrounding storage compared.','Aligned/misaligned/NULL pointers,log arguments/mutations/native write faults sampled; add-pool/startup/hardware gates remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
