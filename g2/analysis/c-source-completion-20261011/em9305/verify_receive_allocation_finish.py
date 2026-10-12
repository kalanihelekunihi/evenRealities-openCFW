from pathlib import Path
import subprocess,re,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated receive allocation/finalization324ea4'):s.index('/* Authenticated receive time check319838')];b=re.sub(r'__asm__ volatile\("div %0,%1,%2".*?;','index=delta/912u;',b)
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned scenario,n,phase;static char trace[32];static uintptr_t source=0x840000,packet=0x850002;static uint32_t chosen_expected,size_expected;
static void mark(char c){trace[n++]=c;}
static uint32_t id_callback(uint32_t id){assert(id==3);mark('I');*(uint16_t *)(source+566)=17;return scenario==0?7:0;}
uint32_t opencfw_em9305_radio_query_3253a4(uint32_t size){assert(size==(scenario==1?17:10));mark('A');if(scenario==7)return 0;*(uint8_t *)0x805ab5=9;*(uint8_t *)(source+337)=255;return 0x820002;}
uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t queue,uint32_t id,uintptr_t event){assert(phase==1&&queue==0x805abc&&id==3&&event==packet-2);assert(*(uint8_t *)(packet-2)==0x34&&*(uint8_t *)(packet-1)==0x12);mark('E');*(uint8_t *)0x805b18=99;return 0;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t handler,uint32_t events){assert(handler==99&&events==2);mark('P');return 0x31;}
uint32_t opencfw_em9305_receive_packet_release_3253bc(uintptr_t p){assert(p==chosen_expected);mark('R');return 0x32;}
static uint32_t payload_callback(uint32_t low,uint32_t high){if(scenario==4)assert(low==0x1234&&high==0);else assert(low==0x12345678&&high==0xabcdef01);mark('C');*(uint16_t *)(source+566)=65535;return 0;}
uint32_t opencfw_em9305_radio_request_start_303cd8(uint32_t chosen,uint32_t size){assert(chosen==chosen_expected&&size==size_expected);mark('Q');return 0x33;}
'''+b+r'''
static void reset(void){memset((void *)0x800000,0,0x100000);n=0;memset(trace,0,sizeof(trace));*(uint32_t *)0x805c70=source-912*3;*(uint16_t *)(source+566)=10;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;phase=0;for(scenario=0;scenario<12;scenario++){reset();*(uint8_t *)(source+344)=scenario<2||scenario==10?0:scenario==5?4:scenario==11?3:1;*(uint8_t *)(source+346)=scenario==2?1:0;*(uint8_t *)(source+349)=scenario==3?15:scenario==4?0:7;*(uint8_t *)0x805ab5=scenario==6?0:2;*(uint8_t *)(source+109)=1;*(uint8_t *)(source+111)=scenario==11?2:0;*(uint32_t *)(source+464)=0xffffffff;*(uint32_t *)(source+468)=0xffffffff;*(uint32_t *)0x8052cc=scenario==9?0:0x1234;if(scenario<2){*(uint32_t *)0x805cd8=0x830000;*(uint32_t *)(0x830000+16)=(uint32_t)(uintptr_t)id_callback;}
unsigned result=opencfw_em9305_receive_state_324ea4(source);if(scenario==0)assert(result==0&&strcmp(trace,"I")==0);else if(scenario==1)assert(result==0x820002&&strcmp(trace,"IA")==0);else if(scenario==2)assert(result==0&&n==0&&*(uint8_t *)(source+337)==0);else if(scenario==3||scenario==4||scenario==5||scenario==10)assert(result==0&&n==0&&*(uint8_t *)(source+337)==1);else if(scenario==6)assert(result==0xffffffff&&n==0&&*(uint8_t *)(source+337)==0);else if(scenario==7)assert(result==0xffffffff&&strcmp(trace,"A")==0&&*(uint8_t *)0x805ab5==2);else{assert(result==0x820002&&strcmp(trace,"A")==0&&*(uint8_t *)0x805ab5==8&&*(uint8_t *)(source+337)==0);assert(*(uint32_t *)(source+464)==(scenario==8?0:0xffffffff)&&*(uint32_t *)(source+468)==(scenario==8?0:0xffffffff));}cases++;}
phase=1;for(scenario=0;scenario<8;scenario++){reset();*(uint16_t *)(source+262)=0x1234;*(uint8_t *)(source+109)=scenario==7?0:1;*(uint8_t *)(source+111)=scenario==4?1:scenario==6?2:0;*(uint32_t *)(source+464)=0x12345678;*(uint32_t *)(source+468)=0xabcdef01;if(scenario>=4)*(uint32_t *)0x8052cc=(uint32_t)(uintptr_t)payload_callback;uintptr_t input=scenario==0?0:packet;uint32_t data=scenario==2||scenario==4?0x820002:0;chosen_expected=data?data:input;size_expected=scenario==4||scenario==5?5:16;unsigned result=opencfw_em9305_receive_packet_finish_3253c4(source,input,data,scenario>=3);const char *expected=scenario==0?"":scenario==1?"R":scenario==2?"EPR":scenario==4?"EPCQ":scenario==5?"CQ":"Q";assert(strcmp(trace,expected)==0);assert(result==(scenario==0?source:scenario<=2?0x32:0x33));cases++;}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('receive-allocation-finish-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('receive-allocation-finish-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Actual selected C fixed RAM; controlled allocator/enqueue/post/release/request and optional id/payload callbacks; DIV normalized. Failure effects, fresh allocator/callback reads, 64-bit carry, packet header and routing. No native ARC runtime/layout/hardware proof.'},indent=2)+'\n')
