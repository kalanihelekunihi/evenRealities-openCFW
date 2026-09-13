/* SPDX-License-Identifier: MIT */
/* Recovered codec flash probe wrapper at package 0x16770.
 * Retry while elapsed unsigned microseconds are below 5,000,000.
 * States >=2 suppress the probe callback; successful probe sets state 1.
 */
#include <stdint.h>
extern uint64_t gx_clock_get_time_us(void);
volatile uint8_t open_cfw_gx8002_flash_probe_state;
typedef void *(*probe_function)(unsigned, unsigned, unsigned, unsigned);
extern probe_function volatile open_cfw_gx8002_flash_probe_callback;
void *open_cfw_gx8002_flash_probe(unsigned bus, unsigned cs, unsigned speed, unsigned mode)
{
    uint64_t started = gx_clock_get_time_us();
    do {
        if (open_cfw_gx8002_flash_probe_state < 2u) {
            void *device = open_cfw_gx8002_flash_probe_callback(bus, cs, speed, mode);
            if (device) {
                open_cfw_gx8002_flash_probe_state = 1;
                return device;
            }
        }
    } while (gx_clock_get_time_us() - started < UINT64_C(5000000));
    return 0;
}
