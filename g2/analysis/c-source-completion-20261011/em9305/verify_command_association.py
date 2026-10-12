from pathlib import Path
import subprocess,json,re
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated command association apply307fcc'):]
b=re.sub(r'__asm__ volatile\("mpyuw %0,%1,(784|912)":"=r"\((offset|peer_offset)\):"r"\((id|peer)\)\);',lambda m:m[2]+'=host_mpy('+m[3]+','+m[1]+'u);',b)
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned alloc_ok,found,lookups,allocs,sends;
static uint32_t host_mpy(uint32_t id,uint32_t unit){assert(id<8);return id*unit;}
static uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t peer){assert(peer==0x12340003);lookups++;return found?0x830000:0;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==10);allocs++;*(uint8_t *)0x805b18=71;return alloc_ok?0x840000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t msg){assert(handler==71&&msg==0x840000);sends++;return 99;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;
for(unsigned variant=0;variant<2;variant++)for(unsigned count=0;count<5;count++)for(unsigned id=0;id<5;id++)for(unsigned lookup=0;lookup<2;lookup++)for(unsigned role=0;role<3;role++)for(unsigned active=0;active<2;active++)for(unsigned flags=0;flags<4;flags++)for(unsigned start=0;start<2;start++)for(unsigned allocation=0;allocation<2;allocation++){
memset((void *)0x800000,0,0x100000);lookups=allocs=sends=0;found=lookup;alloc_ok=allocation;*(uint32_t *)0x805cac=0x810000;*(uint8_t *)0x810022=count;*(uint32_t *)0x805c70=0x820000;uintptr_t row=0x820000+id*912;*(uint8_t *)row=active;*(uint8_t *)(row+547)=flags;*(uint8_t *)(row+534)=start;*(uint8_t *)(0x830000+369)=role;*(uint8_t *)(0x803d78+3*784)=lookup;*(uint8_t *)(0x803d79+3*784)=role;
unsigned expected=variant?(!lookup||role!=1?66:id>=count?2:!active?2:!(flags&2)||!start?26:0):(id>=count?2:!lookup?66:role!=1?12:!active?2:!(flags&2)||!start?26:0);
unsigned result=variant?opencfw_em9305_command_apply_30805c(id,0xabcde,3):opencfw_em9305_command_apply_307fcc(id,0xabcde,0x12340003);assert(result==expected);unsigned eligible=expected==0;assert(allocs==eligible&&sends==(eligible&&allocation));assert(lookups==(!variant&&id<count));if(sends){uint16_t *msg=(uint16_t *)0x840000;assert(msg[0]==id&&msg[1]==0x2201&&msg[2]==!variant&&msg[3]==3&&msg[4]==0xbcde);}cases++;
}
for(unsigned peer=6;peer<0x10000;peer++){assert(opencfw_em9305_command_apply_30805c(0xffffffff,0,peer)==(peer>=0xf00?18:66));cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('command-association-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('command-association-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Actual selected association bodies with bounded MPYUW normalization and controlled lookup/allocation/send. Guard priorities, message fields, fresh handler, allocation failure. No native DSP or hardware proof.'},indent=2)+'\n')
