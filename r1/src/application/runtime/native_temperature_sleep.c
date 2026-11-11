#include <stdint.h>
#include <stddef.h>
#include "native_temperature_state.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);

/* Native 0x4bad0 captures the status byte before any logging callbacks. */
void r1_temp_sleep_status_plan(const volatile void *status)
{
    uint32_t sleeping=*(const volatile uint8_t *)status;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c400000,"[RING]algo temp sleep status change: %d","[RING]algo temp sleep status change: %d",sleeping);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0003,"algo temp sleep status change: %d",sleeping);
    if (sleeping==1) {
        __aeabi_memclr((void *)r1_temperature_sleep_capture,106);
        r1_temperature_sleep_capture[0]=1;
        uint32_t saved=r1_temperature_mode_control.mode;
        r1_temperature_sleep_capture[1]=(uint8_t)saved;
        if (saved==1) return;
        if (!r1_temperature_mode_handles[1]) {
            __aeabi_memclr((void *)r1_temperature_timing_record,14);
            r1_temperature_timing_record[12]=1;
            r1_temperature_mode_handles[1]=r1_sensor_stream_register_by_name(
                "temp","timing",(uintptr_t)r1_temperature_stream_sample_callback,1,1);
        }
        r1_temperature_mode_set(1);
    } else if (r1_temperature_sleep_capture[0]==1) {
        uint32_t saved=r1_temperature_sleep_capture[1];
        if (saved==1) return;
        r1_temperature_mode_set(saved);
        uint32_t handle=r1_temperature_mode_handles[1];
        if (handle) {
            r1_sensor_stream_unregister_by_name("temp",handle);
            r1_temperature_mode_handles[1]=0;
        }
    }
}

/* Native 0x4bd54 exposes a word-backed status byte to the controller.
 * The ordinary C wrapper does not promise stock's incidental R3 residue. */
void r1_temp_sleep_status_report(uint32_t status)
{
    volatile uint32_t word=status;
    r1_temp_sleep_status_plan(&word);
}
