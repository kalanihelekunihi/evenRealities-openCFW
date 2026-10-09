#ifndef AUDIO_CLOCK_DRIVER_CONFIG_H
#define AUDIO_CLOCK_DRIVER_CONFIG_H
#include <stdint.h>
/* Exact stock12-byte SYSPLL config. Mode1 is integer; mode0 fractional. */
typedef struct {uint8_t reference,vco,mode,refdiv,postdiv1,postdiv2;uint16_t fbdiv;uint32_t fraction;} audio_pll_config;
uint32_t audio_pll_init(uint32_t module,uint32_t *handle);
uint32_t audio_pll_deinit(uint32_t handle),audio_pll_enable(uint32_t handle),audio_pll_disable(uint32_t handle),audio_pll_wait(uint32_t handle);
uint32_t audio_pll_configure(uint32_t handle,const audio_pll_config *config);
uint32_t audio_hfrc2_config(uint32_t requested,const uint32_t *config);
uint32_t audio_syspll_config(uint32_t requested,const uint32_t *config);
uint32_t audio_clock_config(uint32_t clock,uint32_t requested,const uint32_t *config);
#endif
