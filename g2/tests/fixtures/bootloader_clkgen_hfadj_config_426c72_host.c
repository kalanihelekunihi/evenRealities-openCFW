/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <stdint.h>

volatile uint32_t open_cfw_hfadj_config_host_register;

uint32_t open_cfw_bootloader_clkgen_hfadj_config_426c72(uint32_t configuration);

static void verify(uint32_t configuration, uint32_t expected)
{
    open_cfw_hfadj_config_host_register = 0xA5A5A5A5U;
    assert(open_cfw_bootloader_clkgen_hfadj_config_426c72(configuration) == 0U);
    assert(open_cfw_hfadj_config_host_register == expected);
}

int main(void)
{
    verify(0U, 1U);
    verify(1U, 1U);
    verify(2U, 3U);
    verify(0xFFFFFFFEU, 0xFFFFFFFFU);
    verify(0xFFFFFFFFU, 0xFFFFFFFFU);
    return 0;
}
