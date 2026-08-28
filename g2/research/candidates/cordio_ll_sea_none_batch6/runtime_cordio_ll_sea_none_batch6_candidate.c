/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_none_batch6_candidate.h"
#define FT_LICENSE "FreeType Project License; retained file-specific notices and grants"
/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_none_batch6_evidence_t evidence[]={
 {0x005DA1E8u,0x005DA202u,26u,"sfdriver.c","fmix32",FT_LICENSE},
 {0x005DA202u,0x005DA446u,580u,"sfdriver.c","murmur_hash_3_128",FT_LICENSE},
 {0x005DA446u,0x005DA518u,210u,"sfdriver.c","get_win_string",FT_LICENSE},
 {0x005DA518u,0x005DA5D6u,190u,"sfdriver.c","get_apple_string",FT_LICENSE},
 {0x005DA5D6u,0x005DA656u,128u,"sfdriver.c","sfnt_get_name_id",FT_LICENSE},
 {0x005DA656u,0x005DA73Au,228u,"sfdriver.c","fixed2float",FT_LICENSE},
 {0x005DA73Au,0x005DAA9Cu,866u,"sfdriver.c","sfnt_get_var_ps_name",FT_LICENSE},
 {0x005DAA9Cu,0x005DAB3Au,158u,"sfdriver.c","sfnt_get_ps_name",FT_LICENSE},
};
size_t open_cfw_cordio_ll_sea_none_batch6_evidence_count(void){return sizeof(evidence)/sizeof(evidence[0]);}
const open_cfw_none_batch6_evidence_t *open_cfw_cordio_ll_sea_none_batch6_evidence(size_t i){return i<open_cfw_cordio_ll_sea_none_batch6_evidence_count()?&evidence[i]:NULL;}
const open_cfw_none_batch6_evidence_t *open_cfw_cordio_ll_sea_none_batch6_evidence_by_address(uint32_t a){size_t i;for(i=0;i<open_cfw_cordio_ll_sea_none_batch6_evidence_count();++i)if(evidence[i].start==a)return &evidence[i];return NULL;}
int open_cfw_cordio_ll_sea_none_batch6_candidate(uint32_t a,open_cfw_none_batch6_provider_t p,void *c,open_cfw_none_batch6_invocation_t *v){const open_cfw_none_batch6_evidence_t *e;if(v==NULL)return 1;e=open_cfw_cordio_ll_sea_none_batch6_evidence_by_address(a);if(e==NULL)return 2;if(p==NULL)return 3;return p(c,e->module,e->function,v)==0?0:4;}
#undef FT_LICENSE
