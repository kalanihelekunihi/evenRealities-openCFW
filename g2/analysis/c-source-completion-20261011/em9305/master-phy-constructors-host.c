#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t packet[8];static uintptr_t base;static unsigned fail,sent,msg,term,set,clear,complete;static uint32_t ef,es;
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t n){if(n!=3)abort();return fail?0:(uint32_t)(uintptr_t)packet;}
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t r,uintptr_t p){if(r!=base||p!=(uintptr_t)packet)abort();sent++;return 66;}
uint32_t opencfw_em9305_radio_phy_project_3183d4(uint32_t v){return v&2?2:v&1?1:v&4;}
uint32_t opencfw_em9305_phy_update_message_326814(uintptr_t r,uint32_t a,uint32_t c){if(r!=base||a!=ef||c!=es)abort();msg++;return 0;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t r,uint32_t e){if(r!=base||e!=110||msg!=1)abort();term++;return 0;}
uint32_t opencfw_em9305_phy_apply_327544(uintptr_t r,uint32_t a){if(r!=base||a!=ef||msg!=1)abort();set++;return 0;}
uintptr_t opencfw_em9305_phy_record_325250(uintptr_t r){if(r!=base||msg!=1)abort();clear++;return r+597;}
uint32_t opencfw_em9305_phy_update_complete_32e220(uintptr_t r){if(r!=base||msg!=1||set+clear!=1)abort();complete++;return 77;}
/* Native32671c..32673c complete three-byte control packet. */
uint32_t opencfw_em9305_phy_control_packet_32671c(uintptr_t record,uint32_t opcode,uint32_t first,uint32_t second)
{
 uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(3u);
 if(packet==0u)return 0u;
 *(volatile uint8_t *)(packet+2u)=(uint8_t)second;
 *(volatile uint8_t *)(packet+1u)=(uint8_t)first;
 *(volatile uint8_t *)packet=(uint8_t)opcode;
 return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}
/* Native326740..326754 stores second before first then tail opcode22. */
uint32_t opencfw_em9305_phy_initiate_packet_326740(uintptr_t record,uint32_t first,uint32_t second)
{
 *(volatile uint8_t *)(record+721u)=(uint8_t)second;
 *(volatile uint8_t *)(record+720u)=(uint8_t)first;
 return opencfw_em9305_phy_control_packet_32671c(record,22u,first,second);
}
uint32_t opencfw_em9305_phy_response_packet_326758(uintptr_t record,uint32_t first,uint32_t second)
{ return opencfw_em9305_phy_control_packet_32671c(record,23u,first,second); }
extern uint32_t opencfw_em9305_phy_update_message_326814(uintptr_t,uint32_t,uint32_t);
/* Native326764..326810 full directional PHY negotiation/update parent. */
uint32_t opencfw_em9305_phy_update_packet_326764(uintptr_t record,uint32_t first,uint32_t second,uint32_t third,uint32_t fourth)
{
 uint32_t second_mask=third&second,first_mask=fourth&first;
 uint32_t common=opencfw_em9305_radio_phy_project_3183d4(fourth|third);
 if((fourth!=0u&&common==third&&common==fourth)||(*(volatile uint8_t *)(record+4u)&128u)!=0u){
  second_mask&=first_mask;first_mask=second_mask;
 }
 first=opencfw_em9305_radio_phy_project_3183d4(first_mask);
 second=opencfw_em9305_radio_phy_project_3183d4(second_mask);
 uint32_t old_first=*(volatile uint8_t *)(record+76u),old_second=*(volatile uint8_t *)(record+77u);
 uint32_t a=old_first-2u,b=old_second-2u;
 uint32_t mapped=a>=3u?1u:(0x00080402u>>(a*8u))&255u;
 if(first==mapped)first=0u;
 mapped=b>=3u?1u:(0x00080402u>>(b*8u))&255u;
 if(second==mapped)second=0u;
 (void)opencfw_em9305_phy_update_message_326814(record,first,second);
 if((first|second)==0u)(void)opencfw_em9305_receive_terminate_325c08(record,110u);
 if((uint8_t)first!=0u)(void)opencfw_em9305_phy_apply_327544(record,(uint8_t)first);
 else (void)opencfw_em9305_phy_record_325250(record);
 return opencfw_em9305_phy_update_complete_32e220(record);
}

int main(void){
 uint8_t r[800];base=(uintptr_t)r;unsigned count=0;
 for(unsigned a=0;a<256;a++)for(unsigned c=0;c<256;c++)for(fail=0;fail<2;fail++){
 memset(packet,0xa5,sizeof packet);sent=0;
 if(opencfw_em9305_phy_initiate_packet_326740(base,a,c)!=(fail?0:66)||r[720]!=a||r[721]!=c||sent!=!fail)abort();
 if(!fail&&(packet[0]!=22||packet[1]!=a||packet[2]!=c||packet[3]!=0xa5))abort();
 sent=0;if(opencfw_em9305_phy_response_packet_326758(base,a,c)!=(fail?0:66)||sent!=!fail)abort();if(!fail&&packet[0]!=23)abort();
 count++;
 }
 const unsigned priority[8]={0,1,2,2,4,1,2,2},mapping[5]={1,1,2,4,8};
 for(unsigned a=0;a<8;a++)for(unsigned c=0;c<8;c++)for(unsigned d=0;d<8;d++)for(unsigned e=0;e<8;e++)for(unsigned flag=0;flag<2;flag++)for(unsigned m1=0;m1<5;m1++)for(unsigned m2=0;m2<5;m2++){
 memset(r,0,sizeof r);r[4]=flag?128:0;r[76]=m1;r[77]=m2;unsigned fm=e&a,sm=d&c;unsigned joint=flag||(e&&priority[d|e]==d&&priority[d|e]==e);if(joint){fm&=sm;sm=fm;}
 ef=priority[fm];es=priority[sm];if(ef==mapping[m1])ef=0;if(es==mapping[m2])es=0;msg=term=set=clear=complete=0;
 if(opencfw_em9305_phy_update_packet_326764(base,a,c,d,e)!=77||msg!=1||term!=!(ef|es)||set!=!!ef||clear!=!ef||complete!=1)abort();
 count++;
 }
 printf("PASS %u PHY-packet constructor cases\n",count);return 0;
}
