#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uintptr_t base;static unsigned total,queue_position,processed,empty,caps,posted;
uint32_t opencfw_em9305_phy_supported_31b39c(void){return 7;}
uint32_t opencfw_em9305_radio_phy_project_3183d4(uint32_t v){return v&2?2:v&1?1:v&4;}
uint32_t opencfw_em9305_wsf_queue_empty(uintptr_t q){if(q!=base+352||*(uint8_t*)(base+404))abort();return empty;}
uint32_t opencfw_em9305_ll_event_mode_32d4b0(uintptr_t p){if(p!=base)abort();caps++;return 321;}
uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t q,uintptr_t h){if(q!=base+352)abort();*(uint8_t*)h=5;return queue_position<total?++queue_position:0;}
uint32_t opencfw_em9305_ll_event_decode_32dae4(uintptr_t out,uintptr_t in){*(uint16_t*)out=(uint16_t)in;return 4;}
uint32_t opencfw_em9305_ll_event_process_32d380(uintptr_t p,uint32_t cap,uintptr_t d,uintptr_t m){if(p!=base||cap!=321||*(uint16_t*)d!=m||m!=processed+1)abort();processed++;*(volatile uint8_t*)0x805b18=(uint8_t)processed;return 0;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t h,uint32_t e){if(h!=*(volatile uint8_t*)0x805b18||e!=4||processed!=total)abort();posted++;return 99;}
/* Native327544..32754a full first-PHY state setter. */
uint32_t opencfw_em9305_phy_apply_327544(uintptr_t record,uint32_t value)
{ *(volatile uint8_t *)(record+597u)=(uint8_t)value;return (uint32_t)(record+597u); }
/* Native316610..316696 full PHY preference selector, including incidental R0. */
uint32_t opencfw_em9305_phy_choose_316610(uintptr_t record,uint32_t flags,uintptr_t first,uintptr_t second,uint32_t preferred)
{
 uint32_t b=*(volatile uint8_t *)second,a;
 if((flags&1u)==0u)a=*(volatile uint8_t *)first;
 else a=opencfw_em9305_phy_supported_31b39c();
 if((flags&2u)!=0u)b=opencfw_em9305_phy_supported_31b39c();
 uint32_t result=*(volatile uint8_t *)(record+4u);
 if((result&128u)!=0u){
  b&=a;
  if((uint8_t)b!=0u){
   uint32_t chosen=b&preferred;
   if(chosen!=0u)b=chosen;
   result=opencfw_em9305_radio_phy_project_3183d4((uint8_t)b);
   a=result;b=result;
  }else{
   uint32_t mode_first=*(volatile uint8_t *)(record+76u);
   uint32_t mode_second=*(volatile uint8_t *)(record+77u);
   uint32_t queue_position=mode_first-2u;
   result=(uint8_t)queue_position*8u;
   a=queue_position>=3u?1u:(0x00080402u>>(queue_position*8u));
   b=mode_second==4u?8u:mode_second==3u?4u:mode_second==2u?2u:1u;
  }
 }
 *(volatile uint8_t *)first=(uint8_t)a;
 *(volatile uint8_t *)second=(uint8_t)b;
 return result;
}
/* Native32e220..32e276 full pending update queue drain. */
uint32_t opencfw_em9305_phy_update_complete_32e220(uintptr_t record)
{
 *(volatile uint8_t *)(record+404u)=0u;
 uintptr_t queue=record+352u;
 uint32_t empty=opencfw_em9305_wsf_queue_empty(queue);
 if(empty!=0u)return empty;
 uint32_t capacity=opencfw_em9305_ll_event_mode_32d4b0(record);
 _Alignas(4) uint8_t decoded[8];uint8_t handler;
 for(;;){
  uintptr_t message=opencfw_em9305_wsf_event_remove(queue,(uintptr_t)&handler);
  if(message==0u)break;
  (void)opencfw_em9305_ll_event_decode_32dae4((uintptr_t)decoded,message);
  (void)opencfw_em9305_ll_event_process_32d380(record,capacity,(uintptr_t)decoded,message);
 }
 uint32_t event_handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 return opencfw_em9305_wsf_event_post(event_handler,4u);
}

int main(void){
 if(mmap((void*)0x805000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uint8_t r[800];base=(uintptr_t)r;unsigned count=0;
 for(unsigned a=0;a<256;a++)for(unsigned c=0;c<256;c++)for(unsigned pref=0;pref<8;pref++)for(unsigned shared=0;shared<2;shared++){
 memset(r,0,sizeof r);r[4]=shared?128:9;r[76]=3;r[77]=4;uint8_t first=a,second=c;uint32_t expected=shared?8:9;unsigned ef=a,es=c;
 if(shared){unsigned common=a&c;if(common){unsigned selected=common&pref;if(!selected)selected=common;unsigned v=selected&2?2:selected&1?1:selected&4;expected=v;ef=v;es=v;}else{ef=4;es=8;}}
 if(opencfw_em9305_phy_choose_316610(base,0,(uintptr_t)&first,(uintptr_t)&second,pref)!=expected||first!=ef||second!=es)abort();
 count++;
 }
 const unsigned mapping[5]={1,1,2,4,8};
 for(unsigned a=0;a<256;a++)for(unsigned c=0;c<256;c++){
 memset(r,0,sizeof r);r[4]=128;r[76]=a;r[77]=c;uint8_t first=1,second=2;
 unsigned ef=a<5?mapping[a]:1,es=c<5?mapping[c]:1;
 if(opencfw_em9305_phy_choose_316610(base,0,(uintptr_t)&first,(uintptr_t)&second,0)!=(uint8_t)(a-2)*8u||first!=ef||second!=es)abort();
 count++;
 }
 for(total=0;total<256;total++)for(empty=0;empty<2;empty++){
 memset(r,0,sizeof r);r[404]=1;queue_position=processed=caps=posted=0;*(volatile uint8_t*)0x805b18=7;
 if(opencfw_em9305_phy_update_complete_32e220(base)!=(empty?1:99)||caps!=!empty||posted!=!empty||processed!=(empty?0:total))abort();
 count++;
 }
 printf("PASS %u selection/queue cases\n",count);return 0;
}
