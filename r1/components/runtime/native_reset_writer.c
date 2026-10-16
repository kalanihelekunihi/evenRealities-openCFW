#include <stdint.h>
#include "../board/native_battery_memory.h"
#include "../../source/include/r1_stock_checksums.h"
extern volatile uint32_t r1_reset_trace_context[];
extern void __aeabi_memclr(void *,uint32_t);
__attribute__((noinline)) uint32_t r1_reset_trace_byte_write(uint32_t index,uint32_t value)
{
 if(index>12u)return 0;
 volatile uint8_t *record=(volatile uint8_t *)(uintptr_t)r1_reset_trace_context[5];
 uint32_t invalid=record[0]!=0;
 if(!invalid){uint32_t checksum=r1_stock_crc16_modbus((const uint8_t *)(uintptr_t)record,14);invalid=read16(record+14)!=checksum;}
 if(invalid)__aeabi_memclr((void *)(uintptr_t)r1_reset_trace_context[5],16);
 record[0]=0;record[index+1]=(uint8_t)value;
 uint32_t checksum=r1_stock_crc16_modbus((const uint8_t *)(uintptr_t)record,14);
 write16(record+14,checksum);return 1;
}
__attribute__((noinline)) uint32_t r1_reset_trace_return_address_write(uint32_t value)
{
 (void)r1_reset_trace_byte_write(2,(uint8_t)value);
 (void)r1_reset_trace_byte_write(3,(uint8_t)(value>>8));
 (void)r1_reset_trace_byte_write(4,(uint8_t)(value>>16));
 return r1_reset_trace_byte_write(5,(uint8_t)(value>>24));
}
__attribute__((noinline)) uint32_t r1_reset_trace_addresses_clear(void)
{
 (void)r1_reset_trace_byte_write(2,0);(void)r1_reset_trace_byte_write(3,0);
 (void)r1_reset_trace_byte_write(4,0);(void)r1_reset_trace_byte_write(5,0);
 (void)r1_reset_trace_byte_write(6,0);(void)r1_reset_trace_byte_write(7,0);
 (void)r1_reset_trace_byte_write(8,0);return r1_reset_trace_byte_write(9,0);
}
__attribute__((noinline)) uint32_t r1_reset_trace_program_counter_write(uint32_t value)
{
 (void)r1_reset_trace_byte_write(6,(uint8_t)value);
 (void)r1_reset_trace_byte_write(7,(uint8_t)(value>>8));
 (void)r1_reset_trace_byte_write(8,(uint8_t)(value>>16));
 return r1_reset_trace_byte_write(9,(uint8_t)(value>>24));
}
uint32_t r1_reset_trace_reboot_caller_write(uint32_t value)
{(void)r1_reset_trace_addresses_clear();return r1_reset_trace_byte_write(1,value);}
uint32_t r1_reset_trace_persist_tag_write(uint32_t value)
{if(value!=7u)(void)r1_reset_trace_addresses_clear();return r1_reset_trace_byte_write(0,value);}
__attribute__((naked,noinline,section(".r1.reset.writer.probe")))
uint32_t r1_reset_trace_program_counter_probe(void){__asm__ volatile("mov r0, pc\nbx lr");}
void r1_reset_trace_capture_site_adapter(uintptr_t caller)
{
 uint32_t pc=r1_reset_trace_program_counter_probe();
 if(pc)(void)r1_reset_trace_program_counter_write(pc);
 if(caller)(void)r1_reset_trace_return_address_write(caller);
}
uint32_t r1_reset_trace_current_site_capture(void)
{
 uintptr_t caller=(uintptr_t)__builtin_return_address(0);
 (void)r1_reset_trace_program_counter_write(r1_reset_trace_program_counter_probe());
 return r1_reset_trace_return_address_write(caller);
}
