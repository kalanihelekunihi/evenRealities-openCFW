#include <stdint.h>
/* Product-specific 0x659e8. Context initialization remains a separate gate.
 * The native queue record is two words: argument, then callback address. */
extern volatile uint32_t r1_delayed_context[6];
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern int32_t osMessageQueuePut(void *,const void *,uint8_t,uint32_t);
void r1_native_delayed_push(void (*callback)(uint32_t),uint32_t argument,uint32_t timeout)
{
    if (!r1_delayed_context[1]) {
        const char *ring="[RING][fw_evt_loop_push]fw_evt_loop_thread_id is NULL";
        if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x04000000,ring,ring);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_0(0x001c0001,"[fw_evt_loop_push]fw_evt_loop_thread_id is NULL");
        return;
    }
    uint32_t record[2]={argument,(uint32_t)(uintptr_t)callback};
    uint32_t queue=r1_delayed_context[0];
    if (!queue) return;
    int32_t status=osMessageQueuePut((void *)(uintptr_t)queue,record,0,timeout);
    if (status) {
        const char *ring="[RING][fw_evt_loop_push]fw_event_push error:0x%x";
        if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x04400000,ring,ring,(uint32_t)status);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_1(0x001c0001,"[fw_evt_loop_push]fw_event_push error:0x%x",(uint32_t)status);
    }
}
