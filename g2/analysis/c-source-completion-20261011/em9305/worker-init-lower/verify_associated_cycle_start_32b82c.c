#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_associated_cycle_start_32b82c(uintptr_t,uintptr_t);
static uintptr_t const record=0x810000u,packet=0x812000u,choices=0x813000u,dest=0x814000u;
static uint32_t mask_first,mask_second,mask_calls,event_count,insert_calls,retry_once,crc_calls;
uint32_t opencfw_em9305_pal_current_time(void){return 100u;}
uint32_t opencfw_em9305_radio_schedule_313424(uint32_t scaled,uint32_t row,uint32_t now,uint32_t a,uint32_t b){assert(scaled==6u&&row==4u&&now==100u&&a==0u&&b==0u);return 20u;}
uint32_t opencfw_em9305_pal_random_step(void){assert(*(volatile uint32_t *)(record+800u)==120u);return 5u;}
uint32_t opencfw_em9305_crc_update_304678(uint32_t seed,uint32_t count,uintptr_t data){assert(seed==5u&&count==0u&&data==0u);return crc_calls++==0u?0x123u:0x456u;}
uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t low,uint32_t high){assert(low==0x1234u&&high==0x5678u);return mask_calls++==0u?mask_first:mask_second;}
uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t object,uintptr_t tie){assert(object==record+380u&&tie==0u);if(retry_once){if(insert_calls++==0u){assert(*(volatile uint32_t *)(object+8u)==120u);return 0u;}assert(*(volatile uint32_t *)(object+8u)==144u&&*(volatile uint32_t *)(object+12u)==24u);}return 1u;}
uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t p,uint32_t seed){assert(retry_once&&p==record+720u&&seed==5u);return 4u;}
uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t choice){assert(retry_once&&choice==5u&&*(volatile uint8_t *)(record+697u)==4u);return 2u;}
uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t a,uint32_t b){assert(retry_once&&a==48u&&b==2u);return 24u;}
uint32_t opencfw_em9305_associated_cycle_event_30e858(uint32_t id,uint32_t old,uint32_t count){assert(id==9u&&old==0u&&count==(mask_first>=3u?3u:mask_second));assert(*(volatile uint8_t *)(dest+79u)==count);++event_count;return 0u;}
static void reset_case(void){
 memset((void *)record,0,4096u);memset((void *)packet,0,4096u);memset((void *)choices,0,4096u);memset((void *)dest,0,4096u);
 *(uint32_t *)(record+380u+44u)=(uint32_t)packet;
 *(uint32_t *)(record+2812u)=(uint32_t)dest;
 *(uint32_t *)(record+1160u)=(uint32_t)choices;
 *(uint32_t *)(record+792u)=6u;*(uint32_t *)(record+700u)=8u;
 *(uint8_t *)(record+1u)=9u;*(uint8_t *)(record+788u)=3u;
 *(uint8_t *)(choices+0xf0cu)=2u;*(uint8_t *)(choices+512u)=9u;
 *(uint32_t *)(choices+0xf08u)=0x5678u;*(uint32_t *)(choices+0xf04u)=0x1234u;
 *(uint32_t *)(uintptr_t)0x805c38u=(uint32_t)record;
 mask_calls=event_count=insert_calls=crc_calls=0u;retry_once=0u;
}
int main(void){
 uintptr_t addresses[]={record,packet,choices,dest,0x805000u};
 for(unsigned i=0;i<5;i++)assert(mmap((void *)addresses[i],4096u,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)addresses[i]);
 reset_case();mask_first=4u;mask_second=2u;
 assert(opencfw_em9305_associated_cycle_start_32b82c(record,record+380u)==9u);
 assert(mask_calls==1u&&event_count==1u&&*(uint8_t *)(dest+79u)==3u);
 reset_case();mask_first=1u;mask_second=2u;
 assert(opencfw_em9305_associated_cycle_start_32b82c(record,record+380u)==9u);
 assert(mask_calls==2u&&event_count==1u&&*(uint8_t *)(dest+79u)==2u);
 reset_case();mask_first=4u;mask_second=2u;retry_once=1u;
 *(uint8_t *)(record+799u)=2u;*(uint16_t *)(record+376u)=5u;
 *(uint8_t *)(choices+0xf0cu)=2u;
 assert(opencfw_em9305_associated_cycle_start_32b82c(record,record+380u)==9u);
 assert(insert_calls==2u&&*(uint8_t *)(record+799u)==0u&&*(uint16_t *)(record+376u)==6u);
 reset_case();mask_first=4u;mask_second=2u;*(uint8_t *)(choices+512u)=0u;
 assert(opencfw_em9305_associated_cycle_start_32b82c(record,record+380u)==0x456u);
 assert(crc_calls==2u&&*(uint16_t *)(record+1144u)==0u&&*(uint16_t *)(record+706u)==0x456u);
 return 0;
}
