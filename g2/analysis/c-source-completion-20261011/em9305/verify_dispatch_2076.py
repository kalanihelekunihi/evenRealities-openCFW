from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated response33118c'):s.index('/* Authenticated command2076 providers')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t request;static uint8_t input[10],output[16];static unsigned alloc_ok,calls,query_calls;static uint32_t args[6],length;static uintptr_t query_input;
static uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t cmd){assert(cmd==request);length=n;return alloc_ok?(uintptr_t)output:0;}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)output-5);return 87;}
static uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t p,uint32_t status){assert(p==(uintptr_t)&request&&status==99);calls++;return 5;}
'''+b+r'''
uint32_t opencfw_em9305_command_30c65c(uint32_t a,uint32_t c,uint32_t d){assert(a==0x2211&&c==0&&d==0x33);calls++;return 99;}
uint32_t opencfw_em9305_command_30da5c(uint32_t a,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g){uint32_t v[]={a,c,d,e,f,g};memcpy(args,v,sizeof(v));calls++;return 98;}
uint32_t opencfw_em9305_command_30da2c(uint32_t a,uint32_t c){assert(a==0x2211&&c==0x33);calls++;return 97;}
uint32_t opencfw_em9305_command_30e000(uint32_t a,uint32_t c,uint32_t d){assert(a==0x2211&&c==0x33&&d==0x44);calls++;return 96;}
uint32_t opencfw_em9305_command_query_30bd34(uint32_t a,uint32_t c,uintptr_t f,uintptr_t s){assert(a==0x2211&&c==0x33&&*(uint8_t *)f==0&&*(uint8_t *)s==0);query_input=f;*(uint8_t *)f=0x55;*(uint8_t *)s=0x66;query_calls++;return 95;}
int main(void){unsigned cases=0;for(unsigned command=0;command<65536;command++){if(command>=0x2076&&command<=0x207a)continue;request=command;assert(opencfw_em9305_dispatch_331074((uintptr_t)&request,0)==0);cases++;}
for(unsigned allocation=0;allocation<2;allocation++)for(unsigned index=0;index<5;index++){request=0x2076+index;for(unsigned n=0;n<10;n++)input[n]=0x11*(n+1);memset(output,0xaa,sizeof(output));alloc_ok=allocation;calls=query_calls=length=0;assert(opencfw_em9305_dispatch_331074((uintptr_t)&request,(uintptr_t)input)==1);if(index==1){assert(calls==2&&query_calls==0&&length==0);}else{assert(calls==(index!=0)&&length==(index==0?6:3));assert(query_calls==(index==0&&allocation));if(allocation){assert(output[0]==(index==0?95:index==2?98:index==3?97:96)&&output[1]==0x11&&output[2]==0x22);if(index==0)assert(output[3]==0x33&&output[4]==0x55&&output[5]==0x66);}}if(index==2){uint32_t expected[]={0x2211,0x33,0x44,0x55,0x66,0x8877};assert(memcmp(args,expected,sizeof(args))==0);}cases++;}
assert(query_input);printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('dispatch-2076-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('dispatch-2076-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Actual dispatch/response bodies with controlled providers, allocation and event lower. Unsupported 16-bit commands, all five packing paths and allocation cuts. No target runtime/hardware proof.'},indent=2)+'\n')
