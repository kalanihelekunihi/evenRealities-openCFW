#include <stdint.h>
extern uint32_t audio_i2s_clock_release(uint32_t,uint32_t);
extern void audio_i2s_reconfigure(uint32_t,uint32_t);
extern uint32_t audio_i2s_clock_source(uint32_t);
uint32_t audio_i2s_dma_stop_selected(uint32_t *handle){
 /* Original dereferences handle+4 before its NULL test; non-NULL mapped handle is required. */
 uint32_t module=handle[1],peripheral=module?30:29;
 if((handle[0]&~0xfe000000u)!=0x01125125u)return 2;
 if(!(handle[0]&0x02000000u))return 0;
 audio_i2s_clock_release(4,peripheral);
 if(((uint8_t*)handle)[0x60]){
  volatile uint32_t *control=(void*)(0x40208100u+(module<<12));
  *control&=~1u;*control&=~0x1000u;
  audio_i2s_reconfigure(module,0x217);
  audio_i2s_clock_release((uint8_t)audio_i2s_clock_source(handle[0x5c/4]),peripheral);
 }
 handle[0]&=~0x02000000u;return 0;
}
/* Only 0x217 request and matching source selector 2; other hardware configuration paths excluded. */
void audio_i2s_reconfigure_217_matching_source(uint32_t module){
 volatile uint32_t *aux=(void*)(0x40208054u+(module<<12));
 volatile uint32_t *control=(void*)(0x40208100u+(module<<12));
 *aux&=~1u;uint32_t enable12=(*control>>12)&1;
 *control&=~0x1000u;*control=(*control&~0x70000u)|0x40000u;
 *control=(*control&~0x1000u)|(enable12<<12);
 uint32_t divider=(*control>>4)&31;
 if(divider!=23){uint32_t bit0=*control&1u;*control&=~1u;*control=(*control&~0x1f0u)|(23u<<4);*control=(*control&~1u)|bit0;}
}
