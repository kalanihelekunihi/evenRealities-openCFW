from pathlib import Path
import subprocess,re,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated receive time check319838'):s.index('/* Authenticated receive command predicate31b7c8')];b=re.sub(r'__asm__ volatile\("div %0,%1,%2".*?;','index=delta/912u;',b);b=b.replace('__asm__ volatile("mpyuw %0,%1,%2":"=r"(limit):"r"(interval),"r"(1250u));','limit=interval*1250u;')
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned scenario,n,elapsed_calls,fail;static char trace[32];static uintptr_t source=0x840000;static uint32_t reason_expected;
static void mark(char c){trace[n++]=c;}
uint32_t opencfw_em9305_pal_current_time(void){mark('T');return 300;}
uint32_t opencfw_em9305_auxiliary_guard_interval(void){mark('G');return scenario==8?0xffffffff:200;}
uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t timestamp,uint32_t reference){assert(reference==77);mark('E');elapsed_calls++;if(timestamp==300)return scenario==2?2051:scenario==3?2050:100;if(elapsed_calls==1){assert(timestamp==11);*(uint32_t *)(source+20)=0x820000;return scenario==6?2600:scenario==7?2500:1000;}assert(timestamp==1234);return scenario==5?500:scenario==7?550:600;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t bytes){assert(bytes==4);mark('A');*(uint32_t *)0x805c70=source-912*3-42;*(uint8_t *)0x805b18=77;return fail?0:0x850000;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t message){assert(handler==77&&message==0x850000);assert(*(uint16_t *)message==3&&*(uint8_t *)(message+2)==1&&*(uint8_t *)(message+3)==(uint8_t)reason_expected);mark('S');return 0x55;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(scenario=0;scenario<9;scenario++){memset((void *)0x800000,0,0x100000);n=elapsed_calls=0;memset(trace,0,sizeof(trace));*(uint16_t *)(source+266)=scenario==8?0:2;*(uint8_t *)(source+4)=scenario==0?4:0;if(scenario>=4&&scenario<=7)*(uint32_t *)(source+20)=0x830000;*(uint32_t *)(0x830000+8)=11;*(uint32_t *)(0x820000+8)=1234;unsigned result=opencfw_em9305_receive_check_319838(source,77,100);assert(result==(scenario==2||scenario==5||scenario==8));assert(strcmp(trace,scenario==0?"":scenario>=4&&scenario<=7?scenario==6?"TGEE":"TGEEE":"TGE")==0);cases++;}
for(fail=0;fail<2;fail++){for(unsigned reason=0;reason<256;reason++){n=0;memset(trace,0,sizeof(trace));memset((void *)0x850000,0xa5,4);reason_expected=reason|0xffffff00;unsigned result=opencfw_em9305_receive_terminate_325c08(source,reason_expected);assert(result==(fail?0:0x55)&&strcmp(trace,fail?"A":"AS")==0);if(fail)assert(*(uint32_t *)0x850000==0xa5a5a5a5);cases++;}}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('receive-time-termination-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('receive-time-termination-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected C fixed RAM with controlled clock/guard/elapsed and allocate/send children. Object-pointer refresh, threshold equality/wrap, all reason low bytes, null allocation effects. DIV/MPYUW normalized; no native ARC runtime/layout/hardware proof.'},indent=2)+'\n')
