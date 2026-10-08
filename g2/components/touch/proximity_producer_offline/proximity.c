/* Independent reconstruction of locked touch CPU routines. See analysis provenance.
 * Caller supplies acquired counts and coherent ARM32 widget/history pointers. */
#include <stdint.h>
#include "../slider_producer_offline/slider.h"
void touch_raw_filters(const uint8_t *widget,uint8_t *sensor,uint16_t *history,uint8_t *fraction){
 uint16_t flags=*(const uint16_t *)(widget+116),x=*(uint16_t *)sensor;
 if(flags&0x10){uint16_t a=x,b=history[0],c=history[1],t;if(a<=b){t=a;a=b;b=t;}if(a<=c)c=a;history[1]=history[0];history[0]=x;x=b>=c?b:c;history+=2;}
 if(flags&0x80){uint32_t y;if((flags&0x300)==0x200){y=touch_position_iir((uint32_t)x<<8,((uint32_t)*history<<8)|*fraction,*(const uint32_t *)(widget+36));*fraction=(uint8_t)y;x=(uint16_t)(y>>8);}else{x=(uint16_t)touch_position_iir(x,*history,*(const uint32_t *)(widget+36));}*history++=x;}
 if(flags&0x400){uint32_t total=x+history[0];if((flags&0x1800)==0x1000){total+=history[1]+history[2];history[2]=history[1];history[1]=history[0];history[0]=x;x=(uint16_t)(total>>2);}else{history[0]=x;x=(uint16_t)(total>>1);}}
 *(uint16_t *)sensor=x;
}
void touch_proximity_process(uint8_t *widget){
 uint8_t *ctx=*(uint8_t **)widget,*sensors=*(uint8_t **)(widget+4),*deb=*(uint8_t **)(widget+40);ctx[35]&=(uint8_t)~1u;
 for(uint32_t q=0;q<2u**(uint16_t *)(widget+56);q++){
  uint8_t *s=sensors+(q/2)*10,mask=(q&1)?2:1;uint32_t threshold=*(uint16_t *)(ctx+((q&1)?8:10)),h=*(uint16_t *)(ctx+30);
  threshold=(s[6]&mask)?threshold-h:threshold+h;
  if(deb[q])deb[q]--;
  if(*(uint16_t *)(s+4)<=threshold){deb[q]=ctx[32];s[6]&=(uint8_t)~mask;}
  if(!deb[q])s[6]|=mask;
  if(s[6]&mask)ctx[35]|=1;
 }
}
uint32_t touch_proximity_raw(uint32_t id,const uint8_t *context){
 uint8_t *w=(uint8_t *)(*(const uint32_t *)(context+12)+id*144u),*c=*(uint8_t **)w,*s=*(uint8_t **)(w+4);uint16_t *history=*(uint16_t **)(w+28);uint8_t *fraction=*(uint8_t **)(w+32);uint32_t result=0;uint16_t flags=*(uint16_t *)(w+116);
 /* Selected one-frequency firmware. Integrity leaf4db4 returnszero. */
 for(uint32_t i=0;i<*(uint16_t *)(w+56);i++,s+=10){touch_raw_filters(w,s,history,(flags&0x300)==0x200?fraction+i:0);result|=touch_sensor_baseline(c,s,context);touch_sensor_difference(c,s);history+=flags&15;}
 return result;
}
