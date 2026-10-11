from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native317980..317a10'):s.index('/* Native31ae74..31ae84')].replace('*(volatile uint8_t *)(uintptr_t)0x805adcu','counter_byte').replace('__asm__ volatile("mpyuw %0,%1,%2":"=r"(product):"r"(truncated),"r"(unit));','product=truncated*unit;')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t stream[256],packet[24],counter_byte;static unsigned present,removed,released,completed,depth,needed,mutate;
uintptr_t opencfw_em9305_wsf_event_peek(uintptr_t q,uintptr_t h){assert(q==(uintptr_t)(stream+8));*(uint8_t *)h=3;return present?(uintptr_t)packet:0;}
uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t l,uint32_t u){assert(l==*(uint16_t *)(packet+8)&&u==packet[10]);if(mutate)packet[10]=5;return needed;}
uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t q,uintptr_t h){assert(q==(uintptr_t)(stream+8)&&present);*(uint8_t *)h=3;present=0;removed++;return (uintptr_t)packet;}
uint32_t opencfw_em9305_wsf_event_release(uintptr_t p){assert(p==(uintptr_t)packet&&removed==1);released++;return 0;}
void opencfw_em9305_radio_packet_complete_31ae74(uintptr_t p){assert(p==(uintptr_t)packet&&released==1);completed++;}
uint32_t opencfw_em9305_wsf_critical_enter(void){assert(depth==0&&completed==1);depth=1;return 0;}
uint32_t opencfw_em9305_wsf_critical_exit(void){assert(depth==1&&counter_byte==0);depth=0;return 0;}
'''+b+r'''
int main(void){unsigned n=0;for(unsigned budget=0;budget<512;budget++)for(needed=1;needed<5;needed++)for(unsigned len=1;len<17;len++)for(unsigned flags=0;flags<4;flags++)for(mutate=0;mutate<2;mutate++){
 memset(stream,0,256);memset(packet,0,24);stream[36]=flags&1;stream[108]=flags&2;stream[16]=255;packet[10]=2;*(uint16_t *)(packet+8)=len;present=1;counter_byte=255;removed=released=completed=depth=0;
 unsigned rem=budget,progress=0,done=0;while((uint8_t)rem){if(needed<=(uint8_t)rem){progress+=needed;rem-=needed;}else{progress+=rem;rem=0;}progress=(uint8_t)progress;if(progress*(mutate?5:2)>=len){done=1;break;}}
 opencfw_em9305_radio_stream_queue_step_317980((uintptr_t)stream,budget);assert(packet[11]==progress&&removed==done&&released==done&&completed==done&&depth==0);assert(counter_byte==(done?0:255)&&stream[16]==(done&&flags==0?0:255));n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('stream-queue-step-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C budgets0..511/timing cuts/lengths/mode flags/child-mutated fresh unit, queue release/completion/critical byte-wrap order. Genuine children andMPYUW normalized; nativeISA/hardware unproved.'},indent=2)+'\n');print('PASS',n)
