#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned duplicate,allocfail,packetfail,events,packets,posts,terminates;
static uint32_t opencfw_em9305_command_duplicate_307c5c(uint32_t role,uint32_t kind,uint32_t low,uint32_t high){if(role!=3||kind!=4||low!=11||high!=12)abort();return duplicate;}
static uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t n){if(n!=2)abort();packets++;return packetfail?0:0x809100;}
static uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t r,uintptr_t p){if(r!=0x806390||p!=0x809100||*(uint8_t*)p!=7||*(uint8_t*)(p+1)!=42)abort();return 17;}
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){if(n!=56)abort();events++;return allocfail?0:0x809000;}
static void *opencfw_em9305_memcpy(void* a,const void*b,uint32_t n){if(n!=18)abort();return memcpy(a,b,n);}
static uint32_t opencfw_em9305_associated_slot_sdiv(uint32_t a,uint32_t b){return (uint32_t)((int32_t)a/(int32_t)b);}
static uint32_t opencfw_em9305_wsf_task_message_send(uint32_t h,uintptr_t e){if(h!=9||e!=0x809000||*(uint16_t*)(e+2)!=268||*(uint16_t*)(e+4)!=123||memcmp((void*)(e+6),(void*)0x80281e,18)||*(uint16_t*)(e+24)!=1||*(uint16_t*)(e+28)!=65535||*(uint16_t*)e!=0xa5a5||*(uint8_t*)(e+47)!=0xa5)abort();posts++;return 18;}
static uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t r,uint32_t why){if(r!=0x806390||why!=110)abort();terminates++;return 71;}
#include "init-registered-324fb4-prepared.c"
#define W(a) (*(uint32_t*)(uintptr_t)(a))
#define B(a) (*(uint8_t*)(uintptr_t)(a))
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)!=(void*)0x800000)abort();unsigned cases=0;
for(duplicate=0;duplicate<2;duplicate++)for(allocfail=0;allocfail<2;allocfail++)for(packetfail=0;packetfail<2;packetfail++)for(unsigned capacity=0;capacity<2;capacity++)for(unsigned type=0;type<2;type++)for(unsigned request=0;request<8;request++)for(unsigned feature=0;feature<4;feature++)for(unsigned bad=0;bad<5;bad++){
memset((void*)0x800000,0,0x10000);memset((void*)0x809000,0xa5,56);events=packets=posts=terminates=0;W(0x802838)=11;W(0x80283c)=12;B(0x802834)=3;B(0x802835)=4;B(0x802837)=request;B(0x802818)=type?42:1;*(uint16_t*)0x80281c=123;for(unsigned j=0;j<18;j++)B(0x80281eu+j)=j+17;B(0x805b18)=9;W(0x805c70)=0x806000;*(uint16_t*)(0x806390+262)=65535;B(0x806390+614)=capacity;W(0x805a94)=((feature&1)?1u<<8:0)|((feature&2)?1u<<11:0);
B(0x802848)=bad==1?16:1;B(0x802849)=bad==2?5:10;B(0x80284a)=bad==3?0:3;B(0x80284b)=bad==4?1:2;
unsigned valid=capacity&&((request==1)||(request==2&&(feature&1))||(request==4&&(feature&2)));unsigned accepted=valid&&(!type||bad==0);
uint32_t result=opencfw_em9305_init_registered_324fb4(0x806390);
if(duplicate){if(result!=1||events||packets||posts||terminates)abort();}else {if(result!=71||terminates!=1||events!=accepted||posts!=(accepted&&!allocfail)||packets!=(!accepted&&type))abort();}
cases++;
}
printf("PASS %u isolated response callback cases\n",cases);return 0;}
