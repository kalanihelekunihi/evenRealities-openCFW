#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "../board/native_battery_memory.h"
extern uint32_t r1_protocol_send_response(uint32_t,const void *,const void *,uint32_t);
extern uint32_t r1_kv_class_read(void *,void *,uint32_t);
extern void *r1_native_memory_move(void *,const void *,size_t);
/* Source-owned cold class bytes; only authenticated offsets are interpreted.
 * Preserve the observed erased regions and mixed configuration bytes. */
struct r1_serial_record_class {uint32_t link_00;char key[12];uint16_t tag_16;volatile uint16_t flags;volatile uint16_t payload_size;uint16_t reserved_22;uint8_t payload[124];};
#define FF4 255,255,255,255
#define FF8 FF4,FF4
#define FF16 FF8,FF8
#define FF32 FF16,FF16
#define FF64 FF32,FF32
struct r1_serial_record_class r1_serial_record_class __attribute__((section(".r1.serial.kv.class"),aligned(4)))={.key="nv_r1",.tag_16=1,.flags=2,.payload_size=124,.payload={FF64,FF8,255,255,0,0,FF32,FF4,90,0,0,0,0,0,0,0,0,0,0,0}};
#undef FF64
#undef FF32
#undef FF16
#undef FF8
#undef FF4
_Static_assert(sizeof(struct r1_serial_record_class)==148 && offsetof(struct r1_serial_record_class,flags)==18 && offsetof(struct r1_serial_record_class,payload_size)==20 && offsetof(struct r1_serial_record_class,payload)==24,"native124-byte KV class layout");
void *volatile r1_device_info_kv_handle __attribute__((section(".r1.serial.kv.handle"),aligned(4)))=&r1_serial_record_class;
/* Frame views retain native header R2/R3 and checked-send R1/R2/R3 outputs.
 * Protocol bit/guard behavior remains ordinary C below the ABI-only bridges. */
__attribute__((used,noinline)) static uint32_t header_send_kernel(uint32_t handle,uint32_t command,volatile uint32_t *frame,uint32_t force_ack)
{
 uint32_t version=frame[0],flags=frame[1],sequence=frame[8];
 const void *payload=(const void *)(uintptr_t)frame[9];uint32_t length=frame[10];
 frame[0]=(uint8_t)((flags^1u)|force_ack)|((uint32_t)(uint8_t)version<<8)|((command&0xff00u)<<8)|((command&255u)<<24);
 frame[1]=(uint16_t)sequence;
 return r1_protocol_send_response(handle,(const void *)(uintptr_t)frame,payload,length);
}
#define HEADER_SEND(name,ack_word) \
__attribute__((naked,noinline)) uint32_t name(uint32_t handle __attribute__((unused)),uint32_t command __attribute__((unused)),uint32_t version __attribute__((unused)),uint32_t flags __attribute__((unused)),uint32_t sequence __attribute__((unused)),const void *payload __attribute__((unused)),uint32_t length __attribute__((unused))) { \
 __asm__ volatile("push {r2,r3,r4,r5,r6,r7,r8,lr}\nmov r2,sp\nmovs r3,#" #ack_word "\nbl header_send_kernel\npop {r2,r3,r4,r5,r6,r7,r8,pc}"); }
HEADER_SEND(r1_protocol_ack_header_send,2)
HEADER_SEND(r1_protocol_send_flag_inv,0)
__attribute__((used,noinline)) static uint32_t checked_send_kernel(uint32_t handle,volatile uint32_t *frame)
{
 /* Native loads both incoming stack arguments even on the rejected handle. */
 const void *payload=(const void *)(uintptr_t)frame[8];uint32_t length=frame[9];
 if(handle==0xffffu)return 0;
 uint32_t command=frame[0],flags=frame[1],sequence=frame[2];
 frame[0]=sequence;frame[1]=(uintptr_t)payload;frame[2]=length;
 return r1_protocol_ack_header_send(handle,command,1,flags,sequence,payload,length)==0;
}
__attribute__((naked,noinline)) uint32_t r1_protocol_send_checked(uint32_t handle __attribute__((unused)),uint32_t command __attribute__((unused)),uint32_t flags __attribute__((unused)),uint32_t sequence __attribute__((unused)),const void *payload __attribute__((unused)),uint32_t length __attribute__((unused)))
{__asm__ volatile("push {r1,r2,r3,r4,r5,r6,r7,lr}\nmov r1,sp\nbl checked_send_kernel\npop {r1,r2,r3,r4,r5,r6,r7,pc}");}
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
