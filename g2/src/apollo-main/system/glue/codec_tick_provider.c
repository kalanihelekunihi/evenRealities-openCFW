#include <stdint.h>

/* Original 0x58fac8 calls osKernelGetTickCount and clears the high half
 * (a zero-extended tick snapshot). osKernelGetTickCount is compiled from
 * upstream CMSIS-FreeRTOS cmsis_os2.c (U4-freertos), so the former direct read
 * of the xTickCount word 0x20074a34 is no longer needed. */
extern uint32_t osKernelGetTickCount(void);
uint64_t codec_tick64(void) {
    return (uint64_t)osKernelGetTickCount();
}
uint64_t codec_tick_snapshot(void) __attribute__((alias("codec_tick64")));
