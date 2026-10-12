#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
static uint8_t record[4096] __attribute__((aligned(4))),expected[4096];static unsigned found,enters,exits,lookups;static uint32_t lastid;
static uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){lastid=id;lookups++;return found?(uintptr_t)record:0;}
static uint32_t opencfw_em9305_wsf_critical_enter(void){enters++;return 0;}
static uint32_t opencfw_em9305_wsf_critical_exit(void){exits++;return 0;}
/* Native30cf28 tail308780..30879c: saved record, critical store word72. */
uint32_t opencfw_em9305_command_vendor_mask_30cf28(uint32_t id,uint32_t mask)
{uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);if(record==0u)return 66u;(void)opencfw_em9305_wsf_critical_enter();*(volatile uint32_t *)(record+72u)=mask;(void)opencfw_em9305_wsf_critical_exit();return 0u;}
/* Native30d5a8 tail308c44..308c6c: exact byte wrapping validation. */
uint32_t opencfw_em9305_command_vendor_mode_30d5a8(uint32_t id,uint32_t mode)
{uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);if(record==0u)return 66u;if((uint8_t)(mode+4u)<5u)return 18u;(void)opencfw_em9305_wsf_critical_enter();*(volatile uint8_t *)(record+76u)=(uint8_t)mode;(void)opencfw_em9305_wsf_critical_exit();return 0u;}
/* Native30d75c..30d772 tail308f28..308f50: low-byte OR validation, ordered stores. */
uint32_t opencfw_em9305_command_vendor_option_30d75c(uint32_t id,uint32_t first,uint32_t second)
{if((uint8_t)((first-1u)|(second-1u))>1u)return 18u;uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);if(record==0u)return 66u;(void)opencfw_em9305_wsf_critical_enter();*(volatile uint8_t *)(record+2531u)=(uint8_t)second;*(volatile uint8_t *)(record+2327u)=(uint8_t)first;(void)opencfw_em9305_wsf_critical_exit();return 0u;}
static void reset(void){memset(record,0xa5,sizeof record);memcpy(expected,record,sizeof record);enters=exits=lookups=0;lastid=0;}
int main(void){uint64_t count=0;uint32_t ids[]={0,7,255,256,65535,0xffffffff};for(unsigned i=0;i<6;i++)for(found=0;found<2;found++)for(unsigned a=0;a<256;a++)for(unsigned b=0;b<256;b++){
reset();uint32_t mask=(a<<24)|(b<<16)|0xabcd;uint32_t r=opencfw_em9305_command_vendor_mask_30cf28(ids[i],mask);if(found)memcpy(expected+72,&mask,4);if(r!=(found?0:66)||enters!=found||exits!=found||lookups!=1||lastid!=ids[i]||memcmp(record,expected,4096))abort();count++;
reset();unsigned valid=(uint8_t)(a+4)>=5;r=opencfw_em9305_command_vendor_mode_30d5a8(ids[i],a);if(found&&valid)expected[76]=a;if(r!=(!found?66:valid?0:18)||enters!=(found&&valid)||exits!=enters||lookups!=1||memcmp(record,expected,4096))abort();count++;
reset();valid=(uint8_t)((a-1u)|(b-1u))<=1;r=opencfw_em9305_command_vendor_option_30d75c(ids[i],a,b);if(found&&valid){expected[2531]=b;expected[2327]=a;}if(r!=(!valid?18:!found?66:0)||enters!=(found&&valid)||exits!=enters||lookups!=valid||memcmp(record,expected,4096))abort();count++;
}printf("PASS %llu\n",(unsigned long long)count);return 0;}
