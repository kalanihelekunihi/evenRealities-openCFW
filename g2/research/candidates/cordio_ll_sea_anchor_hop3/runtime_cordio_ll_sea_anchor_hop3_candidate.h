/* SPDX-License-Identifier: Apache-2.0 */
#ifndef OPEN_CFW_RUNTIME_CORDIO_LL_SEA_ANCHOR_HOP3_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CORDIO_LL_SEA_ANCHOR_HOP3_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

typedef enum {
    OPEN_CFW_SEA_ANCHOR = 0,
    OPEN_CFW_SEA_HOP2_REFINEMENT = 1,
    OPEN_CFW_SEA_HOP3 = 2
} open_cfw_sea_source_class_t;

typedef enum {
    OPEN_CFW_SEA_SOURCE_OK = 0,
    OPEN_CFW_SEA_SOURCE_INVALID_ARGUMENT = 1,
    OPEN_CFW_SEA_SOURCE_UNKNOWN_ADDRESS = 2,
    OPEN_CFW_SEA_SOURCE_PROVIDER_MISSING = 3,
    OPEN_CFW_SEA_SOURCE_PROVIDER_FAILED = 4
} open_cfw_sea_source_status_t;

typedef struct {
    uint32_t stock_start;
    uint32_t stock_end_exclusive;
    size_t stock_bytes;
    open_cfw_sea_source_class_t source_class;
    const char *upstream_module;
    const char *upstream_function;
    const char *upstream_license;
} open_cfw_sea_source_evidence_t;

typedef struct {
    uintptr_t words[8];
} open_cfw_sea_source_invocation_t;

typedef int (*open_cfw_sea_source_provider_t)(
    void *context, const char *module, const char *function,
    open_cfw_sea_source_invocation_t *invocation);

size_t open_cfw_cordio_ll_sea_anchor_hop3_evidence_count(void);
const open_cfw_sea_source_evidence_t *
open_cfw_cordio_ll_sea_anchor_hop3_evidence(size_t index);
const open_cfw_sea_source_evidence_t *
open_cfw_cordio_ll_sea_anchor_hop3_evidence_by_address(uint32_t stock_start);
open_cfw_sea_source_status_t open_cfw_cordio_ll_sea_anchor_hop3_candidate(
    uint32_t stock_start, open_cfw_sea_source_provider_t provider,
    void *provider_context, open_cfw_sea_source_invocation_t *invocation);

#endif
