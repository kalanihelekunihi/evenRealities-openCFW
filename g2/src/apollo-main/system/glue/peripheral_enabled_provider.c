/* Apollo MAIN 0x47F90C: read selected power-domain status bit. */
#include <stdint.h>
#include "../../../apollo-common/power-domain/power_domain.h"

uint32_t stock_peripheral_enabled(uint32_t domain, uint8_t *enabled) {
    if (!enabled) return 6;
    *enabled = 0;
    opencfw_power_domain_descriptor_t descriptor;
    uint32_t status = opencfw_power_domain_descriptor(&descriptor, (uint8_t)domain);
    if (status) return status;
    *enabled = (*(volatile uint32_t *)(uintptr_t)descriptor.status_register & descriptor.status_mask) != 0;
    return 0;
}

__asm__(".global am_hal_pwrctrl_periph_enabled\n"
        ".set am_hal_pwrctrl_periph_enabled, stock_peripheral_enabled\n");
