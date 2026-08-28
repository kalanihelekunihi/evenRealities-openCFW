/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_none_batch9_candidate.h"

#define FT_LICENSE \
  "FreeType Project License; retained file-specific notices and grants"

/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_none_batch9_evidence_t evidence[] = {
  { 0x005DC542u, 0x005DC5B4u, 114u, "ttcmap.c", "tt_cmap0_validate", FT_LICENSE },
  { 0x005DC600u, 0x005DC790u, 400u, "ttcmap.c", "tt_cmap2_validate", FT_LICENSE },
  { 0x005DC790u, 0x005DC7E2u, 82u, "ttcmap.c", "tt_cmap2_get_subheader", FT_LICENSE },
  { 0x005DD584u, 0x005DD780u, 508u, "ttcmap.c", "tt_cmap8_validate", FT_LICENSE },
  { 0x005DD780u, 0x005DD832u, 178u, "ttcmap.c", "tt_cmap8_char_index", FT_LICENSE },
  { 0x005DD832u, 0x005DD934u, 258u, "ttcmap.c", "tt_cmap8_char_next", FT_LICENSE },
  { 0x005DDB3Au, 0x005DDC74u, 314u, "ttcmap.c", "tt_cmap12_validate", FT_LICENSE },
  { 0x005DDC74u, 0x005DDD38u, 196u, "ttcmap.c", "tt_cmap12_next", FT_LICENSE },
  { 0x005DDEF8u, 0x005DE026u, 302u, "ttcmap.c", "tt_cmap13_validate", FT_LICENSE },
  { 0x005DE026u, 0x005DE0CAu, 164u, "ttcmap.c", "tt_cmap13_next", FT_LICENSE },
  { 0x005DE270u, 0x005DE2A8u, 56u, "ttcmap.c", "tt_cmap14_ensure", FT_LICENSE },
  { 0x005DE2CEu, 0x005DE576u, 680u, "ttcmap.c", "tt_cmap14_validate", FT_LICENSE },
  { 0x005DE590u, 0x005DE5EEu, 94u, "ttcmap.c", "tt_cmap14_char_map_def_binary", FT_LICENSE },
  { 0x005DE5EEu, 0x005DE652u, 100u, "ttcmap.c", "tt_cmap14_char_map_nondef_binary", FT_LICENSE },
  { 0x005DE652u, 0x005DE6ACu, 90u, "ttcmap.c", "tt_cmap14_find_variant", FT_LICENSE },
  { 0x005DE6ACu, 0x005DE72Au, 126u, "ttcmap.c", "tt_cmap14_char_var_index", FT_LICENSE },
  { 0x005DE8C2u, 0x005DE8F6u, 52u, "ttcmap.c", "tt_cmap14_def_char_count", FT_LICENSE },
  { 0x005DE8F6u, 0x005DE970u, 122u, "ttcmap.c", "tt_cmap14_get_def_chars", FT_LICENSE },
  { 0x005DE970u, 0x005DE9D2u, 98u, "ttcmap.c", "tt_cmap14_get_nondef_chars", FT_LICENSE },
  { 0x005DE9D2u, 0x005DEC32u, 608u, "ttcmap.c", "tt_cmap14_variant_chars", FT_LICENSE },
};

size_t open_cfw_cordio_ll_sea_none_batch9_evidence_count(void) {
  return sizeof(evidence) / sizeof(evidence[0]);
}

const open_cfw_none_batch9_evidence_t *
open_cfw_cordio_ll_sea_none_batch9_evidence(size_t index) {
  return index < open_cfw_cordio_ll_sea_none_batch9_evidence_count()
             ? &evidence[index]
             : NULL;
}

const open_cfw_none_batch9_evidence_t *
open_cfw_cordio_ll_sea_none_batch9_evidence_by_address(uint32_t address) {
  size_t index;
  for (index = 0; index < open_cfw_cordio_ll_sea_none_batch9_evidence_count();
       ++index) {
    if (evidence[index].start == address)
      return &evidence[index];
  }
  return NULL;
}

int open_cfw_cordio_ll_sea_none_batch9_candidate(
    uint32_t address, open_cfw_none_batch9_provider_t provider, void *context,
    open_cfw_none_batch9_invocation_t *invocation) {
  const open_cfw_none_batch9_evidence_t *record;
  if (invocation == NULL)
    return 1;
  record = open_cfw_cordio_ll_sea_none_batch9_evidence_by_address(address);
  if (record == NULL)
    return 2;
  if (provider == NULL)
    return 3;
  return provider(context, record->module, record->function, invocation) == 0
             ? 0
             : 4;
}

#undef FT_LICENSE
