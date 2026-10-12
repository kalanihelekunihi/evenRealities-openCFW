#define _GNU_SOURCE
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
/* Native31dd88..31df6c: full slot initialization, callback providers and
 * optional source timing. Null-source incidental R0 is slot+64; nonnull
 * incidental R0 is the native product-derived word, not a success flag. */
uint32_t opencfw_em9305_radio_transfer_31dd88(uintptr_t slot,uintptr_t input,uintptr_t source)
{
 *(volatile uint16_t *)(slot+262u)=0u;
 *(volatile uint8_t *)(slot+270u)=0u;
 (void)opencfw_em9305_memset((void *)(slot+16u),0u,176u);
 uint32_t timeout=*(volatile uint16_t *)(input+36u);
 uint32_t high=*(volatile uint32_t *)(input+28u);
 uint32_t low=*(volatile uint32_t *)(input+24u),scaled_timeout;
 scaled_timeout=timeout*10u;
 uint32_t flags=*(volatile uint8_t *)(input+42u);
 uint32_t period=*(volatile uint16_t *)(input+32u);
 uint32_t limit=*(volatile uint16_t *)(input+34u);
 *(volatile uint16_t *)(slot+382u)=(uint16_t)scaled_timeout;
 *(volatile uint32_t *)(slot+492u)=30000u;
 *(volatile uint32_t *)(slot+280u)=high;
 *(volatile uint32_t *)(slot+276u)=low;
 *(volatile uint8_t *)(slot+271u)=(uint8_t)flags;
 *(volatile uint16_t *)(slot+266u)=(uint16_t)period;
 *(volatile uint16_t *)(slot+260u)=(uint16_t)limit;
 uint32_t adjusted=opencfw_em9305_ll_slot_adjust_317c10(slot,30000u);
 high=*(volatile uint32_t *)(input+20u);
 low=*(volatile uint32_t *)(input+16u);
 *(volatile uint32_t *)(slot+472u)=adjusted;
 *(volatile uint8_t *)(slot+635u)=255u;
 *(volatile uint32_t *)(slot+324u)=high;
 *(volatile uint32_t *)(slot+328u)=low;
 (void)opencfw_em9305_radio_channels_317ac0(slot);
 *(volatile uint16_t *)(slot+76u)=257u;
 uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 low=*(volatile uint32_t *)(input+16u);
 high=*(volatile uint32_t *)(input+20u);
 *(volatile uint8_t *)(slot+64u)=4u;
 uint32_t config_flags=*(volatile uint8_t *)(configuration+40u);
 *(volatile uint32_t *)(slot+72u)=high;
 *(volatile uint16_t *)(slot+322u)=(uint16_t)((low>>16)^low);
 *(volatile uint8_t *)(slot+78u)=2u;
 *(volatile uint32_t *)(slot+68u)=low;
 *(volatile uint8_t *)(slot+66u)=(uint8_t)config_flags;
 (void)opencfw_em9305_radio_phy_tables_31b6cc(slot);
 *(volatile uint8_t *)(slot+336u)=255u;
 *(volatile uint8_t *)(slot+110u)=1u;
 uint32_t first=opencfw_em9305_radio_limit_317b10(slot,slot+574u);
 *(volatile uint16_t *)(slot+592u)=(uint16_t)first;
 uint32_t second=opencfw_em9305_radio_limit_317b10(slot,slot+566u);
 period=*(volatile uint16_t *)(slot+266u);
 uint32_t captured=*(volatile uint16_t *)(slot+592u);
 uint32_t upper=*(volatile uint32_t *)(uintptr_t)0x805cb4u;
 uint32_t lower=*(volatile uint32_t *)(uintptr_t)0x805cb8u,scaled;
 scaled=period*1250u;
 *(volatile uint16_t *)(slot+590u)=(uint16_t)second;
 *(volatile uint8_t *)(slot+42u)=1u;
 *(volatile uint32_t *)(slot+48u)=(uint32_t)(uintptr_t)opencfw_em9305_radio_cb_31dc68;
 *(volatile uint32_t *)(slot+44u)=(uint32_t)(uintptr_t)opencfw_em9305_radio_cb_31dfd0;
 *(volatile uint32_t *)(slot+176u)=(uint32_t)(uintptr_t)opencfw_em9305_radio_cb_31e620;
 *(volatile uint32_t *)(slot+172u)=(uint32_t)(uintptr_t)opencfw_em9305_radio_cb_31e7c8;
 *(volatile uint32_t *)(slot+168u)=(uint32_t)(uintptr_t)opencfw_em9305_radio_cb_31df6c;
 *(volatile uint32_t *)(slot+164u)=(uint32_t)(uintptr_t)opencfw_em9305_radio_cb_31dca0;
 *(volatile uint16_t *)(slot+40u)=1u;
 *(volatile uint32_t *)(slot+52u)=(uint32_t)slot;
 *(volatile uint32_t *)(slot+60u)=(uint32_t)(slot+64u);
 *(volatile uint32_t *)(slot+28u)=captured;
 *(volatile uint32_t *)(slot+180u)=upper;
 *(volatile uint32_t *)(slot+184u)=lower;
 *(volatile uint32_t *)(slot+32u)=scaled;
 *(volatile uint32_t *)(slot+36u)=scaled;
 if(source==0u) return (uint32_t)(slot+64u);
 uint32_t mode=*(volatile uint8_t *)(slot+78u);
 uint32_t phy=*(volatile uint8_t *)(slot+76u);
 uint32_t source_time=*(volatile uint32_t *)(source+388u);
 if(mode==0u) mode=2u;
 uint32_t duration=opencfw_em9305_radio_duration_piece_312b88(phy,mode,36u);
 uint32_t second_phy=*(volatile uint8_t *)(slot+77u);
 duration+=source_time;
 uint32_t second_duration=opencfw_em9305_radio_duration_piece_312b88(second_phy,2u,16u);
 second_phy=*(volatile uint8_t *)(slot+77u);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 period=*(volatile uint16_t *)(slot+266u);
 uint32_t delta=(uint32_t)slot-(uint32_t)base,index;
 index=delta/912u;
 uint32_t total=second_duration+duration+(second_phy==3u?3750u:2500u);
 scaled=period*1250u;
 uint32_t elapsed=opencfw_em9305_radio_schedule_313424(scaled,(uint8_t)index,total+150u,0u,0u);
 struct opencfw_em9305_native_product_pair product=opencfw_em9305_native_mpydu_329154(elapsed,0x1a36e3u);
 uint32_t result=(product.high<<1)|(product.low>>31);
 *(volatile uint8_t *)(source+1100u)=(uint8_t)(product.high>>7);
 *(volatile uint8_t *)(source+1099u)=(uint8_t)result;
 *(volatile uint32_t *)(slot+24u)=total+elapsed+150u;
 return result;
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned present=0;present<2;present++)for(alternate=0;alternate<2;alternate++){memset((void *)0x800000,0xa5,0x100000);uintptr_t slot=0x880000,input=0x850000,source=present?0x860000:0;calls=0;*(uint32_t *)0x805cac=0x840000;*(uint8_t *)(0x840000+40)=9;*(uint32_t *)0x805cb4=0x123;*(uint32_t *)0x805cb8=0x456;*(uint32_t *)0x805c70=slot-912*3;
*(uint16_t *)(input+32)=3;*(uint16_t *)(input+34)=5;*(uint16_t *)(input+36)=9;*(uint32_t *)(input+16)=0x10203040;*(uint32_t *)(input+20)=0x22334455;*(uint32_t *)(input+24)=0x11223344;*(uint32_t *)(input+28)=0x55667788;*(uint8_t *)(input+42)=7;if(source)*(uint32_t *)(source+388)=20;
expected_total=352+20+(alternate?1616:192)+(alternate?3750:2500);uint64_t product=0x12345678ULL*0x1a36e3;uint32_t result=((uint32_t)(product>>32)<<1)|((uint32_t)product>>31);assert(opencfw_em9305_radio_transfer_31dd88(slot,input,source)==(source?result:slot+64));assert(calls==(source?7:6));assert(*(uint32_t *)(slot+32)==3750&&*(uint32_t *)(slot+36)==3750&&*(uint32_t *)(slot+28)==0x2345);assert(*(uint16_t *)(slot+590)==0x6789&&*(uint16_t *)(slot+592)==0x2345);assert(*(uint32_t *)(slot+180)==0x123&&*(uint32_t *)(slot+184)==0x456&&*(uint8_t *)(slot+42)==1&&*(uint16_t *)(slot+40)==1&&*(uint8_t *)(slot+336)==255&&*(uint8_t *)(slot+110)==1);assert(*(uint32_t *)(slot+48)==(uint32_t)(uintptr_t)opencfw_em9305_radio_cb_31dc68&&*(uint32_t *)(slot+52)==slot&&*(uint32_t *)(slot+60)==slot+64);assert(*(uint16_t *)(slot+382)==90&&*(uint32_t *)(slot+492)==30000&&*(uint32_t *)(slot+280)==0x55667788&&*(uint32_t *)(slot+276)==0x11223344&&*(uint8_t *)(slot+271)==7);if(source){assert(*(uint32_t *)(slot+24)==expected_total+0x12345678+150);assert(*(uint8_t *)(source+1099)==(uint8_t)result&&*(uint8_t *)(source+1100)==(uint8_t)(product>>39));}cases++;}printf("PASS %u\n",cases);}
