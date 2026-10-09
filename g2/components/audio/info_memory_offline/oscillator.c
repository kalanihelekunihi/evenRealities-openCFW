#include "oscillator.h"
#define W(a) (*(volatile uint32_t *)(a))
#define B(a) (*(volatile uint8_t *)(a))
extern void stock_delay(uint32_t);
extern uint32_t stock_clock_request(uint32_t,uint32_t),stock_clock_release(uint32_t,uint32_t);
static uint32_t caps(void){return (B(0x200001e0)&63)|((W(0x200001e4)<<6)&960);}
uint32_t audio_oscillator_control(uint32_t action,const void *arguments){
 uint32_t external=0;
 if((uint8_t)action==0||(uint8_t)action==2||(uint8_t)action==3)external=arguments&&*(const uint8_t*)arguments==1;
 switch((uint8_t)action){
 case 0:W(0x40020120)=(W(0x40020120)&~31u)|(external?5:25);return 0;
 case 1:W(0x40020120)&=~3u;return 0;
 case 2:
  W(0x40020128)=(W(0x40020128)&0xc0007000)|caps()|0x0fff8c00;
  W(0x4002012c)=(W(0x4002012c)&~34u)|2;
  W(0x4002012c)|=1;W(0x4002012c)|=16;W(0x4002012c)|=8;
  stock_delay(5);W(0x4002012c)&=~16u;
  if(external)W(0x4002012c)=(W(0x4002012c)&0xfffffef6)|256;
  return 0;
 case 3:
  /* Stock drops old masked bits here, unlike public SDK OR-preservation. */
  W(0x40020128)=caps()|0x0fff8c00;
  W(0x4002012c)=(W(0x4002012c)&~34u)|34;
  W(0x4002012c)|=1;
  if(external)W(0x4002012c)=(W(0x4002012c)&0xfffffefe)|256;
  else W(0x4002012c)=(W(0x4002012c)&~40u)|8;
  return 0;
 case 4:
  W(0x40020128)=(W(0x40020128)&0xc0007000)|caps()|0x03118000;
  W(0x4002012c)=(W(0x4002012c)&0xfffffed4)|2;
  return 0;
 case 5:{
  uint32_t status=stock_clock_request(2,52);if(status)return status;
  uint32_t drive=arguments?*(const uint32_t*)arguments:4;
  if(arguments&&drive!=0&&(drive<3||drive>7))return 6;
  W(0x40020128)=(W(0x40020128)&~28672u)|((drive<<12)&28672);
  W(0x4002012c)|=128;return 0;
 }
 case 6:{
  W(0x40020128)|=28672;W(0x4002012c)&=~128u;
  uint32_t status=stock_clock_release(2,52);return status;
 }
 default:return 6;
 }
}
