/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_EM9305_CONTROLLER_PAWR_BOUNDARY_H
#define OPEN_CFW_EM9305_CONTROLLER_PAWR_BOUNDARY_H

#include <stdint.h>

enum {
    OPEN_CFW_EM9305_PAWR_OK = 0,
    OPEN_CFW_EM9305_PAWR_INVALID_ARGUMENT = 1,
    OPEN_CFW_EM9305_PAWR_UNSUPPORTED = 2,
    OPEN_CFW_EM9305_PAWR_PROVIDER_FAILED = 3,
};

typedef enum open_cfw_em9305_pawr_entry {
    OPEN_CFW_EM9305_PAWR_RX_POST_HANDLER = 0,
    OPEN_CFW_EM9305_PAWR_TRANSFER_COMMIT = 1,
    OPEN_CFW_EM9305_PAWR_WITH_RSP_ABORT = 2,
    OPEN_CFW_EM9305_PAWR_WITH_RSP_COMMIT = 3,
    OPEN_CFW_EM9305_PAWR_ENTRY_COUNT = 4,
} open_cfw_em9305_pawr_entry;

typedef struct open_cfw_em9305_pawr_invocation {
    uintptr_t words[8];
} open_cfw_em9305_pawr_invocation;

typedef int32_t (*open_cfw_em9305_pawr_provider_fn)(
    void *context,
    open_cfw_em9305_pawr_entry entry,
    open_cfw_em9305_pawr_invocation *invocation);

typedef struct open_cfw_em9305_pawr_ports {
    void *context;
    open_cfw_em9305_pawr_provider_fn provider;
} open_cfw_em9305_pawr_ports;

typedef struct open_cfw_em9305_pawr_evidence {
    uint32_t stock_start;
    uint32_t stock_end;
    const char *name;
    const char *stock_sha256;
    const char *source_status;
} open_cfw_em9305_pawr_evidence;

extern const open_cfw_em9305_pawr_evidence
    open_cfw_em9305_pawr_evidence_map[OPEN_CFW_EM9305_PAWR_ENTRY_COUNT];

int32_t open_cfw_em9305_pawr_boundary(
    const open_cfw_em9305_pawr_ports *ports,
    open_cfw_em9305_pawr_entry entry,
    open_cfw_em9305_pawr_invocation *invocation);

#endif
