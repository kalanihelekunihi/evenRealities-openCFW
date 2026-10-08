/* Independent stock71c8/7064/69c4 composition. Synthetic offline only.
 * External end-of-init callback is dispatched if present; tests use null.
 * ISR callback address is stock metadata, not a native ISR implementation.
 * Saturated measurement scope excludes widgettype7 alternate ABI. */
#include "prepare.h"
#include "../clock_selection_offline/clock.h"
#include "../base_frame_offline/base.h"
#include "../all_slot_offline/slots.h"
#include "../auto_dither_offline/dither.h"
#include "../scan_frame_offline/frame.h"
#include "../scan_watchdog_offline/watchdog.h"
#include "../saturated_scan_offline/scan.h"
#include "../max_raw_offline/max_raw.h"
extern uint32_t Cy_MSCLP_Configure(volatile uint32_t *,const void *,uint32_t,void *);
static uint8_t *ptr(const uint8_t *c,unsigned off){return *(uint8_t *const *)(c+off);}
static uint16_t u16(const uint8_t *c,unsigned off){return *(const uint16_t *)(c+off);}
static volatile uint32_t *hardware(const uint8_t *c){return *(volatile uint32_t **)ptr(ptr(c,0),8);}
static uint32_t enabled(uint32_t id,const uint8_t *c){return id<3 && ((ptr(c,16)[id*60+35]&6u)==6u);}
uint32_t touch_dither_measure(const uint32_t *frames,const uint8_t *w,uint32_t stride,uint32_t *max,uint8_t *c){
 uint32_t status=0;*max=0;volatile uint32_t *hw=hardware(c);
 for(unsigned s=0;s<u16(w,56);s++,frames+=stride){
  uint32_t temp[6];for(unsigned j=0;j<6;j++)temp[j]=frames[j];
  temp[5]=(temp[5]&0xc000ffcau)|0x00ff0004u;temp[3]=0x00ff0063u;temp[4]=0x00400064u;
  touch_start_scan_frame(temp,c);
  if(touch_scan_wait(1753,c)){uint32_t value=hw[0x3200/4]&65535u;if(value>*max)*max=value;}else status=4;
 }
 return status;
}
uint32_t touch_dither_scale(uint8_t *c){
 uint32_t status=touch_switch_dither_dependency(7,c);uint8_t *w=ptr(c,12);
 for(unsigned id=0;id<3;id++,w+=144){
  if(!enabled(id,c) || w[138]!=2 || w[122]==10)continue;
  uint32_t maximum=0;const uint32_t *frame;uint32_t stride;
  if(w[123]==7){stride=11;frame=(const uint32_t *)(ptr(c,44)+u16(w,124)*44u+20u);}
  else{stride=7;frame=(const uint32_t *)(ptr(c,40)+u16(w,128)*28u);}
  status|=touch_dither_measure(frame,w,stride,&maximum,c);
  ptr(c,16)[id*60+51]=(uint8_t)(maximum<=32?6:maximum<=55?5:maximum<=111?4:maximum<338?3:maximum<564?2:maximum<1128?1:0);
 }
 touch_generate_all_slots(0,c);touch_generate_all_slots(1,c);
 const uint8_t *ch=ptr(ptr(c,0),8);if(Cy_MSCLP_Configure(hardware(c),ptr(c,36),2,ptr(ch,4)))return 0x40u;
 return status;
}
uint32_t touch_prepare_scan_fields(uint8_t *c){
 uint32_t status=touch_initialize_source_clock(c);uint8_t *i=ptr(c,8),*common=ptr(c,0);
 ptr(c,28)[21]=0;i[82]=0;i[116]=common[41];i[117]=common[42];i[76]=common[43];
 status|=touch_generate_base(c);touch_generate_all_slots(0,c);touch_generate_all_slots(1,c);
 *(uint32_t *)(i+16)=0x6781u;*(uint32_t *)(i+40)=touch_timer_cycles(*(uint32_t *)(i+36),c);
 return status;
}
static uint32_t saturated(uint32_t *out,uint32_t id,uint32_t slot,uint32_t mode,uint8_t *c){
 (void)mode;return touch_execute_saturated(out,id,slot,c,touch_switch_dither_dependency);
}
uint32_t touch_prepare_scan(uint8_t *c){
 uint32_t status=touch_prepare_scan_fields(c);void (*callback)(uint8_t *)=*(void (**)(uint8_t *))(ptr(c,8)+20);
 if(callback)callback(c); /* No return status is consumed. */
 if(!status){status|=touch_switch_dither_dependency(1,c);if(!status)status|=touch_switch_dither_dependency(2,c);}
 if(!status)status=touch_dither_scale(c);
 for(unsigned id=0;id<3;id++)if(enabled(id,c))status|=touch_max_raw_init(id,c,saturated);
 return status;
}
