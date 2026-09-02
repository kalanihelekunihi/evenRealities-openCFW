/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <stdint.h>

volatile uint32_t open_cfw_dual_switch_host_hfadj;
volatile uint32_t open_cfw_dual_switch_host_status;

static uint32_t call_count;
static uint32_t returned_status;

uint32_t open_cfw_bootloader_dual_switch_426c8c(uint32_t enabled);

uint32_t open_cfw_dual_switch_host_status_check(
    uint32_t timeout,
    volatile uint32_t *status,
    uint32_t mask,
    uint32_t expected,
    uint32_t polarity)
{
    ++call_count;
    assert(timeout == 100U);
    assert(status == &open_cfw_dual_switch_host_status);
    assert(mask == 0x01000000U);
    assert(expected == 0x01000000U);
    assert(polarity == 1U);
    return returned_status;
}

static void verify(
    uint32_t enabled,
    uint32_t initial,
    uint32_t expected,
    uint32_t provider_status,
    uint32_t expected_return,
    uint32_t expected_calls)
{
    open_cfw_dual_switch_host_hfadj = initial;
    returned_status = provider_status;
    call_count = 0U;
    assert(open_cfw_bootloader_dual_switch_426c8c(enabled) == expected_return);
    assert(open_cfw_dual_switch_host_hfadj == expected);
    assert(call_count == expected_calls);
}

int main(void)
{
    verify(0U, 0xFFFFFFFFU, 0xFFFFFFDFU, 9U, 0U, 0U);
    verify(0x100U, 0xFFFFFFFFU, 0xFFFFFFDFU, 9U, 0U, 0U);
    verify(1U, 0x20U, 0x20U, 9U, 0U, 0U);
    verify(0x101U, 0U, 0x20U, 0U, 0U, 1U);
    verify(0xFFU, 0xA5A5A585U, 0xA5A5A5A5U, 7U, 7U, 1U);
    return 0;
}
