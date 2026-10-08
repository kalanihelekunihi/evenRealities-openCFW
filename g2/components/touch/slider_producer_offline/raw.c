/* Independent actual CPU slider raw path5bc0->5938->4fee/5920.
 * Caller supplies acquired rawcounts; HW-IIR/commonmode/ADC not reconstructed. */
#include "slider.h"
uint32_t touch_sensor_baseline(uint8_t *w,uint8_t *s,const uint8_t *context){
 uint32_t raw=*(uint16_t *)s,baseline=*(uint16_t *)(s+2);
 if(raw>=baseline)s[7]=0;
 if(baseline>raw+*(uint16_t *)(w+28)){
  if(s[7]<*(uint16_t *)(w+12))s[7]++;
  else {*(uint16_t *)(s+2)=(uint16_t)raw;s[7]=s[8]=0;}
 }else {
  const uint8_t *common=*(const uint8_t **)context;
  if(common[40] || raw<=baseline+*(uint16_t *)(w+26)){
   uint32_t filtered=touch_position_iir(raw<<8,(baseline<<8)|s[8],w[34]);
   *(uint16_t *)(s+2)=(uint16_t)(filtered>>8);s[8]=(uint8_t)filtered;
  }
 }
 return 0;
}
void touch_sensor_difference(const uint8_t *w,uint8_t *s){
 uint32_t raw=*(uint16_t *)s,baseline=*(uint16_t *)(s+2);*(uint16_t *)(s+4)=raw>baseline+*(const uint16_t *)(w+26)?(uint16_t)(raw-baseline):0;
}
void touch_slider_clamp(uint32_t id,const uint8_t *context){
 uint8_t *w=(uint8_t *)(*(const uint32_t *)(context+12)+id*144u),*c=*(uint8_t **)w,*s=*(uint8_t **)(w+4);
 uint32_t limit=*(uint16_t *)(c+4),count=*(uint16_t *)(w+56);
 for(uint32_t i=0;i<count;i++,s+=10){if(w[122]==1 && i>=w[58])limit=*(uint16_t *)(c+6);if(*(uint16_t *)s>limit)*(uint16_t *)s=(uint16_t)limit;}
}
uint32_t touch_slider_raw(uint32_t id,const uint8_t *context){
 uint8_t *w=(uint8_t *)(*(const uint32_t *)(context+12)+id*144u),*c=*(uint8_t **)w,*s=*(uint8_t **)(w+4);uint32_t result=0;
 /* Actual slider's optional CPU filters are alloff; external history/integrity
  * pointer arithmetic in5938 has no dereference here. No invented rawfilter. */
 for(uint32_t i=0;i<*(uint16_t *)(w+56);i++,s+=10){result|=touch_sensor_baseline(c,s,context);touch_sensor_difference(c,s);}
 return result;
}
uint32_t touch_slider_widget(uint32_t id,uint8_t *context){
 if(id>2)return 1;
 uint8_t *w=(uint8_t *)(*(uint32_t *)(context+12)+id*144u);
 if(w[123]==7)return 1;
 uint8_t *runtime=(uint8_t *)(*(uint32_t *)(context+16)+id*60u);if((runtime[35]&6u)!=6u)return 8;
 touch_slider_clamp(id,context);uint32_t result=touch_slider_raw(id,context);
 if(w[122]!=1)return result|1u;
 /* Scoped to slider types2/3; original type6 proximity is a separate producer. */
 touch_slider_process(w);return result;
}
