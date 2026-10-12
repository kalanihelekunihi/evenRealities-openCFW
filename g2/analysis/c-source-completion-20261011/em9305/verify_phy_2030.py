from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated PHY policy332f3c/332f80'):s.index('/* Native PHY slot reads307008/30701c')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned active,pending,allocation,sends;
static uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t id){assert(id==1);return active;}
static uint32_t opencfw_em9305_ll_slot_pending_307434(uint32_t id,uint32_t op){assert(id==1&&op==32);return pending;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==10);*(uint8_t *)0x805b18=73;return allocation?0x830000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t p){assert(h==73&&p==0x830000);sends++;return 88;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);*(uint32_t *)0x805cac=0x820000;*(uint8_t *)0x820022=4;active=allocation=1;pending=0;unsigned cases=0;
for(unsigned flags=0;flags<4;flags++)for(unsigned feature=0;feature<2;feature++)for(unsigned mode=0;mode<8;mode++)for(unsigned first=0;first<16;first++)for(unsigned second=0;second<16;second++)for(unsigned kind=0;kind<4;kind++){*(uint32_t *)0x805a94=(flags&1?256:0)|(flags&2?2048:0);*(uint32_t *)0x805a84=feature?128:0;unsigned capable=(!((first|second)&2)||(flags&1))&&(!((first|second)&4)||(flags&2));unsigned policy=kind>2||mode>3||(first|second)>7||(first!=second&&mode==0&&feature)?17:(!first&&!(mode&1))||(!second&&!(mode&2))?18:0;assert(opencfw_em9305_command_phy_capable_332f80(first,second)==capable&&opencfw_em9305_command_phy_validate_332f3c(mode,first,second,kind)==policy);sends=0;unsigned expected=capable?policy:17;assert(opencfw_em9305_command_30dd04(1,mode,first,second,kind)==expected&&sends==(expected==0));if(!expected){assert(*(uint16_t *)0x830000==1&&*(uint16_t *)0x830002==0x2001&&*(uint8_t *)0x830004==mode&&*(uint8_t *)0x830005==((mode&1)?0:first)&&*(uint8_t *)0x830006==((mode&2)?0:second)&&*(uint16_t *)0x830008==kind);}if(kind==0){*(uint8_t *)0x805ac8=99;unsigned result=opencfw_em9305_command_30d4e4(mode,first,second);assert(result==expected);if(!result)assert(*(uint8_t *)0x805ac8==mode&&*(uint8_t *)0x805ac9==((mode&1)?0:first)&&*(uint8_t *)0x805aca==((mode&2)?0:second));else assert(*(uint8_t *)0x805ac8==99);}cases++;}
*(uint32_t *)0x805a94=2304;*(uint32_t *)0x805a84=0;
for(unsigned count=0;count<3;count++)for(unsigned enabled=0;enabled<2;enabled++)for(unsigned wait=0;wait<2;wait++)for(unsigned alloc=0;alloc<2;alloc++){*(uint8_t *)0x820022=count;active=enabled;pending=wait;allocation=alloc;sends=0;unsigned expected=count<=1||!enabled?2:wait?12:0;assert(opencfw_em9305_command_30dd04(1,0,1,1,0)==expected&&sends==(expected==0&&alloc));cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('phy-2030-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);print(out.strip());p.with_name('phy-2030-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Four actual PHY bodies with controlled active/pending/allocation/send. Policy and feature masks, priorities, guards, disabled-field zeroing, RAM/message bytes. No target runtime/hardware proof.'},indent=2)+'\n')
