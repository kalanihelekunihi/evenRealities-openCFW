from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native3329b0..332a78'):s.index('/* Native304ac4..304af8')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t packet[32],event[32];static unsigned ok,t,allocs,sends,writes;
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t code,uint32_t size){assert(code==255&&size==(t==49?10:15));allocs++;packet[2]=0;packet[4]=77;return ok?(uintptr_t)(event+4):0;}
uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t out,uint32_t low,uint32_t high){assert(out==(uintptr_t)(event+7+writes*6));unsigned off=8+writes*8;uint32_t a,b;memcpy(&a,packet+off,4);memcpy(&b,packet+off+4,4);assert(low==a&&high==b);for(unsigned i=0;i<4;i++)((uint8_t*)out)[i]=low>>(8*i);((uint8_t*)out)[4]=high;((uint8_t*)out)[5]=high>>8;writes++;return out;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)(event+2)&&event[4]==(t==21?241:t==49?243:245)&&event[5]==255&&event[6]==77);if(t==49){assert(memcmp(event+10,packet+8,4)==0);assert(event[7]==0xa5&&event[8]==0xa5&&event[9]==0xa5);}if(t==34){assert(memcmp(event+7,packet+6,4)==0);assert(memcmp(event+11,packet+12,8)==0);}if(t==21)assert(writes==2);sends++;return 0xffffffffu;}
'''+body+r'''
int main(void){unsigned n=0;for(t=0;t<256;t++)for(ok=0;ok<2;ok++)for(unsigned pattern=0;pattern<16;pattern++){for(unsigned i=0;i<32;i++)packet[i]=pattern*13+i;packet[2]=t;memset(event,0xa5,32);allocs=sends=writes=0;unsigned valid=t==21||t==34||t==49;assert(opencfw_em9305_packet_gate_3329b0((uintptr_t)packet)==(valid&&ok));assert(allocs==valid&&sends==(valid&&ok));n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('vendor-packet-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C, all subtype bytes, allocation failure/success, captured subtype mutation, fresh data, untouched event gap, native store layout. Normalized children; native ISA and hardware unverified.'},indent=2)+'\n');print('PASS',n)
