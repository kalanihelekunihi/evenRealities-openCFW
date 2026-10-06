/* SPDX-License-Identifier: MIT. Explicit fixture-only external providers. */
#include <stdint.h>

volatile uint32_t opencfw_test_accepted_power_object_calls
    __attribute__((section(".test_data"), used));
volatile uint32_t opencfw_test_power_control_calls
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

uint32_t opencfw_boot_power_control(uint32_t module, uint32_t enabled,
                                    uint32_t *value)
{
    (void)module;
    (void)enabled;
    (void)value;
    ++opencfw_test_power_control_calls;
    return 0u;
}
