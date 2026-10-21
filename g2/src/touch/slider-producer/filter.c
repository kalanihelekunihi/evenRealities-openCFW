/* Independent selected installed position filter4a2a, helpers49d4/49e6.
 * Original binary implements IIR bit1; other mask bits do not acquire invented
 * median/jitter behavior. History stride derives from configurationbyte+1. */
#include "slider.h"
void touch_position_filters(uint8_t *t,const uint8_t *w){
 uint32_t count=t[4],config=*(const uint32_t *)(w+112);uint8_t *history=*(uint8_t **)(w+60);
 if(count && count!=255){
  uint32_t old=history[4],existing=old==255?0:(count<old?count:old),stride=((config>>8)&255u)*8u;
  uint8_t *position=*(uint8_t **)t,*h=*(uint8_t **)history;
  for(uint32_t i=0;i<existing;i++,position+=8,h+=stride)if(config&2u){
   uint32_t coefficient=(config>>16)&255u;
   uint16_t x=(uint16_t)touch_position_iir(*(uint16_t *)position,*(uint16_t *)h,coefficient);
   uint16_t y=(uint16_t)touch_position_iir(*(uint16_t *)(position+2),*(uint16_t *)(h+2),coefficient);
   *(uint16_t *)h=*(uint16_t *)position=x;*(uint16_t *)(h+2)=*(uint16_t *)(position+2)=y;
  }
  for(uint32_t i=existing;i<count;i++,position+=8,h+=stride)if(config&2u)for(unsigned j=0;j<8;j++)h[j]=position[j];
 }
 history[4]=(uint8_t)count;
}
