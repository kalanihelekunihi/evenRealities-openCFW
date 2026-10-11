from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('extern uint32_t opencfw_em9305_command_30db64'):s.index('extern uint32_t opencfw_em9305_command_apply_3093a0')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static _Alignas(4) uint8_t input[16],request[4],response[16];static unsigned fail,calls,allocated,sent,mutation,initial;
uint32_t opencfw_em9305_command_30db64(uint32_t k,uintptr_t p){assert(k==input[0]);uint8_t *v=(uint8_t *)p;for(unsigned i=0;i<11;i++)assert(v[i]==input[i+1]);calls++;return 0x1234;}
uint32_t opencfw_em9305_command_30dc20(uint32_t a,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uintptr_t p){assert(a==input[0]+((uint32_t)input[1]<<8)&&c==input[2]+((uint32_t)input[3]<<8)&&d==input[4]&&e==input[5]&&f==input[6]&&g==input[7]&&p==(uintptr_t)(input+8));calls++;return 0x1234;}
uint32_t opencfw_em9305_command_30dccc(uint32_t a,uint32_t c,uint32_t n,uintptr_t p){assert(a==input[0]+((uint32_t)input[1]<<8)&&c==input[2]+((uint32_t)input[3]<<8)&&n==input[4]&&p==(uintptr_t)(input+5));calls++;return 0x1234;}
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t c){assert(c==initial&&n==(initial==0x2086?2:3));allocated++;if(mutation)*(uint16_t *)request=mutation==1?0x2086:0x2083;return fail?0:(uintptr_t)(response+5);}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)response&&response[5]==0x34);unsigned c=*(uint16_t *)request;if(c==0x2086)assert(response[6]==(initial==0x2086?input[0]:0));else if(c==0x2083||c==0x2084){assert(response[6]==(initial==0x2086?0:input[0])&&response[7]==(initial==0x2086?0:input[1]));}sent++;return 0;}
'''+b+r'''
int main(void){unsigned cases=0;for(unsigned type=0;type<4;type++)for(unsigned seed=0;seed<256;seed++)for(fail=0;fail<2;fail++)for(mutation=0;mutation<3;mutation++){initial=type==0?0x2083:type==1?0x2084:type==2?0x2086:0;*(uint16_t *)request=initial;for(unsigned i=0;i<16;i++)input[i]=seed+i;calls=allocated=sent=0;assert(opencfw_em9305_dispatch_331204((uintptr_t)request,(uintptr_t)input)==(type<3));assert(calls==(type<3)&&allocated==(type<3)&&sent==(type<3&&!fail));cases++;}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('command208x-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C commands2083/2084/2086/unknown,256input patterns, allocation success/failure, command reread mutation and exact defined scratch/response bytes. Native children normalized; sevenargument30dc20 nativeR6 ABI remains unqualified. No native/layout/hardware proof.'},indent=2)+'\n');print('PASS',n)
