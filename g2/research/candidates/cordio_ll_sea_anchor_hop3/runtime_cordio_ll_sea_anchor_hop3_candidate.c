/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_anchor_hop3_candidate.h"

#define FT_LICENSE "FreeType Project License; retained file-specific notices and grants"

/* Research-only identity and provider adapter; no upstream body is copied. */
static const open_cfw_sea_source_evidence_t evidence[] = {
    { 0x005D2196u, 0x005D21E4u, 78u, OPEN_CFW_SEA_HOP3, "cffdecode.c", "cff_lookup_glyph_by_stdcharcode", FT_LICENSE },
    { 0x005D232Cu, 0x005D2390u, 100u, OPEN_CFW_SEA_HOP3, "psarrst.c", "cf2_arrstack_setNumElements", FT_LICENSE },
    { 0x005D23DAu, 0x005D2418u, 62u, OPEN_CFW_SEA_HOP3, "psarrst.c", "cf2_arrstack_push", FT_LICENSE },
    { 0x005D2418u, 0x005D280Eu, 1014u, OPEN_CFW_SEA_ANCHOR, "psblues.c", "cf2_blues_init", FT_LICENSE },
    { 0x005D2828u, 0x005D2A0Au, 482u, OPEN_CFW_SEA_HOP3, "psblues.c", "cf2_blues_capture", FT_LICENSE },
    { 0x005D2A0Au, 0x005D2A18u, 14u, OPEN_CFW_SEA_ANCHOR, "pserror.c", "cf2_setError", FT_LICENSE },
    { 0x005D2A18u, 0x005D2BAEu, 406u, OPEN_CFW_SEA_ANCHOR, "psfont.c", "cf2_computeDarkening", FT_LICENSE },
    { 0x005D3238u, 0x005D323Eu, 6u, OPEN_CFW_SEA_ANCHOR, "psft.c", "cf2_getSubfont", FT_LICENSE },
    { 0x005D323Eu, 0x005D3248u, 10u, OPEN_CFW_SEA_ANCHOR, "psft.c", "cf2_getVStore", FT_LICENSE },
    { 0x005D3252u, 0x005D3268u, 22u, OPEN_CFW_SEA_ANCHOR, "psft.c", "cf2_getNormalizedVector", FT_LICENSE },
    { 0x005D3268u, 0x005D3272u, 10u, OPEN_CFW_SEA_ANCHOR, "psft.c", "cf2_getPpemY", FT_LICENSE },
    { 0x005D3272u, 0x005D327Eu, 12u, OPEN_CFW_SEA_ANCHOR, "psft.c", "cf2_getStdVW", FT_LICENSE },
    { 0x005D327Eu, 0x005D328Au, 12u, OPEN_CFW_SEA_ANCHOR, "psft.c", "cf2_getStdHW", FT_LICENSE },
    { 0x005D350Cu, 0x005D351Cu, 16u, OPEN_CFW_SEA_ANCHOR, "psft.c", "cf2_outline_reset", FT_LICENSE },
    { 0x005D351Cu, 0x005D352Eu, 18u, OPEN_CFW_SEA_ANCHOR, "psft.c", "cf2_outline_close", FT_LICENSE },
    { 0x005D352Eu, 0x005D3544u, 22u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_getWindingMomentum", FT_LICENSE },
    { 0x005D3544u, 0x005D3634u, 240u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_hint_init", FT_LICENSE },
    { 0x005D3634u, 0x005D3644u, 16u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_hint_initZero", FT_LICENSE },
    { 0x005D3672u, 0x005D3684u, 18u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_hint_isTop", FT_LICENSE },
    { 0x005D3696u, 0x005D36A2u, 12u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_hint_isLocked", FT_LICENSE },
    { 0x005D36A2u, 0x005D36AEu, 12u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_hint_isSynthetic", FT_LICENSE },
    { 0x005D36B8u, 0x005D36EAu, 50u, OPEN_CFW_SEA_HOP2_REFINEMENT, "pshints.c", "cf2_hintmap_init", FT_LICENSE },
    { 0x005D36EAu, 0x005D36EEu, 4u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_hintmap_isValid", FT_LICENSE },
    { 0x005D36EEu, 0x005D36F0u, 2u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_hintmap_dump", FT_LICENSE },
    { 0x005D377Cu, 0x005D3A2Au, 686u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_hintmap_adjustHints", FT_LICENSE },
    { 0x005D3A2Au, 0x005D3C0Au, 480u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_hintmap_insertHint", FT_LICENSE },
    { 0x005D3C0Au, 0x005D3ED0u, 710u, OPEN_CFW_SEA_HOP2_REFINEMENT, "pshints.c", "cf2_hintmap_build", FT_LICENSE },
    { 0x005D3ED0u, 0x005D4032u, 354u, OPEN_CFW_SEA_HOP2_REFINEMENT, "pshints.c", "cf2_glyphpath_init", FT_LICENSE },
    { 0x005D4032u, 0x005D4040u, 14u, OPEN_CFW_SEA_HOP2_REFINEMENT, "pshints.c", "cf2_glyphpath_finalize", FT_LICENSE },
    { 0x005D431Eu, 0x005D4510u, 498u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_glyphpath_pushPrevElem", FT_LICENSE },
    { 0x005D4510u, 0x005D4582u, 114u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_glyphpath_pushMove", FT_LICENSE },
    { 0x005D4582u, 0x005D474Au, 456u, OPEN_CFW_SEA_HOP3, "pshints.c", "cf2_glyphpath_computeOffset", FT_LICENSE },
    { 0x005D4754u, 0x005D47D4u, 128u, OPEN_CFW_SEA_HOP2_REFINEMENT, "pshints.c", "cf2_glyphpath_moveTo", FT_LICENSE },
    { 0x005D47D4u, 0x005D4912u, 318u, OPEN_CFW_SEA_HOP2_REFINEMENT, "pshints.c", "cf2_glyphpath_lineTo", FT_LICENSE },
    { 0x005D4912u, 0x005D4A94u, 386u, OPEN_CFW_SEA_HOP2_REFINEMENT, "pshints.c", "cf2_glyphpath_curveTo", FT_LICENSE },
    { 0x005D4A94u, 0x005D4AFEu, 106u, OPEN_CFW_SEA_HOP2_REFINEMENT, "pshints.c", "cf2_glyphpath_closeOpenPath", FT_LICENSE },
    { 0x005D4B18u, 0x005D4B1Cu, 4u, OPEN_CFW_SEA_HOP3, "psintrp.c", "cf2_hintmask_isNew", FT_LICENSE },
    { 0x005D4B1Cu, 0x005D4B20u, 4u, OPEN_CFW_SEA_HOP3, "psintrp.c", "cf2_hintmask_setNew", FT_LICENSE },
    { 0x005D4B20u, 0x005D4B24u, 4u, OPEN_CFW_SEA_HOP3, "psintrp.c", "cf2_hintmask_getMaskPtr", FT_LICENSE },
    { 0x005D4B24u, 0x005D4B4Cu, 40u, OPEN_CFW_SEA_HOP3, "psintrp.c", "cf2_hintmask_setCounts", FT_LICENSE },
    { 0x005D4B78u, 0x005D4BBAu, 66u, OPEN_CFW_SEA_HOP3, "psintrp.c", "cf2_hintmask_setAll", FT_LICENSE },
    { 0x005D4BBAu, 0x005D4C88u, 206u, OPEN_CFW_SEA_HOP2_REFINEMENT, "psintrp.c", "cf2_doStems", FT_LICENSE },
    { 0x005D4C88u, 0x005D4E40u, 440u, OPEN_CFW_SEA_HOP2_REFINEMENT, "psintrp.c", "cf2_doFlex", FT_LICENSE },
    { 0x005D4E40u, 0x005D4ECEu, 142u, OPEN_CFW_SEA_HOP2_REFINEMENT, "psintrp.c", "cf2_doBlend", FT_LICENSE },
    { 0x005D4ED0u, 0x005D6D98u, 7880u, OPEN_CFW_SEA_ANCHOR, "psintrp.c", "cf2_interpT2CharString", FT_LICENSE },
};

size_t open_cfw_cordio_ll_sea_anchor_hop3_evidence_count(void)
{
    return sizeof(evidence) / sizeof(evidence[0]);
}

const open_cfw_sea_source_evidence_t *
open_cfw_cordio_ll_sea_anchor_hop3_evidence(size_t index)
{
    return index < open_cfw_cordio_ll_sea_anchor_hop3_evidence_count()
               ? &evidence[index] : NULL;
}

const open_cfw_sea_source_evidence_t *
open_cfw_cordio_ll_sea_anchor_hop3_evidence_by_address(uint32_t stock_start)
{
    size_t i;
    for (i = 0; i < open_cfw_cordio_ll_sea_anchor_hop3_evidence_count(); ++i) {
        if (evidence[i].stock_start == stock_start) return &evidence[i];
    }
    return NULL;
}

open_cfw_sea_source_status_t open_cfw_cordio_ll_sea_anchor_hop3_candidate(
    uint32_t stock_start, open_cfw_sea_source_provider_t provider,
    void *provider_context, open_cfw_sea_source_invocation_t *invocation)
{
    const open_cfw_sea_source_evidence_t *item;
    if (invocation == NULL) return OPEN_CFW_SEA_SOURCE_INVALID_ARGUMENT;
    item = open_cfw_cordio_ll_sea_anchor_hop3_evidence_by_address(stock_start);
    if (item == NULL) return OPEN_CFW_SEA_SOURCE_UNKNOWN_ADDRESS;
    if (provider == NULL) return OPEN_CFW_SEA_SOURCE_PROVIDER_MISSING;
    return provider(provider_context, item->upstream_module,
                    item->upstream_function, invocation) == 0
               ? OPEN_CFW_SEA_SOURCE_OK : OPEN_CFW_SEA_SOURCE_PROVIDER_FAILED;
}

#undef FT_LICENSE
