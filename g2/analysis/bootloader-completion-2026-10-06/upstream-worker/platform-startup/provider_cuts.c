/* SPDX-License-Identifier: MIT
 * A guard for the accepted-object continuation, unreachable in the authentic
 * scatter fixture. This is a test-only cut, not a production implementation.
 */
#include <stdint.h>

volatile uint32_t opencfw_test_accepted_power_object_calls
    __attribute__((section(".test_data"), used));

uint32_t opencfw_boot_control_power_apply_configure(uint32_t *object,
                                                    uint32_t operation,
                                                    uint8_t enable)
{
    (void)object;
    (void)operation;
    (void)enable;
    ++opencfw_test_accepted_power_object_calls;
    return 0xbad00001u;
}
