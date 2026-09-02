/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <stdint.h>

volatile uint32_t open_cfw_hfadj_disable_host_register;

uint32_t open_cfw_bootloader_clkgen_hfadj_disable_426c7e(void);

static void verify(uint32_t initial, uint32_t expected)
{
    open_cfw_hfadj_disable_host_register = initial;
    assert(open_cfw_bootloader_clkgen_hfadj_disable_426c7e() == 0U);
    assert(open_cfw_hfadj_disable_host_register == expected);
}

int main(void)
{
    verify(0U, 0U);
    verify(1U, 0U);
    verify(0xA5A5A5A5U, 0xA5A5A5A4U);
    verify(0xFFFFFFFEU, 0xFFFFFFFEU);
    verify(0xFFFFFFFFU, 0xFFFFFFFEU);
    return 0;
}
