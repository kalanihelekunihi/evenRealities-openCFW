from pathlib import Path
import subprocess,json
p=Path('g2/analysis/flashdb-provider-execution-20261010-implementation');pre=p.parent/'flashdb-provider-config-20261010-implementation';s=(pre/'fdb_kvdb.c').read_text()
for n in ['fdb_def.h','fdb_low_lvl.h']: (p/n).write_bytes((pre/n).read_bytes())
(p/'fdb_cfg.h').write_text('#define FDB_USING_KVDB\n#define FDB_USING_FAL_MODE\n#define FDB_WRITE_GRAN 1\n#define FDB_KV_CACHE_TABLE_SIZE 64\n#define FDB_SECTOR_CACHE_TABLE_SIZE 64\n')
def extract(start):
 i=s.index(start);b=s.index('{',i);depth=1;j=b+1
 while depth:
  depth+= (s[j]=='{')-(s[j]=='}');j+=1
 return s[i:j]
struct=s[s.index('struct kv_hdr_data {'):s.index('typedef struct kv_hdr_data *')]
body='#include <stdint.h>\n#include <stddef.h>\n#include <stdbool.h>\n#include <stdio.h>\n#include <time.h>\n#include "fdb_low_lvl.h"\n#define KV_STATUS_TABLE_SIZE FDB_STATUS_TABLE_SIZE(FDB_KV_STATUS_NUM)\n#define KV_MAGIC_OFFSET offsetof(struct kv_hdr_data,magic)\n#define db_init_ok(db) (((fdb_db_t)db)->init_ok)\n#define db_name(db) (((fdb_db_t)db)->name)\n#define db_lock(db) do{if(((fdb_db_t)db)->lock)((fdb_db_t)db)->lock((fdb_db_t)db);}while(0)\n#define db_unlock(db) do{if(((fdb_db_t)db)->unlock)((fdb_db_t)db)->unlock((fdb_db_t)db);}while(0)\n#undef FDB_INFO\n#define FDB_INFO(...) diagnostic()\nvoid diagnostic(void);\nbool find_kv(fdb_kvdb_t,const char*,fdb_kv_t);\n'+struct+'typedef struct kv_hdr_data *kv_hdr_data_t;\n'+extract('static size_t get_kv(')+'\n'+extract('size_t fdb_kv_get_blob(')+'\n'+extract('static fdb_err_t write_kv_hdr(')+'\nsize_t test_get(fdb_kvdb_t d,const char*k,void*b,size_t n,size_t*l){return get_kv(d,k,b,n,l);}\nfdb_err_t test_write(fdb_kvdb_t d,uint32_t a,kv_hdr_data_t h){return write_kv_hdr(d,a,h);}\n'
(p/'candidate.c').write_text(body)
(p/'stubs.S').write_text('.syntax unified\n.thumb\n.section .text\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\n bkpt #0\n bx lr\n' for n in ['find_kv','_fdb_flash_read','_fdb_flash_write','_fdb_write_status','diagnostic']))
inc='g2/analysis/touch-compiler14-successor-2026-10-09/tools/14.2.Rel1/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-eabi/arm-none-eabi/include'
cmd=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O0','-fshort-enums','-fno-inline','-I'+str(p),'-isystem',inc,'-c',str(p/'candidate.c'),'-o',str(p/'candidate.o')];r=subprocess.run(cmd,capture_output=True,text=True);(p/'compile.json').write_text(json.dumps({'command':cmd,'exit':r.returncode,'stderr':r.stderr},indent=2));assert r.returncode==0,r.stderr
subprocess.run(['arm-none-eabi-as','-mcpu=cortex-m4','-mthumb',str(p/'stubs.S'),'-o',str(p/'stubs.o')],check=True);subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',str(p/'candidate.o'),str(p/'stubs.o'),'-o',str(p/'candidate.elf')],check=True)
