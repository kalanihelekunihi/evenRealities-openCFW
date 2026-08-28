/* SPDX-License-Identifier: Apache-2.0 */
#ifndef OPEN_CFW_RUNTIME_CORDIO_LL_SEA_NONE_BATCH7_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CORDIO_LL_SEA_NONE_BATCH7_CANDIDATE_H
#include <stddef.h>
#include <stdint.h>
typedef struct { uint32_t start,end_exclusive; size_t bytes; const char *module,*function,*license; } open_cfw_none_batch7_evidence_t;
typedef struct { uintptr_t words[8]; } open_cfw_none_batch7_invocation_t;
typedef int (*open_cfw_none_batch7_provider_t)(void *,const char *,const char *,open_cfw_none_batch7_invocation_t *);
size_t open_cfw_cordio_ll_sea_none_batch7_evidence_count(void);
const open_cfw_none_batch7_evidence_t *open_cfw_cordio_ll_sea_none_batch7_evidence(size_t index);
const open_cfw_none_batch7_evidence_t *open_cfw_cordio_ll_sea_none_batch7_evidence_by_address(uint32_t address);
int open_cfw_cordio_ll_sea_none_batch7_candidate(uint32_t address,open_cfw_none_batch7_provider_t provider,void *context,open_cfw_none_batch7_invocation_t *invocation);
#endif
