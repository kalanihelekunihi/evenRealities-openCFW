from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native331814..331868'):s.index('/* Native33194c..3319bc')].replace('*(volatile uint8_t *)(uintptr_t)0x8056f9u','mask').replace('*(volatile uint8_t *)(uintptr_t)0x8056efu','enabled')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t packet[48],event[48],mask,enabled;static unsigned ok,allocs,copies,sends;
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t code,uint32_t size){assert(code==62&&size==6);allocs++;packet[4]=77;return ok?(uintptr_t)(event+4):0;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t e){assert(e==(uintptr_t)(event+2)&&event[4]==12&&event[5]==77);assert(memcmp(event+6,packet+6,4)==0);sends++;return 99;}
'''+body+r'''
int main(void){unsigned n=0;for(unsigned type=0;type<256;type++)for(unsigned m=0;m<256;m++)for(unsigned en=0;en<2;en++)for(ok=0;ok<2;ok++){for(unsigned i=0;i<48;i++)packet[i]=i;packet[2]=type;mask=m;enabled=en?32:0;allocs=copies=sends=0;unsigned valid=type==22&&(m&8)&&en;assert(opencfw_em9305_dispatch_331814((uintptr_t)packet)==(valid&&ok));assert(allocs==valid&&copies==0&&sends==(valid&&ok));n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('subtype-twenty-two-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C alltype/maskbytes,enable/allocationgrid,six-byte payload/store order and post-update send pointer; ISA/hardware not proved.'},indent=2)+'\n');print('PASS',n)
