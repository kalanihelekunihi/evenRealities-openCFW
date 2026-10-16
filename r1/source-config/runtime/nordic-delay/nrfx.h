#ifndef R1_NORDIC_DELAY_NRFX_ADAPTER_H
#define R1_NORDIC_DELAY_NRFX_ADAPTER_H
#include <stdint.h>
/* Narrow compilation adapter for unchanged SDK nrf_delay.h. Native R1 uses
 * 64 cycles/us and the separately source-compiled SUBS/BHI/BX primitive. */
extern void r1_rtt_delay_cycles(uint32_t);
static inline void r1_nordic_delay_us(uint32_t us)
{if(us)r1_rtt_delay_cycles(us*64u);}
#define NRFX_DELAY_US(us) r1_nordic_delay_us(us)
#define __STATIC_INLINE static inline
#endif
