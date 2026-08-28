/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_none_batch2_candidate.h"
#define FT_LICENSE "FreeType Project License; retained file-specific notices and grants"

/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_none_batch2_evidence_t evidence[] = {
    { 0x005D70A4u, 0x005D70C6u, 34u, "pshalgo.c", "psh_hint_overlap", FT_LICENSE },
    { 0x005D70C6u, 0x005D7106u, 64u, "pshalgo.c", "psh_hint_table_done", FT_LICENSE },
    { 0x005D7106u, 0x005D7124u, 30u, "pshalgo.c", "psh_hint_table_deactivate", FT_LICENSE },
    { 0x005D7124u, 0x005D718Au, 102u, "pshalgo.c", "psh_hint_table_record", FT_LICENSE },
    { 0x005D718Au, 0x005D71C4u, 58u, "pshalgo.c", "psh_hint_table_record_mask", FT_LICENSE },
    { 0x005D71C4u, 0x005D72A8u, 228u, "pshalgo.c", "psh_hint_table_init", FT_LICENSE },
    { 0x005D72A8u, 0x005D7340u, 152u, "pshalgo.c", "psh_hint_table_activate_mask", FT_LICENSE },
    { 0x005D7340u, 0x005D739Cu, 92u, "pshalgo.c", "psh_dimension_quantize_len", FT_LICENSE },
    { 0x005D739Cu, 0x005D73D0u, 52u, "pshalgo.c", "psh_hint_snap_stem_side_delta", FT_LICENSE },
    { 0x005D73D0u, 0x005D75EEu, 542u, "pshalgo.c", "psh_hint_align", FT_LICENSE },
    { 0x005D75EEu, 0x005D761Au, 44u, "pshalgo.c", "psh_hint_table_align_hints", FT_LICENSE },
    { 0x005D761Au, 0x005D7742u, 296u, "pshalgo.c", "psh_glyph_compute_inflections", FT_LICENSE },
    { 0x005D7742u, 0x005D7782u, 64u, "pshalgo.c", "psh_glyph_done", FT_LICENSE },
    { 0x005D7782u, 0x005D77CAu, 72u, "pshalgo.c", "psh_compute_dir", FT_LICENSE },
    { 0x005D77CAu, 0x005D7802u, 56u, "pshalgo.c", "psh_glyph_load_points", FT_LICENSE },
    { 0x005D7802u, 0x005D784Au, 72u, "pshalgo.c", "psh_glyph_save_points", FT_LICENSE },
    { 0x005D784Au, 0x005D7A6Cu, 546u, "pshalgo.c", "psh_glyph_init", FT_LICENSE },
    { 0x005D7A6Cu, 0x005D7B62u, 246u, "pshalgo.c", "psh_glyph_compute_extrema", FT_LICENSE },
};

size_t open_cfw_cordio_ll_sea_none_batch2_evidence_count(void)
{ return sizeof(evidence) / sizeof(evidence[0]); }

const open_cfw_none_batch2_evidence_t *
open_cfw_cordio_ll_sea_none_batch2_evidence(size_t index)
{ return index < open_cfw_cordio_ll_sea_none_batch2_evidence_count() ? &evidence[index] : NULL; }

const open_cfw_none_batch2_evidence_t *
open_cfw_cordio_ll_sea_none_batch2_evidence_by_address(uint32_t address)
{
    size_t i;
    for (i = 0; i < open_cfw_cordio_ll_sea_none_batch2_evidence_count(); ++i)
        if (evidence[i].start == address) return &evidence[i];
    return NULL;
}

int open_cfw_cordio_ll_sea_none_batch2_candidate(
    uint32_t address, open_cfw_none_batch2_provider_t provider, void *context,
    open_cfw_none_batch2_invocation_t *invocation)
{
    const open_cfw_none_batch2_evidence_t *item;
    if (invocation == NULL) return 1;
    item = open_cfw_cordio_ll_sea_none_batch2_evidence_by_address(address);
    if (item == NULL) return 2;
    if (provider == NULL) return 3;
    return provider(context, item->module, item->function, invocation) == 0 ? 0 : 4;
}
#undef FT_LICENSE
