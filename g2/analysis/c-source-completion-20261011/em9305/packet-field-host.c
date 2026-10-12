#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t record[64] __attribute__((aligned(4))),expected[64],address[6];static unsigned found,enters,exits,packs;static uint32_t lastid;
static uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){lastid=id;return found?(uintptr_t)record:0;}
static uint64_t opencfw_em9305_controller_pack_address(uintptr_t p){uint8_t*b=(uint8_t*)p;packs++;return (uint64_t)b[0]|(uint64_t)b[1]<<8|(uint64_t)b[2]<<16|(uint64_t)b[3]<<24|(uint64_t)b[4]<<32|(uint64_t)b[5]<<40;}
static uint32_t opencfw_em9305_wsf_critical_enter(void){enters++;return 0;}
static uint32_t opencfw_em9305_wsf_critical_exit(void){exits++;return 0;}
/* Native30cee0 tail308ecc..308f24: captured record, live six-byte address and native high-word mask. */
uint32_t opencfw_em9305_command_field_30cee0(uint32_t id,uintptr_t address)
{uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);if(record==0u)return 66u;uint32_t flags=*(volatile uint8_t *)(record+32u);if((flags&1u)!=0u&&*(volatile uint8_t *)(record+2u)!=0u)return 12u;uint64_t packed=opencfw_em9305_controller_pack_address(address);uint32_t low=(uint32_t)packed,high=(uint32_t)(packed>>32),masked=high&0xc000u;if(masked==0x8000u)return 18u;(void)opencfw_em9305_wsf_critical_enter();*(volatile uint32_t *)(record+12u)=high;*(volatile uint32_t *)(record+8u)=low;*(volatile uint8_t *)(record+4u)=1u;*(volatile uint8_t *)(record+3u)=1u;(void)opencfw_em9305_wsf_critical_exit();return 0u;}
int main(void){uint64_t count=0;for(unsigned high=0;high<65536;high++)for(found=0;found<2;found++)for(unsigned flags=0;flags<2;flags++)for(unsigned busy=0;busy<2;busy++){memset(record,0xa5,64);record[32]=flags;record[2]=busy;memcpy(expected,record,64);uint32_t low=high*0x1020304u+19;memcpy(address,&low,4);address[4]=high;address[5]=high>>8;enters=exits=packs=0;unsigned early=!found||(flags&&busy),success=!early&&(high&0xc000)!=0x8000;unsigned r=opencfw_em9305_command_field_30cee0(0xffffff12,(uintptr_t)address);if(success){uint32_t h=high;memcpy(expected+12,&h,4);memcpy(expected+8,&low,4);expected[3]=expected[4]=1;}if(r!=(!found?66:flags&&busy?12:success?0:18)||lastid!=0xffffff12||packs!=!early||enters!=success||exits!=success||memcmp(record,expected,64))abort();count++;}printf("PASS %llu\n",(unsigned long long)count);return 0;}
