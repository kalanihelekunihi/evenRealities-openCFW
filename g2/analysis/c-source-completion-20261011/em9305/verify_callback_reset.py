from pathlib import Path
import subprocess,re,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native31dca0'):s.index('/* Native3253a4')];b=re.sub(r'__asm__ volatile\("div %0,%1,%2".*?;','index=delta/912u;',b)
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned scenario,calls;static char trace[16];static uint32_t expected_span;
static void mark(char c){trace[calls++]=c;}
uint32_t opencfw_em9305_auxiliary_signal_304394(void){mark('S');return 77;}
uint32_t opencfw_em9305_radio_prepare_32780c(uintptr_t p,uint32_t a,uint32_t c){assert(p==0x860000&&a==0&&c==1);assert(*(uint8_t *)0x802a38==0&&*(uint8_t *)0x802a34==0&&*(uint16_t *)0x802a3c==0&&*(uint16_t *)0x802a40==0&&*(uint16_t *)0x802a44==0);assert(*(uint8_t *)(p+349)==0&&*(uint8_t *)(p+347)==0&&*(uint8_t *)(p+344)==1);*(uint16_t *)(p+566)=65534;mark('P');return 44;}
uint32_t opencfw_em9305_auxiliary_start_303f50(uintptr_t p){assert(p==44);mark('A');return scenario==5?88:0;}
uint32_t opencfw_em9305_radio_query_3253a4(uint32_t p){assert(p==65534);mark('Q');return scenario==6?0:99;}
uint32_t opencfw_em9305_radio_request_start_303cd8(uint32_t a,uint32_t b){assert(a==99&&b==expected_span);mark('R');return 66;}
static uint32_t slot_callback(uint32_t id){assert(id==3);mark('I');return 0;}
static uint32_t payload_callback(uint32_t lo,uint32_t hi){if(scenario==7)assert(lo==55&&hi==0);else assert(lo==0x12345678&&hi==0xabcdef01);*(uint16_t *)(0x860000+566)=65535;mark('T');return 0;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(scenario=0;scenario<11;scenario++){memset((void *)0x800000,0,0x100000);calls=0;memset(trace,0,16);uintptr_t source=0x860000,event=0x880000;*(uint32_t *)(event+36)=source;*(uint8_t *)0x802a38=9;*(uint8_t *)(source+1)=scenario<=3?3:2;*(uint8_t *)(source+620)=scenario==0?0:1;*(uint32_t *)(source+360)=scenario==2?0:1;*(uint8_t *)(source+629)=scenario==1;*(uint8_t *)(source+630)=scenario==1;*(uint16_t *)(source+566)=123;
if(scenario==10){*(uint32_t *)0x805cd8=0x830000;*(uint32_t *)(0x830000+24)=(uint32_t)(uintptr_t)slot_callback;*(uint32_t *)0x805c70=source-912*3;}
if(scenario>=7&&scenario<=9){*(uint32_t *)0x8052cc=(uint32_t)(uintptr_t)payload_callback;*(uint8_t *)(source+109)=1;*(uint8_t *)(source+111)=scenario==7?1:scenario==8?0:2;*(uint16_t *)(source+262)=55;*(uint32_t *)(source+464)=0x12345678;*(uint32_t *)(source+468)=0xabcdef01;}
expected_span=scenario==7||scenario==8?5:4;unsigned result=opencfw_em9305_radio_cb_31dca0(event);if(scenario<3){assert(result==77&&strcmp(trace,"S")==0&&*(uint8_t *)0x802a38==9);}else if(scenario==5)assert(result==88&&strcmp(trace,"PA")==0);else if(scenario==6)assert(result==77&&strcmp(trace,"PAQS")==0);else{assert(result==66);assert(strcmp(trace,scenario==10?"IPAQR":scenario==7||scenario==8?"PAQTR":"PAQR")==0);}cases++;}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('callback-reset-host.c');p.write_text(h);output=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);assert output.strip()=='PASS 11';print(output.strip())
p.with_name('callback-reset-host-receipt.json').write_text(json.dumps({'cases_passed':11,'scope':'Host fixed-RAM effects/order, controlled children and real fixture function pointers, optional index/payload callback and fresh pending after mutation. DIV normalized for positive delta; native child/ISA/runtime/hardware unqualified.'},indent=2)+'\n')
