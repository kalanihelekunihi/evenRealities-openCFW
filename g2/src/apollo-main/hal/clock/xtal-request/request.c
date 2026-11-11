#include "request.h"
#include "../clock/clock-manager-ownership/ownership.h"
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_stock_ram_200001c8[] __asm__("g2_stock_ram_200001c8");
extern unsigned char g2ref_g2_stock_ram_20004530[] __asm__("g2_stock_ram_20004530");
extern unsigned char g2ref_g2_stock_ram_20073f30[] __asm__("g2_stock_ram_20073f30");
extern unsigned char g2ref_g2_stock_ram_20074228[] __asm__("g2_stock_ram_20074228");
extern unsigned char g2ref_g2_stock_ram_20074f30[] __asm__("g2_stock_ram_20074f30");
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
#define STABILIZING B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x26u))
#define COUNTER_PTR W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x38u))
extern uint32_t stock_save_irq(void),stock_oscillator(uint32_t,const void *);
extern void stock_delay(uint32_t);
static void restore(uint32_t mask){__asm volatile("msr primask, %0"::"r"(mask):"memory");}
/* Stock 0x4C45E2 (am_hal_clkmgr_board_info_set) */
uint32_t audio_clock_board_set(const void *info){if(!info)return 6;for(unsigned i=0;i<20;i++)B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x4u)+i)=((const uint8_t*)info)[i];return 0;}
void audio_clock_counter_wait(volatile uint8_t *flag,volatile uint32_t *counter){while(*counter){if(!*flag)break;stock_delay(10);--*counter;}}
void audio_xtal_wait(volatile uint32_t *counter){if(STABILIZING){audio_clock_counter_wait((volatile uint8_t*)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x26u),counter);uint32_t mask=stock_save_irq();STABILIZING=0;COUNTER_PTR=0;restore(mask);}}
uint32_t audio_xtal_request(uint32_t user){
 user=(uint8_t)user;uint32_t status=0;volatile uint32_t counter=150;
 if(!W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x8u)))return 7;
 if(audio_clock_user(2,user)){
  uint32_t mask=stock_save_irq();if(STABILIZING)counter=*(volatile uint32_t*)COUNTER_PTR;
  COUNTER_PTR=(uint32_t)&counter;restore(mask);audio_xtal_wait(&counter);return 0;
 }
 uint32_t mask=stock_save_irq();uint8_t mode;audio_xtal_status(&mode);
 if(STABILIZING)counter=*(volatile uint32_t*)COUNTER_PTR;
 if(mode==0){
  if(B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x4u))==1){uint8_t yes=1;stock_oscillator(3,&yes);}
  else {stock_oscillator(2,0);if(!STABILIZING)STABILIZING=1;}
 }else if(mode==2&&B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x4u))==0)status=3;
 else if(mode==1&&B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x4u))==1)status=3;
 if(!status)audio_clock_set(2,user,1);
 if(STABILIZING)COUNTER_PTR=(uint32_t)&counter;
 restore(mask);audio_xtal_wait(&counter);return status;
}
extern uint32_t stock_hfrc_target(uint32_t,uint32_t,uint32_t *),stock_hfrc_apply(uint32_t),stock_hfrc_disable(void);
/* Stock 0x4C38A0 (am_hal_clkmgr HFRC config) */
uint32_t audio_hfrc_config(uint32_t requested,const uint32_t *config){
 uint32_t status=0;uint32_t generated[3]={0x0025b800,0,0};
 if(requested!=0&&requested!=48000000)return 5;
 if(requested){
  if(!W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x10u)))return 7;
  if(!config){uint32_t target;status=stock_hfrc_target(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200001c8+0x10u)),requested,&target);generated[0]=(generated[0]&~0x000fff00u)|((target<<8)&0x000fff00u);config=generated;}
 }
 if(!status){
  uint32_t mask=stock_save_irq();
  if(audio_clock_count(4)){
   status=3;
   if((requested==0||requested==48000000)&&(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x28u))==0||W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x28u))==48000000)){
    if(!requested)status=stock_hfrc_disable();
    else {status=stock_hfrc_apply(config[0]);if(status)stock_hfrc_apply(W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30)));}
   }
  }else if(requested!=W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x28u))){stock_hfrc_disable();B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074f30+0x27u))=0;W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x3cu))=0;}
  if(!status){if(requested)for(unsigned i=0;i<3;i++)W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20073f30)+4*i)=config[i];W(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074228+0x28u))=requested;B(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20004530+0x6u))=1;}
  restore(mask);
 }
 return status;
}
