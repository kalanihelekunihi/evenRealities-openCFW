from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated command dispatch330fa0'):s.index('/* Authenticated five command providers30c5c0')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static unsigned command,calls,responses;
static uint32_t check(unsigned c){assert(command==c);calls++;return 0x12345678;}
uint32_t opencfw_em9305_command_30dbd4(uint32_t a,uint32_t b){assert(a==0x4321&&b==0x65);return check(0x2059);}
uint32_t opencfw_em9305_command_30c5e0(uint32_t a,uint32_t b,uint32_t c){assert(a==0x4321&&b==0x8765&&c==0xcba9);return check(0x205a);}
uint32_t opencfw_em9305_command_30c5c0(uint32_t a,uint32_t b,uint32_t c){assert(a==0x4321&&b==0x8765&&c==0xa9);return check(0x205b);}
uint32_t opencfw_em9305_command_30dc70(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e){assert(a==0x4321&&b==0x65&&c==0xa987&&d==0xedcb&&e==0xff);return check(0x205c);}
uint32_t opencfw_em9305_command_30d48c(uint32_t a,uint32_t b,uint32_t c,uint32_t d){assert(a==0x21&&b==0x6543&&c==0xa987&&d==0xcb);return check(0x205d);}
uint32_t opencfw_em9305_ll_connection_response_32f34c(uintptr_t r,uint32_t s,uint32_t l,uintptr_t p,uint32_t id){assert(*(uint16_t *)r==command&&s==0x12345678&&p==0&&l==((command>=0x205a&&command<=0x205c)?3:1)&&id==((command>=0x205a&&command<=0x205c)?0x4321:0));responses++;return 999;}
'''+b+r'''
int main(void){unsigned cases=0;uint8_t input[8]={0x21,0x43,0x65,0x87,0xa9,0xcb,0xed,0xff};for(command=0x2059;command<=0x205d;command++){uint16_t request=command;calls=responses=0;assert(opencfw_em9305_dispatch_330fa0((uintptr_t)&request,(uintptr_t)input)==1&&calls==1&&responses==1);cases++;}for(unsigned c=0;c<65536;c++){if(c>=0x2059&&c<=0x205d)continue;uint16_t request=c;calls=responses=0;assert(opencfw_em9305_dispatch_330fa0((uintptr_t)&request,0)==0&&calls==0&&responses==0);cases++;}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('dispatch-2059-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('dispatch-2059-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected full dispatch, controlled five command providers and response; native byte-order vectors, full status forwarding, response length/id, every unsupported16-bit opcode with null input. No native ARC execution/layout/hardware proof.'},indent=2)+'\n')
