/* SPDX-License-Identifier: MIT */
#define OPEN_CFW_SYSPLL_POSTDIV_HOST_TEST 1
#include "../../components/bootloader/core_overlay/runtime_syspll_postdiv_427160.c"

const open_cfw_syspll_postdiv_u32 open_cfw_host_syspll_pts_a[4] = {
    435700U, 465700U, 131525U, 139025U,
};
const open_cfw_syspll_postdiv_u32 open_cfw_host_syspll_pts_b[4] = {
    228000U, 396000U, 228000U, 396000U,
};

static open_cfw_syspll_postdiv_config open_cfw_host_low;
static open_cfw_syspll_postdiv_config open_cfw_host_high;
static open_cfw_syspll_postdiv_u32 open_cfw_host_low_status;
static open_cfw_syspll_postdiv_u32 open_cfw_host_high_status;

void open_cfw_host_syspll_postdiv_set_candidates(
    const open_cfw_syspll_postdiv_config *low,
    open_cfw_syspll_postdiv_u32 low_status,
    const open_cfw_syspll_postdiv_config *high,
    open_cfw_syspll_postdiv_u32 high_status)
{
    open_cfw_host_low = *low;
    open_cfw_host_high = *high;
    open_cfw_host_low_status = low_status;
    open_cfw_host_high_status = high_status;
}

open_cfw_syspll_postdiv_u32 open_cfw_bootloader_syspll_min_fvco_427040(
    open_cfw_syspll_postdiv_config *output,
    open_cfw_syspll_postdiv_u32 reference_hz,
    open_cfw_syspll_postdiv_u32 output_hz,
    open_cfw_syspll_postdiv_u32 minimum_vco_hz)
{
    (void)reference_hz;
    (void)output_hz;
    if (minimum_vco_hz == 60000000U) {
        *output = open_cfw_host_low;
        return open_cfw_host_low_status;
    }
    *output = open_cfw_host_high;
    return open_cfw_host_high_status;
}
