#include "native_gomore_accel_history.h"
extern void __aeabi_memclr(void *,uint32_t);
static uint32_t byte(uint32_t at){return *(volatile uint8_t *)(uintptr_t)at;}
static void put_byte(uint32_t at,uint32_t x){*(volatile uint8_t *)(uintptr_t)at=(uint8_t)x;}
static void put_half(uint32_t at,uint32_t x){*(volatile uint16_t *)(uintptr_t)at=(uint16_t)x;}
uint32_t r1_gomore_accel_state_reset_native(uint32_t state)
{
 __aeabi_memclr((void *)(uintptr_t)state,0x26e);
 put_byte(state,8);
 for(uint32_t i=0;i<5;i++)put_half(state+0x264u+i*2u,0xec78);
 return 0;
}
uint32_t r1_gomore_missing_window_reset_native(uint32_t record)
{
 for(uint32_t i=0;i<14;i++)*(volatile uint32_t *)(uintptr_t)(record+i*4u)=0;
 for(uint32_t i=0;i<6;i++)put_byte(record+0x38u+i,0xff);
 return 0;
}
uint32_t r1_gomore_accel_slot_advance_native(uint32_t state)
{
 /* Each index read is live: out-of-range cursors can alias the index byte. */
 put_half(state+2u+byte(state+0x52u)*2u,0);
 put_half(state+0x204u+byte(state+0x52u)*2u,0);
 put_half(state+0x214u+byte(state+0x52u)*2u,0);
 put_half(state+0x12u+byte(state+0x52u)*2u,0);
 put_half(state+0x22u+byte(state+0x52u)*2u,0);
 put_half(state+0x32u+byte(state+0x52u)*2u,0);
 put_half(state+0x42u+byte(state+0x52u)*2u,0);
 put_half(state+0x1e4u+byte(state+0x52u)*2u,0);
 put_half(state+0x1f4u+byte(state+0x52u)*2u,0);
 uint32_t next=byte(state+0x52u)+1u;put_byte(state+0x52u,next<8u?next:0u);
 return 0;
}
