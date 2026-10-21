#include "gpio.h"
#define W(a) (*(volatile uint32_t *)(a))
/* Configuration data, source corroborated and OTA bytes verified. Not executable blobs. */
static const uint32_t extended_drive[7]={0,0x3fe0,0x3ff,0x1ffbfe00,0x7c000,0,0};
static const uint32_t drive_capable[7]={0x8fc007e6,0xe3f3ffff,0x81ffffff,0xffffffff,0xf00fc07f,1,0x189};
extern uint32_t stock_save_irq(void);
uint32_t audio_gpio_pin_get(uint32_t pin,uint32_t *configuration){
 if(pin>=224)return 5;
 if(!configuration)return 6;
 *configuration=W(0x40010000+4*pin);return 0;
}
uint32_t audio_gpio_pin_set(uint32_t pin,uint32_t configuration){
 if(pin>=224)return 5;
 uint32_t index=pin>>5,mask=1u<<(pin&31);
 if(!(extended_drive[index]&mask)){
  if(((configuration>>10)&3)>=2&&!(drive_capable[index]&mask))return 7;
 }else{
  uint32_t pull=(configuration>>13)&7;
  if(pull!=0&&pull!=6&&pull!=1)return 7;
 }
 uint32_t interrupt_mask=stock_save_irq();
 W(0x40010400)=0x73;W(0x40010000+4*pin)=configuration;W(0x40010400)=0;
 __asm volatile("msr primask, %0"::"r"(interrupt_mask):"memory");
 return 0;
}
