from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native33194c..3319bc'):s.index('/* Native30c72c/30c7d0')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t request;static uint8_t input[8],response[32],expected[6];static unsigned command,mutate,ok,children,allocs,copies,sends,fallback;
uint32_t opencfw_em9305_dispatch_331868(uintptr_t r,uintptr_t i){assert(r==(uintptr_t)&request&&i==(uintptr_t)input);fallback++;return 0x12345678;}
static uint32_t child(uint32_t selector,uintptr_t i,uintptr_t out){assert(selector==77&&i==(uintptr_t)(input+1));for(unsigned n=0;n<6;n++){assert(((uint8_t*)out)[n]==0);expected[n]=n+19;}memcpy((void*)out,expected,6);children++;if(mutate==1)request=0x1234;return 0xabcdef12;}
uint32_t opencfw_em9305_link_address_30c7d0(uint32_t s,uintptr_t i,uintptr_t o){assert(command==0x202b);return child(s,i,o);}
uint32_t opencfw_em9305_link_address_30c72c(uint32_t s,uintptr_t i,uintptr_t o){assert(command==0x202c);return child(s,i,o);}
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t c){assert(n==7&&c==request&&children==1);allocs++;if(mutate==2)request=0x1234;return ok?(uintptr_t)(response+8):0;}
uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t d,uintptr_t s){assert(d==(uintptr_t)(response+9)&&response[8]==0x12&&memcmp((void*)s,expected,6)==0);copies++;memcpy((void*)d,(void*)s,6);return d;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)(response+3));assert(copies==(!mutate));sends++;return 99;}
'''+body+r'''
int main(void){unsigned n=0;input[0]=77;for(command=0;command<65536;command++)for(mutate=0;mutate<3;mutate++)for(ok=0;ok<2;ok++){request=command;children=allocs=copies=sends=fallback=0;memset(response,0xa5,32);unsigned valid=command==0x202b||command==0x202c;assert(opencfw_em9305_dispatch_33194c((uintptr_t)&request,(uintptr_t)input)==(valid?1:0x12345678));assert(children==valid&&allocs==valid&&sends==(valid&&ok)&&fallback==!valid);n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('address-dispatch-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C all16bitcommands, child/allocator mutation grid, initialized scratch,status byte, fresh command and fallback forwarding. Normalized children; ISA/hardware unverified.'},indent=2)+'\n');print('PASS',n)
