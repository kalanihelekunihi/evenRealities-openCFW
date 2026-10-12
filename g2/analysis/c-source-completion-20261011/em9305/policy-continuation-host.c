#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned stop,mutate,allocation,insert,release,duration,pattern,request,send;
uint32_t opencfw_em9305_command_stop_30b654(uintptr_t p){assert(p==0);stop++;if(mutate) *(uint8_t *)0x8058dc=mutate;return 99;}
static uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t p){assert(p==0x820000);insert++;return 17;}
static uint32_t opencfw_em9305_wsf_pool_release(uintptr_t p){assert(p==0x840000);release++;return 18;}
static uint32_t opencfw_em9305_common_release_304588(uint32_t n){assert(n==2&&release);request++;if(mutate==4) *(uint8_t *)0x8058dc=4;return 19;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==4&&request);return allocation?0x850000:0;}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t n,uintptr_t p){assert(n==71&&p==0x850000&&*(uint16_t *)(p+2)==261);send++;return 23;}
static uint32_t opencfw_em9305_command_count_down_30e48c(void){*(uint8_t *)0x805a79-=1;return 0x805a79;}
static uint32_t opencfw_em9305_command_duration_332be4(uint32_t a,uint32_t b,uint32_t c){assert(a==13&&b==2&&c==1);duration++;return 65000;}
static uint32_t opencfw_em9305_command_pattern_332b94(uint32_t a,uint32_t b,uintptr_t p){assert(a==13&&b==5&&p==0x840000);pattern++;return 0;}
/* Native continuation332e2c..332efc: complete selected body.
 * Packet pointer and policy kind survive duration332be4's exact register set. */
uint32_t opencfw_em9305_command_callback_332e2c(uintptr_t object)
{
 uintptr_t state=0x8058dcu;
 uint32_t count=*(volatile uint16_t *)(state+4u);
 uint32_t limit=*(volatile uint16_t *)(state+2u);
 uintptr_t record=*(volatile uint32_t *)(object+44u);
 uint32_t next=count+1u;
 *(volatile uint16_t *)(state+4u)=(uint16_t)next;
 if(limit!=0u&&(uint16_t)next>=limit)(void)opencfw_em9305_command_stop_30b654(0u);
 uint32_t fresh=*(volatile uint8_t *)state;
 uintptr_t packet=*(volatile uint32_t *)(record+104u);
 if(fresh==1u){
  uintptr_t policy=0x805994u;
  uint32_t recorded_channel=*(volatile uint8_t *)(record+1u);
  uint32_t channel=*(volatile uint8_t *)(policy+2u);
  uint32_t kind=*(volatile uint8_t *)(policy+1u);
  if(channel==recorded_channel){
   uint32_t header=*(volatile uint8_t *)packet;
   if(kind==(header&~32u)){
    uint32_t packet_pattern=*(volatile uint8_t *)(packet+1u);
    uint32_t pattern=*(volatile uint8_t *)policy;
    if(pattern==packet_pattern){
     uint32_t recorded_mode=*(volatile uint8_t *)(record+12u);
     uint32_t mode=*(volatile uint8_t *)(policy+3u);
     if(mode==recorded_mode){
      uint32_t recorded_encoding=*(volatile uint8_t *)(record+14u);
      uint32_t encoding=*(volatile uint16_t *)(policy+4u);
      if(encoding==recorded_encoding)return opencfw_em9305_auxiliary_insert_313220(object);
     }
    }
   }
  }
  uint32_t mode=*(volatile uint8_t *)(policy+3u);
  uint32_t encoding=*(volatile uint8_t *)(policy+4u);
  uint32_t pattern=*(volatile uint8_t *)policy;
  *(volatile uint8_t *)(record+1u)=(uint8_t)channel;
  *(volatile uint8_t *)(record+15u)=0u;
  *(volatile uint16_t *)(record+108u)=(uint16_t)(pattern+2u);
  *(volatile uint8_t *)(record+13u)=(uint8_t)mode;
  *(volatile uint8_t *)(record+12u)=(uint8_t)mode;
  *(volatile uint8_t *)(record+14u)=(uint8_t)encoding;
  uint32_t duration=opencfw_em9305_command_duration_332be4(pattern,mode,encoding);
  *(volatile uint16_t *)(record+110u)=(uint16_t)duration;
  (void)opencfw_em9305_command_pattern_332b94(pattern,kind,packet);
  return opencfw_em9305_auxiliary_insert_313220(object);
 }
 (void)opencfw_em9305_wsf_pool_release(packet);
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

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);*(uint32_t *)0x82002c=0x830000;*(uint32_t *)0x830068=0x840000;*(uint8_t *)0x805b18=71;unsigned cases=0;uint16_t counts[]={0,1,65535};
for(unsigned state=0;state<5;state++)for(unsigned limit=0;limit<4;limit++)for(unsigned ci=0;ci<3;ci++)for(unsigned mismatch=0;mismatch<6;mismatch++)for(allocation=0;allocation<2;allocation++)for(mutate=0;mutate<5;mutate++){*(uint8_t *)0x8058dc=state;*(uint16_t *)0x8058de=limit;*(uint16_t *)0x8058e0=counts[ci];*(uint8_t *)0x805a78=1;*(uint8_t *)0x805a79=0;*(uint8_t *)0x805996=19;*(uint8_t *)0x830001=mismatch==1?18:19;*(uint8_t *)0x805995=5;*(uint8_t *)0x840000=mismatch==2?4:37;*(uint8_t *)0x805994=13;*(uint8_t *)0x840001=mismatch==3?12:13;*(uint8_t *)0x805997=2;*(uint8_t *)0x83000c=mismatch==4?1:2;*(uint16_t *)0x805998=1;*(uint8_t *)0x83000e=mismatch==5?0:1;*(uint8_t *)0x83000f=77;*(uint16_t *)0x83006c=88;*(uint16_t *)0x83006e=99;stop=insert=release=duration=pattern=request=send=0;unsigned next=(uint16_t)(counts[ci]+1);unsigned expectedstop=limit&&next>=limit;unsigned fresh=expectedstop&&mutate?mutate:state;unsigned finalstate=mutate==4?4:fresh;unsigned result=fresh==1?17:finalstate==4?allocation?23:0:0x805a79;assert(opencfw_em9305_command_callback_332e2c(0x820000)==result&&stop==expectedstop&&*(uint16_t *)0x8058e0==next);if(fresh==1){assert(insert==1&&!release&&!request&&!send&&duration==(mismatch!=0)&&pattern==(mismatch!=0));if(mismatch)assert(*(uint8_t *)0x830001==19&&*(uint8_t *)0x83000c==2&&*(uint8_t *)0x83000d==2&&*(uint8_t *)0x83000e==1&&*(uint8_t *)0x83000f==0&&*(uint16_t *)0x83006c==15&&*(uint16_t *)0x83006e==65000);}else{assert(!insert&&!duration&&!pattern&&release==1&&request==1&&send==(finalstate==4&&allocation));if(finalstate!=4)assert(*(uint8_t *)0x8058dc==0&&*(uint8_t *)0x805a78==0&&*(uint8_t *)0x805a79==255);}cases++;}
printf("PASS %u\n",cases);}
