/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_none_batch4_candidate.h"
#define FT_LICENSE "FreeType Project License; retained file-specific notices and grants"
/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_none_batch4_evidence_t evidence[]={
 {0x005D8B10u,0x005D8B2Au,26u,"pshrec.c","ps_hint_table_done",FT_LICENSE},
 {0x005D8B2Au,0x005D8B60u,54u,"pshrec.c","ps_hint_table_ensure",FT_LICENSE},
 {0x005D8B60u,0x005D8BA2u,66u,"pshrec.c","ps_hint_table_alloc",FT_LICENSE},
 {0x005D8BA2u,0x005D8BC0u,30u,"pshrec.c","ps_mask_done",FT_LICENSE},
 {0x005D8BC0u,0x005D8C00u,64u,"pshrec.c","ps_mask_ensure",FT_LICENSE},
 {0x005D8C00u,0x005D8C1Eu,30u,"pshrec.c","ps_mask_test_bit",FT_LICENSE},
 {0x005D8C1Eu,0x005D8C3Eu,32u,"pshrec.c","ps_mask_clear_bit",FT_LICENSE},
 {0x005D8C3Eu,0x005D8C76u,56u,"pshrec.c","ps_mask_set_bit",FT_LICENSE},
 {0x005D8C76u,0x005D8CA8u,50u,"pshrec.c","ps_mask_table_done",FT_LICENSE},
 {0x005D8CA8u,0x005D8CDEu,54u,"pshrec.c","ps_mask_table_ensure",FT_LICENSE},
 {0x005D8CDEu,0x005D8D18u,58u,"pshrec.c","ps_mask_table_alloc",FT_LICENSE},
 {0x005D8D18u,0x005D8D44u,44u,"pshrec.c","ps_mask_table_last",FT_LICENSE},
 {0x005D8D44u,0x005D8DB4u,112u,"pshrec.c","ps_mask_table_set_bits",FT_LICENSE},
 {0x005D8DB4u,0x005D8E02u,78u,"pshrec.c","ps_mask_table_test_intersect",FT_LICENSE},
 {0x005D8E02u,0x005D8ED0u,206u,"pshrec.c","ps_mask_table_merge",FT_LICENSE},
 {0x005D8ED0u,0x005D8F1Cu,76u,"pshrec.c","ps_mask_table_merge_all",FT_LICENSE},
 {0x005D8F1Cu,0x005D8F40u,36u,"pshrec.c","ps_dimension_done",FT_LICENSE},
 {0x005D8F40u,0x005D8F4Eu,14u,"pshrec.c","ps_dimension_init",FT_LICENSE},
 {0x005D8F4Eu,0x005D8F60u,18u,"pshrec.c","ps_dimension_end_mask",FT_LICENSE},
 {0x005D8F60u,0x005D8F7Au,26u,"pshrec.c","ps_dimension_reset_mask",FT_LICENSE},
 {0x005D8F7Au,0x005D8FAEu,52u,"pshrec.c","ps_dimension_set_mask_bits",FT_LICENSE},
 {0x005D8FAEu,0x005D905Cu,174u,"pshrec.c","ps_dimension_add_t1stem",FT_LICENSE},
 {0x005D905Cu,0x005D9100u,164u,"pshrec.c","ps_dimension_add_counter",FT_LICENSE},
 {0x005D9100u,0x005D9118u,24u,"pshrec.c","ps_dimension_end",FT_LICENSE},
 {0x005D9118u,0x005D913Cu,36u,"pshrec.c","ps_hints_done",FT_LICENSE},
 {0x005D913Cu,0x005D9152u,22u,"pshrec.c","ps_hints_init",FT_LICENSE},
 {0x005D9152u,0x005D916Eu,28u,"pshrec.c","ps_hints_open",FT_LICENSE},
 {0x005D916Eu,0x005D91BCu,78u,"pshrec.c","ps_hints_stem",FT_LICENSE},
 {0x005D91BCu,0x005D9254u,152u,"pshrec.c","ps_hints_t1stem3",FT_LICENSE},
 {0x005D9296u,0x005D92F0u,90u,"pshrec.c","ps_hints_t2mask",FT_LICENSE},
 {0x005D92F0u,0x005D934Au,90u,"pshrec.c","ps_hints_t2counter",FT_LICENSE},
 {0x005D93ACu,0x005D93D6u,42u,"pshrec.c","t1_hints_funcs_init",FT_LICENSE},
 {0x005D9462u,0x005D948Cu,42u,"pshrec.c","t2_hints_funcs_init",FT_LICENSE},
};
size_t open_cfw_cordio_ll_sea_none_batch4_evidence_count(void){return sizeof(evidence)/sizeof(evidence[0]);}
const open_cfw_none_batch4_evidence_t *open_cfw_cordio_ll_sea_none_batch4_evidence(size_t index){return index<open_cfw_cordio_ll_sea_none_batch4_evidence_count()?&evidence[index]:NULL;}
const open_cfw_none_batch4_evidence_t *open_cfw_cordio_ll_sea_none_batch4_evidence_by_address(uint32_t address){size_t i;for(i=0;i<open_cfw_cordio_ll_sea_none_batch4_evidence_count();++i)if(evidence[i].start==address)return &evidence[i];return NULL;}
int open_cfw_cordio_ll_sea_none_batch4_candidate(uint32_t address,open_cfw_none_batch4_provider_t provider,void *context,open_cfw_none_batch4_invocation_t *invocation){const open_cfw_none_batch4_evidence_t *item;if(invocation==NULL)return 1;item=open_cfw_cordio_ll_sea_none_batch4_evidence_by_address(address);if(item==NULL)return 2;if(provider==NULL)return 3;return provider(context,item->module,item->function,invocation)==0?0:4;}
#undef FT_LICENSE
