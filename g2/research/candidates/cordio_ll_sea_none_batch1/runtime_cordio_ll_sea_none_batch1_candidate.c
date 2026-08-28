/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_none_batch1_candidate.h"
#define FT_LICENSE "FreeType Project License; retained file-specific notices and grants"

/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_none_batch1_evidence_t evidence[] = {
    { 0x005D188Au, 0x005D18C8u, 62u, "psobjs.c", "ps_builder_add_point", FT_LICENSE },
    { 0x005D18C8u, 0x005D18EEu, 38u, "psobjs.c", "ps_builder_add_point1", FT_LICENSE },
    { 0x005D18EEu, 0x005D1958u, 106u, "psobjs.c", "ps_builder_add_contour", FT_LICENSE },
    { 0x005D1958u, 0x005D1986u, 46u, "psobjs.c", "ps_builder_start_point", FT_LICENSE },
    { 0x005D1A38u, 0x005D1B4Au, 274u, "psobjs.c", "ps_decoder_init", FT_LICENSE },
    { 0x005D1F26u, 0x005D20BCu, 406u, "t1decode.c", "t1_decoder_parse_metrics", FT_LICENSE },
    { 0x005D20BCu, 0x005D2138u, 124u, "t1decode.c", "t1_decoder_init", FT_LICENSE },
    { 0x005D2170u, 0x005D2196u, 38u, "cffdecode.c", "cff_compute_bias", FT_LICENSE },
    { 0x005D21E4u, 0x005D2250u, 108u, "cffdecode.c", "cff_decoder_init", FT_LICENSE },
    { 0x005D2250u, 0x005D22F2u, 162u, "cffdecode.c", "cff_decoder_prepare", FT_LICENSE },
};

size_t open_cfw_cordio_ll_sea_none_batch1_evidence_count(void)
{ return sizeof(evidence) / sizeof(evidence[0]); }

const open_cfw_none_batch1_evidence_t *
open_cfw_cordio_ll_sea_none_batch1_evidence(size_t index)
{ return index < open_cfw_cordio_ll_sea_none_batch1_evidence_count() ? &evidence[index] : NULL; }

const open_cfw_none_batch1_evidence_t *
open_cfw_cordio_ll_sea_none_batch1_evidence_by_address(uint32_t address)
{
    size_t i;
    for (i = 0; i < open_cfw_cordio_ll_sea_none_batch1_evidence_count(); ++i)
        if (evidence[i].start == address) return &evidence[i];
    return NULL;
}

int open_cfw_cordio_ll_sea_none_batch1_candidate(
    uint32_t address, open_cfw_none_batch1_provider_t provider, void *context,
    open_cfw_none_batch1_invocation_t *invocation)
{
    const open_cfw_none_batch1_evidence_t *item;
    if (invocation == NULL) return 1;
    item = open_cfw_cordio_ll_sea_none_batch1_evidence_by_address(address);
    if (item == NULL) return 2;
    if (provider == NULL) return 3;
    return provider(context, item->module, item->function, invocation) == 0 ? 0 : 4;
}
#undef FT_LICENSE
