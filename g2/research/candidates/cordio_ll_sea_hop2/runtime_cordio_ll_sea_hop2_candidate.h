/* SPDX-License-Identifier: Apache-2.0 */
#ifndef OPEN_CFW_RUNTIME_CORDIO_LL_SEA_HOP2_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CORDIO_LL_SEA_HOP2_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    OPEN_CFW_HOP2_UPSTREAM_FREETYPE = 0,
    OPEN_CFW_HOP2_TYPED_EXTERNAL = 1
} open_cfw_hop2_disposition_t;

typedef enum {
    OPEN_CFW_HOP2_OK = 0,
    OPEN_CFW_HOP2_INVALID_ARGUMENT = 1,
    OPEN_CFW_HOP2_UNKNOWN_ADDRESS = 2,
    OPEN_CFW_HOP2_UNSUPPORTED_EXTERNAL = 3,
    OPEN_CFW_HOP2_PROVIDER_FAILED = 4
} open_cfw_hop2_status_t;

typedef struct {
    uint32_t stock_start;
    uint32_t stock_end_exclusive;
    size_t stock_bytes;
    open_cfw_hop2_disposition_t disposition;
    const char *upstream_module;
    const char *upstream_function;
    const char *upstream_license;
} open_cfw_hop2_evidence_t;

typedef struct {
    uintptr_t words[8];
} open_cfw_hop2_invocation_t;

typedef int (*open_cfw_hop2_upstream_provider_t)(
    void *context,
    const char *upstream_module,
    const char *upstream_function,
    open_cfw_hop2_invocation_t *invocation);

size_t open_cfw_cordio_ll_sea_hop2_evidence_count(void);

const open_cfw_hop2_evidence_t *
open_cfw_cordio_ll_sea_hop2_evidence(size_t index);

const open_cfw_hop2_evidence_t *
open_cfw_cordio_ll_sea_hop2_evidence_by_address(uint32_t stock_start);

open_cfw_hop2_status_t open_cfw_cordio_ll_sea_hop2_candidate(
    uint32_t stock_start,
    open_cfw_hop2_upstream_provider_t provider,
    void *provider_context,
    open_cfw_hop2_invocation_t *invocation);

#ifdef __cplusplus
}
#endif

#endif
