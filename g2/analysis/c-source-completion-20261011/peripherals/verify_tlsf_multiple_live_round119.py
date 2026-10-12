from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-tlsf-multiple-live-round119';D.mkdir(exist_ok=True)
paths=['file_pool_allocate_candidate/pool_allocate.c','tlsf_adjust_request_candidate/adjust.c','tlsf_locate_free_candidate/locate.c','file_pool_free_candidate/tlsf_mapping.c','file_pool_free_candidate/tlsf_absorb_leaves.c','file_pool_free_candidate/tlsf_free_lists.c','tlsf_prepare_allocation_candidate/prepare.c','tlsf_split_block_candidate/split.c','file_pool_free_candidate/tlsf_block_next.c','file_pool_free_candidate/tlsf_mark_free.c','file_pool_free_candidate/tlsf_lists.c','file_pool_free_candidate/tlsf_align.c','file_pool_free_candidate/tlsf_leaf.c','file_pool_free_candidate/pool_free.c','file_pool_free_candidate/tlsf_merge.c','file_pool_free_candidate/tlsf_merge_leaves.c','file_pool_free_candidate/tlsf_absorb.c'];S=[R/'components/audio'/p for p in paths];blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';P=0x20001000;N=0x20004000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as t:
 t=Path(t);shim=t/'shim.c';shim.write_text('void g2_file_close_error(const char*a,const char*b,unsigned c){}');e=t/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,g2_file_pool_allocate','-Wl,-u,g2_file_pool_free',*[str(p) for p in S],str(shim),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,b in segs:u.mem_write(a,b)
  cuts={(syms[s] if isc else a)&~1:op for op,s,a in [('remove','g2_tlsf_remove_free_block',0x4d003a),('error','g2_file_close_error',0x4d09b4)]};engines.append((u,cuts,isc))
 count=0
 for size,available,blocksize,mutation in itertools.product([0,1,4,12,13,64,112,113,124,125,128,129,240,241,256,257,512,0x3fffffff,0x40000000,0xfffffffc],[0,1],[128,256,512],range(6)):
  outs=[]
  for u,cuts,isc in engines:
   fl=blocksize.bit_length()-1-6
   u.mem_write(P,bytes(4096));u.mem_write(N,bytes(1024));u.mem_write(N,W(0,blocksize|1,P,P))
   for index in range(24*32):u.mem_write(P+0x74+index*4,W(P))
   u.mem_write(P+16,W((1<<fl) if available else 0));u.mem_write(P+20+fl*4,W(1 if available else 0));u.mem_write(P+0x74+fl*128,W(N));u.mem_write(N+blocksize+4,W(N,2))
   u.mem_write(0x78f4b4,W(1));u.mem_write(0x78f4b8,W(2));u.mem_write(0x78f4bc,W(4));u.mem_write(0x78f4c0,W(8));calls=[]
   def hook(uc,a,n,user):
    if a not in cuts:return
    op=cuts[a];r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0;calls.append((op,*r[:4 if op=='remove' else 3]))
    if op=='prepare':ret=r[1]+8 if r[1] else 0
    if op=='remove':return
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   h=u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,size);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((syms['g2_file_pool_allocate'] if isc else 0x4d0722)|1,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   pointers=[u.reg_read(UC_ARM_REG_R0)];states=[(pointers[0],bytes(u.mem_read(P,4096)),bytes(u.mem_read(N,1024)))]
   for request in [20,64]:
    u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,request);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((syms['g2_file_pool_allocate'] if isc else 0x4d0722)|1,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
    pointers.append(u.reg_read(UC_ARM_REG_R0));states.append((pointers[-1],bytes(u.mem_read(P,4096)),bytes(u.mem_read(N,1024))))
   order=list(itertools.permutations(range(3)))[mutation]
   for index in order:
    if not pointers[index]:continue
    u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_R1,pointers[index]);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((syms['g2_file_pool_free'] if isc else 0x4d0808)|1,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
    states.append((None,bytes(u.mem_read(P,4096)),bytes(u.mem_read(N,1024))))
   outs.append((calls,pointers,u.reg_read(UC_ARM_REG_SP),states));u.hook_del(h)
  assert outs[0]==outs[1],(size,available,blocksize,mutation,outs);count+=1
 receipt={'status':'PASS_COMPILED_ARM_TLSF_MULTIPLE_LIVE_FREE_ORDERS','cases':count,'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S},'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual pool allocation,adjust/find/remove,prepare/trim/split/insert,physical links,mark-used/free,free/merge/absorb/list insertion and pointer/size helpers execute. Error reporting is the sole controlled cut.','Valid128/256/512 byte initial blocks and empty lists,request/split thresholds and overflow compared with full control and1024 block bytes. Three allocation attempts with all six free-order permutations; full state compared after every operation. Realloc sequences,heap initialization and hardware gates remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
