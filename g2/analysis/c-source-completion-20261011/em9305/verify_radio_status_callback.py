from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated radio status callback333480'):s.index('/* Authenticated two-word mask count30c414')]
b=b.replace('__asm__ volatile("div %0,%1,10" : "=r"(quotient) : "r"(level));','quotient=(uint32_t)((int32_t)level/10);')
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls,code,second,kind,fourth;
uint32_t opencfw_em9305_pal_hook_three(uint32_t a){assert(a==16);return a;}
uint32_t opencfw_em9305_common_activate_310580(uint32_t a){(void)a;return 0;}
uint32_t opencfw_em9305_radio_measured_level_311a40(void){return (uint32_t)-123;}
static uint32_t cb(uint32_t a,uint32_t b,uint32_t c,uint32_t d){calls++;code=a;second=b;kind=c;fourth=d;return 789;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);assert(mmap((void *)0xf00000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0xf00000);unsigned cases=0;for(unsigned event=0;event<16;event++)for(unsigned state=0;state<3;state++)for(unsigned bits=0;bits<8;bits++)for(unsigned valid=0;valid<4;valid++){memset((void *)0x800000,0,0x100000);memset((void *)0xf00000,0,0x10000);calls=0;*(uint8_t *)0x805e78=state;*(uint32_t *)0x805e7c=(uint32_t)(uintptr_t)cb;*(uint32_t *)0x805e94=0x830000;*(uint8_t *)0x830001=1;*(uint8_t *)0x805e99=2;*(uint16_t *)0x805e9c=10;*(uint16_t *)0x805e9e=20;*(uint32_t *)0x805e90=42;*(uint8_t *)0x805ea5=1;*(uint32_t *)0xf01854=1000;*(uint32_t *)0xf0184c=2000;*(uint32_t *)0xf04054=((bits&1)?32:0)|((bits&6)<<7);*(uint32_t *)0xf040a8=valid<<1;unsigned result=opencfw_em9305_radio_callback_333480(event);if(state==1){assert(result==event-8&&calls==0);}else if(event==3){assert(result==970&&calls==0&&*(uint32_t *)0x805e90==970);}else{assert(result==789&&calls==1);if(event>=8&&event<12){assert(code==1&&second==0&&kind==2&&fourth==0);}else if(event==5){assert(code==2&&second==0&&kind==2&&fourth==0);}else{assert(code==((bits&1)?3:valid==1?4:0)&&second==42&&kind==((bits&6)?3:4)&&fourth==(uint32_t)-12&&*(uint32_t *)0x805e8c==1990);}}cases++;}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('radio-status-callback-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('radio-status-callback-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Actual selected callback and MMIO predicates, controlled signal-level/activation children; signed DIV normalized for host. Event/state/status combinations. No native ARC execution or hardware proof.'},indent=2)+'\n')
