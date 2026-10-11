from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native332200..332278'):s.index('/* Native330e78..330f08')].replace('*(volatile uint8_t *)(uintptr_t)0x8056fbu','mask').replace('*(volatile uint8_t *)(uintptr_t)0x8056efu','enabled')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t packet[32],event[64],mask,enabled;static unsigned type,ok,allocs,fills,sends;
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t code,uint32_t size){assert(code==62&&size==(type==39?29:7));allocs++;packet[4]=77;return ok?(uintptr_t)(event+8):0;}
uint32_t opencfw_em9305_packet_event_fill_330e78(uintptr_t e,uintptr_t p){assert(e==(uintptr_t)(event+8)&&p==(uintptr_t)packet&&allocs==1);fills++;return 29;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t e){assert(e==(uintptr_t)(event+6));if(type==40)assert(event[8]==26&&memcmp(event+9,packet+4,6)==0);sends++;return 99;}
'''+body+r'''
int main(void){unsigned n=0;for(type=0;type<256;type++)for(unsigned m=0;m<256;m++)for(unsigned en=0;en<2;en++)for(ok=0;ok<2;ok++){mask=m;enabled=en?32:0;allocs=fills=sends=0;packet[2]=type;packet[4]=42;unsigned valid=(type==39||type==40)&&(mask&(type==39?1:2))&&en;assert(opencfw_em9305_dispatch_332200((uintptr_t)packet)==(valid&&ok));assert(allocs==valid&&sends==(valid&&ok)&&fills==(valid&&ok&&type==39));n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('product-event-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C, all type/mask bytes, enable/allocator outcomes, captured type and fresh input stores. Normalized children/global RAM; native ISA/hardware unverified.'},indent=2)+'\n');print('PASS',n)
