/* SPDX-License-Identifier: MIT */
#include "runtime_none_source_admission.h"

/*
 * FreeType is materialized in g2/third_party/freetype under the FTL, including
 * Adobe's file-specific notices/grant in psft.c.  SEGGER is materialized under
 * its retained upstream terms but remains a separately licensed provider.
 * The third row accounts for the four non-census
 * boundaries and is never a callable implementation provider.
 */
const open_cfw_none_provider_t open_cfw_none_source_providers[3] = {
    {OPEN_CFW_NONE_PROVIDER_FREETYPE_FTL, 192u, 33124u, 1u, 0u},
    {OPEN_CFW_NONE_PROVIDER_SEGGER_RTT_UPSTREAM, 6u, 520u, 1u, 0u},
    {OPEN_CFW_NONE_PROVIDER_TYPED_EXTERNAL, 4u, 1118u, 0u, 0u},
};

const size_t open_cfw_none_source_provider_count =
    sizeof(open_cfw_none_source_providers) /
    sizeof(open_cfw_none_source_providers[0]);

const open_cfw_none_provider_t *
open_cfw_none_source_provider(open_cfw_none_provider_kind_t kind)
{
    size_t i;
    for (i = 0u; i < open_cfw_none_source_provider_count; ++i) {
        if (open_cfw_none_source_providers[i].kind == kind) {
            return &open_cfw_none_source_providers[i];
        }
    }
    return (const open_cfw_none_provider_t *)0;
}

int open_cfw_none_source_admission_validate(void)
{
    const open_cfw_none_provider_t *ft =
        open_cfw_none_source_provider(OPEN_CFW_NONE_PROVIDER_FREETYPE_FTL);
    const open_cfw_none_provider_t *rtt =
        open_cfw_none_source_provider(OPEN_CFW_NONE_PROVIDER_SEGGER_RTT_UPSTREAM);
    const open_cfw_none_provider_t *boundary =
        open_cfw_none_source_provider(OPEN_CFW_NONE_PROVIDER_TYPED_EXTERNAL);

    if (ft == (const open_cfw_none_provider_t *)0 ||
        rtt == (const open_cfw_none_provider_t *)0 ||
        boundary == (const open_cfw_none_provider_t *)0) {
        return 0;
    }
    if (ft->function_count + rtt->function_count != 198u ||
        ft->image_bytes + rtt->image_bytes != 33644u) {
        return 0;
    }
    if (boundary->function_count != 4u || boundary->image_bytes != 1118u) {
        return 0;
    }
    if (ft->binary_overlay_admitted != 0u ||
        rtt->binary_overlay_admitted != 0u ||
        boundary->binary_overlay_admitted != 0u) {
        return 0;
    }
    return 1;
}
