/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_none_batch12_candidate.h"

#define FT_LICENSE \
  "FreeType Project License; retained file-specific notices and grants"
#define RTT_LICENSE \
  "SEGGER RTT redistributable source license; upstream terms retained"

/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_none_batch12_evidence_t evidence[] = {
  { 0x005D1D2Au, 0x005D1D52u, 40u, "FreeType", "t1cmap.c", "t1_cmap_std_init", FT_LICENSE },
  { 0x005D1D64u, 0x005D1DAAu, 70u, "FreeType", "t1cmap.c", "t1_cmap_std_char_index", FT_LICENSE },
  { 0x005D1DAAu, 0x005D1DD4u, 42u, "FreeType", "t1cmap.c", "t1_cmap_std_char_next", FT_LICENSE },
  { 0x005D1EB4u, 0x005D1EC2u, 14u, "FreeType", "t1cmap.c", "t1_cmap_unicode_char_index", FT_LICENSE },
  { 0x005D1EC2u, 0x005D1ED0u, 14u, "FreeType", "t1cmap.c", "t1_cmap_unicode_char_next", FT_LICENSE },
  { 0x005D2EFEu, 0x005D2F22u, 36u, "FreeType/Adobe", "psft.c", "cf2_free_instance", FT_LICENSE },
  { 0x005D2F22u, 0x005D2F34u, 18u, "FreeType/Adobe", "psft.c", "cf2_builder_moveTo", FT_LICENSE },
  { 0x005D9950u, 0x005D99C0u, 112u, "SEGGER", "SEGGER_RTT.c", "SEGGER_RTT_Init", RTT_LICENSE },
  { 0x005D99C0u, 0x005D9A44u, 132u, "SEGGER", "SEGGER_RTT.c", "_WriteBlocking", RTT_LICENSE },
  { 0x005D9A44u, 0x005D9AA2u, 94u, "SEGGER", "SEGGER_RTT.c", "_WriteNoCheck", RTT_LICENSE },
  { 0x005D9AA2u, 0x005D9ABCu, 26u, "SEGGER", "SEGGER_RTT.c", "_GetAvailWriteSpace", RTT_LICENSE },
  { 0x005D9ABCu, 0x005D9B28u, 108u, "SEGGER", "SEGGER_RTT.c", "SEGGER_RTT_WriteNoLock", RTT_LICENSE },
  { 0x005D9B28u, 0x005D9B58u, 48u, "SEGGER", "SEGGER_RTT.c", "SEGGER_RTT_Write", RTT_LICENSE },
  { 0x005DC266u, 0x005DC290u, 42u, "FreeType", "ttbdf.c", "tt_face_free_bdf_props", FT_LICENSE },
};

size_t open_cfw_cordio_ll_sea_none_batch12_evidence_count(void) {
  return sizeof(evidence) / sizeof(evidence[0]);
}

const open_cfw_none_batch12_evidence_t *
open_cfw_cordio_ll_sea_none_batch12_evidence(size_t index) {
  return index < open_cfw_cordio_ll_sea_none_batch12_evidence_count()
             ? &evidence[index]
             : NULL;
}

const open_cfw_none_batch12_evidence_t *
open_cfw_cordio_ll_sea_none_batch12_evidence_by_address(uint32_t address) {
  size_t index;
  for (index = 0; index < open_cfw_cordio_ll_sea_none_batch12_evidence_count();
       ++index) {
    if (evidence[index].start == address)
      return &evidence[index];
  }
  return NULL;
}

int open_cfw_cordio_ll_sea_none_batch12_candidate(
    uint32_t address, open_cfw_none_batch12_provider_t provider, void *context,
    open_cfw_none_batch12_invocation_t *invocation) {
  const open_cfw_none_batch12_evidence_t *record;
  if (invocation == NULL)
    return 1;
  record = open_cfw_cordio_ll_sea_none_batch12_evidence_by_address(address);
  if (record == NULL)
    return 2;
  if (provider == NULL)
    return 3;
  return provider(context, record->provider, record->module, record->function,
                  invocation) == 0
             ? 0
             : 4;
}

#undef RTT_LICENSE
#undef FT_LICENSE
