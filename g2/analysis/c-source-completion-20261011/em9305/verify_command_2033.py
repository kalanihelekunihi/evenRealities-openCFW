from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();s=s[s.index('/* Native command30cba0'):s.index('/* Native command30e120')].replace('__asm__ volatile("mpyuw %0,%1,1000":"=r"(scaled):"r"(duration));','scaled=duration*1000u;')
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned alloc,trace;
static uint32_t opencfw_em9305_ll_command_pending_310634(void){assert(trace==0);trace=1;*(uint8_t *)0x805ec5=1;return 0x805ec5;}
static void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){return memset(p,v,n);}
static uintptr_t opencfw_em9305_wsf_pool_allocate(uint32_t n){assert(n==257&&trace==1);trace=2;return alloc?0x840000:0;}
uint32_t opencfw_em9305_command_callback_332d2c(uintptr_t a){(void)a;return 0;}
uint32_t opencfw_em9305_command_callback_332cd0(uintptr_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
uint32_t opencfw_em9305_common_request_30455c(uint32_t n){assert(n==2&&trace==2);trace=3;return 99;}
uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t p){assert(p==0x8058f4&&trace==3);trace=4;return 98;}
'''+s+r'''
static uint8_t in[24];
static void setup(void){memset((void *)0x8058dc,0xa5,512);*(uint8_t *)0x8058dc=0;memset((void *)0x805a70,0,16);memset(in,0,sizeof in);*(uint16_t *)in=0x1234;*(uint32_t *)(in+4)=0x71764129;in[9]=1;*(uint8_t *)0x805a95=9;*(uint32_t *)0x805cac=0x820000;*(uint16_t *)0x82003c=65000;trace=0;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned n=0;
for(unsigned channel=0;channel<256;channel++)for(unsigned kind=0;kind<5;kind++)for(unsigned mode=0;mode<3;mode++)for(unsigned features=0;features<4;features++)for(alloc=0;alloc<2;alloc++){setup();in[8]=channel;in[9]=kind;in[10]=mode;*(uint8_t *)0x805a95=(features&1?1:0)|(features&2?8:0);unsigned bad=channel>39||kind<1||kind>3||mode>1;unsigned unsupported=(kind==2&&!(features&1))||(kind==3&&!(features&2));unsigned expected=bad?48:unsupported?17:alloc?0:31;assert(opencfw_em9305_command_30cba0((uintptr_t)in)==expected);assert(trace==(bad||unsupported?0:alloc?4:2));if(!bad&&!unsupported){unsigned mapped=channel==0?37:channel<12?channel-1:channel==12?38:channel>=39?39:channel-2;assert(*(uint8_t *)0x8059f8==1&&*(uint8_t *)0x8059f9==mapped&&*(uint32_t *)0x805a00==0x555555&&*(uint32_t *)0x8059fc==0x71764129&&*(uint8_t *)0x805a04==kind&&*(uint8_t *)0x805a05==kind);assert(*(uint16_t *)0x8058de==0x1234&&*(uint8_t *)0x80590e==2&&*(uint32_t *)0x805920==0x8059f8);assert(*(uint32_t *)0x805a5c==65000000&&*(uint16_t *)0x805a68==257&&*(uint32_t *)0x805a64==(alloc?0x840000:0));assert(*(uint8_t *)0x8058dc==(alloc?2:0)&&*(uint8_t *)0x805a78==alloc&&*(uint8_t *)0x805a79==alloc);for(unsigned j=24;j<68;j++)assert(*(uint8_t *)(uintptr_t)(0x8058dc+j)==(j==50?2:(j>=52&&j<56)?(uint8_t)((uintptr_t)&opencfw_em9305_command_callback_332d2c>>(8*(j-52))):0));}n++;}
for(unsigned guard=0;guard<6;guard++){setup();alloc=1;*(uint8_t *)(uintptr_t)(guard==5?0x8058dc:0x805a70+guard)=1;assert(opencfw_em9305_command_30cba0((uintptr_t)in)==12&&trace==0);n++;}
setup();in[11]=1;assert(opencfw_em9305_command_30cba0((uintptr_t)in)==17&&trace==0);n++;
printf("PASS %u\n",n);}
'''
p=Path(__file__).with_name('command-2033-host.c');p.write_text(h)
a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/c && /tmp/c'],text=True);print(a.strip());p.with_name('command-2033-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual2033 body/map/count; controlled allocation/callback/scheduler; bounded MPYUW normalized. Guard priorities, record/state writes and call order. No hardware or native runtime proof.'},indent=2)+'\n')
