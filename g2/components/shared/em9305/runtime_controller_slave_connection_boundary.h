/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_EM9305_CONTROLLER_SLAVE_CONNECTION_BOUNDARY_H
#define OPEN_CFW_EM9305_CONTROLLER_SLAVE_CONNECTION_BOUNDARY_H

#include <stdint.h>

enum {
    OPEN_CFW_EM9305_SLV_CONN_OK = 0,
    OPEN_CFW_EM9305_SLV_CONN_INVALID_ARGUMENT = 1,
    OPEN_CFW_EM9305_SLV_CONN_UNSUPPORTED = 2,
    OPEN_CFW_EM9305_SLV_CONN_PROVIDER_FAILED = 3,
};

typedef enum open_cfw_em9305_slv_conn_entry {
    OPEN_CFW_EM9305_SLV_CONN_END_OP = 0,
    OPEN_CFW_EM9305_SLV_CONN_EXECUTE = 1,
    OPEN_CFW_EM9305_SLV_CONN_EXECUTE_SM = 2,
    OPEN_CFW_EM9305_SLV_CONN_RESET_HANDLER = 3,
    OPEN_CFW_EM9305_SLV_CONN_RX_COMPLETION = 4,
    OPEN_CFW_EM9305_SLV_CONN_TX_COMPLETION = 5,
    OPEN_CFW_EM9305_SLV_CONN_ENTRY_COUNT = 6,
} open_cfw_em9305_slv_conn_entry;

typedef struct open_cfw_em9305_slv_conn_invocation {
    uintptr_t words[8];
} open_cfw_em9305_slv_conn_invocation;

typedef int32_t (*open_cfw_em9305_slv_conn_provider_fn)(
    void *context,
    open_cfw_em9305_slv_conn_entry entry,
    open_cfw_em9305_slv_conn_invocation *invocation);

typedef struct open_cfw_em9305_slv_conn_ports {
    void *context;
    open_cfw_em9305_slv_conn_provider_fn provider;
} open_cfw_em9305_slv_conn_ports;

typedef struct open_cfw_em9305_slv_conn_evidence {
    uint32_t stock_start;
    uint32_t stock_end;
    const char *name;
    const char *stock_sha256;
    const char *source_status;
} open_cfw_em9305_slv_conn_evidence;

extern const open_cfw_em9305_slv_conn_evidence
    open_cfw_em9305_slv_conn_evidence_map[OPEN_CFW_EM9305_SLV_CONN_ENTRY_COUNT];

int32_t open_cfw_em9305_slv_conn_boundary(
    const open_cfw_em9305_slv_conn_ports *ports,
    open_cfw_em9305_slv_conn_entry entry,
    open_cfw_em9305_slv_conn_invocation *invocation);

#endif
