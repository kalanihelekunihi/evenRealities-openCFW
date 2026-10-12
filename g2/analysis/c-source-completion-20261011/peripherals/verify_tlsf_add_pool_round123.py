from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
B=Path(__file__).parent;R=B.parents[2];D=B/'root-tlsf-add-pool-round123';S=[D/'add_pool_candidate.c',D/'tlsf_reallocate_candidate.c']+[R/'components/audio'/p for p in ['tlsf_split_block_candidate/split.c','file_pool_free_candidate/tlsf_absorb_leaves.c','file_pool_free_candidate/tlsf_block_next.c','tlsf_prepare_allocation_candidate/prepare.c']];blob=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701';P=0x20001000;N=0x20004000;W=lambda *v:struct.pack('<'+'I'*len(v),*v);providers=[('g2_tlsf_add_pool_4d0608',0x4d0608),('g2_tlsf_block_set_free_4cfdc0',0x4cfdc0),('g2_tlsf_block_set_used_4cfdce',0x4cfdce),('g2_tlsf_block_clear_prev_free',0x4cfdf6)]
with tempfile.TemporaryDirectory() as t:
 t=Path(t);shim=t/'shim.c';shim.write_text('void audio_ble_hci_boot_log_4733ee(const char*p,...){} void g2_tlsf_block_insert(void*a,void*b){} void g2_file_close_error(const char*a,const char*b,unsigned c){}');e=t/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0],*['-Wl,-u,'+n for n,a in providers],*[str(p) for p in S],str(shim),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=line.split())==3}
 with e.open('rb') as f:segs=[(p['p_vaddr'],p.data()) for p in ELFFile(f).iter_segments() if p['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,b in segs:u.mem_write(a,b)
  cuts={(syms[s] if isc else a)&~1:op for op,s,a in [('log','audio_ble_hci_boot_log_4733ee',0x4733ee),('insert','g2_tlsf_block_insert',0x4d019a),('error','g2_file_close_error',0x4d09b4)]};engines.append((u,cuts,isc))
 counts={n:0 for n,a in providers}
 def check(idx,ptr=N,size=64,free=1,prev=2,overhead=4,offset=8,word=0xa5a5a5a5,mutation=0):
  outs=[];name,address=providers[idx]
  for u,cuts,isc in engines:
   u.mem_write(N-32,bytes([0xa5])*2048);u.mem_write(N+4,W(word));u.mem_write(0x78f4b4,W(free,prev,overhead,offset,12,256));calls=[]
   def hook(uc,a,n,user):
    if a not in cuts:return
    op=cuts[a];r=[uc.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];ret=0
    if op=='insert':
     calls.append((op,*r[:2]))
     if mutation:uc.mem_write(r[1]+4,W(64|free|prev));uc.mem_write(0x78f4b8,W(8 if mutation==2 else prev))
    elif op=='log':calls.append((op,*r[:2 if r[0]==0x72f468 else 3]));ret=0x12345678
    else:calls.append((op,*r))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   h=u.hook_add(UC_HOOK_CODE,hook);args=[P,ptr,size] if idx==0 else [N];u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,val in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(reg,val)
   u.emu_start((syms[name] if isc else address)|1,0x600000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,u.reg_read(UC_ARM_REG_R0) if idx==0 else None,u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(N-32,2048))));u.hook_del(h)
  assert outs[0]==outs[1],(name,ptr,size,free,prev,overhead,offset,word,mutation,outs);counts[name]+=1
 for ptr,size,flags,overhead,offset,mutation in itertools.product(range(N,N+4),[0,1,8,19,20,24,64,256,264,0xffffffff],[(1,2),(4,8)],[0,4,8],[8,12],[0,1,2]):check(0,ptr,size,*flags,overhead,offset,mutation=mutation)
 for idx,free,prev,word in itertools.product(range(1,4),[0,1,4,0x80000000],[0,2,8,0x80000000],[0,1,2,3,0xa5a5a5a5,0xffffffff]):check(idx,free=free,prev=prev,word=word)
 receipt={'status':'PASS_COMPILED_ARM_TLSF_ADD_POOL_FLAGS_NATIVE','cases':sum(counts.values()),'by_provider':counts,'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in S},'payload_sha256':hashlib.sha256(blob).hexdigest(),'limits':['Actual add-pool,size/link/physical-next/flag helpers execute; insertion/logger/error controlled cuts.','Alignment,size bounds/word wrap,overheads0/4/8,header offsets8/12,configured flag masks and insertion mutations compared. Actual startup/control insertion and hardware gates remain.']};(D/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
