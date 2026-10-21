/* Independent software watchdog7288 and completion polling6980. */
#include <stdint.h>
#include "watchdog.h"
uint32_t touch_scan_watchdog(uint32_t id,uint32_t slot,const uint8_t *context){
 (void)slot;const uint8_t *w=(const uint8_t *)(*(const uint32_t *)(context+12)+id*144u),*c=*(const uint8_t **)w,*i=*(const uint8_t **)(context+8);
 uint32_t divider=*(const uint16_t *)(c+14),clock=c[33]&3;
 uint32_t cycles=*(const uint16_t *)(i+48)+*(const uint16_t *)(i+50)+i[83];
 uint32_t epi=clock==2?*(const uint16_t *)(i+62)+*(const uint16_t *)(i+66):*(const uint16_t *)(i+64)+*(const uint16_t *)(i+68);
 cycles+=(divider>>2)*epi;cycles+=divider*(i[77]+*(const uint16_t *)(c+44));if(clock==2)cycles*=2;cycles*=w[132];return (cycles/46)*5;
}
uint32_t touch_scan_wait(uint32_t watchdog,const uint8_t *context){
 const uint8_t *common=*(const uint8_t **)context;volatile uint32_t *hw=**(volatile uint32_t *const *const *)(common+8);
 uint32_t count=(watchdog*(*(const uint32_t *)common/1000000u))/5u;
 while(!(hw[0x100/4]&0x100u)){if(!count)break;count--;}
 hw[0x100/4]=0xc1011111u;(void)hw[0x100/4];return count;
}
