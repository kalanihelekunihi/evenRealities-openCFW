/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_hop4_residue_candidate.h"

#define FT_LICENSE "FreeType Project License; retained file-specific notices and grants"

/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_sea_residue_evidence_t evidence[] = {
    { 0x005D185Eu, 0x005D188Au, 44u, OPEN_CFW_SEA_RESIDUE_HOP2, "psobjs.c", "ps_builder_check_points", FT_LICENSE },
    { 0x005D1986u, 0x005D1A38u, 178u, OPEN_CFW_SEA_RESIDUE_HOP2, "psobjs.c", "ps_builder_close_contour", FT_LICENSE },
    { 0x005D1ED0u, 0x005D1F26u, 86u, OPEN_CFW_SEA_RESIDUE_HOP2, "t1decode.c", "t1_lookup_glyph_by_stdcharcode_ps", FT_LICENSE },
    { 0x005D3068u, 0x005D3228u, 448u, OPEN_CFW_SEA_RESIDUE_ISLAND_CALLER, "psft.c", "cf2_decoder_parse_charstrings", FT_LICENSE },
    { 0x005D3644u, 0x005D3654u, 16u, OPEN_CFW_SEA_RESIDUE_HOP4, "pshints.c", "cf2_hint_isValid", FT_LICENSE },
    { 0x005D3654u, 0x005D3666u, 18u, OPEN_CFW_SEA_RESIDUE_HOP4, "pshints.c", "cf2_hint_isPair", FT_LICENSE },
    { 0x005D3666u, 0x005D3672u, 12u, OPEN_CFW_SEA_RESIDUE_HOP4, "pshints.c", "cf2_hint_isPairTop", FT_LICENSE },
    { 0x005D3684u, 0x005D3696u, 18u, OPEN_CFW_SEA_RESIDUE_HOP4, "pshints.c", "cf2_hint_isBottom", FT_LICENSE },
    { 0x005D36AEu, 0x005D36B8u, 10u, OPEN_CFW_SEA_RESIDUE_HOP4, "pshints.c", "cf2_hint_lock", FT_LICENSE },
    { 0x005D36F0u, 0x005D377Cu, 140u, OPEN_CFW_SEA_RESIDUE_HOP4, "pshints.c", "cf2_hintmap_map", FT_LICENSE },
    { 0x005D4040u, 0x005D40C0u, 128u, OPEN_CFW_SEA_RESIDUE_HOP4, "pshints.c", "cf2_glyphpath_hintPoint", FT_LICENSE },
    { 0x005D40C0u, 0x005D431Eu, 606u, OPEN_CFW_SEA_RESIDUE_HOP4, "pshints.c", "cf2_glyphpath_computeIntersection", FT_LICENSE },
};

size_t open_cfw_cordio_ll_sea_hop4_residue_evidence_count(void)
{
    return sizeof(evidence) / sizeof(evidence[0]);
}

const open_cfw_sea_residue_evidence_t *
open_cfw_cordio_ll_sea_hop4_residue_evidence(size_t index)
{
    return index < open_cfw_cordio_ll_sea_hop4_residue_evidence_count()
               ? &evidence[index] : NULL;
}

const open_cfw_sea_residue_evidence_t *
open_cfw_cordio_ll_sea_hop4_residue_evidence_by_address(uint32_t address)
{
    size_t i;
    for (i = 0; i < open_cfw_cordio_ll_sea_hop4_residue_evidence_count(); ++i)
        if (evidence[i].stock_start == address) return &evidence[i];
    return NULL;
}

int open_cfw_cordio_ll_sea_hop4_residue_candidate(
    uint32_t address, open_cfw_sea_residue_provider_t provider, void *context,
    open_cfw_sea_residue_invocation_t *invocation)
{
    const open_cfw_sea_residue_evidence_t *item;
    if (invocation == NULL) return 1;
    item = open_cfw_cordio_ll_sea_hop4_residue_evidence_by_address(address);
    if (item == NULL) return 2;
    if (provider == NULL) return 3;
    return provider(context, item->upstream_module, item->upstream_function,
                    invocation) == 0 ? 0 : 4;
}

#undef FT_LICENSE
