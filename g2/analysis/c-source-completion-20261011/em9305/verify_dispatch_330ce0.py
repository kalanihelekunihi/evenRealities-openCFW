from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
pending=Path(__file__).with_name('dispatch-330ce0-pending.c');s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated dispatch330ce0'):s.index('/* Authenticated completion303fb8')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocation,sends,allocs;static uint32_t code,length;
static uintptr_t opencfw_em9305_ll_event_allocate(uint32_t c,uint32_t n){code=c;length=n;allocs++;*(uint8_t *)0x805718=100;return allocation?0x820000:0;}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==0x81fffe);sends++;return 99;}
static void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){return memcpy(d,s,n);}
static uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t d,uintptr_t s){memcpy((void *)d,(void *)s,6);return d;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uintptr_t input=0x810000;
for(unsigned type=0;type<256;type++){if(type==2||type==4)continue;*(uint8_t *)(input+2)=type;assert(opencfw_em9305_dispatch_330ce0(input)==0);cases++;}
for(unsigned alloc=0;alloc<2;alloc++){*(uint8_t *)(input+2)=4;*(uint8_t *)(input+3)=0x79;allocation=alloc;sends=allocs=0;assert(opencfw_em9305_dispatch_330ce0(input)==alloc);assert(allocs==1&&code==14&&length==4&&sends==alloc);if(alloc)assert(*(uint32_t *)0x820000==0x79200c01);cases++;}
for(unsigned extended=0;extended<2;extended++)for(unsigned mask=0;mask<4;mask++)for(unsigned feature=0;feature<2;feature++)for(unsigned count=0;count<3;count++)for(unsigned alloc=0;alloc<2;alloc++)for(unsigned bytes=0;bytes<256;bytes++){memset((void *)0x800000,0,0x100000);*(uint32_t *)0x805cac=0x840000;*(uint8_t *)0x84000e=2;*(uint32_t *)0x8056f8=(mask&1?2:0)|(mask&2?1024:0);*(uint8_t *)0x8056ef=feature?32:0;*(uint8_t *)0x805718=count;*(uint8_t *)(input+2)=2;*(uint32_t *)(input+4)=0x830000;*(uint8_t *)(input+8)=bytes;*(uint8_t *)(input+9)=0xf0;*(uint8_t *)(input+10)=0x11;*(uint8_t *)(input+11)=0x22;for(unsigned n=0;n<6;n++){*(uint8_t *)(input+12+n)=n+1;*(uint8_t *)(input+19+n)=n+11;}*(uint8_t *)(input+18)=extended?7:255;for(unsigned n=0;n<256;n++)*(uint8_t *)(uintptr_t)(0x830000+n)=n;allocation=alloc;sends=allocs=0;unsigned eligible=(mask&(extended?2:1))&&feature&&count<2;unsigned expected=eligible&&alloc?1:extended;assert(opencfw_em9305_dispatch_330ce0(input)==expected);assert(allocs==eligible&&sends==(eligible&&alloc));if(eligible){assert(code==62&&length==(extended?18:(uint8_t)(bytes+12)));if(alloc){uint8_t *e=(uint8_t *)0x820000;assert(e[0]==(extended?11:2)&&e[1]==1&&e[2]==0x11&&e[3]==0x22&&!memcmp(e+4,(void *)(input+12),6));if(extended)assert(e[10]==7&&!memcmp(e+11,(void *)(input+19),6)&&e[17]==0xf0);else assert(e[10]==bytes&&!memcmp(e+11,(void *)0x830000,bytes)&&e[11+bytes]==0xf0);assert(*(uint8_t *)0x805718==101);}}cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('dispatch-330ce0-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);print(out.strip());p.with_name('dispatch-330ce0-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Actual dispatch body with controlled allocation/copy/send. All length bytes, masks/count guard, unsupported type, return asymmetry and fresh count. No native target runtime/layout/hardware proof.'},indent=2)+'\n')
