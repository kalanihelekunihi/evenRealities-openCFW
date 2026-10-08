/* Independent stock6d74..702c; public6.10 is a semantic comparator.
 * No simulated analog filter or claimed physical IRQ/timing. */
#include "scan.h"
#include "../mode_offline/mode.h"
#include "../auto_dither_offline/dither.h"
static uint8_t *ptr(const uint8_t *c,unsigned n){return *(uint8_t *const *)(c+n);}
static uint16_t get16(const uint8_t *c,unsigned n){return *(const uint16_t *)(c+n);}
static void set16(uint8_t *c,unsigned n,uint16_t x){*(uint16_t *)(c+n)=x;}
uint32_t touch_start_lp_slots(uint32_t first,uint32_t count,uint8_t *c){
 uint32_t last=first+count-1u;if(!c || !count || count>8u || last>3u)return 1;
 uint8_t *common=ptr(c,4);*(uint32_t *)(common+8)&=~0x400u;
 if(*(uint32_t *)(common+8)&0x80u)return 0x40;
 uint32_t status=touch_switch_dither_dependency(2,c);if(status)return status;
 *(uint32_t *)(common+8)|=0x81u;uint8_t *i=ptr(c,8);
 volatile uint32_t *hw=*(volatile uint32_t **)ptr(ptr(c,0),8);i[115]=1;
 if(first!=get16(i,52) || last!=get16(i,54) || !(*(uint32_t *)(common+8)&0x20u)){
  set16(i,52,(uint16_t)first);set16(i,54,(uint16_t)last);set16(i,70,(uint16_t)count);i[113]=3;
  hw[0]|=0x30000u;hw[0]&=0xffff0fffu;hw[0x74/4]=0x80000100u;hw[0]&=0x7fffffffu;
  if(!(hw[0x180/4]&0x1000000u)){hw[0x144/4]=1;status=touch_wait_mrss(315,2,c);}else hw[0x144/4]=0x10000u;
  if(!status){
   const uint32_t *frame=(const uint32_t *)(ptr(c,44)+44u*first);
   for(uint32_t n=0;n<count*11u;n++)hw[0x2000/4+n]=frame[n];
   hw[0x2000/4+count*11u-1u]|=4u;hw[0x3c00/4]|=1u;
   if(!(hw[0x341c/4]&1u))status=4;
   if(hw[0x180/4]&0x1000000u)hw[0x144/4]=0x100u;
   if(!status){
    hw[0xc/4]&=0xfc00ffffu;hw[0]&=0xffff0fffu;hw[0x70/4]&=0xc000ffffu;
    if(get16(i,74)>=0x4000u)set16(i,74,0x3fffu);
    hw[0x70/4]|=(uint32_t)get16(i,74)<<16;hw[0x70/4]|=0x80000000u;
    /* Stock rereads the configured base through the context. */
    volatile uint32_t *base=*(volatile uint32_t **)ptr(ptr(c,0),8);base[0x70/4]&=0xffff0000u;
    base=*(volatile uint32_t **)ptr(ptr(c,0),8);base[0x70/4]|=*(uint32_t *)(ptr(c,8)+40);
    hw[8/4]=(hw[8/4]&0xfc00ffffu)|(((256u-((256u/count-11u)*count))<<16)&0x03ff0000u);
   }
  }
 }else if(hw[0x180/4]&1u){hw[0]&=0x7fffffffu;hw[0x144/4]=0x100u;(void)touch_wait_mrss(126,1,c);}
 *(uint32_t *)(common+8)&=~0x30u;*(uint32_t *)(common+8)|=0x20u;
 if(!status){void (*callback)(void *)=*(void (**)(void *))i;if(callback)callback(ptr(c,28));hw[0]&=0x7fffffffu;hw[0]|=0x80000000u;hw[0x128/4]=0x10u;(void)hw[0x128/4];hw[0x140/4]|=1u;}
 return status;
}
