from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native3327f4..3328c6'):s.index('/* Native332038..332192')].replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','state_pointer').replace('*(volatile uint8_t *)(uintptr_t)0x805700u','counter').replace('*(volatile uint8_t *)(uintptr_t)0x8056fau','host_mask').replace('*(volatile uint8_t *)(uintptr_t)0x8056efu','enabled')
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static uint8_t packet[32],output[32],state[32],counter,host_mask,enabled;static uintptr_t state_pointer;static unsigned type,ok,allocs,copies,sends;
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t code,uint32_t size){assert(code==((type==27||type==29)?14:62)&&size==((type==27||type==29)?4:type==26?9:6));allocs++;packet[4]=77;return ok?(uintptr_t)(output+8):0;}
uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t d,uintptr_t s){assert(d==(uintptr_t)(output+11)&&s==(uintptr_t)(packet+6));memcpy((void *)d,(void *)s,6);counter=254;copies++;return s+6;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t e){assert(e==(uintptr_t)(output+6));uint8_t *o=output+8;if(type==27||type==29){assert(o[0]==1&&o[1]==(type==29?64:57)&&o[2]==32&&o[3]==77);}else{assert(o[0]==(type==26?19:18)&&o[1]==77&&o[2]==packet[5]);assert(!memcmp(o+3,packet+6,type==26?6:3));}sends++;return 99;}
'''+b+r'''
int main(void){unsigned n=0;state_pointer=(uintptr_t)state;
for(type=0;type<256;type++)for(unsigned m=0;m<8;m++)for(unsigned en=0;en<2;en++)for(ok=0;ok<2;ok++)for(unsigned c=0;c<4;c++){
 host_mask=m;enabled=en?32:0;counter=c;state[31]=2;allocs=copies=sends=0;memset(output,0xa5,sizeof output);for(unsigned j=0;j<sizeof packet;j++)packet[j]=j;packet[2]=type;
 unsigned valid=type==27||type==29||((type==26||type==28)&&(m&(type==26?4:2))&&en&&(type!=26||c<2));unsigned success=valid&&ok;assert(opencfw_em9305_dispatch_3327f4((uintptr_t)packet)==success);assert(allocs==valid&&sends==success&&copies==(success&&type==26));assert(counter==(success&&type==26?255:c));n++;
}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('quota-event-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C all type bytes/relevant mask bits, enable/allocation outcomes, quota boundary and child-mutated fresh counter; normalized RAM/children, no native ISA/hardware execution.'},indent=2)+'\n');print('PASS',n)
