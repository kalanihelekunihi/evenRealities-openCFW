#include <stdint.h>

/* Original 0x58fac8 calls osKernelGetTickCount and clears the high half.
 * Both task and ISR tick getters called there read the same 0x20074a34
 * word. The isolated source contract is a zero-extended tick snapshot. */
uint64_t codec_tick64(void) {
    return (uint64_t)*(volatile const uint32_t *)(uintptr_t)0x20074a34u;
}
uint64_t codec_tick_snapshot(void) __attribute__((alias("codec_tick64")));
