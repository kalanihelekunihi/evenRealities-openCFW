from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated receive gate children324f68'):s.index('/* Authenticated receive allocation/finalization324ea4')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uintptr_t source=0x840000;static unsigned advance_result,calls;
uint32_t opencfw_em9305_radio_packet_advance_32d738(uintptr_t p){assert(p==source&&*(uint8_t *)(p+341)==0);calls++;return advance_result;}
uint32_t opencfw_em9305_radio_packet_complete_32d790(uintptr_t p){assert(p==source);return 0x55;}
uint32_t opencfw_em9305_wsf_event_release(uintptr_t p){assert(p==0x850000-2);return 0x56;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned a=0;a<256;a++)for(unsigned c=0;c<256;c++)for(unsigned mode=0;mode<2;mode++){memset((void *)source,0,1024);*(uint8_t *)(source+345)=a;*(uint8_t *)(source+338)=c;*(uint8_t *)(source+341)=mode;*(uint8_t *)(source+336)=3;*(uint8_t *)(source+378)=1;*(uint8_t *)(source+379)=1;advance_result=0;calls=0;unsigned gate=opencfw_em9305_receive_gate_324f68(source);assert(gate==((a^c)&1));assert(*(uint8_t *)(source+338)==(gate?(uint8_t)(c+1):c));assert(calls==(gate&&mode));assert(*(uint8_t *)(source+378)==(gate&&mode?0:1));assert(*(uint8_t *)(source+379)==(gate&&!mode?0:1));cases++;}
for(unsigned scenario=0;scenario<7;scenario++){memset((void *)source,0,1024);*(uint8_t *)(source+341)=1;advance_result=scenario!=0;*(uint32_t *)0x8052d0=scenario==1?0:0x123456;*(uint8_t *)(source+108)=scenario==2?0:1;*(uint8_t *)(source+111)=scenario==3?7:0;uint32_t low=scenario==4||scenario==5?0xffffffff:0,high=scenario==4?0xffffffff:7;*(uint32_t *)(source+456)=low;*(uint32_t *)(source+460)=high;unsigned result=opencfw_em9305_receive_advance_32d5ac(source);assert(*(uint8_t *)(source+341)==0);if(scenario<3)assert(result==0&&*(uint32_t *)(source+456)==low&&*(uint32_t *)(source+460)==high);else if(scenario==3)assert(result==7&&*(uint32_t *)(source+456)==low);else assert(result==high+(low==0xffffffff)&&*(uint32_t *)(source+456)==low+1&&*(uint32_t *)(source+460)==result);cases++;}
assert(opencfw_em9305_receive_finish_324fb0(source)==0x55);assert(opencfw_em9305_receive_packet_release_3253bc(0x850000)==0x56);cases+=2;printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('receive-gate-children-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('receive-gate-children-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected gate/advance/wrappers fixed-RAM with controlled packet children. All byte parity pairs, mode branches, optional presence/mode gates, counter carry and incidental returns. No native ARC runtime/layout/hardware proof.'},indent=2)+'\n')
