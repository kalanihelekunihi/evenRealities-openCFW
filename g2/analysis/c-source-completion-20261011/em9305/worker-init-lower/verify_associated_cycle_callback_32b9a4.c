#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_associated_cycle_callback_32b9a4(uintptr_t);
static uintptr_t const record=0x810000u,packet=0x812000u,choices=0x813000u,dest=0x814000u,choices2=0x815000u;
static uint32_t close_calls,open_calls,pending_calls,insert_calls,report_calls,mask_calls,event_calls;
static uint32_t retry_once,return_mask,first_mask,crc_mutates_index,mask_mutates_choices;
uint32_t opencfw_em9305_init_callback_child_3246dc(uintptr_t p){assert(p==packet&&*(uint16_t *)(packet+224u)==0u);++close_calls;return 0u;}
uint32_t opencfw_em9305_init_callback_child_3246c0(uintptr_t p){assert(p==packet);++open_calls;return 0u;}
uint32_t opencfw_em9305_associated_cleanup_3266d0(uintptr_t r,uint32_t n){assert(r==record&&n==3u);return 77u;}
uint32_t opencfw_em9305_associated_report_30e89c(uint32_t id,uint32_t count,uint32_t zero,uint32_t interval,uint32_t stamp){assert(id==9u&&count==0u&&zero==0u&&interval==20u&&stamp==100u);++report_calls;return 0u;}
uint32_t opencfw_em9305_associated_channel_pending_327af4(uintptr_t r){assert(r==record);++pending_calls;return 0u;}
uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t p,uint32_t seed){assert(p==record+720u);(void)seed;return 4u;}
uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t p,uintptr_t tie){assert(p==record+380u&&tie==0u);if(retry_once&&insert_calls++==0u){*(uint32_t *)(record+700u)=50u;return 0u;}return 1u;}
uint32_t opencfw_em9305_pal_random_step(void){return 3u;}
uint32_t opencfw_em9305_crc_update_304678(uint32_t seed,uint32_t n,uintptr_t p){assert(seed==3u&&n==0u&&p==0u);if(crc_mutates_index)*(uint8_t *)(record+799u)=1u;return 0x211u;}
uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t low,uint32_t high){assert(low==0x1234u&&high==0x5678u);++mask_calls;if(mask_mutates_choices)*(uint32_t *)(record+1160u)=(uint32_t)choices2;return first_mask;}
uint32_t opencfw_em9305_associated_cycle_event_30e858(uint32_t id,uint32_t zero,uint32_t count){assert(id==9u&&zero==0u&&count==2u);++event_calls;return 55u;}
static void reset_case(void){
 memset((void *)record,0,4096u);memset((void *)packet,0,4096u);memset((void *)choices,0xff,4096u);memset((void *)dest,0,4096u);memset((void *)choices2,0xff,4096u);
 *(uint32_t *)(record+380u+44u)=(uint32_t)packet;
 *(uint32_t *)(record+380u+36u)=(uint32_t)record;
 *(uint32_t *)(record+1160u)=(uint32_t)choices;
 *(uint32_t *)(record+2812u)=(uint32_t)dest;
 *(uint32_t *)(record+700u)=20u;*(uint32_t *)(record+792u)=2u;
 *(uint32_t *)(record+380u+8u)=100u;
 *(uint8_t *)(record+788u)=2u;*(uint8_t *)(record+1u)=9u;
 *(uint32_t *)(choices+0xf04u)=0x1234u;*(uint32_t *)(choices+0xf08u)=0x5678u;
 *(uint8_t *)(packet+15u)=4u;*(uint8_t *)(dest+76u)=7u;
 *(uint8_t *)(uintptr_t)0x805beeu=1u;
 close_calls=open_calls=pending_calls=insert_calls=report_calls=mask_calls=event_calls=0u;
 retry_once=return_mask=crc_mutates_index=mask_mutates_choices=0u;first_mask=3u;
}
int main(void){
 uintptr_t addresses[]={record,packet,choices,dest,choices2,0x805000u};
 for(unsigned i=0;i<6;i++)assert(mmap((void *)addresses[i],4096u,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)addresses[i]);
 reset_case();*(uint8_t *)(record+698u)=1u;
 assert(opencfw_em9305_associated_cycle_callback_32b9a4(record+380u)==77u);
 assert(close_calls==1u&&open_calls==0u);
 reset_case();*(uint8_t *)(choices+0xf0cu+1u)=1u;*(uint8_t *)(choices+256u)=7u;
 assert(opencfw_em9305_associated_cycle_callback_32b9a4(record+380u)==7u);
 assert(close_calls==1u&&open_calls==1u&&report_calls==1u&&pending_calls==1u&&*(uint32_t *)(record+380u+8u)==102u);
 reset_case();retry_once=1u;*(uint8_t *)(choices+0xf0cu)=6u;*(uint8_t *)(choices+1536u)=8u;
 assert(opencfw_em9305_associated_cycle_callback_32b9a4(record+380u)==6u);
 assert(insert_calls==2u&&open_calls==1u&&report_calls==1u&&pending_calls==2u);
 assert(*(uint32_t *)(record+380u+8u)==120u&&*(uint8_t *)(record+799u)==0u);
 reset_case();*(uint8_t *)(record+799u)=1u;*(uint8_t *)(choices+0xf0cu)=255u;first_mask=2u;
 assert(opencfw_em9305_associated_cycle_callback_32b9a4(record+380u)==55u);
 assert(event_calls==1u&&mask_calls==1u&&*(uint8_t *)(dest+79u)==2u);
 reset_case();*(uint8_t *)(record+799u)=1u;crc_mutates_index=1u;
 assert(opencfw_em9305_associated_cycle_callback_32b9a4(record+380u)==0x211u);
 assert(event_calls==0u&&mask_calls==0u&&*(uint8_t *)(record+799u)==1u);
 reset_case();*(uint8_t *)(record+799u)=1u;first_mask=2u;mask_mutates_choices=1u;
 *(uint8_t *)(choices+0xf0cu)=6u;*(uint8_t *)(choices+1536u)=8u;
 *(uint8_t *)(choices2+0xf0cu)=12u;*(uint8_t *)(choices2+0xf0du)=255u;
 assert(opencfw_em9305_associated_cycle_callback_32b9a4(record+380u)==12u);
 assert(mask_calls==1u&&event_calls==0u);
 return 0;
}
