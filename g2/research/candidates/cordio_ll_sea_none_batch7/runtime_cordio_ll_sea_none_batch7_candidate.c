/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_ll_sea_none_batch7_candidate.h"
#define FT_LICENSE "FreeType Project License; retained file-specific notices and grants"
/* Research-only identity/provider adapter; no upstream implementation copied. */
static const open_cfw_none_batch7_evidence_t evidence[]={
 {0x005DAB8Eu,0x005DABEEu,96u,"sfobjs.c","tt_name_ascii_from_utf16",FT_LICENSE},
 {0x005DABEEu,0x005DAC40u,82u,"sfobjs.c","tt_name_ascii_from_other",FT_LICENSE},
 {0x005DAC40u,0x005DADEEu,430u,"sfobjs.c","tt_face_get_name",FT_LICENSE},
 {0x005DADF8u,0x005DAE28u,48u,"sfobjs.c","sfnt_find_encoding",FT_LICENSE},
 {0x005DAE90u,0x005DB3DEu,1358u,"sfobjs.c","woff_open_font",FT_LICENSE},
 {0x005DB3ECu,0x005DB562u,374u,"sfobjs.c","sfnt_open_font",FT_LICENSE},
 {0x005DB578u,0x005DB92Au,946u,"sfobjs.c","sfnt_init_face",FT_LICENSE},
};
size_t open_cfw_cordio_ll_sea_none_batch7_evidence_count(void){return sizeof(evidence)/sizeof(evidence[0]);}
const open_cfw_none_batch7_evidence_t *open_cfw_cordio_ll_sea_none_batch7_evidence(size_t i){return i<open_cfw_cordio_ll_sea_none_batch7_evidence_count()?&evidence[i]:NULL;}
const open_cfw_none_batch7_evidence_t *open_cfw_cordio_ll_sea_none_batch7_evidence_by_address(uint32_t a){size_t i;for(i=0;i<open_cfw_cordio_ll_sea_none_batch7_evidence_count();++i)if(evidence[i].start==a)return &evidence[i];return NULL;}
int open_cfw_cordio_ll_sea_none_batch7_candidate(uint32_t a,open_cfw_none_batch7_provider_t p,void *c,open_cfw_none_batch7_invocation_t *v){const open_cfw_none_batch7_evidence_t *e;if(v==NULL)return 1;e=open_cfw_cordio_ll_sea_none_batch7_evidence_by_address(a);if(e==NULL)return 2;if(p==NULL)return 3;return p(c,e->module,e->function,v)==0?0:4;}
#undef FT_LICENSE
