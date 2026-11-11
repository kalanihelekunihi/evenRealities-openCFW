#include "native_temperature_state.h"
#include <stddef.h>
extern void __aeabi_memclr(void *,size_t);
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);

/* Stock 0x4b6c0. Once and timing share the native fourteen-byte record. */
void r1_temperature_once_enable(uint32_t enabled)
{
    uint32_t handle=r1_temperature_mode_handles[0];
    if (enabled) {
        if (handle) return;
        __aeabi_memclr((void *)r1_temperature_timing_record,14);
        r1_temperature_timing_record[12]=1;
        r1_temperature_mode_handles[0]=r1_sensor_stream_register_by_name(
            "temp","once",(uintptr_t)r1_temperature_stream_sample_callback,1,1);
    } else if (handle) {
        r1_sensor_stream_unregister_by_name("temp",handle);
        r1_temperature_mode_handles[0]=0;
    }
}
extern void r1_event_service_0004b6c0(uint32_t)
    __attribute__((alias("r1_temperature_once_enable")));
