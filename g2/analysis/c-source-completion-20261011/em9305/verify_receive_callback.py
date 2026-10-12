from pathlib import Path
import re,subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated receive callback31e620'):s.index('/* Authenticated receive gate children324f68')];b=re.sub(r'__asm__ volatile\("div %0,%1,%2".*?;','index=delta/912u;',b)
a=s.index('uint32_t opencfw_em9305_short_header_decode_32dedc');decoder=s[a:s.index('uint32_t opencfw_em9305_radio_prepare_state_32d694',a)]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned scenario,n;static char trace[64];static uintptr_t source=0x840000,input=0x850000;static unsigned status,gate_expected;
static void mark(char c){trace[n++]=c;}
static uint32_t pending_callback(uint32_t id){assert(id==3&&*(uint8_t *)(source+628)==0);mark('I');return 0;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t p,uint32_t reason){assert(p==source);assert(reason==(scenario==10?72:110));mark('T');return 0;}
uint32_t opencfw_em9305_receive_packet_release_3253bc(uintptr_t p){assert(p==input);mark('L');return 0x71;}
uint32_t opencfw_em9305_auxiliary_signal_304394(void){mark('S');return 0;}
uint32_t opencfw_em9305_receive_state_324ea4(uintptr_t p){assert(p==source);mark('D');return 0x25;}
uint32_t opencfw_em9305_receive_gate_324f68(uintptr_t p){assert(p==source);mark('G');return scenario==15?6:0;}
uint32_t opencfw_em9305_receive_check_319838(uintptr_t p,uint32_t value,uint32_t size){assert(p==source&&value==77&&size==88);mark('C');return scenario==12||scenario==15?2:0;}
uint32_t opencfw_em9305_receive_command_31b7c8(uintptr_t p){assert(p==source);mark('O');return scenario==13?1:0;}
uint32_t opencfw_em9305_radio_prepare_32780c(uintptr_t p,uint32_t st,uint32_t gate){assert(p==source&&st==status&&gate==gate_expected);mark('P');return scenario==14?0:11;}
uint32_t opencfw_em9305_auxiliary_start_303f50(uintptr_t ignored){assert(ignored==11);mark('A');return scenario==16?1:0;}
uint32_t opencfw_em9305_receive_finish_324fb0(uintptr_t p){assert(p==source);mark('F');
if(scenario==17){*(uint8_t *)(source+344)=2;}return 0;}
uint32_t opencfw_em9305_receive_packet_finish_3253c4(uintptr_t p,uintptr_t packet,uint32_t data,uint32_t success){assert(p==source&&packet==input&&data==(status==4?0:0x25));assert(success==(scenario==12||scenario==13||scenario==14||scenario==15||scenario==16?0:1));mark('N');return 0x72;}
'''+decoder+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(scenario=0;scenario<18;scenario++){memset((void *)0x800000,0,0x100000);n=0;memset(trace,0,sizeof(trace));*(uint32_t *)(0x830000+36)=source;*(uint32_t *)(0x830000+8)=77;*(uint16_t *)(source+592)=88;*(uint8_t *)(source+620)=1;*(uint8_t *)(source+635)=19;*(uint8_t *)(source+4)=8;*(uint8_t *)(source+630)=1;*(uint8_t *)input=3;*(uint8_t *)(input+2)=5;*(uint16_t *)0x802a3c=65535;status=scenario==0?2:scenario==1?1:scenario==2?3:scenario==3||scenario==4||scenario==5?4:scenario==10||scenario==11?6:0;gate_expected=1;
if(scenario==3)*(uint8_t *)0x802a34=1;
if(scenario==4)*(uint8_t *)0x802a34=255;
if(scenario==6||scenario==7||scenario==8){*(uint8_t *)(source+1)=3;*(uint8_t *)(source+629)=scenario==6?1:0;
if(scenario==7)*(uint8_t *)(source+620)=0;}
if(scenario==9){*(uint8_t *)(source+628)=1;*(uint8_t *)(source+635)=1;*(uint32_t *)0x801314=(uint32_t)(uintptr_t)pending_callback;*(uint32_t *)0x805c70=source-912*3;}
if(scenario==11)*(uint8_t *)(source+337)=1;
if(scenario>=12&&scenario<=17)*(uint8_t *)(input+1)=1;
if(scenario==15)*(uint8_t *)(source+4)=0;
unsigned result=opencfw_em9305_radio_cb_31e620(0x830000,input,status);const char *expected=scenario==0?"L":scenario==1||scenario==2||scenario==3||scenario==6||scenario==7||scenario==8?"SL":scenario==4||scenario==5?"PAFN":scenario==9?"ITDGCPAFN":scenario==10?"TSL":scenario==11?"DGCPAFN":scenario==12||scenario==15?"DGCSOFN":scenario==13?"DGCOSFN":scenario==14?"DGCOPSFN":scenario==16?"DGCOPAFN":"DGCOPAFN";if(strcmp(trace,expected)!=0){fprintf(stderr,"scenario=%u trace=%s expected=%s\n",scenario,trace,expected);}assert(strcmp(trace,expected)==0);assert(result==(strchr(expected,'L')?0x71:0x72));assert(*(uint8_t *)(source+269)==status);if(strchr(expected,'N')){assert(*(uint16_t *)0x802a3c==65535);if(status!=4)assert(*(uint8_t *)(source+630)==(scenario==17?1:0));}
if(scenario>=12)assert(*(uint16_t *)0x802a44==1);
if(scenario==4){assert(*(uint8_t *)0x802a34==0);}cases++;}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('receive-callback-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('receive-callback-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected C callback and real header decoder; controlled lower/state/prepare/auxiliary providers; DIV normalized. Full status cuts, pending callback, discard gates, partial accounting and callback-mutated header. No native ARC runtime/layout/hardware proof.'},indent=2)+'\n')
