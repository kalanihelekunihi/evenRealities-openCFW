from pathlib import Path
import hashlib,json,struct,subprocess,ctypes,sys
sys.path.insert(0,'/tmp/mspi-enable-python-deps')
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;R=next(p for p in D.parents if (p/'g2/blobs').exists());S=R/'g2/analysis/flashdb-provider-config-20261010-implementation';raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(raw)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
assert sha((S/'fdb_def.h').read_bytes())=='748d07c650c6c0be98b380af4af43a556791f9a37cc205167176df0c7ec8e10b'
assert sha((S/'fdb_kvdb.c').read_bytes())=='96e09b3f7b8b0dc77b51cb387701e4e9ef7a5cbce2eaa606380962aff25582ac'
objcopy='/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-objcopy'
inc=R/'g2/analysis/touch-compiler14-successor-2026-10-09/tools/14.2.Rel1/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-eabi/arm-none-eabi/include'
probe=D/'layout.c';probe.write_text('#include <stddef.h>\n#include <stdint.h>\n#include <stdbool.h>\n#include "fdb_cfg.h"\n#include "fdb_def.h"\nconst unsigned evidence[]={sizeof(struct fdb_kvdb),offsetof(struct fdb_kvdb,kv_cache_table),offsetof(struct fdb_kvdb,sector_cache_table),sizeof(struct kv_cache_node),sizeof(struct kvdb_sec_info),offsetof(struct kv_cache_node,addr),offsetof(struct kvdb_sec_info,addr),offsetof(struct fdb_kvdb,user_data)};\n')
layouts=[]
for k,s in [(64,64),(61,65)]:
 v=D/f'k{k}-s{s}';v.mkdir(exist_ok=True);(v/'fdb_cfg.h').write_text(f'#define FDB_USING_KVDB\n#define FDB_USING_FAL_MODE\n#define FDB_WRITE_GRAN 1\n#define FDB_KV_CACHE_TABLE_SIZE {k}\n#define FDB_SECTOR_CACHE_TABLE_SIZE {s}\n')
 cmd=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-fshort-enums','-I'+str(v),'-I'+str(S),'-isystem',str(inc),'-c',str(probe),'-o',str(v/'layout.o')];cp=subprocess.run(cmd,capture_output=True,text=True);assert cp.returncode==0,cp.stderr
 subprocess.run([objcopy,'--dump-section','.rodata='+str(v/'constants.bin'),str(v/'layout.o')],check=True);values=list(struct.unpack('<8I',(v/'constants.bin').read_bytes()));layouts.append({'KV_count':k,'sector_count':s,'values':values,'command':cmd,'object_sha256':sha((v/'layout.o').read_bytes())})
assert layouts[0]['values']==[2220,168,680,8,24,4,4,2216];assert layouts[1]['values']==[2220,168,656,8,24,4,4,2216]
t=(S/'fdb_kvdb.c').read_text();a=t.index('static void update_kv_cache(');i=t.index('{',a);depth=0
while i<len(t):
 depth+=(t[i]=='{')-(t[i]=='}');i+=1
 if not depth:break
body=t[a:i]
pre=r'''#include <stdint.h>
#include <stddef.h>
#define FDB_KV_CACHE_TABLE_SIZE 64
#define FDB_DATA_UNUSED 0xffffffffu
struct node{uint16_t name_crc,active;uint32_t addr;};
typedef struct{struct node kv_cache_table[64];}*fdb_kvdb_t;
static uint32_t fdb_calc_crc32(uint32_t seed,const void*name,size_t len){return 0x77770000u;}
'''
post=r'''
static struct{struct node kv_cache_table[64];}db;
void test(int mode){for(int i=0;i<64;i++){db.kv_cache_table[i].name_crc=i;db.kv_cache_table[i].active=5;db.kv_cache_table[i].addr=0x10000+i;}if(mode==1)db.kv_cache_table[63].name_crc=0x7777;update_kv_cache((fdb_kvdb_t)&db,"name",4,0x12345678);}
const void*output(void){return &db;}
'''
c=D/'source-projection.c';c.write_text(pre+body+post);dll=D/'source-projection.dylib';subprocess.run(['clang','-O0','-shared','-fPIC',str(c),'-o',str(dll)],check=True);l=ctypes.CDLL(str(dll));l.output.restype=ctypes.c_void_p
extents=[(0x543cc0,0x543cec,'sector-lookup'),(0x543d1c,0x543e28,'KV-update')];receipts=[{'start':hex(a),'end':hex(b),'label':n,'sha256':sha(raw[a-0x437fe0:b-0x437fe0])} for a,b,n in extents]
assert [x['sha256'] for x in receipts]==['0d15a85efe5382c95472f445049055bc2bc4c863c55684c37857445b04581bcc','401e21dae4030689d43d37aad6726150e094a8d5f2b263dac43d0b1d01b40932']
B=0x20080000;SP=0x200ff000;NAME=0x20090000;results=[]
def cpu():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x438000,0x360000);u.mem_write(0x438000,raw[32:]);u.mem_map(0x20000000,0x100000);u.mem_map(0x100000,0x1000);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x100001);return u
for last_hit in [True,False]:
 u=cpu();u.mem_write(B,b'\xa5'*2304)
 for n in range(64):u.mem_write(B+680+24*n+4,struct.pack('<I',0x10000+n))
 target=0x1003f if last_hit else 0xabcdef00
 # index64 is an out-of-table readable poison: useful bound guard, not a sector.
 u.mem_write(B+680+24*64+4,struct.pack('<I',target));before=bytes(u.mem_read(B,2304));reads=[];writes=[]
 u.reg_write(UC_ARM_REG_R0,B);u.reg_write(UC_ARM_REG_R1,target);u.reg_write(UC_ARM_REG_R4,0x11223344)
 def code(uc,a,size,user):
  if a==0x100000:uc.emu_stop();return
  assert 0x543cc0<=a<0x543cec,hex(a)
 def read(uc,access,a,size,value,user):
  if B<=a<B+2304:reads.append((a,size));assert B+684<=a<=B+684+24*63 and size==4
 def write(uc,access,a,size,value,user):writes.append((a,size));assert SP-4<=a and a+size<=SP
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(0x543cc1,0,count=2000)
 expected=B+680+24*63 if last_hit else 0;assert u.reg_read(UC_ARM_REG_R0)==expected and len(reads)==64 and reads==[(B+684+24*n,4) for n in range(64)];assert bytes(u.mem_read(B,2304))==before and u.reg_read(UC_ARM_REG_R4)==0x11223344 and u.reg_read(UC_ARM_REG_SP)==SP
 results.append({'case':'sector-last-hit' if last_hit else 'sector-miss-poison64','return':hex(expected),'counted_cache_reads':64,'reads':[(hex(a),s) for a,s in reads],'database_unchanged':True,'no_mock_providers':True,'ABI_preserved':True})
for mode in [1,0]:
 u=cpu();u.mem_write(B,b'\xa5'*2304);u.mem_write(NAME,b'name')
 for n in range(64):u.mem_write(B+168+8*n,struct.pack('<HHI',0x7777 if mode==1 and n==63 else n,5,0x10000+n))
 u.mem_write(B+680,struct.pack('<HHI',0x7777,9,0x10040));before=bytes(u.mem_read(B,2304));reads=[];writes=[];calls=[];saved={r:0x78900000+n for n,r in enumerate([UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7])}
 for r,v in saved.items():u.reg_write(r,v)
 for r,v in [(UC_ARM_REG_R0,B),(UC_ARM_REG_R1,NAME),(UC_ARM_REG_R2,4),(UC_ARM_REG_R3,0x12345678)]:u.reg_write(r,v)
 def code(uc,a,size,user):
  if a==0x100000:uc.emu_stop();return
  if 0x543d1c<=a<0x543e28:return
  assert a==0x585840,hex(a);assert [uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]==[0,NAME,4];calls.append('CRC32-projection');uc.reg_write(UC_ARM_REG_R0,0x77770000);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 def read(uc,access,a,size,value,user):
  if B<=a<B+2304:reads.append((a,size));assert B+168<=a and a+size<=B+680
 def write(uc,access,a,size,value,user):
  writes.append((a,size));assert B+168<=a and a+size<=B+680 or SP-256<=a and a+size<=SP
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(0x543d1d,0,count=10000)
 l.test(mode);source_out=ctypes.string_at(l.output(),512);assert bytes(u.mem_read(B+168,512))==source_out;assert bytes(u.mem_read(B,168))==before[:168] and bytes(u.mem_read(B+680,1624))==before[680:];assert u.reg_read(UC_ARM_REG_SP)==SP and all(u.reg_read(r)==v for r,v in saved.items());assert calls==['CRC32-projection']
 visited_slots=sorted({(a-B-168)//8 for a,s in reads});assert visited_slots==list(range(64))
 results.append({'case':'KV-last-match' if mode==1 else 'KV-miss-poison64-replacement','read_slots':visited_slots,'source_output_equal':True,'cache_sha256_after':sha(source_out),'reads':[(hex(a),s) for a,s in reads],'writes':[(hex(a),s) for a,s in writes],'prefix_and_sector_guard_unchanged':True,'CRC_provider_mock':True,'ABI_preserved':True})
(D/'results.json').write_text(json.dumps({'layouts':layouts,'layout_labels':['database_size','KV_cache_offset','sector_cache_offset','KV_node_size','sector_node_size','KV_addr_offset','sector_addr_offset','KVDB_userdata_offset'],'stride_equal_candidates':[{'KV':256-3*s,'sector':s} for s in range(1,86)],'cases':results,'stock_sha256':sha(raw),'extents':receipts,'source_body_sha256':sha(body.encode()),'source_header_sha256':sha((S/'fdb_def.h').read_bytes()),'source_file_sha256':sha((S/'fdb_kvdb.c').read_bytes()),'scope':'cache memory/layout only; no database flash/storage operation'},indent=2)+'\n');print('PASS 4 cache-boundary cases and 2 equal-size header layouts; counts independently constrained64/64')
