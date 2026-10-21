#include <stdint.h>
#include <stddef.h>
extern volatile uint32_t r1_reset_trace_context[6];
extern int32_t r1_time_utc_offset_get(void);
extern uint32_t r1_time_backend_timestamp(void),r1_time_status_get(void);
extern void *r1_crash_record_marker_set(volatile uint16_t *);
extern void *memcpy(void *,const void *,size_t);
/* Supersede the earlier single-kernel initializer: all preparation frames
 * return before the actual snapshot call, preserving native query pointers. */
__attribute__((used,noinline)) uint32_t r1_crash_prepare_native_call(volatile uint16_t *frame)
{
 uint32_t base=r1_reset_trace_context[2];
 volatile uint32_t *words=(volatile uint32_t *)(uintptr_t)base;
 volatile uint16_t *halves=(volatile uint16_t *)(uintptr_t)base;
 words[0]=UINT32_C(0x5a5a5a5a);halves[3]=(uint16_t)r1_time_utc_offset_get();
 words[2]=r1_time_backend_timestamp();uint32_t valid=r1_time_status_get();
 halves[2]=(uint16_t)((halves[2]&0xfffeu)|(valid&1u));frame[0]=0;
 void *blob=r1_crash_record_marker_set(frame);
 if(blob && frame[0]==896){(void)memcpy((void *)(uintptr_t)(base+12),blob,896);*(volatile uint32_t *)(uintptr_t)(base+908)=UINT32_C(0x5a5a5a5a);}
 return base;
}
__attribute__((naked)) uint32_t r1_health_crash_record_initializer(void)
{
 __asm__ volatile("push {r3,r4,r5,r6,r7,lr}\n"
                  "mov r0,sp\n"
                  "bl r1_crash_prepare_native_call\n"
                  "mov r4,r0\n"
                  "ldrh r2,[r4,#6]\n"
                  "add.w r0,r4,#912\n"
                  "ldr r1,[r4,#8]\n"
                  "bl r1_health_crash_snapshot_builder\n"
                  "mov.w r1,#964\n"
                  "mov r0,r4\n"
                  "bl r1_stock_crc16_modbus\n"
                  "strh.w r0,[r4,#964]\n"
                  "pop {r3,r4,r5,r6,r7,pc}\n");
}
