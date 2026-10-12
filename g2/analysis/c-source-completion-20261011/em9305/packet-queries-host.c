#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned gate,found,lookups,powers;static uint32_t lastid;static int32_t lastrequest;static uint8_t record[128] __attribute__((aligned(4)));
static uint32_t opencfw_em9305_ll_stream_gate_30e510(void){*(uint32_t*)0x805cac=0x810000;return gate;}
static uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){lastid=id;lookups++;return found?(uintptr_t)record:0;}
static uint32_t opencfw_em9305_command_radio_power_310230(int32_t a,uint32_t b){lastrequest=a;if(b)abort();powers++;return (uint32_t)(a+11);}
/* Native30c768..30c788: post-gate live config, signed min on positive halfword. */
uint32_t opencfw_em9305_command_packet_size_30c768(uintptr_t output)
{if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;uint32_t size=*(volatile uint16_t *)(config+16u);if(size>1650u)size=1650u;*(volatile uint16_t *)output=(uint16_t)size;return 0u;}
/* Native30c7b0..30c7cc: failure preserves caller output. */
uint32_t opencfw_em9305_command_packet_count_30c7b0(uintptr_t output)
{if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;uint32_t count=*(volatile uint8_t *)(config+12u);*(volatile uint8_t *)output=(uint8_t)count;return 0u;}
/* Native30bd8c tail306ee8..306f08: initial output sentinel before lookup. */
uint32_t opencfw_em9305_command_packet_power_30bd8c(uint32_t id,uintptr_t output)
{*(volatile uint8_t *)output=129u;uintptr_t record=opencfw_em9305_radio_record_find_31aa64((uint8_t)id);if(record==0u)return 66u;int32_t requested=*(volatile int8_t *)(record+60u);uint32_t power=opencfw_em9305_command_radio_power_310230(requested,0u);*(volatile uint8_t *)output=(uint8_t)power;return 0u;}
int main(void){if(mmap((void*)0x800000,0x20000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;uint64_t count=0;uint8_t output[16] __attribute__((aligned(4))),expected[16];
for(unsigned n=0;n<65536;n++)for(gate=0;gate<2;gate++){memset(output,0xa5,16);memcpy(expected,output,16);*(uint16_t*)0x810010=n;*(uint32_t*)0x805cac=0;unsigned r=opencfw_em9305_command_packet_size_30c768((uintptr_t)(output+4));if(gate){uint16_t v=n>1650?1650:n;memcpy(expected+4,&v,2);}if(r!=(gate?0:12)||memcmp(output,expected,16))abort();count++;}
for(unsigned n=0;n<256;n++)for(gate=0;gate<2;gate++){memset(output,0xa5,16);memcpy(expected,output,16);*(uint8_t*)0x81000c=n;unsigned r=opencfw_em9305_command_packet_count_30c7b0((uintptr_t)(output+4));if(gate)expected[4]=n;if(r!=(gate?0:12)||memcmp(output,expected,16))abort();count++;}
for(unsigned id=0;id<65536;id++)for(found=0;found<2;found++){memset(output,0xa5,16);memcpy(expected,output,16);record[60]=id;lookups=powers=0;unsigned r=opencfw_em9305_command_packet_power_30bd8c(id,(uintptr_t)(output+4));expected[4]=found?(uint8_t)((int8_t)id+11):129;if(r!=(found?0:66)||lastid!=(uint8_t)id||lookups!=1||powers!=found||(found&&lastrequest!=(int8_t)id)||memcmp(output,expected,16))abort();count++;}
printf("PASS %llu\n",(unsigned long long)count);return 0;}
