/* SPDX-License-Identifier: MIT */
#include "runtime_clkmgr_divider_candidate.h"

#include <assert.h>
#include <stdint.h>

int main(void)
{
    uint32_t value = 0xA5A5A5A5U;

    assert(open_cfw_clkmgr_hfrc_integer_divider(
               48000000U, 24000000U, &value) ==
           OPEN_CFW_CLKMGR_DIVIDER_OK);
    assert(value == 0U);
    assert(open_cfw_clkmgr_hfrc_integer_divider(
               24000000U, 48000000U, &value) ==
           OPEN_CFW_CLKMGR_DIVIDER_OK);
    assert(value == 2U);

    assert(open_cfw_clkmgr_hfrc2_uq15_divider(
               250000000U, 196608000U, 0U, &value) ==
           OPEN_CFW_CLKMGR_DIVIDER_OK);
    assert(value == 25769U);
    assert(open_cfw_clkmgr_hfrc2_uq15_divider(
               250000000U, 125000000U, 1U, &value) ==
           OPEN_CFW_CLKMGR_DIVIDER_OK);
    assert(value == 32768U);
    assert(open_cfw_clkmgr_hfrc2_uq15_divider(
               1U, 1U, 31U, &value) ==
           OPEN_CFW_CLKMGR_DIVIDER_INVALID_ARGUMENT);
    assert(value == 32768U);
    assert(open_cfw_clkmgr_hfrc_integer_divider(0U, 1U, &value) ==
           OPEN_CFW_CLKMGR_DIVIDER_INVALID_ARGUMENT);
    assert(value == 32768U);
    assert(open_cfw_clkmgr_hfrc2_uq15_divider(
               1U, 1U, 0U, 0) ==
           OPEN_CFW_CLKMGR_DIVIDER_INVALID_ARGUMENT);
    return 0;
}
