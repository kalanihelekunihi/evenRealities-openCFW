#include <stdint.h>
extern uint32_t audio_power_peripheral_on(uint32_t),audio_power_peripheral_off(uint32_t);
extern uint32_t audio_power_clock_acquire(uint32_t,uint32_t),audio_power_clock_release(uint32_t,uint32_t),audio_power_clock_source(uint32_t);
extern void audio_power_reconfigure(uint32_t,uint32_t);
static const uint16_t offsets[]={0x48,0x40,0x44,0x54,0x100,0x4c,0x10,0x30,0x300,0x200,0x60,0x64};
uint32_t audio_i2s_power_selected(uint32_t *h,uint32_t mode,uint32_t backup){
 /* Original reads module before checking NULL. Valid mapped non-NULL contract. */
 uint32_t module=h[1],peripheral=module?30:29;uint8_t op=mode,save=backup;
 if((h[0]&~0xfe000000u)!=0x01125125u)return 2;
 volatile uint8_t *bytes=(void*)h;volatile uint8_t *base=(void*)(0x40208000u+(module<<12));
 if(op==0){
  if(save&&!bytes[8])return 7;
  audio_power_peripheral_on((uint8_t)(module+31));
  if(!save)return 0;
  for(unsigned i=0;i<12;i++)*(volatile uint32_t*)(base+offsets[i])=h[3+i];
  uint32_t status=audio_power_clock_acquire(4,peripheral);if(status)return status;
  if(bytes[0x60]){
   status=audio_power_clock_acquire((uint8_t)audio_power_clock_source(h[0x5c/4]),peripheral);
   if(status){audio_power_clock_release(4,peripheral);return status;}
   audio_power_reconfigure(module,h[0x5c/4]);
  }
  bytes[8]=0;return 0;
 }
 if(op==1||op==2){
  if(save){
   audio_power_reconfigure(module,0x217);audio_power_clock_release(4,peripheral);
   if(bytes[0x60])audio_power_clock_release((uint8_t)audio_power_clock_source(h[0x5c/4]),peripheral);
   for(unsigned i=0;i<12;i++){uint32_t value=*(volatile uint32_t*)(base+offsets[i]);h[3+i]=i?value:value&0x11u;}bytes[8]=1;
  }
  audio_power_peripheral_off((uint8_t)(module+31));return 0;
 }
 return 6;
}
uint32_t audio_i2s_uninitialize_selected(uint32_t *h){
 if(!h||(h[0]&~0xfe000000u)!=0x01125125u)return 2;
 h[0]&=~0x01000000u;h[0]&=0xff000000u;h[1]=0;return 0;
}
/* Optional platform control callback at table+4; NULL is an actual no-op provider branch. */
uint32_t audio_power_control_dispatch(uint32_t action,uint32_t enable,void *metadata){
 uint32_t (*callback)(uint8_t,uint8_t,void*)=*(void**)0x20073274u;
 return callback?callback((uint8_t)action,(uint8_t)enable,metadata):0;
}
