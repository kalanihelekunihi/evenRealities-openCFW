from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-tlsf-connected-locate-round116';D.mkdir(exist_ok=True)
paths=['file_pool_allocate_candidate/pool_allocate.c','tlsf_adjust_request_candidate/adjust.c','tlsf_locate_free_candidate/locate.c','file_pool_free_candidate/tlsf_mapping.c','file_pool_free_candidate/tlsf_absorb_leaves.c','file_pool_free_candidate/tlsf_free_lists.c'];S=[R/'components/audio'/p for p in paths];blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';P=0x20001000;N=0x20004000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as t:
 t=Path(t);shim=t/'shim.c';shim.write_text('void g2_file_close_error(const char*a,const char*b,unsigned c){} void*g2_tlsf_prepare_allocation(void*a,void*b,unsigned c){return 0;}');e=t/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,g2_file_pool_allocate',*[str(p) for p in S],str(shim),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,b in segs:u.mem_write(a,b)
  cuts={(syms[s] if isc else a)&~1:op for op,s,a in [('prepare','g2_tlsf_prepare_allocation',0x4d04e6),('remove','g2_tlsf_remove_free_block',0x4d003a),('error','g2_file_close_error',0x4d09b4)]};engines.append((u,cuts,isc))
 count=0
 for size,available,blocksize,mutation in itertools.product([0,1,4,12,13,64,124,125,128,129,255,256,0x3fffffff,0x40000000,0xfffffffc],[0,1],[64,128,256],[0,1]):
  outs=[]
  for u,cuts,isc in engines:
   u.mem_write(P,bytes(4096));u.mem_write(N,W(0,blocksize|1,P,P));u.mem_write(P+16,W(2 if available else 0));u.mem_write(P+24,W(1 if available else 0));u.mem_write(P+0x74+128,W(N));u.mem_write(0x78f4b4,W(1));u.mem_write(0x78f4b8,W(2));calls=[]
   def hook(uc,a,n,user):
    if a not in cuts:return
    op=cuts[a];r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0;calls.append((op,*r[:4 if op=='remove' else 3]))
    if op=='prepare':ret=r[1]+8 if r[1] else 0
    if mutation and op=='remove':uc.mem_write(P+16,W(0));uc.mem_write(N+4,W(32))
    if op=='remove':return
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   h=u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,size);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((syms['g2_file_pool_allocate'] if isc else 0x4d0722)|1,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(P,4096)),bytes(u.mem_read(N,16))));u.hook_del(h)
  assert outs[0]==outs[1],(size,available,blocksize,mutation,outs);count+=1
 receipt={'status':'PASS_COMPILED_ARM_CONNECTED_TLSF_ADJUST_LOCATE_REMOVE','cases':count,'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S},'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual pool allocate/request adjustment/align/size mapping/search/find/block-size and actual free-list removal execute; prepare/error remain controlled cuts.','One available size class plus empty bitmap,size overflow/assertion boundaries and remove mutation compared. Full allocator/free/realloc and hardware gates remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
