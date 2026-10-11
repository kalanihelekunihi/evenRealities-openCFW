from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native332194..332200'):s.index('/* Native306a20..306a7c')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint16_t request;static uint8_t input[3],response[16];static unsigned command,ok,mutate,queries,modes,allocs,posts,sends,status;
uint32_t opencfw_em9305_link_query_30aec4(uint32_t handle){assert(handle==(unsigned)(input[0]+input[1]*256));queries++;return status;}
uint32_t opencfw_em9305_link_mode_30c940(uint32_t handle,uint32_t mode){assert(handle==(unsigned)(input[0]+input[1]*256)&&mode==input[2]);modes++;if(mutate==1)request=0x1234;return status;}
uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t p,uint32_t value){assert(p==(uintptr_t)&request&&queries==1&&value==status);posts++;return 88;}
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t size,uint32_t code){assert(size==3&&code==request&&modes==1);allocs++;if(mutate==2)request=0x1234;return ok?(uintptr_t)(response+8):0;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)(response+3));if(request==0x2067)assert(response[8]==(uint8_t)status&&response[9]==input[0]&&response[10]==0);else assert(response[8]==0xa5&&response[9]==0xa5&&response[10]==0xa5);sends++;return 88;}
'''+body+r'''
int main(void){unsigned n=0;for(command=0;command<65536;command++)for(ok=0;ok<2;ok++)for(mutate=0;mutate<3;mutate++){request=command;input[0]=command;input[1]=command>>8;input[2]=77;status=0x12345678;queries=modes=allocs=posts=sends=0;memset(response,0xa5,16);unsigned valid=command==0x2066||command==0x2067;assert(opencfw_em9305_dispatch_332194((uintptr_t)&request,(uintptr_t)input)==valid);assert(queries==(command==0x2066)&&posts==queries&&modes==(command==0x2067)&&allocs==modes&&sends==(modes&&ok));n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('link-command-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C all16-bitcommands, allocator/mutation grid, status/fullword, fresh request after children. Normalized providers; native ISA/hardware not proved.'},indent=2)+'\n');print('PASS',n)
