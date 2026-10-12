from pathlib import Path
import subprocess,re,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated packet advance 32d738'):s.index('/* Authenticated packet completion 32d790')]
b=re.sub(r'__asm__ volatile\("mpyuw %0,%1,%2".*?;','product=unit*index;',b)
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned removed;static uintptr_t expected;static uint8_t expectedhandler;
uintptr_t opencfw_em9305_wsf_event_peek(uintptr_t queue,uintptr_t handler){uint32_t node=*(volatile uint32_t *)queue;if(!node)return 0;*(volatile uint8_t *)handler=*(volatile uint8_t *)(uintptr_t)(node+4);return node+8;}
uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t handler){assert(*(uint32_t *)0x805cd4==expected&&*(uint8_t *)0x8056e4==expectedhandler);assert(*(uint32_t *)queue==expected-8);removed++;*(uint32_t *)queue=0;*(uint8_t *)handler=19;*(uint32_t *)0x805cd4=0xabcdef;return 0;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);uintptr_t source=0x860000,node=0x840000,packet=node+8;unsigned cases=0;assert(opencfw_em9305_radio_packet_advance_32d738(source)==0&&removed==0);cases++;
for(unsigned handler=0;handler<256;handler++)for(unsigned index=0;index<256;index++)for(unsigned unit=0;unit<256;unit+=17)for(unsigned len=0;len<65536;len+=8191){*(uint32_t *)(source+360)=node;*(uint8_t *)(node+4)=handler;*(uint8_t *)(packet+7)=index;*(uint8_t *)(packet+6)=unit;*(uint16_t *)(packet+4)=len;*(uint32_t *)0x805cd4=0x123456;*(uint8_t *)0x8056e4=91;removed=0;expected=packet;expectedhandler=handler;assert(opencfw_em9305_radio_packet_advance_32d738(source)==1);unsigned take=handler==255||unit*(index+1)>=len;if(take){assert(removed==1&&*(uint32_t *)0x805cd4==0xabcdef&&*(uint8_t *)(packet+7)==index);}else{assert(removed==0&&*(uint8_t *)(packet+7)==(uint8_t)(index+1)&&*(uint32_t *)0x805cd4==0x123456&&*(uint8_t *)0x8056e4==91);}cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('packet-advance-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('packet-advance-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected C host fixed-RAM packet advance with controlled removal checking store-before-call, all handler/index values, unit/length threshold and byte wrap. MPYUW normalized. Not native ARC runtime/layout/hardware proof.'},indent=2)+'\n')
