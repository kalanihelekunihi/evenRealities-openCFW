from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native317320..317334'):s.index('/* Native317508..317524')].replace('*(volatile uint32_t *)(stream+4u)','parent_pointer').replace('*(volatile uint8_t *)(uintptr_t)0x805addu','counter_byte')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t stream[256],parent[512],counter_byte;static uintptr_t parent_pointer;static unsigned rx,tx,queue,events,releases,receives,flushes,depth,pool,raw;
uintptr_t opencfw_em9305_wsf_queue_remove(uintptr_t q){assert(q==(uintptr_t)(parent+184));return raw?--raw,123:0;}
uint32_t opencfw_em9305_wsf_pool_release(uintptr_t p){assert(p==123);pool++;return 0;}
uintptr_t opencfw_em9305_radio_stream_receive_take_317508(uintptr_t s){assert(s==(uintptr_t)stream&&stream[0]==0);return rx?--rx,100:0;}
uint32_t opencfw_em9305_ll_receive_buffer_release_31761c(uintptr_t p){assert(p==100);receives++;return 0;}
uintptr_t opencfw_em9305_ll_stream_take_317624(uintptr_t s){assert(s==(uintptr_t)stream);return tx?--tx,200:0;}
uint32_t opencfw_em9305_wsf_event_release(uintptr_t p){assert(p==200||p==300);releases++;return 0;}
uint32_t opencfw_em9305_wsf_critical_enter(void){assert(depth==0);depth=1;return 0;}
uint32_t opencfw_em9305_wsf_critical_exit(void){assert(depth==1);depth=0;return 0;}
uint32_t opencfw_em9305_wsf_queue_empty(uintptr_t q){assert(q==(uintptr_t)(stream+8));return queue==0;}
void opencfw_em9305_radio_stream_queue_step_317980(uintptr_t s,uint32_t m){assert(s==(uintptr_t)stream&&m==1&&queue);queue--;}
uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t q,uintptr_t h){assert(q==(uintptr_t)(stream+20));*(uint8_t *)h=7;return events?--events,300:0;}
void opencfw_em9305_radio_stream_flush_31bd48(uintptr_t q,uint32_t option){assert(q==(uintptr_t)(stream+16)&&option==77);flushes++;}
'''+b+r'''
int main(void){unsigned n=0;parent_pointer=(uintptr_t)parent;parent[30]=77;for(unsigned mode=0;mode<3;mode++)for(unsigned a=0;a<4;a++)for(unsigned t=0;t<4;t++)for(unsigned q=0;q<4;q++)for(unsigned e=0;e<4;e++){
 stream[0]=1;parent[3]=mode;rx=a;tx=t;queue=q;events=e;counter_byte=255;releases=receives=flushes=depth=0;
 opencfw_em9305_radio_stream_release_31ace0((uintptr_t)stream);assert(stream[0]==0&&depth==0&&receives==(mode==0?a:0)&&releases==(mode==0?t:mode==1?e:0)&&flushes==(mode==0));assert(counter_byte==(mode==0?(uint8_t)(255+t):255));n++;}
for(raw=0;raw<2;){unsigned before=raw;pool=0;opencfw_em9305_radio_record_queue_step_317320((uintptr_t)parent);assert(pool==before);n++;if(before==1)break;raw=1;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('stream-cleanup-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C mode/receive/transmit/queue/event lengths0..3, counter wrap/critical ordering and raw-node release. RAM pointers/children normalized; no nativeISA/hardware execution.'},indent=2)+'\n');print('PASS',n)
