/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <stdint.h>

volatile uint32_t open_cfw_hfadj_host_register;

uint32_t open_cfw_bootloader_clkgen_hfadj_enable_426c58(uint32_t enable);

static void verify(uint32_t initial, uint32_t enable, uint32_t expected)
{
    open_cfw_hfadj_host_register = initial;
    assert(open_cfw_bootloader_clkgen_hfadj_enable_426c58(enable) == 0U);
    assert(open_cfw_hfadj_host_register == expected);
}

int main(void)
{
    verify(0xA5A5A5A5U, 0U, 0xA5A5A5A4U);
    verify(0x5A5A5A5AU, 1U, 0x5A5A5A5BU);
    verify(0xFFFFFFFEU, 0xFFU, 0xFFFFFFFFU);
    verify(0x13579BDFU, 0x100U, 0x13579BDEU);
    verify(0x2468ACE0U, 0x101U, 0x2468ACE1U);
    return 0;
}
