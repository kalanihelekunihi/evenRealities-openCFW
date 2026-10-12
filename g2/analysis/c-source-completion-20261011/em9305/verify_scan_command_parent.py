from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated command-dispatch parent330c60'):s.index('/* Authenticated scan command children30ccf8')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned fail,mutate,allocated,status,sends;static uintptr_t sent;
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){return memcpy(d,s,n);}
void *opencfw_em9305_memset(void *d,uint32_t v,uint32_t n){return memset(d,v,n);}
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t command){allocated++;assert(n==(command==0xfffc?41:1));if(fail)return 0;if(mutate)*(uint16_t *)0x810000=0x200c;return 0x820005;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){sent=p;sends++;return 0;}
uint32_t opencfw_em9305_command_30ccf8(uint32_t a,uint32_t b){assert(a==2&&b==3);status=12;return 99;}
uint32_t opencfw_em9305_command_30df08(uintptr_t p){assert(*(uint16_t *)p==0x0403&&*(uint16_t *)(p+2)==0x0605&&*(uint8_t *)(p+4)==2&&*(uint8_t *)(p+5)==7&&*(uint8_t *)(p+6)==8);status=77;return status;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;unsigned commands[]={0x200b,0x200c,0xfffc,0xffe0,0x1234};for(unsigned ci=0;ci<5;ci++)for(fail=0;fail<2;fail++)for(mutate=0;mutate<2;mutate++){memset((void *)0x800000,0,0x100000);allocated=sends=status=sent=0;unsigned cmd=commands[ci];*(uint16_t *)0x810000=cmd;for(unsigned j=0;j<7;j++)*(uint8_t *)(uintptr_t)(0x811000+j)=j+2;for(unsigned j=0;j<40;j++)*(uint8_t *)(uintptr_t)(0x801820+j)=j+11;unsigned result=opencfw_em9305_dispatch_330c60(0x810000,0x811000);if(cmd==0x200b){assert(result==!fail&&allocated==1&&status==77&&sends==!fail);if(!fail){assert(sent==0x820000&&*(uint8_t *)0x820005==(mutate?0:77));}}else if(cmd==0x200c){assert(result==1&&allocated==0&&sends==0&&status==12);}else if(cmd==0xfffc||cmd==0xffe0){assert(result==1&&allocated==1&&sends==!fail);if(!fail){assert(sent==0x820000&&*(uint8_t *)0x820005==0);if(cmd==0xfffc&&!mutate)assert(memcmp((void *)0x820006,(void *)0x801820,40)==0);}}else assert(result==0&&allocated==0&&sends==0);cases++;}for(unsigned a=0;a<3;a++)for(unsigned b=0;b<3;b++)for(unsigned v=0;v<256;v++){*(uint8_t *)0x805a73=a;*(uint8_t *)0x805a74=b;*(uint8_t *)0x805b00=99;unsigned r=opencfw_em9305_command_30dfd8(v);assert(r==((a|b)?12:v>=1&&v<=7?0:18));assert(*(uint8_t *)0x805b00==(r==0?v:99));cases++;}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('scan-command-parent-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('scan-command-parent-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected dispatch/shared handler/byte-setting command/info-copy with controlled allocation, lower commands and event send. Semantic record packing, failed allocation, mutable request command and 256 input bytes/guard combinations. No native ARC execution or hardware proof.'},indent=2)+'\n')
