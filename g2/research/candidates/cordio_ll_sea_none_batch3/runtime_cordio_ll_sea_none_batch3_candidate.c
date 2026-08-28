/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_none_batch3_candidate.h"
#define FT_LICENSE "FreeType Project License; retained file-specific notices and grants"
/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_none_batch3_evidence_t evidence[] = {
    { 0x005D7B62u, 0x005D7D1Cu, 442u, "pshalgo.c", "psh_hint_table_find_strong_points", FT_LICENSE },
    { 0x005D7D1Cu, 0x005D7E1Au, 254u, "pshalgo.c", "psh_glyph_find_strong_points", FT_LICENSE },
    { 0x005D7E1Au, 0x005D7F04u, 234u, "pshalgo.c", "psh_glyph_find_blue_points", FT_LICENSE },
    { 0x005D7F04u, 0x005D7F90u, 140u, "pshalgo.c", "psh_glyph_interpolate_strong_points", FT_LICENSE },
    { 0x005D7F90u, 0x005D816Cu, 476u, "pshalgo.c", "psh_glyph_interpolate_normal_points", FT_LICENSE },
    { 0x005D816Cu, 0x005D82C8u, 348u, "pshalgo.c", "psh_glyph_interpolate_other_points", FT_LICENSE },
    { 0x005D82C8u, 0x005D843Au, 370u, "pshalgo.c", "ps_hints_apply", FT_LICENSE },
    { 0x005D843Au, 0x005D849Au, 96u, "pshglob.c", "psh_globals_scale_widths", FT_LICENSE },
    { 0x005D849Au, 0x005D857Cu, 226u, "pshglob.c", "psh_blues_set_zones_0", FT_LICENSE },
    { 0x005D857Cu, 0x005D868Au, 270u, "pshglob.c", "psh_blues_set_zones", FT_LICENSE },
    { 0x005D868Au, 0x005D87FAu, 368u, "pshglob.c", "psh_blues_scale_zones", FT_LICENSE },
    { 0x005D87FAu, 0x005D8828u, 46u, "pshglob.c", "psh_calc_max_height", FT_LICENSE },
    { 0x005D8828u, 0x005D88D4u, 172u, "pshglob.c", "psh_blues_snap_stem", FT_LICENSE },
    { 0x005D88D4u, 0x005D8908u, 52u, "pshglob.c", "psh_globals_destroy", FT_LICENSE },
    { 0x005D8A48u, 0x005D8AA4u, 92u, "pshglob.c", "psh_globals_set_scale", FT_LICENSE },
    { 0x005D8AA4u, 0x005D8AB8u, 20u, "pshglob.c", "psh_globals_funcs_init", FT_LICENSE },
};
size_t open_cfw_cordio_ll_sea_none_batch3_evidence_count(void)
{ return sizeof(evidence) / sizeof(evidence[0]); }
const open_cfw_none_batch3_evidence_t *open_cfw_cordio_ll_sea_none_batch3_evidence(size_t index)
{ return index < open_cfw_cordio_ll_sea_none_batch3_evidence_count() ? &evidence[index] : NULL; }
const open_cfw_none_batch3_evidence_t *open_cfw_cordio_ll_sea_none_batch3_evidence_by_address(uint32_t address)
{
    size_t i;
    for (i=0;i<open_cfw_cordio_ll_sea_none_batch3_evidence_count();++i)
        if (evidence[i].start == address) return &evidence[i];
    return NULL;
}
int open_cfw_cordio_ll_sea_none_batch3_candidate(
    uint32_t address, open_cfw_none_batch3_provider_t provider, void *context,
    open_cfw_none_batch3_invocation_t *invocation)
{
    const open_cfw_none_batch3_evidence_t *item;
    if (invocation == NULL) return 1;
    item=open_cfw_cordio_ll_sea_none_batch3_evidence_by_address(address);
    if (item == NULL) return 2;
    if (provider == NULL) return 3;
    return provider(context,item->module,item->function,invocation)==0 ? 0 : 4;
}
#undef FT_LICENSE
