/* SPDX-License-Identifier: MIT
 * Stock 0x0800a408 and 0x0800a148 loop semantics. Volatile counters preserve
 * busy loops in C, but cycle timing still needs compiler/device validation.
 */
#include <stdint.h>

/* Stock 0x0800A408 (case_delay_10) */
uint32_t case_binary_sensor_delay(void)
{
    volatile uint8_t count=0u;
    do { ++count; } while(count<10u);
    return count;
}

uint32_t case_binary_sensor_delay_count(uint32_t count)
{
    for(volatile int32_t outer=0;outer<(int32_t)count;++outer) {
        volatile int32_t inner=0;
        do { ++inner; } while(inner<0x32c8);
    }
    return count;
}
