/* Reconstructed stock register/dispatch bodies; no retained opcode arrays. */
#include "dispatch.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
void pcm_buck_control(uint32_t enable){
 uint32_t bit=((uint8_t)enable)&1u;
 W(0x40020060u)=(W(0x40020060u)&~0x10000u)|(bit<<16);
 W(0x40020060u)=(W(0x40020060u)&~1u)|bit;
 W(0x40020060u)=(W(0x40020060u)&~32u)|(bit<<5);
}
#define DISPATCH0(name,address) uint32_t name(void){ \
 if(W(address)) {uint32_t (*callback)(void)=(void*)(uintptr_t)W(address);return callback();} \
 return 0; }
DISPATCH0(pcm_before_enable_dispatch,0x20073284u)
DISPATCH0(pcm_after_enable_dispatch,0x20073288u)
DISPATCH0(pcm_tempco_suspend_dispatch,0x2007328cu)
DISPATCH0(pcm_lp_switch_initialize_dispatch,0x20073290u)
uint32_t pcm_ton_dispatch(uint32_t gpu_on,uint32_t gpu_mode){
 if(W(0x20073294u)){
  uint32_t (*callback)(uint32_t,uint32_t)=(void*)(uintptr_t)W(0x20073294u);
  return callback((uint8_t)gpu_on,(uint8_t)gpu_mode);
 }
 return 0;
}
