#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned trace,stop,mutate,allocation,message;
static uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t p){assert(trace==0&&p==0x820000);trace=1;return 17;}
static uint32_t opencfw_em9305_wsf_pool_release(uintptr_t p){assert(trace==0&&p==0x840000);trace=2;return 99;}
static uint32_t opencfw_em9305_wsf_event_release(uintptr_t p){assert(trace==2&&p==0x850000);trace=3;return 98;}
uint32_t opencfw_em9305_command_stop_30b654(uintptr_t p){assert(p==0&&trace==0);stop++;if(mutate) *(uint8_t *)0x8058dc=mutate;return 97;}
uint32_t opencfw_em9305_common_release_304588(uint32_t n){assert(n==2&&trace==(message?3:2));trace=4;if(mutate==4) *(uint8_t *)0x8058dc=4;return 96;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==4&&trace==4);trace=5;return allocation?0x860000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t handler,uintptr_t p){assert(trace==5&&handler==71&&p==0x860000&&*(uint16_t *)0x860002==261);trace=6;return 23;}
/* Native continuation332d2c..332db4 and byte-decrement30e48c..30e49c.
 * Native rereads state after stop/release/event effects. */
extern uint32_t opencfw_em9305_command_stop_30b654(uintptr_t);
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
uint32_t opencfw_em9305_command_count_down_30e48c(void)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805a79u;
 *(volatile uint8_t *)(uintptr_t)0x805a79u=(uint8_t)(count-1u);
 return 0x805a79u;
}
uint32_t opencfw_em9305_command_callback_332d2c(uintptr_t object)
{
 uintptr_t state=0x8058dcu;
 uint32_t limit=*(volatile uint16_t *)(state+2u);
 uintptr_t record=*(volatile uint32_t *)(object+44u);
 if(limit!=0u){
  uint32_t success=*(volatile uint16_t *)(state+6u);
  uint32_t failed=*(volatile uint16_t *)(state+8u);
  uint32_t other=*(volatile uint16_t *)(state+10u);
  if(success+failed+other>=limit)(void)opencfw_em9305_command_stop_30b654(0u);
 }
 if(*(volatile uint8_t *)state==2u)return opencfw_em9305_auxiliary_insert_313220(object);
 (void)opencfw_em9305_wsf_pool_release(*(volatile uint32_t *)(record+108u));
 uintptr_t message=*(volatile uint32_t *)(uintptr_t)0x805a6cu;
 if(message!=0u){
  (void)opencfw_em9305_wsf_event_release(message);
  *(volatile uint32_t *)(uintptr_t)0x805a6cu=0u;
 }
 (void)opencfw_em9305_common_release_304588(2u);
 if(*(volatile uint8_t *)state==4u){
  uintptr_t response=opencfw_em9305_wsf_event_allocate(4u);
  if(response==0u)return 0u;
  *(volatile uint16_t *)(response+2u)=261u;
  uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
  return opencfw_em9305_wsf_task_message_send(handler,response);
 }
 *(volatile uint8_t *)state=0u;
 *(volatile uint8_t *)(uintptr_t)0x805a78u=0u;
 return opencfw_em9305_command_count_down_30e48c();
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);*(uint32_t *)0x82002c=0x830000;*(uint32_t *)0x83006c=0x840000;*(uint8_t *)0x805b18=71;unsigned cases=0;
for(unsigned state=0;state<5;state++)for(unsigned limit=0;limit<4;limit++)for(unsigned count=0;count<4;count++)for(message=0;message<2;message++)for(allocation=0;allocation<2;allocation++)for(mutate=0;mutate<5;mutate++){*(uint8_t *)0x8058dc=state;*(uint16_t *)0x8058de=limit;*(uint16_t *)0x8058e2=count;*(uint16_t *)0x8058e4=0;*(uint16_t *)0x8058e6=0;*(uint8_t *)0x805a78=1;*(uint8_t *)0x805a79=0;*(uint32_t *)0x805a6c=message?0x850000:0;trace=stop=0;unsigned expectedstop=limit&&count>=limit;unsigned fresh=expectedstop&&mutate?mutate:state;unsigned finalstate=mutate==4?4:fresh;unsigned expected=fresh==2?17:finalstate==4?allocation?23:0:0x805a79;assert(opencfw_em9305_command_callback_332d2c(0x820000)==expected&&stop==expectedstop);if(fresh==2){assert(trace==1&&*(uint32_t *)0x805a6c==(message?0x850000:0));}else{assert(*(uint32_t *)0x805a6c==0);if(finalstate==4){assert(trace==(allocation?6:5)&&*(uint8_t *)0x8058dc==4&&*(uint8_t *)0x805a79==0);}else{assert(trace==4&&*(uint8_t *)0x8058dc==0&&*(uint8_t *)0x805a78==0&&*(uint8_t *)0x805a79==255);}}cases++;}
printf("PASS %u\n",cases);}
