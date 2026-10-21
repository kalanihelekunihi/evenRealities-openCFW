#include <stdint.h>
#include <stddef.h>
extern volatile uint32_t r1_reset_trace_context[6];
extern int32_t r1_time_utc_offset_get(void);
extern uint32_t r1_time_backend_timestamp(void);
extern volatile uint8_t r1_time_state[];
uint32_t r1_time_status_get(void){return r1_time_state[11];}
/* Native6abe4 reports736 bytes; initializer accepts896. Preserve both
 * contracts. Its payload ownership and snapshot builder remain providers. */
extern void *r1_crash_record_marker_set(volatile uint16_t *length);
extern void *memcpy(void *,const void *,size_t);
extern void r1_health_crash_snapshot_builder(void *,uint32_t,uint32_t);
extern uint32_t r1_stock_crc16_modbus(const void *,uint32_t);
__attribute__((used,noinline)) uint32_t r1_crash_initialize_body(volatile uint16_t *frame)
{
 uint32_t base=r1_reset_trace_context[2];
 volatile uint32_t *words=(volatile uint32_t *)(uintptr_t)base;
 volatile uint16_t *halves=(volatile uint16_t *)(uintptr_t)base;
 words[0]=UINT32_C(0x5a5a5a5a);
 halves[3]=(uint16_t)r1_time_utc_offset_get();
 words[2]=r1_time_backend_timestamp();
 uint32_t valid=r1_time_status_get();
 halves[2]=(uint16_t)((halves[2]&0xfffeu)|(valid&1u));
 frame[0]=0;
 void *blob=r1_crash_record_marker_set(frame);
 if(blob && frame[0]==896){
  (void)memcpy((void *)(uintptr_t)(base+12),blob,896);
  *(volatile uint32_t *)(uintptr_t)(base+908)=UINT32_C(0x5a5a5a5a);
 }
 uint32_t offset=halves[3];
 r1_health_crash_snapshot_builder((void *)(uintptr_t)(base+912),words[2],offset);
 uint32_t crc=r1_stock_crc16_modbus((const void *)(uintptr_t)base,964);
 *(volatile uint16_t *)(uintptr_t)(base+964)=(uint16_t)crc;
 return crc;
}
__attribute__((naked)) uint32_t r1_health_crash_record_initializer(void)
{
 __asm__ volatile("push {r3,r4,r5,r6,r7,lr}\n"
                  "mov r0,sp\n"
                  "bl r1_crash_initialize_body\n"
                  "pop {r3,r4,r5,r6,r7,pc}\n");
}
