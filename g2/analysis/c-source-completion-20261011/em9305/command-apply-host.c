#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned scenario,n,copies;static char trace[16];static uint32_t scheduled_fixture;
static void mark(char c){trace[n++]=c;}
static uint32_t timing_callback(void){mark('T');*(uint32_t *)0x804084=0x850000;return 77;}
static uint32_t prepared_callback(uint32_t flags,uintptr_t p,uintptr_t data,uint32_t zero){assert(flags==64&&p==0x840016&&data==0x840058&&zero==0);assert(*(uint32_t *)(0x820000+124)==p);mark('P');*(uint16_t *)(0x840000+98)=13;return 0x12345;}
static uint32_t notify_callback(uintptr_t p,uint32_t duration){assert(p==0x803d78&&duration==100);mark('N');return 0;}
uint32_t opencfw_em9305_radio_duration_312be4(uint32_t phy,uint32_t requested,uint32_t timing,uint32_t spacing,uint32_t size,uint32_t extended,uint32_t mode,uint32_t overhead){assert(phy==2&&requested==0&&timing==(scenario==8?77:0)&&spacing==0&&size==4&&extended==0&&mode==2&&overhead==5);mark('D');return scenario==3?226:100;}
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t bytes){assert(bytes==4);copies++;mark('C');memcpy(d,s,bytes);if(scenario==9&&copies==1)*(uint32_t *)0x804084=0x850000;return d;}
uint32_t opencfw_em9305_pal_current_time(void){mark('K');return 100;}
/* Authenticated command apply 309514..3096a8: retain all validation,
 * partial writes, refreshes after callbacks/copies and native DSP timing. */
uint32_t opencfw_em9305_command_apply_309514(uint32_t id,uint32_t interval,uint32_t first,uint32_t second,uint32_t third,uint32_t size,uintptr_t input)
{
 uint32_t offset;
 offset=id*784u;
 uintptr_t slot=0x804080u+offset;
 uintptr_t record=*(volatile uint32_t *)(slot+4u);
 uint32_t active=*(volatile uint16_t *)(record+16u);
 if((int32_t)(active-interval)>1)return 70u;
 if(second>=first){
  if(interval+1u==active)return 70u;
  if(active==interval&&*(volatile uint8_t *)(record+19u)>second)return 70u;
 }
 uintptr_t table=0x803f7au+offset;
 uint32_t periods=*(volatile uint8_t *)(table+1u),budget;
 budget=periods*125u;
 budget-=150u;
 uint32_t timing=0u;
 if(*(volatile uint8_t *)(table+86u)!=0u){
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x801a14u;
  if(callback!=0u){
   timing=((uint32_t (*)(void))callback)();
   record=*(volatile uint32_t *)(slot+4u);
  }
 }
 uint32_t flags=*(volatile uint16_t *)(record+366u);
 uint32_t phy=*(volatile uint8_t *)(uintptr_t)(0x804080u+offset);
 uint32_t duration=opencfw_em9305_radio_duration_312be4(phy,0u,timing,0u,size,0u,2u,(flags&64u)!=0u?5u:3u);
 if(budget<duration)return 69u;
 record=*(volatile uint32_t *)(slot+4u);
 *(volatile uint8_t *)(record+109u)=(uint8_t)size;
 (void)opencfw_em9305_memcpy((void *)(record+112u),(const void *)input,size);
 *(volatile uint8_t *)(record+108u)=1u;
 record=*(volatile uint32_t *)(slot+4u);
 uint32_t position=*(volatile uint8_t *)(record+19u);
 if(position==second&&*(volatile uint16_t *)(record+16u)==interval){
  uint32_t length=*(volatile uint8_t *)(record+109u);
  uintptr_t owner=*(volatile uint32_t *)(uintptr_t)(0x803d78u+offset+92u);
  uintptr_t destination=*(volatile uint32_t *)(record+92u);
  *(volatile uint16_t *)(record+98u)=0u;
  *(volatile uint16_t *)(record+88u)=(uint16_t)length;
  uint32_t rate=*(volatile uint8_t *)table;
  uint32_t multiplier=*(volatile uint8_t *)(uintptr_t)(0x803d78u+offset+515u);
  (void)opencfw_em9305_memcpy((void *)destination,(const void *)(record+112u),length);
  record=*(volatile uint32_t *)(slot+4u);
  uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805c9cu;
  flags=*(volatile uint16_t *)(record+366u);
  *(volatile uint32_t *)(owner+124u)=(uint32_t)(record+22u);
  uint32_t prepared=((uint32_t (*)(uint32_t,uintptr_t,uintptr_t,uint32_t))callback)(flags,record+22u,record+88u,0u);
  record=*(volatile uint32_t *)(slot+4u);
  uint32_t product;
  product=third*multiplier;
  *(volatile uint16_t *)(owner+120u)=(uint16_t)prepared;
  uint32_t scheduled;
  assert(rate==4&&product==15);scheduled=scheduled_fixture;
  destination=*(volatile uint32_t *)(record+92u);
  uint32_t copied=*(volatile uint16_t *)(record+98u);
  *(volatile uint32_t *)(owner+112u)=scheduled;
  *(volatile uint32_t *)(owner+132u)=(uint32_t)destination;
  *(volatile uint16_t *)(owner+128u)=(uint16_t)copied;
  uint32_t now=opencfw_em9305_pal_current_time();
  uint32_t previous=*(volatile uint32_t *)(owner+144u);
  if((int32_t)(scheduled-now+previous)<0)return 70u;
  callback=*(volatile uint32_t *)(uintptr_t)0x805c94u;
  if(callback!=0u)(void)((uint32_t (*)(uintptr_t,uint32_t))callback)(0x803d78u+offset,duration);
  return 0u;
 }
 *(volatile uint8_t *)(record+100u)=1u;
 uint32_t shift=second&63u;
 uint32_t low=shift<32u?1u<<shift:0u;
 uint32_t high=shift>=32u?1u<<(shift-32u):0u;
 uint32_t oldlow=*(volatile uint32_t *)record;
 uint32_t oldhigh=*(volatile uint32_t *)(record+4u);
 *(volatile uint8_t *)(record+second+368u)=(uint8_t)third;
 *(volatile uint32_t *)record=low|oldlow;
 *(volatile uint32_t *)(record+4u)=high|oldhigh;
 return 0u;
}

int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(scenario=0;scenario<10;scenario++){memset((void *)0x800000,0,0x100000);n=0;copies=0;memset(trace,0,sizeof(trace));uintptr_t record=0x840000;*(uint32_t *)0x804084=record;*(uint8_t *)0x804080=2;*(uint16_t *)(record+16)=scenario==0?4:scenario==1?3:2;*(uint8_t *)(record+19)=scenario==2?3:scenario==4||scenario==9?0:2;*(uint16_t *)(record+366)=64;*(uint32_t *)(record+92)=0x830000;*(uint32_t *)(0x803d78+92)=0x820000;*(uint8_t *)0x803f7a=4;*(uint8_t *)(0x803f7a+1)=2;*(uint8_t *)(0x803d78+515)=3;*(uint32_t *)0x810000=0x12345678;*(uint32_t *)0x805c9c=(uint32_t)(uintptr_t)prepared_callback;*(uint32_t *)0x805c94=scenario==7?0:(uint32_t)(uintptr_t)notify_callback;scheduled_fixture=scenario==5?50:150;
if(scenario==8){*(uint8_t *)(0x803f7a+86)=1;*(uint32_t *)0x801a14=(uint32_t)(uintptr_t)timing_callback;}if(scenario==8||scenario==9){*(uint16_t *)(0x850000+366)=64;*(uint16_t *)(0x850000+16)=2;*(uint8_t *)(0x850000+19)=0;}
unsigned result=opencfw_em9305_command_apply_309514(0,2,1,2,5,4,0x810000);if(scenario<=2){assert(result==70&&n==0&&*(uint8_t *)(record+108)==0);}else if(scenario==3){assert(result==69&&strcmp(trace,"D")==0&&copies==0);}else if(scenario==4||scenario==8||scenario==9){assert(result==0&&strcmp(trace,scenario==8?"TDC":"DC")==0);uintptr_t current=scenario>=8?0x850000:record;assert(*(uint8_t *)(current+100)==1&&*(uint8_t *)(current+370)==5&&*(uint32_t *)current==4);assert(*(uint8_t *)(scenario==8?0x850000+108:record+108)==1);if(scenario==9)assert(*(uint8_t *)(0x850000+108)==0);}else{assert(result==(scenario==5?70:0));assert(strcmp(trace,scenario==5||scenario==7?"DCCPK":"DCCPKN")==0);assert(*(uint32_t *)0x830000==0x12345678&&*(uint16_t *)(0x820000+120)==0x2345&&*(uint32_t *)(0x820000+112)==scheduled_fixture&&*(uint32_t *)(0x820000+132)==0x830000&&*(uint16_t *)(0x820000+128)==13);}cases++;}
scenario=4;for(unsigned second=0;second<256;second++){memset((void *)0x800000,0,0x100000);n=0;copies=0;memset(trace,0,sizeof(trace));*(uint32_t *)0x804084=0x840000;*(uint8_t *)0x804080=2;*(uint16_t *)(0x840000+16)=2;*(uint8_t *)(0x840000+19)=(uint8_t)(second+1);*(uint16_t *)(0x840000+366)=64;*(uint8_t *)(0x803f7a+1)=3;*(uint32_t *)0x810000=0x12345678;*(uint32_t *)0x840000=0x81;*(uint32_t *)(0x840000+4)=0x12;assert(opencfw_em9305_command_apply_309514(0,2,256,second,5,4,0x810000)==0);uint32_t shift=second&63;assert(*(uint32_t *)0x840000==(0x81u|(shift<32?1u<<shift:0u)));assert(*(uint32_t *)(0x840000+4)==(0x12u|(shift>=32?1u<<(shift-32):0u)));assert(*(uint8_t *)(uintptr_t)(0x840000+368+second)==5&&strcmp(trace,"DC")==0);cases++;}
printf("PASS %u\n",cases);}
