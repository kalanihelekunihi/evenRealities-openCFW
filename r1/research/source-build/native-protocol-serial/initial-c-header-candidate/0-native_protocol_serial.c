#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_protocol_send_response(uint32_t,const void *,const void *,uint32_t);
extern uint32_t r1_kv_class_read(void *,void *,uint32_t);
extern void *r1_native_memory_move(void *,const void *,size_t);
void *volatile r1_device_info_kv_handle __attribute__((section(".r1.serial.kv.handle"),aligned(4)))=0;
#define HEADER_SEND(name,force_ack) \
__attribute__((noinline)) uint32_t name(uint32_t handle,uint32_t command,uint32_t version,uint32_t flags,uint32_t sequence,const void *payload,uint32_t length) { \
 uint32_t header[2]={(uint8_t)((flags^1u)|(force_ack))|((uint32_t)(uint8_t)version<<8)|((command&0xff00u)<<8)|((command&255u)<<24),(uint16_t)sequence}; \
 return r1_protocol_send_response(handle,header,payload,length); }
HEADER_SEND(r1_protocol_ack_header_send,2u)
HEADER_SEND(r1_protocol_send_flag_inv,0u)
__attribute__((noinline)) uint32_t r1_protocol_send_checked(uint32_t handle,uint32_t command,uint32_t flags,uint32_t sequence,const void *payload,uint32_t length)
{if(handle==0xffffu)return 0;return r1_protocol_ack_header_send(handle,command,1,flags,sequence,payload,length)==0;}
/* The 124-byte view is provided by an ABI frame bridge, not an uninitialized C
 * object. Cached read failure leaves those existing bytes untouched. */
__attribute__((used,noinline)) static uint32_t serial_read_kernel(volatile uint8_t *destination,volatile uint8_t *length,volatile uint8_t *record)
{
 (void)r1_kv_class_read(r1_device_info_kv_handle,(void *)(uintptr_t)record,124);
 uint32_t result;
 if(record[61]!=255){result=(uintptr_t)r1_native_memory_move((void *)(uintptr_t)destination,(const void *)(uintptr_t)(record+31),15);if(length){*length=15;result=15;}}
 else{(void)memset((void *)(uintptr_t)destination,255,15);result=(uintptr_t)destination+15u;if(length){*length=0;result=0;}}
 return result;
}
__attribute__((naked,noinline)) uint32_t r1_native_product_serial_read(void *destination __attribute__((unused)),uint8_t *length __attribute__((unused)))
{__asm__ volatile("push {r4,r5,lr}\nsub sp,sp,#124\nmov r2,sp\nbl serial_read_kernel\nadd sp,sp,#124\npop {r4,r5,pc}");}
__attribute__((used,noinline)) static uint32_t serial_handler_kernel(uint32_t handle,volatile uint8_t *output,volatile uint8_t *record,const volatile uint8_t *packet)
{
 write32(output,0);write32(output+4,0);write32(output+8,0);write32(output+12,0);
 (void)serial_read_kernel(output,0,record);
 return r1_protocol_send_checked(handle,16,0,read16(packet+3),(const void *)(uintptr_t)output,15);
}
/* Preserve the native serial frame and the nested getter's raw record view.
 * The C kernel runs below that view, so failed/partial reads keep its seed. */
__attribute__((naked,noinline)) uint32_t r1_device_serial_handler(uint32_t handle __attribute__((unused)),const void *packet __attribute__((unused)),uintptr_t scratch __attribute__((unused)),uint32_t seed __attribute__((unused)))
{__asm__ volatile("push {r4,r5,lr}\nsub sp,sp,#28\nmov r5,r0\nmov r4,r1\nsub sp,sp,#136\nmov r3,r4\nmov r2,sp\nadd r1,sp,#144\nmov r0,r5\nbl serial_handler_kernel\nadd sp,sp,#164\npop {r4,r5,pc}");}
