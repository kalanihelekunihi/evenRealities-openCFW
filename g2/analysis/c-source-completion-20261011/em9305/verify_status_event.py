from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native304ac4..304af8'):s.index('/* Native332200..332278')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t packet[8],event[16];static unsigned ok,allocs,packs,sends,offset;
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t type,uint32_t length){assert(type==255&&length==3);allocs++;packet[4]=77;return ok?(uintptr_t)(event+4):0;}
uint32_t opencfw_em9305_ll_pack_halfword_secondary(uintptr_t p,uint32_t value){assert(p==(uintptr_t)(event+4)&&value==0xfe82&&allocs==1);packs++;packet[4]=99;return offset;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)(event+2)&&event[4+offset]==99&&packs==1);sends++;return 0xffffffffu;}
'''+body+r'''
int main(void){unsigned n=0;for(unsigned t=0;t<256;t++)for(ok=0;ok<2;ok++)for(offset=0;offset<4;offset++){packet[2]=t;packet[4]=42;allocs=packs=sends=0;assert(opencfw_em9305_packet_gate_304ac4((uintptr_t)packet)==(t==64&&ok));assert(allocs==(t==64)&&packs==(t==64&&ok)&&sends==(t==64&&ok));n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('status-event-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C with normalized allocator/packer/send; all subtype bytes, allocation misses, packer offset propagation and fresh input after child. Native ISA/hardware not proved.'},indent=2)+'\n');print('PASS',n)
