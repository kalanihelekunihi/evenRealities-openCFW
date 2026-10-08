/* Independent6bd4..6d6a; native closed slot loader/mode dependencies, offline. */
#include "timer.h"
#include "../auto_dither_offline/dither.h"
#include "../scan_isr_offline/isr.h"
static uint8_t *ptr(const uint8_t *c,unsigned n){return *(uint8_t *const *)(c+n);}
static uint16_t u16(const uint8_t *c,unsigned n){return *(const uint16_t *)(c+n);}
static void set16(uint8_t *c,unsigned n,uint16_t v){*(uint16_t *)(c+n)=v;}
uint32_t touch_start_active_slots(uint32_t first,uint32_t count,uint8_t *c){
 uint32_t last=first+count-1u;if(!c || !count || first>4 || last>4)return 1;
 uint8_t *common=ptr(c,4);if(*(uint32_t *)(common+8)&0x80u)return 0x40;
 *(uint32_t *)(common+8)|=0x81u;uint8_t *i=ptr(c,8);volatile uint32_t *hw=*(volatile uint32_t **)ptr(ptr(c,0),8);i[115]=0;
 if((i[85]!=2 && i[85]!=4) || u16(i,72)!=first || u16(i,70)!=count || count>21 || (*(uint32_t *)(common+8)&0x2000u) || !(*(uint32_t *)(common+8)&0x10u)){
  uint32_t status=touch_switch_dither_dependency(2,c);if(status)return status;
  *(uint32_t *)(common+8)&=~0x30u;*(uint32_t *)(common+8)|=0x10u;i[113]=3;
  hw[0]|=0x30000u;hw[0]&=0xffff0fffu;hw[0x70/4]&=0xc000ffffu;hw[0x70/4]|=0x10000u;
  volatile uint32_t *base=*(volatile uint32_t **)ptr(ptr(c,0),8);base[0x70/4]&=0xffff0000u;
  base=*(volatile uint32_t **)ptr(ptr(c,0),8);base[0x70/4]|=*(uint32_t *)(ptr(c,8)+32);
  hw[0x74/4]=0x80000000u|i[118];hw[0x128/4]=0x10000u;(void)hw[0x128/4];
  set16(i,72,(uint16_t)first);set16(i,52,(uint16_t)first);set16(i,54,(uint16_t)last);i[97]=1;if(count<=21)i[115]=1;
  touch_scan_slots(first,count,c);return 0;
 }
 i[115]=1;set16(i,52,(uint16_t)first);void (*callback)(void *)=*(void (**)(void *))ptr(c,8);if(callback)callback(ptr(c,28));
 hw[0]&=0x7fffffffu;hw[0]|=0x80000000u;hw[0x140/4]=1;return 0;
}
