#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned gate,found,stops,downs,notifications,precallbacks,scenario;static uintptr_t lasttimer;
static uint32_t opencfw_em9305_ll_stream_gate_30e510(void){return gate;}
static uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){if(id!=0xabcdef12)abort();return found?0x810000:0;}
static uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t timer){lasttimer=timer;stops++;return 0;}
static uint32_t opencfw_em9305_command_count_down_30e48c(void){downs++;if(scenario==1)*(uint8_t*)0x80f00c=1;if(scenario==2)*(uint32_t*)0x805c38=0x811000;return 0;}
static void notify(uintptr_t record){if(*(uint8_t*)record)abort();notifications++;}
static void pre(uintptr_t record){precallbacks++;*(uint8_t*)(record+2809)=1;}
/* Native31ac54..31ac82: capture notification flag before clearing active byte. */
void opencfw_em9305_command_record_clear_31ac54(uintptr_t record)
{uint32_t notify=*(volatile uint8_t *)(record+2809u);*(volatile uint8_t *)record=0u;if(notify!=0u){uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805c74u;if(callback!=0u)((void (*)(uintptr_t))callback)(record);}(void)opencfw_em9305_wsf_timer_stop(record+808u);(void)opencfw_em9305_command_count_down_30e48c();}
/* Native30ca00 tail308368..3083a0: gate, saved record, two busy flags and callback. */
uint32_t opencfw_em9305_command_clear_30ca00(uint32_t id)
{if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);if(record==0u)return 66u;if(*(volatile uint8_t *)(record+2u)!=0u||*(volatile uint8_t *)(record+369u)!=0u)return 12u;uintptr_t callback=*(volatile uint32_t *)(record+2804u);if(callback!=0u)((void (*)(uintptr_t))callback)(record);opencfw_em9305_command_record_clear_31ac54(record);return 0u;}
/* Native30b118 tail306b14..306b6e: preflight fixed count, then reload after active clears. */
uint32_t opencfw_em9305_command_clear_all_30b118(void)
{if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;uint32_t count=*(volatile uint8_t *)(config+12u);if(count!=0u){uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x805c38u;for(uint32_t i=0;i<count;i++){if(*(volatile uint8_t *)(record+2u)!=0u||*(volatile uint8_t *)(record+369u)!=0u)return 12u;record+=2824u;}}uint32_t index=0u,offset=0u;while(index<count){uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x805c38u+offset;if(*(volatile uint8_t *)record!=0u){opencfw_em9305_command_record_clear_31ac54(record);config=*(volatile uint32_t *)(uintptr_t)0x805cacu;count=*(volatile uint8_t *)(config+12u);}offset+=2824u;index++;}return 0u;}
static void reset(void){memset((void*)0x800000,0,0x20000);*(uint32_t*)0x805cac=0x80f000;*(uint32_t*)0x805c38=0x810000;*(uint32_t*)0x805c74=(uintptr_t)notify;stops=downs=notifications=precallbacks=0;scenario=0;}
int main(void){if(mmap((void*)0x800000,0x20000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
for(gate=0;gate<2;gate++)for(found=0;found<2;found++)for(unsigned a=0;a<256;a++)for(unsigned b=0;b<2;b++){reset();*(uint8_t*)0x810002=a;*(uint8_t*)(0x810000+369)=b;*(uint8_t*)0x810000=1;*(uint32_t*)(0x810000+2804)=(uintptr_t)pre;unsigned r=opencfw_em9305_command_clear_30ca00(0xabcdef12);unsigned success=gate&&found&&!a&&!b;if(r!=(!gate?12:!found?66:a||b?12:0)||stops!=success||downs!=success||notifications!=success||precallbacks!=success||(success&&lasttimer!=0x810000+808))abort();cases++;}
for(gate=0;gate<2;gate++)for(unsigned n=0;n<8;n++)for(unsigned busy=0;busy<9;busy++){reset();*(uint8_t*)0x80f00c=n;for(unsigned i=0;i<n;i++){*(uint8_t*)((uintptr_t)0x810000+i*2824)=i%2;*(uint8_t*)((uintptr_t)0x810000+i*2824+2809)=1;}if(busy<n)*(uint8_t*)((uintptr_t)0x810000+busy*2824+369)=1;unsigned r=opencfw_em9305_command_clear_all_30b118();unsigned success=gate&&busy>=n;if(r!=(success?0:12)||stops!=(success?n/2:0)||downs!=stops||notifications!=stops)abort();cases++;}
reset();gate=1;scenario=1;*(uint8_t*)0x80f00c=4;*(uint8_t*)0x810000=1;*(uint8_t*)(0x810000+2824)=1;if(opencfw_em9305_command_clear_all_30b118()||stops!=1)abort();cases++;
reset();gate=1;scenario=2;*(uint8_t*)0x80f00c=2;*(uint8_t*)0x810000=1;*(uint8_t*)(0x811000+2824)=1;if(opencfw_em9305_command_clear_all_30b118()||stops!=2||lasttimer!=0x811000+2824+808)abort();cases++;printf("PASS %u\n",cases);return 0;}
