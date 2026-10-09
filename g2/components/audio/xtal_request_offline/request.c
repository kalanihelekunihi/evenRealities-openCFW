#include "request.h"
#include "../clock_manager_ownership_offline/ownership.h"
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
#define STABILIZING B(0x20074f56)
#define COUNTER_PTR W(0x20074260)
extern uint32_t stock_save_irq(void),stock_oscillator(uint32_t,const void *);
extern void stock_delay(uint32_t);
static void restore(uint32_t mask){__asm volatile("msr primask, %0"::"r"(mask):"memory");}
uint32_t audio_clock_board_set(const void *info){if(!info)return 6;for(unsigned i=0;i<20;i++)B(0x200001cc+i)=((const uint8_t*)info)[i];return 0;}
void audio_clock_counter_wait(volatile uint8_t *flag,volatile uint32_t *counter){while(*counter){if(!*flag)break;stock_delay(10);--*counter;}}
void audio_xtal_wait(volatile uint32_t *counter){if(STABILIZING){audio_clock_counter_wait((volatile uint8_t*)0x20074f56,counter);uint32_t mask=stock_save_irq();STABILIZING=0;COUNTER_PTR=0;restore(mask);}}
uint32_t audio_xtal_request(uint32_t user){
 user=(uint8_t)user;uint32_t status=0;volatile uint32_t counter=150;
 if(!W(0x200001d0))return 7;
 if(audio_clock_user(2,user)){
  uint32_t mask=stock_save_irq();if(STABILIZING)counter=*(volatile uint32_t*)COUNTER_PTR;
  COUNTER_PTR=(uint32_t)&counter;restore(mask);audio_xtal_wait(&counter);return 0;
 }
 uint32_t mask=stock_save_irq();uint8_t mode;audio_xtal_status(&mode);
 if(STABILIZING)counter=*(volatile uint32_t*)COUNTER_PTR;
 if(mode==0){
  if(B(0x200001cc)==1){uint8_t yes=1;stock_oscillator(3,&yes);}
  else {stock_oscillator(2,0);if(!STABILIZING)STABILIZING=1;}
 }else if(mode==2&&B(0x200001cc)==0)status=3;
 else if(mode==1&&B(0x200001cc)==1)status=3;
 if(!status)audio_clock_set(2,user,1);
 if(STABILIZING)COUNTER_PTR=(uint32_t)&counter;
 restore(mask);audio_xtal_wait(&counter);return status;
}
extern uint32_t stock_hfrc_target(uint32_t,uint32_t,uint32_t *),stock_hfrc_apply(uint32_t),stock_hfrc_disable(void);
uint32_t audio_hfrc_config(uint32_t requested,const uint32_t *config){
 uint32_t status=0;uint32_t generated[3]={0x0025b800,0,0};
 if(requested!=0&&requested!=48000000)return 5;
 if(requested){
  if(!W(0x200001d8))return 7;
  if(!config){uint32_t target;status=stock_hfrc_target(W(0x200001d8),requested,&target);generated[0]=(generated[0]&~0x000fff00u)|((target<<8)&0x000fff00u);config=generated;}
 }
 if(!status){
  uint32_t mask=stock_save_irq();
  if(audio_clock_count(4)){
   status=3;
   if((requested==0||requested==48000000)&&(W(0x20074250)==0||W(0x20074250)==48000000)){
    if(!requested)status=stock_hfrc_disable();
    else {status=stock_hfrc_apply(config[0]);if(status)stock_hfrc_apply(W(0x20073f30));}
   }
  }else if(requested!=W(0x20074250)){stock_hfrc_disable();B(0x20074f57)=0;W(0x20074264)=0;}
  if(!status){if(requested)for(unsigned i=0;i<3;i++)W(0x20073f30+4*i)=config[i];W(0x20074250)=requested;B(0x20004536)=1;}
  restore(mask);
 }
 return status;
}
