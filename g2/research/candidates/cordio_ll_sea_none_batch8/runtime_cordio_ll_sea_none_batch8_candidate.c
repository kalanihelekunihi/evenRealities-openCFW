/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_none_batch8_candidate.h"
#define FT_LICENSE "FreeType Project License; retained file-specific notices and grants"
/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_none_batch8_evidence_t evidence[]={
 {0x005DC99Cu,0x005DCA46u,170u,"ttcmap.c","tt_cmap4_set_range",FT_LICENSE},
 {0x005DCA46u,0x005DCB16u,208u,"ttcmap.c","tt_cmap4_next",FT_LICENSE},
 {0x005DCB16u,0x005DCE22u,780u,"ttcmap.c","tt_cmap4_validate",FT_LICENSE},
 {0x005DCE22u,0x005DCFF6u,468u,"ttcmap.c","tt_cmap4_char_map_linear",FT_LICENSE},
 {0x005DCFF6u,0x005DD39Eu,936u,"ttcmap.c","tt_cmap4_char_map_binary",FT_LICENSE},
 {0x005DD39Eu,0x005DD3C6u,40u,"ttcmap.c","tt_cmap4_char_index",FT_LICENSE},
};
size_t open_cfw_cordio_ll_sea_none_batch8_evidence_count(void){return sizeof(evidence)/sizeof(evidence[0]);}
const open_cfw_none_batch8_evidence_t *open_cfw_cordio_ll_sea_none_batch8_evidence(size_t i){return i<open_cfw_cordio_ll_sea_none_batch8_evidence_count()?&evidence[i]:NULL;}
const open_cfw_none_batch8_evidence_t *open_cfw_cordio_ll_sea_none_batch8_evidence_by_address(uint32_t a){size_t i;for(i=0;i<open_cfw_cordio_ll_sea_none_batch8_evidence_count();++i)if(evidence[i].start==a)return &evidence[i];return NULL;}
int open_cfw_cordio_ll_sea_none_batch8_candidate(uint32_t a,open_cfw_none_batch8_provider_t p,void *c,open_cfw_none_batch8_invocation_t *v){const open_cfw_none_batch8_evidence_t *e;if(v==NULL)return 1;e=open_cfw_cordio_ll_sea_none_batch8_evidence_by_address(a);if(e==NULL)return 2;if(p==NULL)return 3;return p(c,e->module,e->function,v)==0?0:4;}
#undef FT_LICENSE
