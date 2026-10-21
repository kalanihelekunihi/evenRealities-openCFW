/* Independent6ac0; unclosed regular/dither dependencies explicit in ops. */
#include "mode.h"
uint32_t touch_switch_mode(uint32_t desired,uint8_t *c,const touch_mode_dependencies *ops){
 uint8_t *internal=*(uint8_t **)(c+8);uint32_t old=internal[85];if(old==desired)return 0;
 uint32_t status=(old<=2 || (old>=5 && old<=7))?0:1;internal[115]=0;if(status)return status;
 if(desired==0 || desired==1){}
 else if(desired==2 || desired==3){
  ops->ios(c);ops->shield(c);
  if(desired==2)*(uint32_t *)(*(uint8_t **)(c+4)+8)&=~0x30u;
  (*(uint8_t **)(c+28))[21]=0;ops->cmod(c);
  if(desired==2){const uint8_t *common=*(const uint8_t **)c,*ch=*(const uint8_t **)(common+8);volatile uint32_t *hw=*(volatile uint32_t **)ch;
   if(ops->configure(hw,*(const void **)(c+36),2,*(void **)(ch+4)))return 0x40;
   hw[0x108/4]=0;(void)hw[0x108/4];hw[0x120/4]=0x01110011u;(void)hw[0x120/4];}
 }else if(desired==5)touch_saturation_mode(c);
 else if(desired==6)touch_cpu_operating(c);
 else if(desired==7)ops->auto_dither(c);
 else return 1;
 internal[85]=(uint8_t)desired;return 0;
}
uint32_t touch_switch_saturation_dependency(uint32_t desired,uint8_t *context){return touch_switch_mode(desired,context,0);}
