#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint8_t record[4096] __attribute__((aligned(4))),packet[128] __attribute__((aligned(4))),expected[128],data[32],event[64] __attribute__((aligned(4))),expectevent[64];static unsigned found,fail,sends,allocs;
static uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){(void)id;return found?(uintptr_t)record:0;}
static void*opencfw_em9305_memcpy(void*a,const void*b,size_t n){return memcpy(a,b,n);}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){if(n!=24)abort();allocs++;return fail?0:(uintptr_t)event;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t p){if(handler!=9||p!=(uintptr_t)event)abort();sends++;return 0;}
/* Native3132f8..31330c: exact head/state predicate, no invented scheduler status. */
uint32_t opencfw_em9305_command_schedule_idle_3132f8(uintptr_t object)
{uint32_t head=*(volatile uint32_t *)(uintptr_t)0x805f14u;uint32_t state=*(volatile uint8_t *)(uintptr_t)0x805f04u;return (head!=(uint32_t)object)|(state!=2u);}
/* Native3082b0..3082da: sparse24B notification with caller-provided address. */
void opencfw_em9305_command_data_notify_3082b0(uint32_t type,uint32_t low,uint32_t high)
{uintptr_t event=opencfw_em9305_wsf_event_allocate(24u);if(event==0u)return;*(volatile uint16_t *)(event+2u)=774u;uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;*(volatile uint32_t *)(event+8u)=low;*(volatile uint8_t *)(event+5u)=(uint8_t)type;*(volatile uint32_t *)(event+12u)=high;(void)opencfw_em9305_wsf_task_message_send(handler,event);}
/* Native306c8c..306cba: original fullword input saved through record lookup. */
void opencfw_em9305_command_data_notify_mask_306c8c(uint32_t id,uint32_t mask)
{uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);if(record==0u)return;uint32_t flags=*(volatile uint8_t *)(record+2808u);if((flags&mask)!=mask)return;if(*(volatile uint8_t *)(record+1u)!=id)return;uint32_t high=*(volatile uint32_t *)(record+52u),low=*(volatile uint32_t *)(record+48u),type=*(volatile uint8_t *)(record+58u);opencfw_em9305_command_data_notify_3082b0(type,low,high);}
/* Native327510..327540: legacy31-byte replacement; native payload begins at22. */
uint32_t opencfw_em9305_command_payload_legacy_327510(uintptr_t record,uintptr_t packet,uint32_t operation,uint32_t length,uintptr_t data)
{if(operation!=3u||length>=32u)return 18u;*(volatile uint8_t *)(packet+21u)=(uint8_t)length;if(data!=0u)(void)opencfw_em9305_memcpy((void *)(packet+22u),(const void *)data,length);if(*(volatile uint8_t *)(record+2u)==1u)*(volatile uint8_t *)(packet+8u)=1u;*(volatile uint8_t *)(packet+20u)=1u;return 0u;}
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;for(unsigned i=0;i<32;i++)data[i]=i+11;*(uint8_t*)0x805b18=9;uint64_t cases=0;
for(unsigned op=0;op<6;op++){for(unsigned len=0;len<256;len++){for(unsigned busy=0;busy<3;busy++){for(unsigned null=0;null<2;null++){memset(packet,0xa5,128);memcpy(expected,packet,128);record[2]=busy;unsigned valid=op==3&&len<32;if(valid){expected[21]=len;if(!null)memcpy(expected+22,data,len);if(busy==1)expected[8]=1;expected[20]=1;}unsigned r=opencfw_em9305_command_payload_legacy_327510((uintptr_t)record,(uintptr_t)packet,op,len,null?0:(uintptr_t)data);if(r!=(valid?0:18)||memcmp(packet,expected,128))abort();cases++;}}}}
for(unsigned state=0;state<256;state++){for(unsigned same=0;same<2;same++){*(uint8_t*)0x805f04=state;*(uint32_t*)0x805f14=same?0x812abc:0x812abd;if(opencfw_em9305_command_schedule_idle_3132f8(0x812abc)!=(!same||state!=2))abort();cases++;}}
uint32_t low=0x12345678,high=0xabcdef12;memcpy(record+48,&low,4);memcpy(record+52,&high,4);record[58]=29;record[1]=7;for(unsigned flags=0;flags<256;flags++){for(unsigned mask=0;mask<256;mask++){record[2808]=flags;found=1;fail=mask&1;sends=allocs=0;memset(event,0xa5,64);memcpy(expectevent,event,64);unsigned matched=(flags&mask)==mask;if(matched&&!fail){uint16_t type=774;memcpy(expectevent+2,&type,2);expectevent[5]=29;memcpy(expectevent+8,&low,4);memcpy(expectevent+12,&high,4);}opencfw_em9305_command_data_notify_mask_306c8c(7,mask);if(allocs!=matched||sends!=(matched&&!fail)||memcmp(event,expectevent,64))abort();cases++;}}
found=0;allocs=sends=0;opencfw_em9305_command_data_notify_mask_306c8c(7,0);if(allocs||sends)abort();cases++;found=1;opencfw_em9305_command_data_notify_mask_306c8c(0x107,0);if(allocs||sends)abort();cases++;printf("PASS %llu\n",(unsigned long long)cases);return 0;}
