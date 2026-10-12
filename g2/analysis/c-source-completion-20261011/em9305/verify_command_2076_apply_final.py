from pathlib import Path
import subprocess,json,re
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated command apply32754c and derive/refresh'):s.index('/* Authenticated dispatch330ce0')]
b=re.sub(r'__asm__ volatile\("mpyuw %0,%1,912":"=r"\((offset|second_offset)\):"r"\(id\)\);',lambda m:m[1]+'=host_mpy(id);',b).replace('__asm__ volatile("div %0,%1,912":"=r"(quotient):"r"(difference));','quotient=host_div(difference);')
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocation,mutate,sends,events;static uint8_t captured[8];
static uint32_t host_mpy(uint32_t id){assert(id<8);return id*912;}
static uint32_t host_div(uint32_t d){assert((int32_t)d%912==0);return (uint32_t)((int32_t)d/912);}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==6);if(mutate)*(uint32_t *)0x805c70=0x820000+912;*(uint8_t *)0x805b18=71;return allocation?0x840000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t m){assert(h==71&&m==0x840000);sends++;return 123;}
static uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t p){memcpy(captured,(void *)p,8);events++;return 85;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);uintptr_t row=0x820000+912;unsigned cases=0;
for(int baseline=-128;baseline<128;baseline++)for(int current=-128;current<128;current++){*(uint8_t *)(row+766)=5;*(int8_t *)(row+268)=baseline;*(int8_t *)(row+558)=current;int diff=baseline-current;unsigned expected=(uint8_t)(diff<0?-diff:diff);assert(opencfw_em9305_command_delta_317b80(row)==expected);cases++;}
for(unsigned state=0;state<4;state++)for(unsigned delta=0;delta<128;delta++)for(unsigned first=0;first<260;first+=13)for(unsigned second=0;second<260;second+=17){*(uint8_t *)(row+766)=5;*(int8_t *)(row+268)=0;*(int8_t *)(row+558)=delta;*(uint8_t *)(row+776)=first;*(uint8_t *)(row+777)=second;*(uint8_t *)(row+778)=23;*(uint8_t *)(row+779)=7;*(uint8_t *)(row+782)=state;unsigned upper=(uint8_t)((uint8_t)first+(uint8_t)second);unsigned expected=state==2?(delta<16?0:1+(delta>=(uint8_t)((uint8_t)first-(uint8_t)second))):state==1?(upper<delta?2:delta>=16):state==0?(upper<delta?2:30<delta):1;assert(opencfw_em9305_command_derive_317ba8(row)==expected);cases++;}
*(uint32_t *)0x805c70=0x820000;*(uint8_t *)(row+766)=15;*(int8_t *)(row+268)=0;*(int8_t *)(row+568)=11;*(uint8_t *)(row+782)=2;events=0;assert(opencfw_em9305_command_refresh_323268(row)==85);assert(events==1&&*(uint16_t *)captured==1&&*(uint16_t *)(captured+2)==48&&*(uint16_t *)(captured+4)==1&&captured[6]==11&&captured[7]==2);cases++;
for(unsigned state=0;state<4;state++)for(unsigned role=0;role<2;role++)for(unsigned mode=1;mode<6;mode++)for(unsigned select=0;select<3;select++)for(unsigned sentinel=0;sentinel<2;sentinel++)for(unsigned alloc=0;alloc<2;alloc++)for(unsigned change=0;change<2;change++){memset((void *)0x800000,0,0x100000);*(uint32_t *)0x805c70=0x820000;*(uint32_t *)0x805cac=0x810000;*(uint8_t *)0x810028=0x49;*(uint8_t *)(row+2)=role;*(uint8_t *)(row+770)=state;*(uint8_t *)(row+77)=mode;*(uint8_t *)(row+(role?197:189))=select;unsigned extra=mode==3&&select==1,effective=mode+extra;*(uint8_t *)(row+effective+553)=sentinel?127:20;*(uint8_t *)(row+mode-(1-extra)+332)=126;*(uint8_t *)(row+766)=15;*(int8_t *)(row+268)=0;*(int8_t *)(row+568)=11;*(uint8_t *)(row+776)=30;*(uint8_t *)(row+777)=5;*(uint8_t *)(row+778)=23;*(uint8_t *)(row+779)=7;allocation=alloc;mutate=change;sends=events=0;unsigned expected=state!=2?12:sentinel&&!alloc?7:0;assert(opencfw_em9305_command_apply_32754c(1,0xabcdef)==expected);assert(sends==(state==2&&sentinel&&alloc)&&events==(state==2&&!sentinel));assert(*(uint8_t *)(row+770)==(expected==0?1:state));if(state==2&&sentinel){assert(*(uint8_t *)(row+771)==1&&*(uint8_t *)(row+784)==1&&*(uint8_t *)(row+effective+331)==0x49);if(alloc)assert(*(uint16_t *)0x840000==(change?0:1)&&*(uint16_t *)0x840002==0x2801&&*(uint8_t *)0x840004==0&&*(uint8_t *)0x840005==effective);}cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('command-2076-apply-final-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);print(out.strip());p.with_name('command-2076-apply-final-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Four actual selected bodies, genuine delta/derive logic; bounded MPYUW and signed DIV normalization, controlled allocation/send/event. Signed byte pairs, derive state, query sentinel, table mutation and exact event bytes. No target DSP/runtime/hardware proof.'},indent=2)+'\n')
