from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated five command providers30c5c0'):s.index('/* Authenticated command apply307d0c')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned gate=1,ready=1,calls;
uint32_t opencfw_em9305_ll_stream_gate_30e510(void){return gate;}
uint32_t opencfw_em9305_command_apply_307fcc(uint32_t a,uint32_t b,uint32_t c){assert(a==0xffffffff&&b==55&&c==66);calls++;return 100;}
uint32_t opencfw_em9305_command_apply_30805c(uint32_t a,uint32_t b,uint32_t c){assert(a==0xffffffff&&b==55&&c==66);calls++;return 101;}
uint32_t opencfw_em9305_command_ready_3213d0(uint32_t a){assert(a<0xf00);return ready;}
uint32_t opencfw_em9305_command_apply_307d0c(uint32_t a,uint32_t b){assert(a==1&&b<=7);calls++;return 999;}
uint32_t opencfw_em9305_command_apply_309874(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){assert(a==0xffffffff&&b<=3&&c==499&&(d&65535)>=10&&(d&65535)<=0x4000&&e==0x12345678);calls++;return 102;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(gate=0;gate<2;gate++){calls=0;assert(opencfw_em9305_command_30c5c0(0xffffffff,55,66)==(gate?100:12)&&calls==gate);calls=0;assert(opencfw_em9305_command_30c5e0(0xffffffff,55,66)==(gate?101:12)&&calls==gate);cases+=2;}gate=1;for(unsigned cap=0;cap<2;cap++)for(unsigned mode=0;mode<5;mode++)for(unsigned first=499;first<=500;first++)for(unsigned second=0;second<65536;second++){*(uint32_t *)0x805b34=cap?16:0;calls=0;unsigned expected=mode>3?18:mode==3&&!cap?17:first>499||second<10||second>0x4000?18:0;unsigned r=opencfw_em9305_command_30dc70(0xffffffff,mode,first,second|0x10000,0x12345678);assert(r==(expected?expected:102)&&calls==!expected);r=opencfw_em9305_command_30d48c(mode,first,second|0x10000,99);assert(r==expected);if(!expected)assert(*(uint16_t *)0x805ace==second&&*(uint16_t *)0x805acc==first&&*(uint8_t *)0x805acb==mode);cases+=2;}
for(unsigned cap=0;cap<2;cap++)for(ready=0;ready<2;ready++)for(unsigned mode=0;mode<8;mode++){*(uint32_t *)0x805b34=cap?16:0;calls=0;unsigned r=opencfw_em9305_command_30dbd4(1,mode),expected=!ready?66:(mode&3)==3&&!cap?17:0;assert(r==expected&&calls==!expected);cases++;}
gate=0;assert(opencfw_em9305_command_30dbd4(0xffffffff,0)==12&&opencfw_em9305_command_30dc70(0,0,0,0,0)==12&&opencfw_em9305_command_30d48c(0,0,0,0)==12);cases+=3;gate=ready=1;assert(opencfw_em9305_command_30dbd4(0xf00,0)==18);cases++;printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('command-2059-providers-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('command-2059-providers-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected five providers with controlled gate/readiness/apply children. Full incoming ids, modes/capability, exhaustive halfword range plus upper incoming bits, store fields and exact child returns. No native ARC execution/layout/hardware proof.'},indent=2)+'\n')
