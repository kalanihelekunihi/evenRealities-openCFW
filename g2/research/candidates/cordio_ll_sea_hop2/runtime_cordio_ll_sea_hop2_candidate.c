/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_hop2_candidate.h"

#define FT_LICENSE "FreeType Project License plus retained Adobe patent grant"
#define FT(module_, function_) \
    OPEN_CFW_HOP2_UPSTREAM_FREETYPE, module_, function_, FT_LICENSE
#define EXT OPEN_CFW_HOP2_TYPED_EXTERNAL, NULL, NULL, NULL

/*
 * The corrected census supplies reachability topology only.  Authenticated
 * bodies and source order identify the entries marked FT below as FreeType's
 * Adobe CFF engine.  This Apache-2.0 file is only a bounded integration
 * adapter.  It neither copies nor relicenses the upstream implementation.
 */
static const open_cfw_hop2_evidence_t hop2_evidence[] = {
    { 0x005D185Eu, 0x005D188Au, 44u, EXT },
    { 0x005D1986u, 0x005D1A38u, 178u, EXT },
    { 0x005D1D1Cu, 0x005D1D2Au, 14u, FT("psobjs.c", "cff_random") },
    { 0x005D1ED0u, 0x005D1F26u, 86u, EXT },
    { 0x005D22F2u, 0x005D230Eu, 28u, FT("psarrst.c", "cf2_arrstack_init") },
    { 0x005D230Eu, 0x005D232Cu, 30u, FT("psarrst.c", "cf2_arrstack_finalize") },
    { 0x005D2390u, 0x005D23ACu, 28u, FT("psarrst.c", "cf2_arrstack_setCount") },
    { 0x005D23ACu, 0x005D23B2u, 6u, FT("psarrst.c", "cf2_arrstack_clear") },
    { 0x005D23B2u, 0x005D23B6u, 4u, FT("psarrst.c", "cf2_arrstack_size") },
    { 0x005D23B6u, 0x005D23BAu, 4u, FT("psarrst.c", "cf2_arrstack_getBuffer") },
    { 0x005D23BAu, 0x005D23DAu, 32u, FT("psarrst.c", "cf2_arrstack_getPointer") },
    { 0x005D2EA8u, 0x005D2EE4u, 60u, FT("psft.c", "cf2_checkTransform") },
    { 0x005D2EE4u, 0x005D2EFEu, 26u, FT("psft.c", "cf2_setGlyphWidth") },
    { 0x005D2FEEu, 0x005D3014u, 38u, FT("psft.c", "cf2_outline_init") },
    { 0x005D3018u, 0x005D3060u, 72u, FT("psft.c", "cf2_getScaleAndHintFlag") },
    { 0x005D3060u, 0x005D3068u, 8u, FT("psft.c", "cf2_getUnitsPerEm") },
    { 0x005D3248u, 0x005D3252u, 10u, FT("psft.c", "cf2_getMaxstack") },
    { 0x005D328Au, 0x005D32C0u, 54u, FT("psft.c", "cf2_getBlueMetrics") },
    { 0x005D32C0u, 0x005D32D4u, 20u, FT("psft.c", "cf2_getBlueValues") },
    { 0x005D32D4u, 0x005D32E8u, 20u, FT("psft.c", "cf2_getOtherBlues") },
    { 0x005D32E8u, 0x005D32FEu, 22u, FT("psft.c", "cf2_getFamilyBlues") },
    { 0x005D32FEu, 0x005D3314u, 22u, FT("psft.c", "cf2_getFamilyOtherBlues") },
    { 0x005D3314u, 0x005D331Eu, 10u, FT("psft.c", "cf2_getLanguageGroup") },
    { 0x005D331Eu, 0x005D3362u, 68u, FT("psft.c", "cf2_initGlobalRegionBuffer") },
    { 0x005D3362u, 0x005D33BEu, 92u, FT("psft.c", "cf2_getSeacComponent") },
    { 0x005D33BEu, 0x005D33D4u, 22u, FT("psft.c", "cf2_freeSeacComponent") },
    { 0x005D33D4u, 0x005D3434u, 96u, FT("psft.c", "cf2_getT1SeacComponent") },
    { 0x005D3434u, 0x005D3466u, 50u, FT("psft.c", "cf2_freeT1SeacComponent") },
    { 0x005D3466u, 0x005D34F4u, 142u, FT("psft.c", "cf2_initLocalRegionBuffer") },
    { 0x005D34F4u, 0x005D3500u, 12u, FT("psft.c", "cf2_getDefaultWidthX") },
    { 0x005D3500u, 0x005D350Cu, 12u, FT("psft.c", "cf2_getNominalWidthX") },
    { 0x005D36B8u, 0x005D36EAu, 50u, EXT },
    { 0x005D3C0Au, 0x005D3ED0u, 710u, EXT },
    { 0x005D3ED0u, 0x005D4032u, 354u, EXT },
    { 0x005D4032u, 0x005D4040u, 14u, EXT },
    { 0x005D4754u, 0x005D47D4u, 128u, EXT },
    { 0x005D47D4u, 0x005D4912u, 318u, EXT },
    { 0x005D4912u, 0x005D4A94u, 386u, EXT },
    { 0x005D4A94u, 0x005D4AFEu, 106u, EXT },
    { 0x005D4AFEu, 0x005D4B14u, 22u, FT("psintrp.c", "cf2_hintmask_init") },
    { 0x005D4B14u, 0x005D4B18u, 4u, FT("psintrp.c", "cf2_hintmask_isValid") },
    { 0x005D4B4Cu, 0x005D4B78u, 44u, FT("psintrp.c", "cf2_hintmask_read") },
    { 0x005D4BBAu, 0x005D4C88u, 206u, EXT },
    { 0x005D4C88u, 0x005D4E40u, 440u, EXT },
    { 0x005D4E40u, 0x005D4ECEu, 142u, EXT },
    { 0x005D6D98u, 0x005D6DB8u, 32u, FT("psread.c", "cf2_buf_readByte") },
    { 0x005D6DB8u, 0x005D6DCAu, 18u, FT("psread.c", "cf2_buf_isEnd") },
    { 0x005D6DCAu, 0x005D6E22u, 88u, FT("psstack.c", "cf2_stack_init") },
    { 0x005D6E22u, 0x005D6E44u, 34u, FT("psstack.c", "cf2_stack_free") },
    { 0x005D6E44u, 0x005D6E50u, 12u, FT("psstack.c", "cf2_stack_count") },
    { 0x005D6E50u, 0x005D6E7Cu, 44u, FT("psstack.c", "cf2_stack_pushInt") },
    { 0x005D6E7Cu, 0x005D6EA8u, 44u, FT("psstack.c", "cf2_stack_pushFixed") },
    { 0x005D6EA8u, 0x005D6EE0u, 56u, FT("psstack.c", "cf2_stack_popInt") },
    { 0x005D6EE0u, 0x005D6F38u, 88u, FT("psstack.c", "cf2_stack_popFixed") },
    { 0x005D6F38u, 0x005D6F9Eu, 102u, FT("psstack.c", "cf2_stack_getReal") },
    { 0x005D6F9Eu, 0x005D6FCCu, 46u, FT("psstack.c", "cf2_stack_setReal") },
    { 0x005D6FCCu, 0x005D6FF2u, 38u, FT("psstack.c", "cf2_stack_pop") },
    { 0x005D6FF2u, 0x005D7096u, 164u, FT("psstack.c", "cf2_stack_roll") },
    { 0x005D709Cu, 0x005D70A2u, 6u, FT("psstack.c", "cf2_stack_clear") },
};

size_t open_cfw_cordio_ll_sea_hop2_evidence_count(void)
{
    return sizeof(hop2_evidence) / sizeof(hop2_evidence[0]);
}

const open_cfw_hop2_evidence_t *
open_cfw_cordio_ll_sea_hop2_evidence(size_t index)
{
    if (index >= open_cfw_cordio_ll_sea_hop2_evidence_count()) {
        return NULL;
    }
    return &hop2_evidence[index];
}

const open_cfw_hop2_evidence_t *
open_cfw_cordio_ll_sea_hop2_evidence_by_address(uint32_t stock_start)
{
    size_t i;
    for (i = 0; i < open_cfw_cordio_ll_sea_hop2_evidence_count(); ++i) {
        if (hop2_evidence[i].stock_start == stock_start) {
            return &hop2_evidence[i];
        }
    }
    return NULL;
}

open_cfw_hop2_status_t open_cfw_cordio_ll_sea_hop2_candidate(
    uint32_t stock_start,
    open_cfw_hop2_upstream_provider_t provider,
    void *provider_context,
    open_cfw_hop2_invocation_t *invocation)
{
    const open_cfw_hop2_evidence_t *evidence;
    int provider_status;

    if (invocation == NULL) {
        return OPEN_CFW_HOP2_INVALID_ARGUMENT;
    }
    evidence = open_cfw_cordio_ll_sea_hop2_evidence_by_address(stock_start);
    if (evidence == NULL) {
        return OPEN_CFW_HOP2_UNKNOWN_ADDRESS;
    }
    if (evidence->disposition != OPEN_CFW_HOP2_UPSTREAM_FREETYPE) {
        return OPEN_CFW_HOP2_UNSUPPORTED_EXTERNAL;
    }
    if (provider == NULL) {
        return OPEN_CFW_HOP2_UNSUPPORTED_EXTERNAL;
    }
    provider_status = provider(provider_context, evidence->upstream_module,
                               evidence->upstream_function, invocation);
    return provider_status == 0 ? OPEN_CFW_HOP2_OK
                                : OPEN_CFW_HOP2_PROVIDER_FAILED;
}

#undef EXT
#undef FT
#undef FT_LICENSE
