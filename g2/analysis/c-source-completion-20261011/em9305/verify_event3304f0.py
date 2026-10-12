from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();s=s[s.index('/* Native3304f0..33052c'):s.index('/* Native event32f0a0')]
s=s.replace('extern uint32_t opencfw_em9305_dispatch_32f0a0(uintptr_t);','')
h=r"""#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned allocs,sends,fallbacks,fail,status;
static unsigned char storage[6];
static uintptr_t packet_seen;
static uint32_t opencfw_em9305_dispatch_32f0a0(uintptr_t p){fallbacks++;packet_seen=p;return 0x87654321;}
static uintptr_t opencfw_em9305_ll_event_allocate(uint32_t t,uint32_t n){assert(t==14&&n==4);allocs++;return fail?0:(uintptr_t)(storage+2);}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)storage);assert(storage[0]==0xa5&&storage[1]==0xa5&&storage[2]==1&&storage[3]==14&&storage[4]==32&&storage[5]==status);sends++;return 77;}
"""+s+r"""
int main(void){unsigned char packet[8]={0};unsigned cases=0;
for(unsigned type=0;type<256;type++)for(status=0;status<256;status++)for(fail=0;fail<2;fail++){packet[2]=type;packet[4]=status;memset(storage,0xa5,6);allocs=sends=fallbacks=0;packet_seen=0;uint32_t v=opencfw_em9305_dispatch_3304f0((uintptr_t)packet);if(type==8){assert(v==!fail&&allocs==1&&sends==!fail&&!fallbacks);}else{assert(v==0x87654321&&!allocs&&!sends&&fallbacks==1&&packet_seen==(uintptr_t)packet);}cases++;}
printf("PASS %u\n",cases);}
"""
p=Path(__file__).with_name('event3304f0-host.c');p.write_text(h)
a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror /work/'+str(p.relative_to(root))+' -o /tmp/e && /tmp/e'],text=True);print(a.strip());p.with_name('event3304f0-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual C with controlled children, all packet/status byte values and allocation outcomes, preserved header bytes, payload writes before send, fallback argument and full return. No target runtime proof.'},indent=2)+'\n')
