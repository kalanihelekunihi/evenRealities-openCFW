from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();s=s[s.index('/* Native event330400'):s.index('/* Native3304f0..33052c')]
h=r"""#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned allocs,fills,sends,fail;
static uintptr_t packet_seen;
static uintptr_t opencfw_em9305_ll_event_allocate(uint32_t type,uint32_t size){assert(type==62&&size==29);allocs++;return fail?0:0x820002;}
static uint32_t opencfw_em9305_packet_event_fill_330e78(uintptr_t event,uintptr_t packet){assert(event==0x820002);fills++;packet_seen=packet;return 77;}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t event){assert(event==0x820000&&fills==1);sends++;return 99;}
"""+s+r"""
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uintptr_t packet=0x810000;
for(unsigned type=0;type<256;type++)for(unsigned gates=0;gates<4;gates++)for(fail=0;fail<2;fail++){*(uint8_t *)(packet+2)=type;*(uint8_t *)0x8056fb=0xa4|(gates&1);*(uint8_t *)0x8056ef=0xc3|((gates&2)?32:0);allocs=fills=sends=0;packet_seen=0;unsigned guard=type==39&&gates==3;unsigned ok=guard&&!fail;assert(opencfw_em9305_dispatch_330400(packet)==ok);assert(allocs==guard&&fills==ok&&sends==ok);assert(packet_seen==(ok?packet:0));cases++;}
printf("PASS %u\n",cases);}
"""
p=Path(__file__).with_name('event330400-host.c');p.write_text(h)
a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/e && /tmp/e'],text=True);print(a.strip());p.with_name('event330400-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual source with controlled allocation/fill/send; all byte packet types, both feature gates, allocation failure and child order. No native runtime or hardware proof.'},indent=2)+'\n')
