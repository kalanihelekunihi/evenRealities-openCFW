/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_none_batch10_candidate.h"

#define FT_LICENSE \
  "FreeType Project License; retained file-specific notices and grants"

/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_none_batch10_evidence_t evidence[] = {
  { 0x005DEC32u, 0x005DEC3Eu, 12u, "ttcmap.c", "tt_get_glyph_name", FT_LICENSE, 1u },
  { 0x005DEC3Eu, 0x005DEC5Cu, 30u, "ttcmap.c", "tt_cmap_unicode_init", FT_LICENSE, 1u },
  { 0x005DEC5Cu, 0x005DEC74u, 24u, "ttcmap.c", "tt_cmap_unicode_done", FT_LICENSE, 1u },
  { 0x005DEC74u, 0x005DEC82u, 14u, "ttcmap.c", "tt_cmap_unicode_char_index", FT_LICENSE, 1u },
  { 0x005DEC82u, 0x005DEC90u, 14u, "ttcmap.c", "tt_cmap_unicode_char_next", FT_LICENSE, 1u },
  { 0x005DEC90u, 0x005DEE14u, 388u, "ttcmap.c", "tt_face_build_cmaps", FT_LICENSE, 1u },
  { 0x005DEFB6u, 0x005DEFDEu, 40u, "ttkern.c", "tt_face_done_kern", FT_LICENSE, 1u },
  { 0x005DEFDEu, 0x005DF158u, 378u, "ttkern.c", "tt_face_get_kerning", FT_LICENSE, 1u },
  { 0x005DF158u, 0x005DF182u, 42u, "ttload.c", "tt_face_lookup_table", FT_LICENSE, 1u },
  { 0x005DF182u, 0x005DF1AEu, 44u, "ttload.c", "tt_face_goto_table", FT_LICENSE, 1u },
  { 0x005DF1AEu, 0x005DF2F2u, 324u, "ttload.c", "check_table_dir", FT_LICENSE, 1u },
  { 0x005DF2F2u, 0x005DF484u, 402u, "ttload.c", "tt_face_load_font_dir", FT_LICENSE, 1u },
  { 0x005DF484u, 0x005DF4D4u, 80u, "ttload.c", "tt_face_load_any", FT_LICENSE, 1u },
  { 0x005DF4D4u, 0x005DF504u, 48u, "ttload.c", "tt_face_load_generic_header", FT_LICENSE, 1u },
  { 0x005DF504u, 0x005DF510u, 12u, "ttload.c", "tt_face_load_head", FT_LICENSE, 1u },
  { 0x005DF5B6u, 0x005DF832u, 636u, "ttload.c", "tt_face_load_name", FT_LICENSE, 1u },
  { 0x005DFB9Cu, 0x005DFD20u, 388u, "ttmtx.c", "tt_face_get_metrics", FT_LICENSE, 1u },
  { 0x005DFD20u, 0x005DFF5Au, 570u, "ttpost.c", "load_format_20", FT_LICENSE, 1u },
  { 0x005DFF5Au, 0x005E0002u, 168u, "ttpost.c", "load_format_25", FT_LICENSE, 1u },
  { 0x005E0002u, 0x005E0068u, 102u, "ttpost.c", "load_post_names", FT_LICENSE, 0u },
};

size_t open_cfw_cordio_ll_sea_none_batch10_evidence_count(void) {
  return sizeof(evidence) / sizeof(evidence[0]);
}

const open_cfw_none_batch10_evidence_t *
open_cfw_cordio_ll_sea_none_batch10_evidence(size_t index) {
  return index < open_cfw_cordio_ll_sea_none_batch10_evidence_count()
             ? &evidence[index]
             : NULL;
}

const open_cfw_none_batch10_evidence_t *
open_cfw_cordio_ll_sea_none_batch10_evidence_by_address(uint32_t address) {
  size_t index;
  for (index = 0; index < open_cfw_cordio_ll_sea_none_batch10_evidence_count();
       ++index) {
    if (evidence[index].start == address)
      return &evidence[index];
  }
  return NULL;
}

int open_cfw_cordio_ll_sea_none_batch10_candidate(
    uint32_t address, open_cfw_none_batch10_provider_t provider, void *context,
    open_cfw_none_batch10_invocation_t *invocation) {
  const open_cfw_none_batch10_evidence_t *record;
  if (invocation == NULL)
    return 1;
  record = open_cfw_cordio_ll_sea_none_batch10_evidence_by_address(address);
  if (record == NULL)
    return 2;
  if (provider == NULL)
    return 3;
  return provider(context, record->module, record->function, invocation) == 0
             ? 0
             : 4;
}

#undef FT_LICENSE
