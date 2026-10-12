from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated command apply 309514'):s.index('/* Authenticated receive callback31e620')]
b=b.replace('__asm__ volatile("mpyuw %0,%1,%2":"=r"(offset):"r"(id),"r"(784u));','offset=id*784u;').replace('__asm__ volatile("mpyuw %0,%1,%2":"=r"(budget):"r"(periods),"r"(125u));','budget=periods*125u;').replace('__asm__ volatile("mpyuw %0,%1,%2":"=r"(product):"r"(third),"r"(multiplier));','product=third*multiplier;').replace('__asm__ volatile("mpyd 0,%1,%2\\n\\tmac %0,%3,%4":"=r"(scheduled):"r"(rate),"r"(1250u),"r"(product),"r"(125u));','assert(rate==4&&product==15);scheduled=scheduled_fixture;')
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned scenario,n,copies;static char trace[16];static uint32_t scheduled_fixture;
static void mark(char c){trace[n++]=c;}
static uint32_t timing_callback(void){mark('T');*(uint32_t *)0x804084=0x850000;return 77;}
static uint32_t prepared_callback(uint32_t flags,uintptr_t p,uintptr_t data,uint32_t zero){assert(flags==64&&p==0x840016&&data==0x840058&&zero==0);assert(*(uint32_t *)(0x820000+124)==p);mark('P');*(uint16_t *)(0x840000+98)=13;return 0x12345;}
static uint32_t notify_callback(uintptr_t p,uint32_t duration){assert(p==0x803d78&&duration==100);mark('N');return 0;}
uint32_t opencfw_em9305_radio_duration_312be4(uint32_t phy,uint32_t requested,uint32_t timing,uint32_t spacing,uint32_t size,uint32_t extended,uint32_t mode,uint32_t overhead){assert(phy==2&&requested==0&&timing==(scenario==8?77:0)&&spacing==0&&size==4&&extended==0&&mode==2&&overhead==5);mark('D');return scenario==3?226:100;}
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t bytes){assert(bytes==4);copies++;mark('C');memcpy(d,s,bytes);if(scenario==9&&copies==1)*(uint32_t *)0x804084=0x850000;return d;}
uint32_t opencfw_em9305_pal_current_time(void){mark('K');return 100;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(scenario=0;scenario<10;scenario++){memset((void *)0x800000,0,0x100000);n=0;copies=0;memset(trace,0,sizeof(trace));uintptr_t record=0x840000;*(uint32_t *)0x804084=record;*(uint8_t *)0x804080=2;*(uint16_t *)(record+16)=scenario==0?4:scenario==1?3:2;*(uint8_t *)(record+19)=scenario==2?3:scenario==4||scenario==9?0:2;*(uint16_t *)(record+366)=64;*(uint32_t *)(record+92)=0x830000;*(uint32_t *)(0x803d78+92)=0x820000;*(uint8_t *)0x803f7a=4;*(uint8_t *)(0x803f7a+1)=2;*(uint8_t *)(0x803d78+515)=3;*(uint32_t *)0x810000=0x12345678;*(uint32_t *)0x805c9c=(uint32_t)(uintptr_t)prepared_callback;*(uint32_t *)0x805c94=scenario==7?0:(uint32_t)(uintptr_t)notify_callback;scheduled_fixture=scenario==5?50:150;
if(scenario==8){*(uint8_t *)(0x803f7a+86)=1;*(uint32_t *)0x801a14=(uint32_t)(uintptr_t)timing_callback;}if(scenario==8||scenario==9){*(uint16_t *)(0x850000+366)=64;*(uint16_t *)(0x850000+16)=2;*(uint8_t *)(0x850000+19)=0;}
unsigned result=opencfw_em9305_command_apply_309514(0,2,1,2,5,4,0x810000);if(scenario<=2){assert(result==70&&n==0&&*(uint8_t *)(record+108)==0);}else if(scenario==3){assert(result==69&&strcmp(trace,"D")==0&&copies==0);}else if(scenario==4||scenario==8||scenario==9){assert(result==0&&strcmp(trace,scenario==8?"TDC":"DC")==0);uintptr_t current=scenario>=8?0x850000:record;assert(*(uint8_t *)(current+100)==1&&*(uint8_t *)(current+370)==5&&*(uint32_t *)current==4);assert(*(uint8_t *)(scenario==8?0x850000+108:record+108)==1);if(scenario==9)assert(*(uint8_t *)(0x850000+108)==0);}else{assert(result==(scenario==5?70:0));assert(strcmp(trace,scenario==5||scenario==7?"DCCPK":"DCCPKN")==0);assert(*(uint32_t *)0x830000==0x12345678&&*(uint16_t *)(0x820000+120)==0x2345&&*(uint32_t *)(0x820000+112)==scheduled_fixture&&*(uint32_t *)(0x820000+132)==0x830000&&*(uint16_t *)(0x820000+128)==13);}cases++;}
scenario=4;for(unsigned second=0;second<256;second++){memset((void *)0x800000,0,0x100000);n=0;copies=0;memset(trace,0,sizeof(trace));*(uint32_t *)0x804084=0x840000;*(uint8_t *)0x804080=2;*(uint16_t *)(0x840000+16)=2;*(uint8_t *)(0x840000+19)=(uint8_t)(second+1);*(uint16_t *)(0x840000+366)=64;*(uint8_t *)(0x803f7a+1)=3;*(uint32_t *)0x810000=0x12345678;*(uint32_t *)0x840000=0x81;*(uint32_t *)(0x840000+4)=0x12;assert(opencfw_em9305_command_apply_309514(0,2,256,second,5,4,0x810000)==0);uint32_t shift=second&63;assert(*(uint32_t *)0x840000==(0x81u|(shift<32?1u<<shift:0u)));assert(*(uint32_t *)(0x840000+4)==(0x12u|(shift>=32?1u<<(shift-32):0u)));assert(*(uint8_t *)(uintptr_t)(0x840000+368+second)==5&&strcmp(trace,"DC")==0);cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('command-apply-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('command-apply-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected C fixed-RAM with controlled duration/copy/callback/current-time. MPYUW normalized, MPYD/MAC output fixture controlled. Validation, partial effects, pointer refresh, optional callbacks, pending mask. No native DSP arithmetic/runtime/layout/hardware proof.'},indent=2)+'\n')
