/* SPDX-License-Identifier: MIT */
#include "runtime_none_source_admission.h"

/* Freestanding link entry used only by the software admission test. */
int open_cfw_none_cortex_m55_harness(void)
{
    const open_cfw_none_provider_t *ft =
        open_cfw_none_source_provider(OPEN_CFW_NONE_PROVIDER_FREETYPE_FTL);
    const open_cfw_none_provider_t *rtt =
        open_cfw_none_source_provider(OPEN_CFW_NONE_PROVIDER_SEGGER_RTT_UPSTREAM);

    if (!open_cfw_none_source_admission_validate()) {
        return 1;
    }
    if (ft == (const open_cfw_none_provider_t *)0 || ft->source_materialized != 1u) {
        return 2;
    }
    if (rtt == (const open_cfw_none_provider_t *)0 || rtt->source_materialized != 1u) {
        return 3;
    }
    return 0;
}
