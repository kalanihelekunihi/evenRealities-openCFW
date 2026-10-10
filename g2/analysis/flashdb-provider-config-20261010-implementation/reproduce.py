from pathlib import Path
import subprocess,json,hashlib,struct
p=Path('g2/analysis/flashdb-provider-config-20261010-implementation');old=p.parent/'flashdb-blob-build-interface-20261010-implementation'
for n in ['fdb_def.h']: (p/n).write_bytes((old/n).read_bytes())
for a,b in [('to-blob.bin','write-kv-header.bin'),('to.disasm.txt','write-kv-header.disasm.txt')]: (p/a).rename(p/b) if (p/a).exists() else None
s=(p/'fdb_kvdb.c').read_text();body=s[s.index('struct kv_hdr_data {'):s.index('typedef struct kv_hdr_data *')]
probe='#include <stdint.h>\n#include <stddef.h>\n#include <stdbool.h>\n#include <stdio.h>\n#include <time.h>\n#include "fdb_low_lvl.h"\n#define KV_STATUS_TABLE_SIZE FDB_STATUS_TABLE_SIZE(FDB_KV_STATUS_NUM)\n'+body+'\nconst unsigned evidence[]={FDB_WRITE_GRAN,KV_STATUS_TABLE_SIZE,offsetof(struct kv_hdr_data,magic),sizeof(struct kv_hdr_data),sizeof(struct kv_hdr_data)-offsetof(struct kv_hdr_data,magic),sizeof(struct fdb_kv),offsetof(struct fdb_kv,value_len),offsetof(struct fdb_kv,addr.value),sizeof(struct fdb_kvdb),offsetof(struct fdb_db,init_ok),offsetof(struct fdb_db,lock),offsetof(struct fdb_db,unlock)};\n'
(p/'probe.c').write_text(probe)
inc='g2/analysis/touch-compiler14-successor-2026-10-09/tools/14.2.Rel1/arm-gnu-toolchain-14.2.rel1-x86_64-arm-none-eabi/arm-none-eabi/include';rows=[]
for gran in [1,8,32,64,128]:
 for short in [False,True]:
  tag=f'g{gran}-'+('short' if short else 'default');d=p/tag;d.mkdir(exist_ok=True);(d/'fdb_cfg.h').write_text(f'#define FDB_USING_KVDB\n#define FDB_USING_FAL_MODE\n#define FDB_WRITE_GRAN {gran}\n#define FDB_KV_CACHE_TABLE_SIZE 64\n#define FDB_SECTOR_CACHE_TABLE_SIZE 64\n')
  cmd=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-I'+str(d),'-I'+str(p),'-isystem',inc,'-c',str(p/'probe.c'),'-o',str(d/'probe.o')]+(['-fshort-enums'] if short else [])
  r=subprocess.run(cmd,capture_output=True,text=True);(d/'compile.json').write_text(json.dumps({'command':cmd,'exit':r.returncode,'stderr':r.stderr},indent=2));assert r.returncode==0,r.stderr
  subprocess.run(['arm-none-eabi-objcopy','-O','binary','-j','.rodata',str(d/'probe.o'),str(d/'constants.bin')],check=True)
  rows.append({'variant':tag,'columns':['write_gran','status_bytes','magic_offset','header_size','write_count','kv_size','value_len_offset','value_address_offset','db_size','init_offset','lock_offset','unlock_offset'],'values':struct.unpack('<12I',(d/'constants.bin').read_bytes())})
(p/'probe-results.json').write_text(json.dumps(rows,indent=2)+'\n')
raw=Path('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();rec=[]
for name,va,n in [('get-kv',0x5444f4,86),('get-blob',0x54454a,104),('write-kv-header',0x5445b2,64)]:
 b=(p/(name+'.bin')).read_bytes();assert b==raw[va-0x437fe0:va-0x437fe0+n];rec.append(dict(name=name,address=hex(va),length=n,file_offset=hex(va-0x437fe0),sha256=hashlib.sha256(b).hexdigest()))
(p/'receipts.json').write_text(json.dumps({'locked_raw_sha256':hashlib.sha256(raw).hexdigest(),'ranges':rec},indent=2)+'\n')
print(json.dumps(rows))
