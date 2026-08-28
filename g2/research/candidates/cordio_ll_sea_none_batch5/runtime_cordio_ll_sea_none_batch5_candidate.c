/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_none_batch5_candidate.h"
#define FT_LICENSE "FreeType Project License; retained file-specific notices and grants"
/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_none_batch5_evidence_t evidence[]={
 {0x005D94C0u,0x005D9580u,192u,"pstables.h","ft_get_adobe_glyph_index",FT_LICENSE},
 {0x005D9580u,0x005D9672u,242u,"psmodule.c","ps_unicode_value",FT_LICENSE},
 {0x005D96B6u,0x005D96F8u,66u,"psmodule.c","ps_check_extra_glyph_name",FT_LICENSE},
 {0x005D96F8u,0x005D9716u,30u,"psmodule.c","ps_check_extra_glyph_unicode",FT_LICENSE},
 {0x005D9716u,0x005D9840u,298u,"psmodule.c","ps_unicodes_init",FT_LICENSE},
 {0x005D9840u,0x005D9890u,80u,"psmodule.c","ps_unicodes_char_index",FT_LICENSE},
 {0x005D9890u,0x005D98F6u,102u,"psmodule.c","ps_unicodes_char_next",FT_LICENSE},
};
size_t open_cfw_cordio_ll_sea_none_batch5_evidence_count(void){return sizeof(evidence)/sizeof(evidence[0]);}
const open_cfw_none_batch5_evidence_t *open_cfw_cordio_ll_sea_none_batch5_evidence(size_t i){return i<open_cfw_cordio_ll_sea_none_batch5_evidence_count()?&evidence[i]:NULL;}
const open_cfw_none_batch5_evidence_t *open_cfw_cordio_ll_sea_none_batch5_evidence_by_address(uint32_t a){size_t i;for(i=0;i<open_cfw_cordio_ll_sea_none_batch5_evidence_count();++i)if(evidence[i].start==a)return &evidence[i];return NULL;}
int open_cfw_cordio_ll_sea_none_batch5_candidate(uint32_t a,open_cfw_none_batch5_provider_t p,void *c,open_cfw_none_batch5_invocation_t *v){const open_cfw_none_batch5_evidence_t *e;if(v==NULL)return 1;e=open_cfw_cordio_ll_sea_none_batch5_evidence_by_address(a);if(e==NULL)return 2;if(p==NULL)return 3;return p(c,e->module,e->function,v)==0?0:4;}
#undef FT_LICENSE
