from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated packet request30faec'):s.index('/* Authenticated address-resolution lookup303890')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static char trace[32];static unsigned n,mode,length;
static void mark(char c){trace[n++]=c;}
uint32_t opencfw_em9305_radio_request_enter_310678(void){mark('E');return 0;}
uint32_t opencfw_em9305_radio_window_start_3103e0(uint32_t a,uint32_t b){assert(a==0&&b==70&&*(uint32_t *)0x805e84==500&&*(uint8_t *)0x805e78==3&&*(uint16_t *)0x805d24==0&&*(uint32_t *)0x805d34==0x830001&&*(uint16_t *)0x805d38==(uint16_t)length);mark('W');*(uint8_t *)0x805e78=mode;return 99;}
uint32_t opencfw_em9305_radio_state_310260(void){mark('S');return *(uint8_t *)0x805e78;}
uint32_t opencfw_em9305_radio_followup_driver_310374(uint32_t a,uint32_t b){assert(a==0x830000&&b==length);mark('F');return 111;}
static uint32_t cb(uint32_t a,uint32_t b,uint32_t c,uint32_t d){assert(a==1&&b==0&&c==9&&d==0);mark('C');return 222;}
uint32_t opencfw_em9305_radio_request_exit_31069c(void){mark('X');if(mode==3)assert(*(uint8_t *)0x805d22==1&&*(uint32_t *)0x805d18==0);*(uint8_t *)0x805e78=0;*(uint8_t *)0x805e99=9;*(uint32_t *)0x805e7c=(uint32_t)(uintptr_t)cb;return 333;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;unsigned lengths[]={0,1,65535,65536,0xffffffff};for(mode=0;mode<4;mode++)for(unsigned i=0;i<5;i++){memset((void *)0x800000,0,0x100000);memset(trace,0,sizeof(trace));n=0;length=lengths[i];*(uint32_t *)0x805cfc=500;*(uint32_t *)0x805d00=50;*(uint16_t *)0x805d1c=20;*(uint16_t *)0x805d24=99;unsigned r=opencfw_em9305_radio_request_30faec(0x830000,length);assert(r==(mode==0?222:333)&&strcmp(trace,mode==0?"EWSXC":mode==3?"EWSFX":"EWSX")==0);cases++;}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('packet-request-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('packet-request-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected packet-request/window/failure callback; controlled critical/window/followup/state children. Full length vs stored low half, pending stores before window, captured state and callback/selector refresh after critical exit. No native ARC execution/hardware proof.'},indent=2)+'\n')
