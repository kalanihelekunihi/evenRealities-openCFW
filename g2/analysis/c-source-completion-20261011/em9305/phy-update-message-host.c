#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint8_t record[900],packet[8],cfg1[100],cfg2[100];static uint32_t nodes[3];static unsigned locks,unlocks,timingcalls,caps,term,fail;static uint32_t initialtiming;
uint32_t opencfw_em9305_wsf_critical_enter(void){locks++;return 0;}
uint32_t opencfw_em9305_wsf_critical_exit(void){unlocks++;return 0;}
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t n){if(n!=5)abort();return fail?0:(uint32_t)(uintptr_t)packet;}
uint32_t opencfw_em9305_config_link_mpywhul(uint32_t a,uint32_t c){return a*(uint16_t)c;}
uint32_t opencfw_em9305_native_mpyw_309f62(uint32_t a,uint32_t c){return (uint32_t)((int32_t)(int16_t)a*(int32_t)(int16_t)c);}
uint32_t opencfw_em9305_ll_event_mode_32d4b0(uintptr_t p){if(p!=(uintptr_t)record)abort();caps++;return caps==1?11:13;}
uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t a,uint32_t c){timingcalls++;if(timingcalls==1){if(a!=6||c!=11)abort();*(uint32_t*)(record+360)=(uint32_t)(uintptr_t)&nodes[2];*(volatile uint32_t*)0x805cac=(uint32_t)(uintptr_t)cfg2;return initialtiming;}if(a!=5||c!=13||timingcalls!=2)abort();return 3;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t p,uint32_t e){if(p!=(uintptr_t)record||e!=110||*(uint16_t*)(record+724))abort();term++;return 0;}
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t p,uintptr_t q){if(p!=(uintptr_t)record||q!=(uintptr_t)packet)abort();return 99;}
/* Native314114..314130 full locked linked-queue count, 16-bit return. */
uint32_t opencfw_em9305_phy_queue_count_314114(uintptr_t queue)
{
 (void)opencfw_em9305_wsf_critical_enter();
 uintptr_t node=*(volatile uint32_t *)queue;uint32_t count=0u;
 while(node!=0u){node=*(volatile uint32_t *)node;++count;}
 (void)opencfw_em9305_wsf_critical_exit();
 return (uint16_t)count;
}
/* Native326814..3268c8, full update instant calculation and five-byte packet.
 * Native32684a/32686c are MPYWHUL; exact assembly identity is recorded. */
uint32_t opencfw_em9305_phy_update_message_326814(uintptr_t record,uint32_t first,uint32_t second)
{
 uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(5u);
 if(packet==0u)return 0u;
 uintptr_t queue=record+360u;
 *(volatile uint8_t *)(record+723u)=(uint8_t)second;
 *(volatile uint8_t *)(record+722u)=(uint8_t)first;
 uint32_t count=opencfw_em9305_phy_queue_count_314114(queue);
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t unit=*(volatile uint16_t *)(config+76u);
 uint32_t scaled=opencfw_em9305_config_link_mpywhul(count,unit);
 uint32_t capacity=opencfw_em9305_ll_event_mode_32d4b0(record);
 uint32_t timing=opencfw_em9305_radio_record_timing_30c40c(scaled,capacity);
 if(timing<6u)timing=6u;
 else{
  count=opencfw_em9305_phy_queue_count_314114(queue);
  config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  unit=*(volatile uint16_t *)(config+76u);
  scaled=opencfw_em9305_config_link_mpywhul(count,unit);
  capacity=opencfw_em9305_ll_event_mode_32d4b0(record);
  timing=opencfw_em9305_radio_record_timing_30c40c(scaled,capacity);
 }
 if((first|second)!=0u){
  uint32_t latency=*(volatile uint16_t *)(record+260u);
  uint32_t interval=*(volatile uint16_t *)(record+846u);
  uint32_t product=timing*(latency+1u);
  uint32_t anchor=*(volatile uint16_t *)(record+262u);
  product=opencfw_em9305_native_mpyw_309f62(product,interval);
  *(volatile uint16_t *)(record+724u)=(uint16_t)(product+anchor);
 }else{
  *(volatile uint16_t *)(record+724u)=0u;
  (void)opencfw_em9305_receive_terminate_325c08(record,110u);
 }
 *(volatile uint8_t *)(packet+2u)=(uint8_t)second;
 *(volatile uint8_t *)(packet+1u)=(uint8_t)first;
 *(volatile uint8_t *)packet=24u;
 *(volatile uint8_t *)(packet+3u)=*(volatile uint8_t *)(record+724u);
 *(volatile uint8_t *)(packet+4u)=*(volatile uint8_t *)(record+725u);
 return opencfw_em9305_phy_packet_send_32d32c(record,packet);
}

int main(void){
 if(mmap((void*)0x805000,4096,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 unsigned count=0;*(uint16_t*)(cfg1+76)=2;*(uint16_t*)(cfg2+76)=5;
 for(initialtiming=0;initialtiming<65536;initialtiming++)for(unsigned nonzero=0;nonzero<2;nonzero++){
 memset(record,0xa5,sizeof record);memset(packet,0xa5,sizeof packet);nodes[0]=(uint32_t)(uintptr_t)&nodes[1];nodes[1]=(uint32_t)(uintptr_t)&nodes[2];nodes[2]=0;*(uint32_t*)(record+360)=(uint32_t)(uintptr_t)nodes;*(volatile uint32_t*)0x805cac=(uint32_t)(uintptr_t)cfg1;*(uint16_t*)(record+260)=initialtiming;*(uint16_t*)(record+262)=123;*(uint16_t*)(record+846)=0xfffe;locks=unlocks=timingcalls=caps=term=0;fail=0;
 if(opencfw_em9305_phy_update_message_326814((uintptr_t)record,nonzero,0)!=99)abort();
 unsigned tc=initialtiming<6?1:2;unsigned timing=tc==1?6:3;uint16_t instant=nonzero?(uint16_t)((int32_t)(int16_t)(timing*(initialtiming+1))*(-2)+123):0;
 if(locks!=tc||unlocks!=tc||timingcalls!=tc||caps!=tc||term!=!nonzero||record[722]!=nonzero||record[723]!=0||*(uint16_t*)(record+724)!=instant||packet[0]!=24||packet[1]!=nonzero||packet[2]||packet[3]!=(uint8_t)instant||packet[4]!=(uint8_t)(instant>>8)||packet[5]!=0xa5)abort();
 count++;
 }
 fail=1;locks=0;record[722]=37;if(opencfw_em9305_phy_update_message_326814((uintptr_t)record,1,2)||locks||record[722]!=37)abort();
 printf("PASS %u update instant/fresh count cases\n",count+1);return 0;
}
