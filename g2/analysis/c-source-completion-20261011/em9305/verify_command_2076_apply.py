from pathlib import Path
import subprocess,json,re
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated command apply327630/327694'):s.index('/* Authenticated command apply32754c and derive/refresh')]
b=re.sub(r'__asm__ volatile\("mpyuw %0,%1,912":"=r"\((offset|fresh_offset)\):"r"\(id\)\);',lambda m:m[1]+'=host_mpy(id);',b).replace('__asm__ volatile("div %0,%1,912":"=r"(quotient):"r"(difference));','quotient=host_div(difference);')
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned derives,refreshes,allocation,mutate,sends;
static uint32_t host_mpy(uint32_t id){assert(id<8);return id*912;}
static uint32_t host_div(uint32_t d){assert((int32_t)d%912==0);return (uint32_t)((int32_t)d/912);}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==6);if(mutate)*(uint32_t *)0x805c70=0x820000+912;*(uint8_t *)0x805b18=71;return allocation?0x840000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t m){assert(h==71&&m==0x840000);sends++;return 123;}
'''+b+r'''
uint32_t opencfw_em9305_command_derive_317ba8(uintptr_t row){assert(row==0x820000+912);derives++;*(uint32_t *)0x805c70=0x830000;return 0x145;}
uint32_t opencfw_em9305_command_refresh_323268(uintptr_t row){assert(row==0x820000+912&&*(uint8_t *)(row+782)==0x45);refreshes++;return 99;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uintptr_t row=0x820000+912;
for(unsigned state=0;state<4;state++)for(unsigned ready=0;ready<4;ready++){memset((void *)0x800000,0,0x100000);*(uint32_t *)0x805c70=0x820000;memset((void *)(row+776),0xaa,12);*(uint8_t *)(row+769)=state;*(uint8_t *)(row+770)=ready;derives=refreshes=0;assert(opencfw_em9305_command_apply_327630(1,0x123,0x234,0x345,0x456,0x567)==0);unsigned call=state==1&&ready==1;assert(derives==call&&refreshes==call);assert(*(uint32_t *)(row+776)==0x56453423&&*(uint8_t *)(row+780)==0x67&&*(uint8_t *)(row+781)==0&&*(uint8_t *)(row+782)==(call?0x45:1)&&*(uint8_t *)(row+783)==0&&*(uint8_t *)(row+784)==0&&*(uint8_t *)(row+785)==0xaa);if(!call)assert(*(uint8_t *)(row+769)==1&&*(uint8_t *)(row+770)==2);cases++;}
for(unsigned first=0;first<3;first++)for(unsigned second=0;second<3;second++)for(unsigned alloc=0;alloc<2;alloc++)for(unsigned change=0;change<2;change++)for(unsigned mode=0;mode<256;mode++)for(unsigned extra=0;extra<3;extra++){memset((void *)0x800000,0,0x100000);*(uint32_t *)0x805c70=0x820000;*(uint8_t *)(row+77)=mode;*(uint8_t *)(row+78)=extra;*(uint8_t *)(row+771)=0xaa;allocation=alloc;mutate=change;sends=0;assert(opencfw_em9305_command_apply_327694(1,first,second)==0);assert(*(uint8_t *)(row+767)==(first!=0)&&*(uint8_t *)(row+768)==(second!=0)&&*(uint8_t *)(row+771)==(second?1:0xaa));assert(sends==(second!=0&&alloc));if(sends)assert(*(uint16_t *)0x840000==(change?0:1)&&*(uint16_t *)0x840002==0x2801&&*(uint8_t *)0x840004==0&&*(uint8_t *)0x840005==(uint8_t)(mode+(mode==3&&extra==1)));cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('command-2076-apply-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);print(out.strip());p.with_name('command-2076-apply-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Two actual apply bodies. Bounded MPYUW and signed exact DIV normalization, controlled derive/refresh/allocation/send. Full mode bytes, old-base capture/new-base id, scaled word stores and callback paths. No target DSP/runtime/hardware proof.'},indent=2)+'\n')
