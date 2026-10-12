from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text().split('/* Native PHY slot reads307008/30701c')[1].split('/* Native command30cba0')[0]
s=s.replace('__asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));','offset=id*912u;')
h='''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned active;
static uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){(void)id;return active;}
/* Native PHY slot reads307008/30701c'''+s+'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);*(uint32_t *)0x805cac=0x820000;*(uint32_t *)0x805c70=0x830000;unsigned n=0;
for(unsigned count=0;count<4;count++)for(unsigned id=0;id<5;id++)for(active=0;active<2;active++)for(unsigned v=0;v<256;v++){*(uint8_t *)0x820022=count;*(uint8_t *)(uintptr_t)(0x830000+id*912+76)=v;*(uint8_t *)(uintptr_t)(0x830000+id*912+77)=255-v;*(uint8_t *)0x840000=99;*(uint8_t *)0x840001=98;unsigned ok=id<count&&active;assert(opencfw_em9305_command_query_30c824(id,0x840000,0x840001)==(ok?0:2));assert(*(uint8_t *)0x840000==(ok?v:99)&&*(uint8_t *)0x840001==(ok?255-v:98));n++;}
active=1;*(uint8_t *)0x820022=2;*(uint8_t *)0x83004c=231;*(uint8_t *)0x83004d=12;assert(opencfw_em9305_command_query_30c824(0,0x83004d,0x840001)==0&&*(uint8_t *)0x840001==231);assert(opencfw_em9305_ll_command_pending_310634()==0x805ec5&&*(uint8_t *)0x805ec5==1);printf("PASS %u\\n",n+2);}
'''
p=root/'g2/analysis/c-source-completion-20261011/em9305/phy-query-host.c';p.write_text(h)
a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/q && /tmp/q'],text=True);print(a)
p.with_name('phy-query-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual query/slot/flag source; stride MPYUW normalized for bounded IDs, controlled active child; includes alias write-before-read. No target runtime proof.'},indent=2)+'\n')
