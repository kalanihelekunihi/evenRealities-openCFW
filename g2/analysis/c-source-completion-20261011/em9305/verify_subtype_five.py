from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native3319bc..331a40'):s.index('/* Native331814..331868')].replace('*(volatile uint8_t *)(uintptr_t)0x8056f9u','mask').replace('*(volatile uint8_t *)(uintptr_t)0x8056efu','enabled')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t packet[48],event[48],mask,enabled;static unsigned ok,allocs,copies,sends;
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t code,uint32_t size){assert(code==62&&size==31);allocs++;packet[4]=77;return ok?(uintptr_t)(event+4):0;}
uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t d,uintptr_t s){static const unsigned offsets[3]={10,16,29};assert(d==(uintptr_t)(event+10+copies*6)&&s==(uintptr_t)(packet+offsets[copies]));memcpy((void*)d,(void*)s,6);copies++;if(copies==3)packet[16]=99;return d;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t e){assert(e==(uintptr_t)(event+2)&&event[4]==10&&event[5]==77&&copies==3);assert(memcmp(event+6,packet+6,4)==0&&memcmp(event+10,packet+10,6)==0&&memcmp(event+22,packet+29,6)==0&&memcmp(event+28,packet+16,7)==0);sends++;return 99;}
'''+body+r'''
int main(void){unsigned n=0;for(unsigned type=0;type<256;type++)for(unsigned m=0;m<256;m++)for(unsigned en=0;en<2;en++)for(ok=0;ok<2;ok++){for(unsigned i=0;i<48;i++)packet[i]=i;packet[2]=type;mask=m;enabled=en?32:0;allocs=copies=sends=0;unsigned valid=type==5&&(m&2)&&en;assert(opencfw_em9305_dispatch_3319bc((uintptr_t)packet)==(valid&&ok));assert(allocs==valid&&copies==(valid&&ok?3:0)&&sends==(valid&&ok));n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('subtype-five-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C alltype/maskbytes,enable/allocationgrid,three ordered address copies, fresh input after children. Native memcpy R1 advancement statically traced; ISA/hardware not proved.'},indent=2)+'\n');print('PASS',n)
