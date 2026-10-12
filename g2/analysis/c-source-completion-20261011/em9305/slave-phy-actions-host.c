#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static unsigned phase,resp,finish;static uintptr_t savedsecond;
uint32_t opencfw_em9305_phy_defer_32caa0(uintptr_t p){if(!(*(uint32_t*)(p+636)&(1u<<21)))abort();phase=1;return 0;}
uint32_t opencfw_em9305_phy_defer_32cb48(uintptr_t p){(void)p;phase=1;return 0;}
uint32_t opencfw_em9305_phy_action_31592c(uintptr_t p){(void)p;if(phase!=1)abort();phase=2;return 66;}
uintptr_t opencfw_em9305_phy_record_325250(uintptr_t p){*(uint8_t*)(p+597)=0;return p+597;}
uint32_t opencfw_em9305_phy_response_3232dc(uintptr_t p,uint32_t e){(void)p;if(e!=0&&e!=12)abort();resp++;return 70;}
uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t p){(void)p;finish++;return 0;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t p,uint32_t e){(void)p;if(e!=110)abort();return 80;}
uint32_t opencfw_em9305_slave_phy_apply_32cb58(uintptr_t p){(void)p;return 81;}
uint32_t opencfw_em9305_phy_choose_316610(uintptr_t p,uint32_t f,uintptr_t a,uintptr_t c,uint32_t preferred){(void)p;if(f!=85||preferred||*(uint8_t*)a!=12||*(uint8_t*)c!=13||phase)abort();*(uint8_t*)a=7;*(uint8_t*)c=5;savedsecond=c;phase=1;return 0;}
uint32_t opencfw_em9305_phy_apply_327544(uintptr_t p,uint32_t a){(void)p;if(a!=7||phase!=1)abort();phase=2;return 0;}
uint32_t opencfw_em9305_phy_update_complete_32e220(uintptr_t p){(void)p;if(phase!=2)abort();*(volatile uint8_t*)savedsecond=9;phase=3;return 0;}
uint32_t opencfw_em9305_phy_response_packet_326758(uintptr_t p,uint32_t a,uint32_t c){(void)p;if(a!=7||c!=9||phase!=3)abort();phase=4;return 0;}
uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t p){(void)p;if(phase!=4)abort();phase=5;return 90;}
extern uint32_t opencfw_em9305_slave_phy_apply_32cb58(uintptr_t);
/* Native315a28..315a42 full pending action, same authenticated shared path. */
uint32_t opencfw_em9305_phy_action_315a28(uintptr_t record)
{
 uint32_t bits=*(volatile uint32_t *)(record+636u);
 *(volatile uint32_t *)(record+636u)=bits|(1u<<21u);
 (void)opencfw_em9305_phy_defer_32caa0(record);
 return opencfw_em9305_phy_action_31592c(record);
}
/* Native315c30..315c60, preserves incidental pointer/byte return. */
uint32_t opencfw_em9305_phy_action_315c30(uintptr_t record)
{
 (void)opencfw_em9305_phy_record_325250(record);
 uint32_t bits=*(volatile uint32_t *)(record+636u);
 uint32_t result=(uint32_t)(record+400u);
 if((bits&(1u<<21u))==0u)return result;
 uint32_t enabled=*(volatile uint8_t *)(record+400u);
 *(volatile uint32_t *)(record+640u)=0u;
 *(volatile uint32_t *)(record+636u)=bits&~(1u<<21u);
 if(enabled==0u)return result;
 result=*(volatile uint8_t *)(record+1u);
 if(result==3u)return result;
 return opencfw_em9305_phy_response_3232dc(record,0u);
}
/* Native315e70..315e7e and315e80 real branch tail. */
uint32_t opencfw_em9305_phy_action_315e70(uintptr_t record)
{
 (void)opencfw_em9305_phy_defer_32cb48(record);
 return opencfw_em9305_phy_action_31592c(record);
}
uint32_t opencfw_em9305_phy_action_315e80(uintptr_t record)
{ return opencfw_em9305_phy_action_315e70(record); }
/* Native315eac..315ed4 after timer completion reads global direction bytes. */
uint32_t opencfw_em9305_phy_action_315eac(uintptr_t record)
{
 (void)opencfw_em9305_phy_complete_32c818(record);
 uint32_t second=*(volatile uint8_t *)(uintptr_t)0x80281du;
 uint32_t first=*(volatile uint8_t *)(uintptr_t)0x80281cu;
 if((first|second)==0u)return opencfw_em9305_receive_terminate_325c08(record,110u);
 return opencfw_em9305_slave_phy_apply_32cb58(record);
}
uint32_t opencfw_em9305_phy_action_316354(uintptr_t record)
{ return opencfw_em9305_phy_response_3232dc(record,12u); }
/* Native31644c..3164a6 full slave preference/response/timer action. */
uint32_t opencfw_em9305_phy_action_31644c(uintptr_t record)
{
 volatile uint8_t first=*(volatile uint8_t *)(record+595u);
 volatile uint8_t second=*(volatile uint8_t *)(record+596u);
 uint32_t direction_a=*(volatile uint8_t *)(record+720u);
 uint32_t direction_b=*(volatile uint8_t *)(record+721u);
 uint32_t flags=*(volatile uint8_t *)(record+594u);
 (void)opencfw_em9305_phy_choose_316610(record,flags,(uintptr_t)&first,(uintptr_t)&second,direction_a&direction_b);
 uint32_t chosen_first=first;
 (void)opencfw_em9305_phy_apply_327544(record,chosen_first);
 (void)opencfw_em9305_phy_update_complete_32e220(record);
 uint32_t chosen_second=second;
 (void)opencfw_em9305_phy_response_packet_326758(record,chosen_first,chosen_second);
 return opencfw_em9305_phy_timer_start_32c7e4(record);
}

int main(void){
 if(mmap((void*)0x802000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uint8_t r[800];unsigned count=0;
 for(unsigned seed=0;seed<65536;seed++){
 memset(r,0,sizeof r);*(uint32_t*)(r+636)=seed;phase=0;if(opencfw_em9305_phy_action_315a28((uintptr_t)r)!=66||phase!=2||*(uint32_t*)(r+636)!=(seed|(1u<<21)))abort();
 phase=0;if(opencfw_em9305_phy_action_315e70((uintptr_t)r)!=66||phase!=2)abort();phase=0;if(opencfw_em9305_phy_action_315e80((uintptr_t)r)!=66||phase!=2)abort();
 *(volatile uint8_t*)0x80281c=(uint8_t)seed;*(volatile uint8_t*)0x80281d=(uint8_t)(seed>>8);finish=0;
 if(opencfw_em9305_phy_action_315eac((uintptr_t)r)!=(seed?81:80)||finish!=1)abort();
 count++;
 }
 for(unsigned value=0;value<256;value++)for(unsigned enabled=0;enabled<2;enabled++)for(unsigned pending=0;pending<2;pending++){
 memset(r,0,sizeof r);r[597]=9;r[1]=value;r[400]=enabled;*(uint32_t*)(r+636)=pending?(1u<<21):0;*(uint32_t*)(r+640)=77;resp=0;
 uint32_t expected=!pending||!enabled?(uint32_t)(uintptr_t)(r+400):value==3?3:70;
 if(opencfw_em9305_phy_action_315c30((uintptr_t)r)!=expected||r[597]||*(uint32_t*)(r+636)||*(uint32_t*)(r+640)!=(pending?0:77)||resp!=(pending&&enabled&&value!=3))abort();
 count++;
 }
 memset(r,0,sizeof r);r[594]=85;r[595]=12;r[596]=13;r[720]=32;r[721]=16;phase=0;if(opencfw_em9305_phy_action_31644c((uintptr_t)r)!=90||phase!=5)abort();resp=0;if(opencfw_em9305_phy_action_316354((uintptr_t)r)!=70||resp!=1)abort();
 printf("PASS %u slave action cases\n",count+2);return 0;
}
