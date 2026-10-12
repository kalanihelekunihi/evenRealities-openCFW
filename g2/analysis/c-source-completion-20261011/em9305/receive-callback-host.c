#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned scenario,n;static char trace[64];static uintptr_t source=0x840000,input=0x850000;static unsigned status,gate_expected;
static void mark(char c){trace[n++]=c;}
static uint32_t pending_callback(uint32_t id){assert(id==3&&*(uint8_t *)(source+628)==0);mark('I');return 0;}
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t p,uint32_t reason){assert(p==source);assert(reason==(scenario==10?72:110));mark('T');return 0;}
uint32_t opencfw_em9305_receive_packet_release_3253bc(uintptr_t p){assert(p==input);mark('L');return 0x71;}
uint32_t opencfw_em9305_auxiliary_signal_304394(void){mark('S');return 0;}
uint32_t opencfw_em9305_receive_state_324ea4(uintptr_t p){assert(p==source);mark('D');return 0x25;}
uint32_t opencfw_em9305_receive_gate_324f68(uintptr_t p){assert(p==source);mark('G');return scenario==15?6:0;}
uint32_t opencfw_em9305_receive_check_319838(uintptr_t p,uint32_t value,uint32_t size){assert(p==source&&value==77&&size==88);mark('C');return scenario==12||scenario==15?2:0;}
uint32_t opencfw_em9305_receive_command_31b7c8(uintptr_t p){assert(p==source);mark('O');return scenario==13?1:0;}
uint32_t opencfw_em9305_radio_prepare_32780c(uintptr_t p,uint32_t st,uint32_t gate){assert(p==source&&st==status&&gate==gate_expected);mark('P');return scenario==14?0:11;}
uint32_t opencfw_em9305_auxiliary_start_303f50(uintptr_t ignored){assert(ignored==11);mark('A');return scenario==16?1:0;}
uint32_t opencfw_em9305_receive_finish_324fb0(uintptr_t p){assert(p==source);mark('F');
if(scenario==17){*(uint8_t *)(source+344)=2;}return 0;}
uint32_t opencfw_em9305_receive_packet_finish_3253c4(uintptr_t p,uintptr_t packet,uint32_t data,uint32_t success){assert(p==source&&packet==input&&data==(status==4?0:0x25));assert(success==(scenario==12||scenario==13||scenario==14||scenario==15||scenario==16?0:1));mark('N');return 0x72;}
uint32_t opencfw_em9305_short_header_decode_32dedc(uintptr_t output,uintptr_t input)
{
 uint32_t b1=*(volatile uint8_t *)(input+1u);
 uint32_t b0=*(volatile uint8_t *)input;
 uint32_t packed=b0+(b1<<8),low=(uint8_t)packed;
 *(volatile uint8_t *)(output+5u)=(uint8_t)b1;
 *(volatile uint8_t *)output=(uint8_t)(packed&3u);
 uint32_t flag=(low>>5)&1u;
 *(volatile uint8_t *)(output+4u)=(uint8_t)flag;
 *(volatile uint8_t *)(output+3u)=(uint8_t)((low>>4)&1u);
 *(volatile uint8_t *)(output+2u)=(uint8_t)((low>>3)&1u);
 *(volatile uint8_t *)(output+1u)=(uint8_t)((low>>2)&1u);
 if(flag!=0u){
  uint32_t extra=*(volatile uint8_t *)(input+2u);
  *(volatile uint8_t *)(output+6u)=(uint8_t)(extra>>6);
  *(volatile uint8_t *)(output+7u)=(uint8_t)(extra&31u);
  return 3u;
 }
 return 2u;
}
/* Authenticated receive callback31e620..31e7c8. R1 is the received packet,
 * R2 is the fullword status. The decoder output address is captured in its
 * BL.D delay slot, before its returned header length indexes the input. */
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_receive_state_324ea4(uintptr_t);
extern uint32_t opencfw_em9305_receive_gate_324f68(uintptr_t);
extern uint32_t opencfw_em9305_receive_check_319838(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_receive_command_31b7c8(uintptr_t);
extern uint32_t opencfw_em9305_receive_packet_release_3253bc(uintptr_t);
extern uint32_t opencfw_em9305_receive_finish_324fb0(uintptr_t);
extern uint32_t opencfw_em9305_receive_packet_finish_3253c4(uintptr_t,uintptr_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_radio_cb_31e620(uintptr_t event,uintptr_t input,uint32_t status)
{
 uintptr_t source=*(volatile uint32_t *)(event+36u);
 uint32_t pending=*(volatile uint8_t *)(source+628u);
 *(volatile uint8_t *)(source+269u)=(uint8_t)status;
 if(pending!=0u){
  uint32_t mode=*(volatile uint8_t *)(source+635u);
  *(volatile uint8_t *)(source+628u)=0u;
  if(mode==1u){
   uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x801314u;
   if(callback!=0u){
    uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
    uint32_t delta=(uint32_t)(source-base),index;
    index=delta/912u;
    (void)((uint32_t (*)(uint32_t))callback)((uint8_t)index);
   }
  }
  (void)opencfw_em9305_receive_terminate_325c08(source,110u);
 }
 if(status==2u)return opencfw_em9305_receive_packet_release_3253bc(input);
 if(*(volatile uint8_t *)(source+1u)==3u){
  if(*(volatile uint8_t *)(source+629u)!=0u){
   if(*(volatile uint8_t *)(source+630u)!=0u)goto discard;
  }else if(*(volatile uint8_t *)(source+620u)==0u||*(volatile uint32_t *)(source+360u)==0u)goto discard;
 }
 uint32_t data=0u,gate,success;
 if(status==1u||status==3u)goto discard;
 if(status==4u){
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x802a34u;
  count+=1u;
  *(volatile uint8_t *)(uintptr_t)0x802a34u=(uint8_t)count;
  if((uint8_t)count>=2u)goto discard;
  gate=(*(volatile uint8_t *)(source+4u)&8u)==0u;
  goto prepare;
 }
 if(status==0u){
  *(volatile uint8_t *)(uintptr_t)0x802a34u=0u;
  *(volatile uint8_t *)(uintptr_t)0x802a38u=1u;
 }
 uintptr_t decoded=source+344u;
 uint32_t header=opencfw_em9305_short_header_decode_32dedc(decoded,input);
 uint32_t subtype=*(volatile uint8_t *)(input+header);
 if(status==6u){
  uint32_t b1=*(volatile uint8_t *)(source+346u);
  uint32_t b0=*(volatile uint8_t *)(source+337u);
  if(((b0^b1)&1u)==0u){
   (void)opencfw_em9305_receive_terminate_325c08(source,72u);
   goto discard;
  }
 }
 if(*(volatile uint8_t *)(source+349u)!=0u){
  uint32_t count=*(volatile uint16_t *)(uintptr_t)0x802a44u;
  *(volatile uint16_t *)(uintptr_t)0x802a44u=(uint16_t)(count+1u);
 }
 data=opencfw_em9305_receive_state_324ea4(source);
 gate=opencfw_em9305_receive_gate_324f68(source);
 uint32_t length=*(volatile uint16_t *)(source+592u);
 uint32_t value=*(volatile uint32_t *)(event+8u);
 uint32_t check=opencfw_em9305_receive_check_319838(source,value,length);
 if(check!=0u)(void)opencfw_em9305_auxiliary_signal_304394();
 if((((status!=0u)|check)&1u)==0u&&*(volatile uint8_t *)decoded==3u&&subtype==5u&&*(volatile uint8_t *)(source+620u)==1u&&*(volatile uint8_t *)(source+635u)==19u){
  if(opencfw_em9305_receive_command_31b7c8(source)!=0u)goto failed;
 }
 if(check!=0u){success=0u;goto finish;}
 if(gate!=0u)gate=1u;
 else gate=(*(volatile uint8_t *)(source+4u)&8u)==0u;
prepare:
 success=1u;
 uint32_t prepared=opencfw_em9305_radio_prepare_32780c(source,status,1u&~gate);
 if(prepared==0u)goto failed;
 if(opencfw_em9305_auxiliary_start_303f50(prepared)!=0u)success=0u;
 goto finish;
failed:
 (void)opencfw_em9305_auxiliary_signal_304394();
 success=0u;
finish:
 {
  uint32_t count=*(volatile uint16_t *)(uintptr_t)0x802a3cu;
  *(volatile uint16_t *)(uintptr_t)0x802a3cu=(uint16_t)(count+(gate&1u));
 }
 (void)opencfw_em9305_receive_finish_324fb0(source);
 if(*(volatile uint8_t *)(source+344u)==3u)*(volatile uint8_t *)(source+630u)=0u;
 return opencfw_em9305_receive_packet_finish_3253c4(source,input,data,success);
discard:
 (void)opencfw_em9305_auxiliary_signal_304394();
 return opencfw_em9305_receive_packet_release_3253bc(input);
}


int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(scenario=0;scenario<18;scenario++){memset((void *)0x800000,0,0x100000);n=0;memset(trace,0,sizeof(trace));*(uint32_t *)(0x830000+36)=source;*(uint32_t *)(0x830000+8)=77;*(uint16_t *)(source+592)=88;*(uint8_t *)(source+620)=1;*(uint8_t *)(source+635)=19;*(uint8_t *)(source+4)=8;*(uint8_t *)(source+630)=1;*(uint8_t *)input=3;*(uint8_t *)(input+2)=5;*(uint16_t *)0x802a3c=65535;status=scenario==0?2:scenario==1?1:scenario==2?3:scenario==3||scenario==4||scenario==5?4:scenario==10||scenario==11?6:0;gate_expected=1;
if(scenario==3)*(uint8_t *)0x802a34=1;
if(scenario==4)*(uint8_t *)0x802a34=255;
if(scenario==6||scenario==7||scenario==8){*(uint8_t *)(source+1)=3;*(uint8_t *)(source+629)=scenario==6?1:0;
if(scenario==7)*(uint8_t *)(source+620)=0;}
if(scenario==9){*(uint8_t *)(source+628)=1;*(uint8_t *)(source+635)=1;*(uint32_t *)0x801314=(uint32_t)(uintptr_t)pending_callback;*(uint32_t *)0x805c70=source-912*3;}
if(scenario==11)*(uint8_t *)(source+337)=1;
if(scenario>=12&&scenario<=17)*(uint8_t *)(input+1)=1;
if(scenario==15)*(uint8_t *)(source+4)=0;
unsigned result=opencfw_em9305_radio_cb_31e620(0x830000,input,status);const char *expected=scenario==0?"L":scenario==1||scenario==2||scenario==3||scenario==6||scenario==7||scenario==8?"SL":scenario==4||scenario==5?"PAFN":scenario==9?"ITDGCPAFN":scenario==10?"TSL":scenario==11?"DGCPAFN":scenario==12||scenario==15?"DGCSOFN":scenario==13?"DGCOSFN":scenario==14?"DGCOPSFN":scenario==16?"DGCOPAFN":"DGCOPAFN";if(strcmp(trace,expected)!=0){fprintf(stderr,"scenario=%u trace=%s expected=%s\n",scenario,trace,expected);}assert(strcmp(trace,expected)==0);assert(result==(strchr(expected,'L')?0x71:0x72));assert(*(uint8_t *)(source+269)==status);if(strchr(expected,'N')){assert(*(uint16_t *)0x802a3c==65535);if(status!=4)assert(*(uint8_t *)(source+630)==(scenario==17?1:0));}
if(scenario>=12)assert(*(uint16_t *)0x802a44==1);
if(scenario==4){assert(*(uint8_t *)0x802a34==0);}cases++;}printf("PASS %u\n",cases);}
