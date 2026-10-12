#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_pal_random_step(void),opencfw_em9305_radio_crc_seed_318960(void),opencfw_em9305_pal_current_time(void);
extern uint32_t opencfw_em9305_radio_duration_312be4(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_schedule_313424(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void *opencfw_em9305_memset(void*,uint32_t,uint32_t);
static uint32_t opencfw_em9305_native_mpywhl(uint32_t a,uint32_t b){return (uint32_t)((int64_t)(int32_t)a*(int16_t)b);}
extern uint32_t opencfw_em9305_associated_radio_callback_32b538(uintptr_t);
extern uint32_t opencfw_em9305_associated_packet_callback_32c69c(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_slot_allocate_3133b4(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,uint32_t);
/* Native32b2d0 true tail to32b538, represented with actual source relocation. */
uint32_t opencfw_em9305_associated_radio_tail_32b2d0(uintptr_t record)
{ return opencfw_em9305_associated_radio_callback_32b538(record); }
/* Native31896c..318986 keeps named XBFU and native low-bit BMSK semantics. */
uint32_t opencfw_em9305_associated_random_31896c(void)
{
 uint32_t value=opencfw_em9305_pal_random_step(),first,second;
 first=(value>>8)&3u;
 second=(value>>16)&1u;
 return (value&7u)+first+second+5u;
}
/* Native31b2fc..31b32a: exact signed low-word2824B record stride. */
uint32_t opencfw_em9305_associated_slot_query_31b2fc(uint32_t id,uintptr_t output)
{
 uint32_t offset=opencfw_em9305_native_mpywhl(id-4u,2824u);
 uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x805c38u;record+=offset;
 if(*(volatile uint8_t *)(record+368u)!=1u)return 0u;
 uint32_t result=*(volatile uint32_t *)(record+388u);
 if(output!=0u){uint32_t extent=*(volatile uint32_t *)(record+392u);*(volatile uint32_t *)output=extent;}
 return result;
}
static uint32_t opencfw_em9305_associated_macwhul(uint32_t prior,uint32_t factor,uint32_t iteration)
{return prior+factor*(iteration&65535u);}
/* Native32b2d4..32b4e2 complete validation/record/scheduler parent. */
uint32_t opencfw_em9305_associated_validate_32b2d4(uintptr_t record)
{
 uintptr_t object=record+380u;
 (void)opencfw_em9305_memset((void *)object,0u,148u);
 *(volatile uint8_t *)(record+406u)=1u;*(volatile uint8_t *)(record+404u)=1u;
 *(volatile uint32_t *)(record+412u)=(uint32_t)(uintptr_t)opencfw_em9305_associated_radio_tail_32b2d0;
 *(volatile uint32_t *)(record+408u)=(uint32_t)(uintptr_t)opencfw_em9305_associated_radio_callback_32b538;
 *(volatile uint32_t *)(record+416u)=(uint32_t)record;
 *(volatile uint32_t *)(record+424u)=(uint32_t)(record+428u);
 *(volatile uint32_t *)(record+420u)=(uint32_t)(record+1144u);
 uint32_t random=opencfw_em9305_associated_random_31896c();
 int32_t power=*(volatile int8_t *)(record+60u);uint32_t channel=*(volatile uint8_t *)(record+697u);
 *(volatile uint8_t *)(record+696u)=(uint8_t)random;
 *(volatile uint8_t *)(record+428u)=8u;*(volatile uint8_t *)(record+429u)=(uint8_t)channel;
 if(power==127)power=*(volatile uint8_t *)(uintptr_t)0x805a9cu;
 uint32_t access=*(volatile uint32_t *)(record+372u);
 *(volatile uint8_t *)(record+430u)=(uint8_t)power;
 *(volatile uint32_t *)(record+432u)=access;
 uint32_t crc=opencfw_em9305_radio_crc_seed_318960();
 uint32_t mode=*(volatile uint8_t *)(record+69u);
 *(volatile uint32_t *)(record+436u)=crc;
 *(volatile uint32_t *)(record+568u)=(uint32_t)(record+1077u);
 *(volatile uint32_t *)(record+532u)=(uint32_t)(record+1077u);
 *(volatile uint16_t *)(record+1154u)=0u;
 uint32_t index=mode-1u,decoded=index<4u?(0x02010201u>>((index&3u)*8u)):0u;
 uint32_t phy=*(volatile uint8_t *)(record+63u);
 *(volatile uint8_t *)(record+443u)=(uint8_t)decoded;*(volatile uint8_t *)(record+442u)=(uint8_t)decoded;
 *(volatile uint32_t *)(record+588u)=(uint32_t)(uintptr_t)opencfw_em9305_associated_packet_callback_32c69c;
 *(volatile uint8_t *)(record+441u)=(uint8_t)phy;*(volatile uint8_t *)(record+440u)=(uint8_t)phy;
 (void)opencfw_em9305_associated_object_init_312918(object,0u);
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t spacing=*(volatile uint16_t *)(config+20u),budget=*(volatile uint32_t *)(record+72u);
 uint32_t maximum=*(volatile uint32_t *)(record+712u),minimum=*(volatile uint32_t *)(record+708u);
 if(budget>spacing)spacing=budget;
 uint32_t timing=0u;
 if(*(volatile uint8_t *)(record+804u)!=0u){uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x801a14u;if(callback!=0u)timing=((uint32_t (*)(void))callback)();}
 uint32_t size=*(volatile uint16_t *)(record+1144u);
 phy=*(volatile uint8_t *)(record+63u);
 uint32_t duration=opencfw_em9305_radio_duration_312be4(phy,0u,timing,(uint16_t)spacing,size,1u,2u,0u);
 config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t chosen=*(volatile uint16_t *)(config+28u);
 if(chosen<duration){size=*(volatile uint16_t *)(record+1144u);phy=*(volatile uint8_t *)(record+63u);chosen=opencfw_em9305_radio_duration_312be4(phy,0u,timing,(uint16_t)spacing,size,1u,2u,0u);}
 uint32_t extent=*(volatile uint32_t *)(record+392u);if(chosen>extent)extent=chosen;
 *(volatile uint32_t *)(record+392u)=extent;
 if(maximum<chosen)return 69u;
 if(chosen>minimum)minimum=chosen;
 int32_t delta=(int32_t)((uint32_t)record-*(volatile uint32_t *)(uintptr_t)0x805c38u),row=delta/2824;
 volatile uint32_t allocation;
 uint32_t success=opencfw_em9305_associated_slot_allocate_3133b4((uint8_t)(row+4),1u,minimum,maximum,extent,(uintptr_t)&allocation,(uintptr_t)opencfw_em9305_associated_slot_query_31b2fc);
 if(success==0u)return 67u;
 uint32_t base=*(volatile uint32_t *)(record+2476u),selected=allocation;
 *(volatile uint32_t *)(record+700u)=selected;*(volatile uint32_t *)(record+400u)=selected;
 if(base==0u){selected=*(volatile uint32_t *)(record+700u);base=opencfw_em9305_pal_current_time();}
 delta=(int32_t)((uint32_t)record-*(volatile uint32_t *)(uintptr_t)0x805c38u);
 row=delta/2824;
 uint32_t elapsed=opencfw_em9305_radio_schedule_313424(selected,(uint8_t)(row+4),base,0u,0u);
 uint32_t half=*(volatile uint32_t *)(record+36u);if(elapsed==half)elapsed=half>>1u;
 uint32_t first=elapsed+base,next=first,iteration=1u;
 for(;;){
  *(volatile uint32_t *)(record+388u)=next;
  if(opencfw_em9305_associated_schedule_insert_312da4(object,0u)!=0u)return 0u;
  uint32_t count=*(volatile uint16_t *)(record+752u);selected=*(volatile uint32_t *)(record+700u);
  count+=1u;next=opencfw_em9305_associated_macwhul(first,selected,iteration);
  *(volatile uint16_t *)(record+752u)=(uint16_t)count;iteration+=1u;
 }
}

static uint8_t record[2824] __attribute__((aligned(4))),config[32];static unsigned gate,basekind,mode,seed,durationcalls,allocations,inserts,timecalls,timingcalls;
uint32_t opencfw_em9305_pal_random_step(void){return 0x00010307;}
uint32_t opencfw_em9305_radio_crc_seed_318960(void){return 0xabcdef;}
void *opencfw_em9305_memset(void*p,uint32_t v,uint32_t n){if(p!=record+380||v||n!=148)abort();return memset(p,v,n);}
uint32_t opencfw_em9305_associated_radio_callback_32b538(uintptr_t p){return (uint32_t)p;}
uint32_t opencfw_em9305_associated_packet_callback_32c69c(uintptr_t p,uint32_t v){return (uint32_t)p+v;}
uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t p,uint32_t v){if(p!=(uintptr_t)record+380||v||record[404]!=1||record[406]!=1||record[428]!=8||record[429]!=19||record[696]!=16||*(uint32_t*)(record+432)!=0x91237845||*(uint32_t*)(record+436)!=0xabcdef||*(uint32_t*)(record+416)!=(uint32_t)(uintptr_t)record||*(uint32_t*)(record+420)!=(uint32_t)(uintptr_t)(record+1144)||*(uint32_t*)(record+424)!=(uint32_t)(uintptr_t)(record+428)||record[442]!=(mode>=1&&mode<=4?(mode%2?1:2):0)||record[443]!=record[442]||record[440]!=7||record[441]!=7||record[430]!=(seed==127?5:seed)||*(uint16_t*)(record+1154))abort();return 61;}
static uint32_t timing(void){timingcalls++;*(uint32_t*)(record+712)=1;return 8;}
uint32_t opencfw_em9305_radio_duration_312be4(uint32_t phy,uint32_t req,uint32_t t,uint32_t spacing,uint32_t size,uint32_t ext,uint32_t m,uint32_t overhead){if(phy!=7||req||t!=8||spacing!=30||size!=16||ext!=1||m!=2||overhead)abort();durationcalls++;return durationcalls==1?20:22;}
uint32_t opencfw_em9305_associated_slot_allocate_3133b4(uint32_t id,uint32_t on,uint32_t minimum,uint32_t maximum,uint32_t extent,uintptr_t out,uintptr_t callback){if(id!=4||on!=1||minimum!=22||maximum!=100||extent!=22||callback!=(uintptr_t)opencfw_em9305_associated_slot_query_31b2fc)abort();allocations++;if(gate==1)return 0;*(uint32_t*)out=40;return 1;}
uint32_t opencfw_em9305_pal_current_time(void){timecalls++;*(uint32_t*)(record+700)=41;return 50;}
uint32_t opencfw_em9305_radio_schedule_313424(uint32_t selected,uint32_t id,uint32_t base,uint32_t a,uint32_t b){if(selected!=40||id!=4||base!=(basekind?30:50)||a||b)abort();return 60;}
uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t p,uint32_t v){unsigned first=basekind?60:80,step=basekind?40:41;if(p!=(uintptr_t)record+380||v||*(uint32_t*)(record+388)!=first+inserts*step||*(uint16_t*)(record+752)!=(uint16_t)(seed+inserts))abort();inserts++;return inserts==3;}
int main(void){if(mmap((void*)0x800000,0x7000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
for(gate=0;gate<3;gate++)for(basekind=0;basekind<2;basekind++)for(mode=0;mode<256;mode++)for(seed=0;seed<256;seed++){
 memset(record,0,sizeof record);memset(config,0,sizeof config);record[60]=seed;record[63]=7;record[69]=mode;record[697]=19;record[804]=1;*(uint16_t*)(record+1144)=16;*(uint16_t*)(record+752)=seed;*(uint32_t*)(record+372)=0x91237845;*(uint32_t*)(record+72)=30;*(uint32_t*)(record+708)=18;*(uint32_t*)(record+712)=gate?100:10;*(uint32_t*)(record+36)=60;*(uint32_t*)(record+2476)=basekind?30:0;*(uint16_t*)(config+20)=20;*(uint16_t*)(config+28)=16;*(volatile uint32_t*)0x805cac=(uint32_t)(uintptr_t)config;*(volatile uint32_t*)0x805c38=(uint32_t)(uintptr_t)record;*(volatile uint32_t*)0x801a14=(uint32_t)(uintptr_t)timing;*(volatile uint8_t*)0x805a9c=5;durationcalls=allocations=inserts=timecalls=timingcalls=0;
 unsigned expected=gate==0?69:gate==1?67:0;
 if(opencfw_em9305_associated_validate_32b2d4((uintptr_t)record)!=expected||durationcalls!=2||timingcalls!=1||allocations!=(gate!=0)||inserts!=(gate==2?3:0)||timecalls!=(gate==2&&!basekind)||*(uint32_t*)(record+392)!=22)abort();
 cases++;
}
printf("PASS %u validation captured/fresh-state cases\n",cases);return 0;}
