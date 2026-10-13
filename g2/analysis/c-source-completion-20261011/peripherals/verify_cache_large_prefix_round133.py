from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools,sys
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-cache-contract-round133';D.mkdir(exist_ok=True);S=D/'cache_candidate.c'
if '--baseline' in sys.argv or '--selected' in sys.argv:S=R/'components/audio/uart_thread_source_candidate/display_ble_cache_maintenance.c'
blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';W=lambda *v:struct.pack('<'+'I'*len(v),*v);ram=[0x200007bc,0x200007d4,0x20000630,0x20000c20];barriers={bytes.fromhex('bff35f8f'):'dmb',bytes.fromhex('bff34f8f'):'dsb',bytes.fromhex('bff36f8f'):'isb'}
with tempfile.TemporaryDirectory() as t:
 t=Path(t);shim=t/'shim.c';shim.write_text('void audio_uart_checksum_copy(void*a,const void*b,unsigned c){}');e=t/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_privacy_cache_maintenance',str(S),str(shim),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,4096)
  for a,b in segs:u.mem_write(a,b)
  engines.append((u,{},isc))
 count=0
 for length,clean,mutation in itertools.product([0x7ffffff0,0x7ffffffe,0x7fffffff],[0,1,255],[0,1]):
  outs=[]
  for u,cuts,isc in engines:
   u.mem_write(0xe000ed14,W(0x10000));u.mem_write(0x20001000,W(0x2000201f,length));events=[];writes=[]
   def code(uc,a,n,user):
    if n==4 and (op:=barriers.get(bytes(uc.mem_read(a,4)))):events.append((op,))
   def memory(uc,access,a,n,value,user):
    if a not in [0x20001000,0x20001004,0xe000ed14,0xe000ef70,0xe000ef5c]:return
    events.append(('read',a,n,struct.unpack('<I',uc.mem_read(a,4))[0]) if access==16 else ('write',a,n,value))
    if access==17:
     writes.append(value)
     if len(writes)==10:uc.emu_stop()
    if mutation and access==16 and a==0x20001004:uc.mem_write(0x20001000,W(0x2000203f))
   h=u.hook_add(UC_HOOK_CODE,code);m=u.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,memory);u.reg_write(UC_ARM_REG_CPSR,0x33);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20001000);u.reg_write(UC_ARM_REG_R1,clean);u.emu_start((syms['audio_ble_privacy_cache_maintenance'] if isc else 0x475014)|1,0x600000,count=10000);assert len(writes)==10
   outs.append(events);u.hook_del(h);u.hook_del(m)
  if outs[0]!=outs[1]:
   failure={'status':'NATIVE_CACHE_RANGE_TRACE_MISMATCH','length':length,'clean':clean,'mutation':mutation,'native':outs[0],'source':outs[1],'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest()};(D/'baseline-mismatch.json').write_text(json.dumps(failure,indent=2)+'\n');print(json.dumps(failure));raise SystemExit(0 if '--baseline' in sys.argv else 1)
  count+=1
 receipt={'status':'PASS_COMPILED_ARM_CACHE_LARGE_RANGE_PREFIX_TRACE','cases':count,'source_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Native and source execution stopped after first10 cache writes; read/barrier/write prefix and address mutation compared.','No terminal claim for huge positive lengths; unsigned wrap preserved,physical effects and full image gates remain open.']};(D/'large-range-prefix-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
