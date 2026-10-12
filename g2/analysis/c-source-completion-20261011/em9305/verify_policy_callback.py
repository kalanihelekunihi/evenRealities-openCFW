from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();s=s[s.index('/* Native policy callback332db4'):s.index('/* Native continuation332e2c')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
'''+s+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);*(uint32_t *)0x82002c=0x830000;*(uint32_t *)0x830068=0x840000;uint16_t counts[]={0,1,65534,65535};unsigned cases=0;
for(unsigned state=0;state<4;state++)for(unsigned event=0;event<3;event++)for(unsigned ci=0;ci<4;ci++)for(unsigned limit=0;limit<4;limit++)for(unsigned mismatch=0;mismatch<5;mismatch++)for(unsigned index=0;index<34;index++)for(unsigned bits=0;bits<2;bits++){*(uint8_t *)0x8058dc=state;*(uint16_t *)0x8058e0=counts[ci];*(uint16_t *)0x8058de=limit;*(uint8_t *)0x805996=19;*(uint8_t *)0x830001=mismatch==1?18:19;*(uint8_t *)0x805995=5;*(uint8_t *)0x840000=mismatch==2?4:37;*(uint8_t *)0x805994=13;*(uint8_t *)0x840001=mismatch==3?12:13;*(uint8_t *)0x805997=2;*(uint8_t *)0x83000c=mismatch==4?1:2;*(uint32_t *)0x8059a4=index;*(uint32_t *)0x8059a0=bits?0xffffffff:0;*(uint32_t *)0x830008=0x12345678;unsigned next=(uint16_t)(counts[ci]+1);unsigned good=state==1&&event!=1&&(!limit||next<limit)&&!mismatch;assert(opencfw_em9305_command_callback_332db4(0x820000,event)==good);assert(*(uint16_t *)0x8058e0==next&&*(uint32_t *)0x8059a4==(good?(index+1)&31:index)&&*(uint32_t *)0x830008==(good?(bits?0x555555:0xaaaaaa):0x12345678));cases++;}
printf("PASS %u\n",cases);}
''';p=Path(__file__).with_name('policy-callback-host.c');p.write_text(h);a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/q && /tmp/q'],text=True);print(a.strip());p.with_name('policy-callback-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual full callback, counter wrap, guards/event/limit, four policy mismatch exits, bit5 clear, 32-bit pattern and rolling index. No target interrupt/hardware proof.'},indent=2)+'\n')
