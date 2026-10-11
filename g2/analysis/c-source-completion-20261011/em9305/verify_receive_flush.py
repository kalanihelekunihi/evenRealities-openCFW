from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native317508..317524'):s.index('/* Native317980..317a10')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static _Alignas(4) uint8_t buffer[64];static unsigned available,queued,releases,take;
uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t q,uintptr_t h){*(uint8_t *)h=7;if(take){assert(q==(uintptr_t)(buffer+8));return available?100:0;}assert(q==(uintptr_t)(buffer+16));return queued?--queued,200:0;}
uint32_t opencfw_em9305_wsf_event_release(uintptr_t p){assert(p==100||p==200);releases++;return 0;}
'''+b+r'''
int main(void){unsigned n=0;for(unsigned mode=0;mode<256;mode++)for(available=0;available<2;available++)for(unsigned q=0;q<8;q++){
 take=1;assert(opencfw_em9305_radio_stream_receive_take_317508((uintptr_t)buffer)==(available?110:0));take=0;queued=q;releases=0;*(uint32_t *)buffer=available?100:0;*(uint16_t *)(buffer+6)=65535;opencfw_em9305_radio_stream_flush_31bd48((uintptr_t)buffer,mode);assert(releases==(mode?available:q)&&*(uint16_t *)(buffer+6)==0);assert(*(uint32_t *)buffer==(mode?0:available?100:0));n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('receive-flush-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C modebytes/event presence/queue length0..7, privateprefix return/buffer clear/count reset. Real children normalized; no nativeISA/hardware proof.'},indent=2)+'\n');print('PASS',n)
