/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <stdint.h>

volatile uint32_t open_cfw_clkgen_disable_host_register;

uint32_t open_cfw_bootloader_clkgen_disable_426d1e(void);

int main(void)
{
    open_cfw_clkgen_disable_host_register = 0xFFFFFFFFU;
    assert(open_cfw_bootloader_clkgen_disable_426d1e() == 0U);
    assert(open_cfw_clkgen_disable_host_register == 0xFFFFFFFEU);

    open_cfw_clkgen_disable_host_register = 0xA5A5A5A4U;
    assert(open_cfw_bootloader_clkgen_disable_426d1e() == 0U);
    assert(open_cfw_clkgen_disable_host_register == 0xA5A5A5A4U);
    return 0;
}
