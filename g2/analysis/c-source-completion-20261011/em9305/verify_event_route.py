from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native331a40..'):s.index('/* Native331b3c..')].replace('(uintptr_t)0x80585cu','((uintptr_t)cells)')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t cells[40];static unsigned type,handler_value,mutate,releases,enqueues,posts,stage;static uintptr_t input_event;
uint32_t opencfw_em9305_wsf_event_release(uintptr_t event){assert(event==input_event&&stage==0);releases++;return 0xabcd;}
uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t queue,uint32_t handler,uintptr_t event){assert(event==input_event&&handler==0&&queue==(uintptr_t)(cells+(type==0?12:type==1?4:28))&&stage==0);enqueues++;stage=1;if(mutate)cells[0]=255-handler_value;return 99;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t handler,uint32_t bits){assert(stage==1&&handler==(mutate?255-handler_value:handler_value)&&bits==(type==0?2:type==1?1:16));posts++;stage=2;return 0x1234;}
'''+body+r'''
int main(void){unsigned count=0;for(type=0;type<256;type++){for(handler_value=0;handler_value<256;handler_value++){for(mutate=0;mutate<2;mutate++){for(unsigned present=0;present<2;present++){
 memset(cells,0xa5,40);cells[0]=handler_value;input_event=present?0x12345678:0;releases=enqueues=posts=stage=0;unsigned routed=type==0||type==1||type==3;assert(opencfw_em9305_dispatch_331a40(type,input_event)==(routed?0x1234:0xabcd)&&enqueues==routed&&posts==routed&&releases==!routed&&stage==(routed?2:0));for(unsigned i=1;i<40;i++)assert(cells[i]==0xa5);count++;
}}}}printf("%u\n",count);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('event-route-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual event-route C, normalized product queue base; alltype/handlerbytes, queue child mutates handler, exact queue/event bits and child order/return forwarding, null/non-null event native unguarded. Controlled children; not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
