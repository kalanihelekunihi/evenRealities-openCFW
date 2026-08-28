/* SPDX-License-Identifier: Apache-2.0 */
#ifndef OPEN_CFW_RUNTIME_CORDIO_LL_SEA_HOP4_RESIDUE_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CORDIO_LL_SEA_HOP4_RESIDUE_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

typedef enum {
    OPEN_CFW_SEA_RESIDUE_HOP2 = 0,
    OPEN_CFW_SEA_RESIDUE_ISLAND_CALLER = 1,
    OPEN_CFW_SEA_RESIDUE_HOP4 = 2
} open_cfw_sea_residue_class_t;

typedef struct {
    uint32_t stock_start;
    uint32_t stock_end_exclusive;
    size_t stock_bytes;
    open_cfw_sea_residue_class_t source_class;
    const char *upstream_module;
    const char *upstream_function;
    const char *upstream_license;
} open_cfw_sea_residue_evidence_t;

typedef struct { uintptr_t words[8]; } open_cfw_sea_residue_invocation_t;
typedef int (*open_cfw_sea_residue_provider_t)(
    void *, const char *, const char *, open_cfw_sea_residue_invocation_t *);

size_t open_cfw_cordio_ll_sea_hop4_residue_evidence_count(void);
const open_cfw_sea_residue_evidence_t *
open_cfw_cordio_ll_sea_hop4_residue_evidence(size_t index);
const open_cfw_sea_residue_evidence_t *
open_cfw_cordio_ll_sea_hop4_residue_evidence_by_address(uint32_t address);
int open_cfw_cordio_ll_sea_hop4_residue_candidate(
    uint32_t address, open_cfw_sea_residue_provider_t provider, void *context,
    open_cfw_sea_residue_invocation_t *invocation);

#endif
