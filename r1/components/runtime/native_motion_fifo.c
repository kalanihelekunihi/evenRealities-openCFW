#include <stdint.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_motion_bus_acquire(void),r1_motion_bus_release(void);
extern int32_t r1_lis2dw12_fifo_read(uint8_t *,uint32_t),r1_bma456w_fifo_read(uint8_t *,uint32_t),r1_qma6100_bounded_fifo_read(uint8_t *,uint32_t);
/* Defined arithmetic-right-shift of a signed16 input, retaining its low16
 * result without implementation-defined signed C shifts or division rounding. */
static __attribute__((always_inline)) inline uint16_t shift_two(uint16_t value)
{return (uint16_t)((value>>2)|((value&0x8000u)?0xc000u:0));}
#define NORMALIZER(name,provider,preload) \
int32_t name(uint8_t *destination,uint32_t requested) \
{ \
 (void)r1_motion_bus_acquire(); \
 int32_t count=provider(destination,requested); \
 (void)r1_motion_bus_release(); \
 for(int32_t i=0;i<count;i++){ \
  volatile uint8_t *sample=destination+(uint32_t)i*6u; \
  uint16_t x=read16(sample); \
  if(preload){uint16_t y=read16(sample+2),z=read16(sample+4);write16(sample,shift_two(x));write16(sample+2,shift_two(y));write16(sample+4,shift_two(z));} \
  else {write16(sample,shift_two(x));uint16_t y=read16(sample+2);write16(sample+2,shift_two(y));uint16_t z=read16(sample+4);write16(sample+4,shift_two(z));} \
 } \
 return count; \
}
NORMALIZER(r1_lis2dw12_fifo_normalized,r1_lis2dw12_fifo_read,0)
NORMALIZER(r1_bma456w_fifo_normalized,r1_bma456w_fifo_read,0)
NORMALIZER(r1_qma6100_fifo_normalized,r1_qma6100_bounded_fifo_read,1)
