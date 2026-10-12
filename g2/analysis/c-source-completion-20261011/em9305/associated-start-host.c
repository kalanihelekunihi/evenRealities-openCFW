#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_pal_random_step(void);
extern uint32_t opencfw_em9305_crc_update_304678(uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t);
extern uint32_t opencfw_em9305_radio_access_raw_318878(void);
extern uint32_t opencfw_em9305_radio_channel_transform_30e3fc(uintptr_t);
extern uint32_t opencfw_em9305_command_periodic_status_30e878(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_count_30e4bc(void);
extern uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_validate_32b2d4(uintptr_t);
extern uint32_t opencfw_em9305_associated_cleanup_3266d0(uintptr_t,uint32_t);
static uint32_t opencfw_em9305_associated_timing_crc(uintptr_t record)
{
 uint32_t count=*(volatile uint16_t *)(record+2250u);
 uintptr_t input=*(volatile uint32_t *)(record+1424u);
 uint32_t seed=opencfw_em9305_pal_random_step();
 return opencfw_em9305_crc_update_304678(seed,count,input);
}
/* Native324b3c..324c5c complete associated start action. */
uint32_t opencfw_em9305_associated_action_324b3c(uintptr_t record)
{
 (void)opencfw_em9305_common_request_30455c(1u);
 *(volatile uint8_t *)(record+698u)=0u;
 uint32_t access=opencfw_em9305_radio_access_raw_318878();
 *(volatile uint32_t *)(record+372u)=access;
 uint32_t second=*(volatile uint32_t *)(uintptr_t)0x805aa4u;
 uint32_t first=*(volatile uint32_t *)(uintptr_t)0x805aa0u;
 *(volatile uint32_t *)(record+720u)=first;
 *(volatile uint8_t *)(record+799u)=0u;
 *(volatile uint16_t *)(record+752u)=0u;
 *(volatile uint32_t *)(record+724u)=second;
 (void)opencfw_em9305_radio_channel_transform_30e3fc(record+720u);
 access=*(volatile uint32_t *)(record+372u);
 uint32_t flag=*(volatile uint8_t *)(record+2809u);
 uint32_t seed=*(volatile uint16_t *)(record+752u);
 *(volatile uint8_t *)(record+766u)=1u;
 *(volatile uint16_t *)(record+768u)=(uint16_t)(access^(access>>16u));
 if(flag!=0u)seed^=*(volatile uint8_t *)(record+799u);
 uint32_t channel=opencfw_em9305_associated_channel_seed_324c98(record+720u,seed);
 *(volatile uint8_t *)(record+697u)=(uint8_t)channel;
 uint32_t status;
 flag=*(volatile uint8_t *)(record+2809u);
 uintptr_t callback=0u;
 if(flag!=0u)callback=*(volatile uint32_t *)(uintptr_t)0x805cc4u;
 if(callback!=0u)status=((uint32_t (*)(uintptr_t))callback)(record);
 else status=opencfw_em9305_associated_validate_32b2d4(record);
 if(status!=0u){
  (void)opencfw_em9305_associated_cleanup_3266d0(record,3u);
  return opencfw_em9305_command_periodic_status_30e878(*(volatile uint8_t *)(record+1u),status);
 }
 uint32_t kind=*(volatile uint8_t *)(record+2u);
 *(volatile uint8_t *)(record+369u)=1u;
 if(kind==1u){
  if(*(volatile uint8_t *)(record+2785u)==0u)*(volatile uint8_t *)(record+378u)=1u;
  uint32_t crc=opencfw_em9305_associated_timing_crc(record);
  *(volatile uint8_t *)(record+2786u)=1u;
  *(volatile uint16_t *)(record+1442u)=(uint16_t)crc;
 }
 if(*(volatile uint8_t *)(record+704u)!=0u){
  uint32_t crc=opencfw_em9305_associated_timing_crc(record);
  *(volatile uint16_t *)(record+706u)=(uint16_t)crc;
 }
 (void)opencfw_em9305_command_periodic_status_30e878(*(volatile uint8_t *)(record+1u),0u);
 return opencfw_em9305_command_count_30e4bc();
}

static uint8_t row[2824] __attribute__((aligned(4))),one[8],two[8];static unsigned seed,flag,status,callback_mode,randoms,crcs,cleanups,events,validation,callbacks;
uint32_t opencfw_em9305_common_request_30455c(uint32_t p){if(p!=1)abort();return 19;}
uint32_t opencfw_em9305_radio_access_raw_318878(void){if(row[698])abort();return 0x78123645;}
uint32_t opencfw_em9305_radio_channel_transform_30e3fc(uintptr_t p){if(p!=(uintptr_t)row+720||*(uint32_t*)(row+720)!=0x12345678||*(uint32_t*)(row+724)!=0x87654321||row[799]||*(uint16_t*)(row+752))abort();*(uint32_t*)(row+372)=0x87651234;*(uint16_t*)(row+752)=seed;row[799]=13;row[2809]=flag;return 91;}
uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t p,uint32_t v){if(p!=(uintptr_t)row+720||v!=(seed^(flag?13:0))||row[766]!=1||*(uint16_t*)(row+768)!=(uint16_t)(0x8765^0x1234))abort();row[2809]=callback_mode;return 0x123409;}
uint32_t opencfw_em9305_associated_validate_32b2d4(uintptr_t p){if(p!=(uintptr_t)row||row[697]!=9)abort();validation++;return status;}
static uint32_t hook(uintptr_t p){if(p!=(uintptr_t)row||row[697]!=9)abort();callbacks++;return status;}
uint32_t opencfw_em9305_associated_cleanup_3266d0(uintptr_t p,uint32_t v){if(p!=(uintptr_t)row||v!=3)abort();cleanups++;row[1]=99;return 888;}
uint32_t opencfw_em9305_pal_random_step(void){randoms++;*(uint32_t*)(row+1424)=(uint32_t)(uintptr_t)two;*(uint16_t*)(row+2250)=9;return 0x13579;}
uint32_t opencfw_em9305_crc_update_304678(uint32_t v,uint32_t n,uintptr_t p){if(v!=0x13579||n!=(crcs?9:seed)||p!=(uintptr_t)(crcs?two:one))abort();crcs++;return 0x56780000+crcs;}
uint32_t opencfw_em9305_command_periodic_status_30e878(uint32_t id,uint32_t v){if(id!=(status?99:51)||v!=status)abort();events++;return 0xf001;}
uint32_t opencfw_em9305_command_count_30e4bc(void){if(events!=1)abort();return 0xf002;}
int main(void){if(mmap((void*)0x805000,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
for(seed=0;seed<256;seed++)for(flag=0;flag<2;flag++)for(callback_mode=0;callback_mode<3;callback_mode++)for(status=0;status<=37;status+=37)for(unsigned kind=0;kind<2;kind++)for(unsigned enabled=0;enabled<2;enabled++)for(unsigned hold=0;hold<2;hold++){
 memset(row,0,sizeof row);row[1]=51;row[2]=kind?1:2;row[698]=91;row[704]=enabled;row[2785]=hold;row[378]=91;*(uint32_t*)(row+1424)=(uint32_t)(uintptr_t)one;*(uint16_t*)(row+2250)=seed;*(volatile uint32_t*)0x805aa0=0x12345678;*(volatile uint32_t*)0x805aa4=0x87654321;*(volatile uint32_t*)0x805cc4=callback_mode==2?(uint32_t)(uintptr_t)hook:0;randoms=crcs=cleanups=events=validation=callbacks=0;
 unsigned expectedcrc=status?0:kind+enabled;
 if(opencfw_em9305_associated_action_324b3c((uintptr_t)row)!=(status?0xf001:0xf002)||randoms!=expectedcrc||crcs!=expectedcrc||cleanups!=(status!=0)||events!=1||validation!=(callback_mode!=2)||callbacks!=(callback_mode==2))abort();
 if(!status&&(row[369]!=1||row[2786]!=kind||row[378]!=(kind&&!hold?1:91)||(kind&&*(uint16_t*)(row+1442)!=1)||(enabled&&*(uint16_t*)(row+706)!=(kind?2:1))))abort();
 cases++;
}
printf("PASS %u associated-start mutation/return cases\n",cases);return 0;}
