from pathlib import Path
import subprocess,json
p=Path('g2/analysis/flashdb-provider-execution-20261010-implementation');s=(p.parent/'flashdb-provider-config-20261010-implementation'/'fdb_kvdb.c').read_text();i=s.index('    if (strlen(key) > FDB_KV_NAME_MAX)',s.index('static fdb_err_t create_kv_blob'));guard=s[i:s.index('\n    memset(&kv_hdr',i)]
code='#include <stddef.h>\n#define FDB_KV_NAME_ERR 5\nvoid diagnostic(void);\n#define FDB_INFO(...) diagnostic()\nsize_t strlen(const char*s){const char*p=s;while(*p)p++;return p-s;}\nint name_guard(const char*key){\n'+guard+'\nreturn 0;\n}\n'
(p/'name-guard.c').write_text(code);receipts=[]
for limit in range(61,66):
 cmd=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O0','-fno-builtin',f'-DFDB_KV_NAME_MAX={limit}','-c',str(p/'name-guard.c'),'-o',str(p/f'name-{limit}.o')];r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr;receipts.append({'command':cmd,'exit':r.returncode,'stderr':r.stderr});subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-e','name_guard',str(p/f'name-{limit}.o'),str(p/'stubs.o'),'-o',str(p/f'name-{limit}.elf')],check=True)
(p/'name-compile.json').write_text(json.dumps(receipts,indent=2)+'\n')
