/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_EM9305_CONTROLLER_MASTER_CONNECTION_BOUNDARY_H
#define OPEN_CFW_EM9305_CONTROLLER_MASTER_CONNECTION_BOUNDARY_H
#include <stdint.h>
enum { OPEN_CFW_EM9305_MST_CONN_OK = 0, OPEN_CFW_EM9305_MST_CONN_INVALID = 1,
       OPEN_CFW_EM9305_MST_CONN_UNSUPPORTED = 2, OPEN_CFW_EM9305_MST_CONN_FAILED = 3 };
typedef enum open_cfw_em9305_mst_conn_entry {
    OPEN_CFW_EM9305_MST_CONN_ENTRY_31DFD0 = 0,
    OPEN_CFW_EM9305_MST_CONN_ENTRY_31E458 = 1,
    OPEN_CFW_EM9305_MST_CONN_ENTRY_31E4A0 = 2,
    OPEN_CFW_EM9305_MST_CONN_ENTRY_COUNT = 3,
} open_cfw_em9305_mst_conn_entry;
typedef struct open_cfw_em9305_mst_conn_invocation { uintptr_t words[8]; }
    open_cfw_em9305_mst_conn_invocation;
typedef int32_t (*open_cfw_em9305_mst_conn_provider_fn)(
    void *, open_cfw_em9305_mst_conn_entry, open_cfw_em9305_mst_conn_invocation *);
typedef struct open_cfw_em9305_mst_conn_ports {
    void *context; open_cfw_em9305_mst_conn_provider_fn provider;
} open_cfw_em9305_mst_conn_ports;
int32_t open_cfw_em9305_mst_conn_boundary(
    const open_cfw_em9305_mst_conn_ports *, open_cfw_em9305_mst_conn_entry,
    open_cfw_em9305_mst_conn_invocation *);
#endif
