#include <stdint.h>
volatile uint32_t r1_log_persist_last_tick __attribute__((section(".r1.log.persist.last_tick"),aligned(4)))=0;
uint8_t r1_log_persist_buffer[4096] __attribute__((section(".bss.r1.log.persist.buffer"),aligned(4)));
extern uint32_t r1_structured_log_export_active(void);
extern uint32_t r1_structured_log_cache_copy(uint32_t,void *,uint32_t);
extern uint32_t osKernelGetTickCount(void),osDelay(uint32_t);
extern void r1_log_bin_write(const void *,uint32_t);

/* Stock 0x914a0: cache extraction precedes the strict unsigned time gate. */
void r1_structured_log_periodic_persist(void)
{
    if (r1_structured_log_export_active()) return;
    if (!r1_structured_log_cache_copy(0,r1_log_persist_buffer,4096)) return;
    uint32_t now=osKernelGetTickCount();
    if (now<=r1_log_persist_last_tick+10000u) return;
    r1_log_persist_last_tick=now;
    (void)r1_log_bin_write(r1_log_persist_buffer,4096);
    (void)osDelay(80);
}
extern void r1_event_service_000914a0(void) __attribute__((alias("r1_structured_log_periodic_persist")));
