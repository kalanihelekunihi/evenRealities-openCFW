from pathlib import Path
import subprocess,re,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native31dd88'):s.index('/* Native317ac0')]
b=re.sub(r'__asm__ volatile\("(mpyuw|div) %0,%1,%2":"=r"\((\w+)\):"r"\((\w+)\),"r"\((\d+)u\)\);',lambda m:m[2]+'='+m[3]+('/' if m[1]=='div' else '*')+m[4]+'u;',b)
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls,alternate;static uint32_t expected_total;
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){assert(p==(void *)(0x880000+16)&&v==0&&n==176);assert(*(uint16_t *)(0x880000+262)==0&&*(uint8_t *)(0x880000+270)==0);calls++;return memset(p,v,n);}
uint32_t opencfw_em9305_ll_slot_adjust_317c10(uintptr_t p,uint32_t n){assert(p==0x880000&&n==30000);assert(*(uint16_t *)(p+266)==3&&*(uint16_t *)(p+260)==5);calls++;return 1111;}
uint32_t opencfw_em9305_radio_channels_317ac0(uintptr_t p){assert(p==0x880000&&*(uint32_t *)(p+472)==1111&&*(uint32_t *)(p+324)==0x22334455&&*(uint32_t *)(p+328)==0x10203040);calls++;return 0;}
uint32_t opencfw_em9305_radio_phy_tables_31b6cc(uintptr_t p){assert(p==0x880000&&*(uint16_t *)(p+76)==257&&*(uint8_t *)(p+66)==9);if(alternate)*(uint8_t *)(p+77)=3;calls++;return 0;}
uint32_t opencfw_em9305_radio_limit_317b10(uintptr_t p,uintptr_t q){assert(p==0x880000&&(q==p+574||q==p+566));calls++;return q==p+574?0x12345:0x6789;}
uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy,uint32_t mode,uint32_t size){return phy==2?36+4*size:phy==3?(27+8*size)*(mode==1?2:8)+376:8*size+64;}
uint32_t opencfw_em9305_radio_schedule_313424(uint32_t period,uint32_t id,uint32_t total,uint32_t a,uint32_t c){assert(period==3750&&id==3&&total==expected_total+150&&a==0&&c==0);calls++;return 0x12345678;}
struct opencfw_em9305_native_product_pair{uint32_t low,high;};
static struct opencfw_em9305_native_product_pair opencfw_em9305_native_mpydu_329154(uint32_t a,uint32_t b){uint64_t v=(uint64_t)a*b;return (struct opencfw_em9305_native_product_pair){(uint32_t)v,(uint32_t)(v>>32)};}
void opencfw_em9305_radio_cb_31dc68(void){}void opencfw_em9305_radio_cb_31dfd0(void){}void opencfw_em9305_radio_cb_31e620(void){}void opencfw_em9305_radio_cb_31e7c8(void){}void opencfw_em9305_radio_cb_31df6c(void){}void opencfw_em9305_radio_cb_31dca0(void){}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned present=0;present<2;present++)for(alternate=0;alternate<2;alternate++){memset((void *)0x800000,0xa5,0x100000);uintptr_t slot=0x880000,input=0x850000,source=present?0x860000:0;calls=0;*(uint32_t *)0x805cac=0x840000;*(uint8_t *)(0x840000+40)=9;*(uint32_t *)0x805cb4=0x123;*(uint32_t *)0x805cb8=0x456;*(uint32_t *)0x805c70=slot-912*3;
*(uint16_t *)(input+32)=3;*(uint16_t *)(input+34)=5;*(uint16_t *)(input+36)=9;*(uint32_t *)(input+16)=0x10203040;*(uint32_t *)(input+20)=0x22334455;*(uint32_t *)(input+24)=0x11223344;*(uint32_t *)(input+28)=0x55667788;*(uint8_t *)(input+42)=7;if(source)*(uint32_t *)(source+388)=20;
expected_total=352+20+(alternate?1616:192)+(alternate?3750:2500);uint64_t product=0x12345678ULL*0x1a36e3;uint32_t result=((uint32_t)(product>>32)<<1)|((uint32_t)product>>31);assert(opencfw_em9305_radio_transfer_31dd88(slot,input,source)==(source?result:slot+64));assert(calls==(source?7:6));assert(*(uint32_t *)(slot+32)==3750&&*(uint32_t *)(slot+36)==3750&&*(uint32_t *)(slot+28)==0x2345);assert(*(uint16_t *)(slot+590)==0x6789&&*(uint16_t *)(slot+592)==0x2345);assert(*(uint32_t *)(slot+180)==0x123&&*(uint32_t *)(slot+184)==0x456&&*(uint8_t *)(slot+42)==1&&*(uint16_t *)(slot+40)==1&&*(uint8_t *)(slot+336)==255&&*(uint8_t *)(slot+110)==1);assert(*(uint32_t *)(slot+48)==(uint32_t)(uintptr_t)opencfw_em9305_radio_cb_31dc68&&*(uint32_t *)(slot+52)==slot&&*(uint32_t *)(slot+60)==slot+64);assert(*(uint16_t *)(slot+382)==90&&*(uint32_t *)(slot+492)==30000&&*(uint32_t *)(slot+280)==0x55667788&&*(uint32_t *)(slot+276)==0x11223344&&*(uint8_t *)(slot+271)==7);if(source){assert(*(uint32_t *)(slot+24)==expected_total+0x12345678+150);assert(*(uint8_t *)(source+1099)==(uint8_t)result&&*(uint8_t *)(source+1100)==(uint8_t)(product>>39));}cases++;}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('transfer-host.c');p.write_text(h);output=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);assert output.strip()=='PASS 4';print(output.strip())
p.with_name('transfer-host-receipt.json').write_text(json.dumps({'cases_passed':4,'scope':'Host fixed RAM effects/null-source and PHY3 mutation/scheduler arguments. Native MPYUW/DIV/MPYDU normalized, helper/callback children controlled. No full child/runtime/ISA/hardware proof.'},indent=2)+'\n')
