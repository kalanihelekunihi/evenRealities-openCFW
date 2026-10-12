from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated dispatch3316e0'):s.index('/* Authenticated PHY policy332f3c/332f80')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t request;static uint8_t input[10],output[10];static unsigned allocation,calls,queries,status_calls;static uint32_t length;
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t cmd){assert(cmd==request);length=n;return allocation?(uintptr_t)output:0;}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)output-5);return 99;}
static uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t p,uint32_t status){assert(p==(uintptr_t)&request&&status==92);status_calls++;return 98;}
'''+b+r'''
uint32_t opencfw_em9305_command_30d4e4(uint32_t a,uint32_t c,uint32_t d){assert(a==0x11&&c==0x22&&d==0x33);calls++;return 91;}
uint32_t opencfw_em9305_command_30dd04(uint32_t a,uint32_t c,uint32_t d,uint32_t e,uint32_t f){assert(a==0x2211&&c==0x33&&d==0x44&&e==0x55&&f==0x7766);calls++;return 92;}
uint32_t opencfw_em9305_command_30cba0(uintptr_t p){assert(*(uint16_t *)p==0&&*(uint32_t *)(p+16)==0&&*(uint8_t *)(p+14)==2&&*(uint8_t *)(p+11)==0&&*(uint32_t *)(p+4)==0x71764129&&*(uint16_t *)(p+12)==256&&*(uint8_t *)(p+8)==0x11&&*(uint8_t *)(p+9)==0x22&&*(uint8_t *)(p+10)==0x33);calls++;return 93;}
uint32_t opencfw_em9305_command_30e120(uintptr_t p){assert(*(uint16_t *)p==0&&*(uint32_t *)(p+12)==0&&*(uint8_t *)(p+8)==2&&*(uint16_t *)(p+6)==0&&*(uint8_t *)(p+16)==127&&*(uint8_t *)(p+2)==0x11&&*(uint8_t *)(p+3)==0x22&&*(uint8_t *)(p+4)==0x33&&*(uint8_t *)(p+5)==0x44);calls++;return 94;}
uint32_t opencfw_em9305_command_query_30c824(uint32_t id,uintptr_t a,uintptr_t c){assert(id==0x2211&&*(uint8_t *)a==0&&*(uint8_t *)c==0);*(uint8_t *)a=0x55;*(uint8_t *)c=0x66;queries++;return 90;}
int main(void){unsigned cases=0;for(unsigned command=0;command<65536;command++){if(command>=0x2030&&command<=0x2034)continue;request=command;assert(opencfw_em9305_dispatch_3316e0((uintptr_t)&request,0)==0);cases++;}
for(unsigned alloc=0;alloc<2;alloc++)for(unsigned index=0;index<5;index++){request=0x2030+index;for(unsigned n=0;n<10;n++)input[n]=0x11*(n+1);allocation=alloc;calls=queries=status_calls=length=0;memset(output,0xaa,sizeof(output));assert(opencfw_em9305_dispatch_3316e0((uintptr_t)&request,(uintptr_t)input)==1);assert(calls==(index!=0));if(index==2){assert(status_calls==1&&length==0&&queries==0);}else{assert(length==(index==0?5:1)&&queries==(index==0&&alloc));if(alloc){assert(output[0]==90+index);if(index==0)assert(output[1]==0x11&&output[2]==0x22&&output[3]==0x55&&output[4]==0x66);}}cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('dispatch-2030-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);print(out.strip());p.with_name('dispatch-2030-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Actual selected five-command dispatch with controlled providers, query, allocation/send. Unsupported16bit commands, packing, initialized scratch fields only, allocation/query/status paths. Native padding intentionally not read by fixture; hardware/runtime unproved.'},indent=2)+'\n')
