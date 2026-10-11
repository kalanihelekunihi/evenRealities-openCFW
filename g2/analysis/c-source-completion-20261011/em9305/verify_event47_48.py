from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native331100..33118c'):s.index('extern uint32_t opencfw_em9305_command_30db64')]
for addr,name in [('8056fc','mask47'),('8056fb','mask48'),('8056ef','enabled')]:b=b.replace(f'*(volatile uint8_t *)(uintptr_t)0x{addr}u',name)
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t input[16],event[16],mask47,mask48,enabled;static unsigned fail,allocated,sent;
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t code,uint32_t n){assert(code==62&&n==(input[2]==47?9:5));allocated++;return fail?0:(uintptr_t)(event+2);}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)event);sent++;uint8_t *e=event+2;assert(e[0]==(input[2]==47?33:32));if(input[2]==47){assert(e[1]==input[4]);for(unsigned i=2;i<9;i++)assert(e[i]==input[i+4]);}else for(unsigned i=1;i<5;i++)assert(e[i]==input[i+3]);return 0;}
'''+b+r'''
int main(void){unsigned cases=0;for(unsigned type=0;type<256;type++)for(unsigned mask=0;mask<256;mask++)for(unsigned enable=0;enable<2;enable++)for(fail=0;fail<2;fail++){for(unsigned i=0;i<16;i++)input[i]=i+91;input[2]=type;mask47=mask48=mask;enabled=enable?255:0;allocated=sent=0;unsigned expected_alloc=(type==47?(mask&1)!=0:type==48?(mask&128)!=0:0)&&enable;unsigned expected=expected_alloc&&!fail;assert(opencfw_em9305_dispatch_331100((uintptr_t)input)==expected&&allocated==expected_alloc&&sent==expected);cases++;}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('event47-48-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C all256 type/mask values, enabled/disabled, alloc success/failure, exact payload bytes and send-header pointer. Globals/children controlled, no nativeISA/layout/hardware proof.'},indent=2)+'\n');print('PASS',n)
