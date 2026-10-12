from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();s=s[s.index('/* Native pattern332b94'):s.index('/* Native completion332cd0')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){return memset(p,v,n);}
'''+s+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);static const uint8_t pn[]={0xff,0xc1,0xfb,0xe8,0x4c,0x90,0x72,0x8b,0xe7,0xb3,0x51,0x89,0x63,0xab,0x23,0x23};unsigned cases=0;uint8_t *p=(void *)0x840000;
for(unsigned n=0;n<256;n++)for(unsigned selector=0;selector<10;selector++){memset(p,0xa5,300);unsigned result=opencfw_em9305_command_pattern_332b94(n,selector,(uintptr_t)p);assert(p[0]==0xa5&&p[1]==n&&p[n+3]==0xa5);if(selector>=8||selector==3){assert(result==n&&p[2]==selector&&p[3]==0xa5);}else if(selector==0){assert(result==0x840002+n);if(!n)assert(p[2]==0);else assert(memcmp(p+2,pn,n<sizeof pn?n:sizeof pn)==0);}else{unsigned v=selector==1?15:selector==2?85:selector==4?255:selector==5?0:selector==6?240:170;assert(result==0x840002);for(unsigned j=0;j<n;j++)assert(p[j+2]==v);if(!n)assert(p[2]==selector);}cases++;}
assert(opencfw_em9305_command_pn9_332c50((uintptr_t)p,256)==0x840100);assert(opencfw_em9305_command_pn9_332c50((uintptr_t)p,257)==0x840001);cases+=2;printf("PASS %u\n",cases);}
''';p=Path(__file__).with_name('command-pattern-host.c');p.write_text(h);a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/p && /tmp/p'],text=True);print(a.strip());p.with_name('command-pattern-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual pattern/PN9 source with real memset. Header/payload overlap, length0..255, selector0..9, PN9 known16-byte prefix and low-byte outer count. No target runtime proof.'},indent=2)+'\n')
