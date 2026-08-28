/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_none_batch11_candidate.h"

#define FT_LICENSE \
  "FreeType Project License; retained file-specific notices and grants"

/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_none_batch11_evidence_t evidence[] = {
  { 0x005D008Eu, 0x005D018Au, 252u, "psconv.c", "PS_Conv_Strtol", FT_LICENSE },
  { 0x005D018Au, 0x005D01DEu, 84u, "psconv.c", "PS_Conv_ToInt", FT_LICENSE },
  { 0x005D01DEu, 0x005D0414u, 566u, "psconv.c", "PS_Conv_ToFixed", FT_LICENSE },
  { 0x005D0414u, 0x005D049Eu, 138u, "psconv.c", "PS_Conv_StringDecode", FT_LICENSE },
  { 0x005D049Eu, 0x005D04E8u, 74u, "psconv.c", "PS_Conv_ASCIIHexDecode", FT_LICENSE },
  { 0x005D04E8u, 0x005D0570u, 136u, "psconv.c", "PS_Conv_EexecDecode", FT_LICENSE },
  { 0x005D0574u, 0x005D0596u, 34u, "psobjs.c", "shift_elements", FT_LICENSE },
  { 0x005D0596u, 0x005D05E6u, 80u, "psobjs.c", "reallocate_t1_table", FT_LICENSE },
  { 0x005D05E6u, 0x005D0682u, 156u, "psobjs.c", "ps_table_add", FT_LICENSE },
  { 0x005D0682u, 0x005D06C6u, 68u, "psobjs.c", "ps_table_done", FT_LICENSE },
  { 0x005D071Cu, 0x005D0736u, 26u, "psobjs.c", "skip_comment", FT_LICENSE },
  { 0x005D0736u, 0x005D0794u, 94u, "psobjs.c", "skip_spaces", FT_LICENSE },
  { 0x005D0794u, 0x005D0814u, 128u, "psobjs.c", "skip_literal_string", FT_LICENSE },
  { 0x005D0814u, 0x005D087Cu, 104u, "psobjs.c", "skip_string", FT_LICENSE },
  { 0x005D087Cu, 0x005D08F6u, 122u, "psobjs.c", "skip_procedure", FT_LICENSE },
  { 0x005D08F6u, 0x005D0A68u, 370u, "psobjs.c", "ps_parser_skip_PS_token", FT_LICENSE },
  { 0x005D0A68u, 0x005D0A72u, 10u, "psobjs.c", "ps_parser_skip_spaces", FT_LICENSE },
  { 0x005D0A72u, 0x005D0B7Cu, 266u, "psobjs.c", "ps_parser_to_token", FT_LICENSE },
  { 0x005D0B7Cu, 0x005D0C04u, 136u, "psobjs.c", "ps_parser_to_token_array", FT_LICENSE },
  { 0x005D0C04u, 0x005D0CC2u, 190u, "psobjs.c", "ps_tocoordarray", FT_LICENSE },
  { 0x005D0CC2u, 0x005D0D84u, 194u, "psobjs.c", "ps_tofixedarray", FT_LICENSE },
  { 0x005D0D84u, 0x005D0DE0u, 92u, "psobjs.c", "ps_tobool", FT_LICENSE },
  { 0x005D0DE0u, 0x005D10C4u, 740u, "psobjs.c", "ps_parser_load_field", FT_LICENSE },
  { 0x005D10C4u, 0x005D1190u, 204u, "psobjs.c", "ps_parser_load_field_table", FT_LICENSE },
  { 0x005D1190u, 0x005D11A4u, 20u, "psobjs.c", "ps_parser_to_int", FT_LICENSE },
  { 0x005D11A4u, 0x005D121Au, 118u, "psobjs.c", "ps_parser_to_bytes", FT_LICENSE },
  { 0x005D128Cu, 0x005D1306u, 122u, "psobjs.c", "t1_builder_init", FT_LICENSE },
  { 0x005D1306u, 0x005D131Cu, 22u, "psobjs.c", "t1_builder_done", FT_LICENSE },
  { 0x005D131Cu, 0x005D1348u, 44u, "psobjs.c", "t1_builder_check_points", FT_LICENSE },
  { 0x005D1348u, 0x005D139Eu, 86u, "psobjs.c", "t1_builder_add_point", FT_LICENSE },
  { 0x005D139Eu, 0x005D13C4u, 38u, "psobjs.c", "t1_builder_add_point1", FT_LICENSE },
  { 0x005D13C4u, 0x005D142Eu, 106u, "psobjs.c", "t1_builder_add_contour", FT_LICENSE },
  { 0x005D142Eu, 0x005D1460u, 50u, "psobjs.c", "t1_builder_start_point", FT_LICENSE },
  { 0x005D1512u, 0x005D159Au, 136u, "psobjs.c", "cff_builder_init", FT_LICENSE },
  { 0x005D15B0u, 0x005D15DCu, 44u, "psobjs.c", "cff_check_points", FT_LICENSE },
  { 0x005D15DCu, 0x005D161Au, 62u, "psobjs.c", "cff_builder_add_point", FT_LICENSE },
  { 0x005D161Au, 0x005D1640u, 38u, "psobjs.c", "cff_builder_add_point1", FT_LICENSE },
  { 0x005D1640u, 0x005D16A2u, 98u, "psobjs.c", "cff_builder_add_contour", FT_LICENSE },
  { 0x005D16A2u, 0x005D16D0u, 46u, "psobjs.c", "cff_builder_start_point", FT_LICENSE },
  { 0x005D176Au, 0x005D1848u, 222u, "psobjs.c", "ps_builder_init", FT_LICENSE },
};

size_t open_cfw_cordio_ll_sea_none_batch11_evidence_count(void) {
  return sizeof(evidence) / sizeof(evidence[0]);
}

const open_cfw_none_batch11_evidence_t *
open_cfw_cordio_ll_sea_none_batch11_evidence(size_t index) {
  return index < open_cfw_cordio_ll_sea_none_batch11_evidence_count()
             ? &evidence[index]
             : NULL;
}

const open_cfw_none_batch11_evidence_t *
open_cfw_cordio_ll_sea_none_batch11_evidence_by_address(uint32_t address) {
  size_t index;
  for (index = 0; index < open_cfw_cordio_ll_sea_none_batch11_evidence_count();
       ++index) {
    if (evidence[index].start == address)
      return &evidence[index];
  }
  return NULL;
}

int open_cfw_cordio_ll_sea_none_batch11_candidate(
    uint32_t address, open_cfw_none_batch11_provider_t provider, void *context,
    open_cfw_none_batch11_invocation_t *invocation) {
  const open_cfw_none_batch11_evidence_t *record;
  if (invocation == NULL)
    return 1;
  record = open_cfw_cordio_ll_sea_none_batch11_evidence_by_address(address);
  if (record == NULL)
    return 2;
  if (provider == NULL)
    return 3;
  return provider(context, record->module, record->function, invocation) == 0
             ? 0
             : 4;
}

#undef FT_LICENSE
