from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native331868..33194c'):s.index('/* Native30cd94/30b150')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t request;static uint8_t input[32],response[32];static unsigned command,ok,mutate,calls,allocs,sends;
static uint32_t child(unsigned c){assert(command==c);calls++;return 0x1234;}
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t size,uint32_t c){assert(c==request&&size==(command==0x202a?2:1));allocs++;if(mutate)request=0x1234;return ok?(uintptr_t)(response+8):0;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)(response+3));if(!mutate)assert(response[8]==0x34);else assert(response[8]==0xa5);sends++;return 99;}
'''+body+r'''
uint32_t opencfw_em9305_command_30af30(uint32_t a,uintptr_t b,uintptr_t c,uintptr_t d){assert(a==17&&b==(uintptr_t)(input+1)&&c==(uintptr_t)(input+7)&&d==(uintptr_t)(input+23));return child(0x2027);}
uint32_t opencfw_em9305_command_30ca68(uint32_t a,uintptr_t b){assert(a==17&&b==(uintptr_t)(input+1));return child(0x2028);}
uint32_t opencfw_em9305_command_30b150(void){return child(0x2029);}
uint32_t opencfw_em9305_command_30cd94(uint32_t a){assert(a==17);return child(0x202d);}
uint32_t opencfw_em9305_command_30deec(uint32_t a){assert(a==0x2211);return child(0x202e);}
uint32_t opencfw_em9305_command_30ddd4(uint32_t a,uintptr_t b,uint32_t c){assert(a==17&&b==(uintptr_t)(input+1)&&c==33);return child(0x204e);}
uint32_t opencfw_em9305_command_30d45c(uint32_t a,uint32_t b){assert(a==17&&b==34);return child(0x207c);}
uint32_t opencfw_em9305_command_30c918(uintptr_t p){assert(*(uint8_t*)p==0);*(uint8_t*)p=77;return child(0x202a);}
int main(void){unsigned n=0;input[0]=17;input[1]=34;input[7]=33;for(command=0;command<65536;command++)for(ok=0;ok<2;ok++)for(mutate=0;mutate<2;mutate++){request=command;calls=allocs=sends=0;memset(response,0xa5,32);unsigned valid=(command>=0x2027&&command<=0x202a)||command==0x202d||command==0x202e||command==0x204e||command==0x207c;assert(opencfw_em9305_dispatch_331868((uintptr_t)&request,(uintptr_t)input)==valid);assert(allocs==valid&&sends==(valid&&ok));assert(calls==(valid&&(command!=0x202a||(ok&&!mutate))));if(command==0x202a&&ok&&!mutate)assert(response[9]==77&&response[10]==0);n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('generic-link-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C all16bitcommands, allocator mutation/outcomes, child arguments, response selectors/layout. Normalized genuine providers; nativeISA/hardware unproved.'},indent=2)+'\n');print('PASS',n)
