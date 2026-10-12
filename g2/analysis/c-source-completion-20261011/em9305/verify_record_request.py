from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated record requests30fc68'):s.index('/* Authenticated packet request30faec')]
b=b.replace('__asm__ volatile("mpywhl %0,%1,%2":"=r"(product):"r"(size+9u),"r"(unit));','product=host_mpy(size+9u,unit);')
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static char trace[32];static unsigned n,mode,expected,which;
static void mark(char c){trace[n++]=c;}
uint32_t opencfw_em9305_radio_request_enter_310678(void){mark('E');return 0;}
uint32_t opencfw_em9305_radio_request_exit_31069c(void){mark('X');return 888;}
uint32_t opencfw_em9305_radio_request_base_310640(uint32_t base){assert(base==500&&*(uint16_t *)0x805d24==0);mark('B');*(uint8_t *)0x805e78=mode;return 0;}
uintptr_t opencfw_em9305_radio_flatten_333064(uintptr_t p,uint32_t s){assert(p==0x810000&&s<5);mark('F');*(uint16_t *)p=65530;*(uint16_t *)(p+8)=20;*(uint16_t *)(p+16)=10;return 0x830000;}
uint32_t opencfw_em9305_radio_request_3105b8(uintptr_t p,uint32_t size){assert(p==0x830000&&size==expected);mark('R');if(which==0){*(uint8_t *)0x805d1e=7;*(uint8_t *)0x805d20=9;}else{*(uint8_t *)0x805d1f=7;*(uint8_t *)0x805d21=9;*(uint32_t *)0x805d18=1000;}return 0;}
static uint32_t host_mpy(uint32_t a,uint32_t b){assert(a==expected+9&&b==7);mark('M');return 0x12345;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(which=0;which<2;which++)for(mode=0;mode<4;mode++)for(unsigned selector=0;selector<5;selector++){memset((void *)0x800000,0,0x100000);memset(trace,0,sizeof(trace));n=0;*(uint32_t *)0x805cfc=500;*(uint16_t *)0x805d24=99;expected=selector==1?65530:selector==2?14:selector==3?24:0;unsigned r=which?opencfw_em9305_radio_request_30fcd8(0x810000,selector):opencfw_em9305_radio_record_request_30fc68(0x810000,selector);if(which){assert(r==1000+9+0x12345&&*(uint32_t *)0x805d18==r&&strcmp(trace,"FRM")==0);}else{assert(r==888&&*(uint16_t *)0x805d24==0);if(mode==2){assert(strcmp(trace,"EBFRMX")==0&&*(uint32_t *)0x805d18==9+0x12345&&*(uint8_t *)0x805d22==0);}else assert(strcmp(trace,"EBX")==0);}cases++;}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('record-request-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('record-request-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected record-request bodies/state query; controlled lower children and MPYWHL output. Length reload/wrap, mode guard, flattened argument and fresh child-mutated unit/extra/time. No native DSP execution or hardware proof.'},indent=2)+'\n')
