from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text()
body=s[s.index('/* Native331ec0..331efe'):s.index('/* Native3329b0..332a78')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t packet[8],storage[32];static unsigned a,b,ok,calls,allocs,sends;
uint32_t opencfw_em9305_packet_gate_3329b0(uintptr_t p){assert(p==(uintptr_t)packet&&calls==0);calls++;return a;}
uint32_t opencfw_em9305_packet_gate_304ac4(uintptr_t p){assert(p==(uintptr_t)packet&&calls==1);calls++;return b;}
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t type,uint32_t size){assert(type==14&&size==4&&calls==2);allocs++;packet[3]=77;return ok?(uintptr_t)(storage+8):0;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)(storage+6)&&storage[6]==1&&storage[9]==10&&storage[10]==32&&storage[11]==77);sends++;return 0xffffffffu;}
'''+body+r'''
int main(void){unsigned n=0;for(unsigned t=0;t<256;t++)for(a=0;a<2;a++)for(b=0;b<2;b++)for(ok=0;ok<2;ok++){calls=allocs=sends=0;packet[2]=t;packet[3]=42;unsigned expect=a||b||(t==3&&ok);assert(opencfw_em9305_dispatch_331ec0((uintptr_t)packet)==expect);assert(calls==(a?1:2));assert(allocs==(!a&&!b&&t==3));assert(sends==(!a&&!b&&t==3&&ok));n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('packet-subtype-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual dispatcher C; normalized genuine predicates/allocator/send, all subtype bytes, ordering and allocator input mutation; no native ISA or hardware proof.'},indent=2)+'\n')
print('PASS',n)
