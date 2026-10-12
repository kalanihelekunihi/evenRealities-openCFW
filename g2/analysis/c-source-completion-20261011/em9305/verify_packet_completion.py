from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated packet completion 32d790'):s.index('/* Authenticated duration quantization 312c5c')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned raw,n;static char trace[8];static uintptr_t source=0x860000,packet=0x840008;
static void mark(char c){trace[n++]=c;}
uint32_t opencfw_em9305_wsf_event_release(uintptr_t p){assert(p==(raw?packet:0x830008));assert(*(uint32_t *)0x805cd4==packet);mark('F');*(uint8_t *)0x805b18=23;return 11;}
uint32_t opencfw_em9305_wsf_queue_append(uintptr_t q,uintptr_t p){assert(q==0x8056dc&&p==packet-12);mark('Q');return 12;}
uint32_t opencfw_em9305_wsf_critical_enter(void){mark('E');return 0;}
uint32_t opencfw_em9305_wsf_critical_exit(void){mark('X');*(uint8_t *)(source+376)=255;return 0;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t handler,uint32_t flags){assert(handler==23&&flags==1&&*(uint32_t *)0x805cd4==0);mark('P');return 0x76543210;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;assert(opencfw_em9305_radio_packet_complete_32d790(source)==source&&n==0);cases++;
for(raw=0;raw<2;raw++){for(unsigned count=0;count<256;count++){memset(trace,0,sizeof(trace));n=0;*(uint32_t *)0x805cd4=packet;*(uint8_t *)0x8056e4=raw?255:19;*(uint32_t *)packet=0x830008;*(uint8_t *)0x805ab4=count;*(uint8_t *)(source+376)=17;*(uint8_t *)0x805b18=22;assert(opencfw_em9305_radio_packet_complete_32d790(source)==0x76543210);assert(strcmp(trace,raw?"FP":"FQEXP")==0);assert(*(uint8_t *)0x805ab4==(raw?count:(uint8_t)(count+1)));assert(*(uint8_t *)(source+376)==(raw?17:0));cases++;}}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('packet-completion-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('packet-completion-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected C host fixed RAM, controlled release/queue/critical/event children, call order, refreshed handler/counter, byte wrap and delay-slot clear. No native ARC runtime/layout/hardware proof.'},indent=2)+'\n')
