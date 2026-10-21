#include "native_delayed_state.h"
/* Supplemental worker0x65ea8. A successful queue receive supplies both words;
 * errors log and retry. Native dispatch does not reject a null callback. */
extern int32_t osMessageQueueGet(void *,void *,uint8_t *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
_Noreturn void r1_native_delayed_worker(void *argument)
{
    (void)argument;
    uint32_t record[2];
    for (;;) {
        int32_t status=osMessageQueueGet((void *)(uintptr_t)r1_delayed_context[0],record,0,UINT32_MAX);
        if (!status) {
            ((void (*)(uint32_t))(uintptr_t)record[1])(record[0]);
        } else {
            const char *ring="[RING][fw_evt_loop_task]app treat event invalid status:%d";
            if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u))
                r1_structured_log_format(0x04400000,ring,ring,(uint32_t)status);
            if (r1_structured_log_mode_get()&2u)
                nrf_log_frontend_std_1(0x001c0001,"[fw_evt_loop_task]app treat event invalid status:%d",(uint32_t)status);
        }
    }
}
