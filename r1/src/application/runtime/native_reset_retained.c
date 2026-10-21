#include <stdint.h>
#include "../board/native_battery_memory.h"
#include "../../include/r1_stock_checksums.h"
/* Recovered cold context words. The retained record itself is never initialized
 * or cleared by this source; its address lies outside the cold scatter ranges. */
__attribute__((section(".r1.reset.retained.context"),aligned(4),used))
volatile uint32_t r1_reset_trace_context[6]={0,0x2003f000u,0x2003f010u,0x2003f3f0u,0,0x2003ffb0u};
__attribute__((noinline)) uint32_t r1_reset_trace_byte_read(uint32_t index,uint8_t *out)
{
 if(index>12u || !out)return 0;
 volatile uint8_t *record=(volatile uint8_t *)(uintptr_t)r1_reset_trace_context[5];
 if(record[0])return 0;
 uint32_t crc=r1_stock_crc16_modbus((const uint8_t *)(uintptr_t)record,14);
 if(read16(record+14)!=crc)return 0;
 *out=record[index+1];return 1;
}
typedef union {uint32_t alignment;uint8_t byte[4];} r1_retained_byte_slot;
_Static_assert(sizeof(r1_retained_byte_slot)==4,"native byte-slot stride");
static __attribute__((always_inline)) inline uint32_t read_word(uint32_t first,uint32_t *out)
{
 if(!out)return 0;
 r1_retained_byte_slot slots[4];
 for(uint32_t i=0;i<4;i++)if(!r1_reset_trace_byte_read(first+i,slots[i].byte))return 0;
 write32((volatile uint8_t *)out,(uint32_t)slots[0].byte[0]|((uint32_t)slots[1].byte[0]<<8)|((uint32_t)slots[2].byte[0]<<16)|((uint32_t)slots[3].byte[0]<<24));
 return 1;
}
uint32_t r1_reset_trace_return_address_read(uint32_t *out){return read_word(2,out);}
uint32_t r1_reset_trace_program_counter_read(uint32_t *out){return read_word(6,out);}
