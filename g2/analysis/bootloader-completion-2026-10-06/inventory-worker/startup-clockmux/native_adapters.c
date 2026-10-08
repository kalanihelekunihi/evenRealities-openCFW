/* Source-call adapters for the linked clockmux child chain. */
#include <stdint.h>
#include "clock_class_provider2.h"
#include "clock_class_provider4.h"

extern uint32_t opencfw_bl_power_register_read(uint32_t, uint32_t *);
extern void opencfw_test_syspll_power_initialize(void);
extern void opencfw_test_syspll_power_restore(void);

void opencfw_hal_delay_us(uint32_t usec)
{
    opencfw_bl_delay_us(usec);
}

uint64_t opencfw_legacy_gpio_mode(uint32_t mode, uint8_t *state)
{
    return opencfw_bl_radio_mode_apply((uint8_t)mode,
        (const uint32_t *)(const void *)state, 0u, 0u);
}

uint32_t opencfw_power_register_read(uint32_t id, uint32_t *value)
{
    return opencfw_bl_power_register_read(id, value);
}

uint64_t opencfw_low_power_prepare(void)
{
    opencfw_test_syspll_power_initialize();
    return 0u;
}

uint64_t opencfw_low_power_finish(void)
{
    opencfw_test_syspll_power_restore();
    return 0u;
}
