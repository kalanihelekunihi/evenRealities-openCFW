/* SPDX-License-Identifier: MIT */
/* Address-derived typed seam; no Packetcraft/EM implementation is copied. */
#include "runtime_controller_master_connection_boundary.h"
int32_t open_cfw_em9305_mst_conn_boundary(
    const open_cfw_em9305_mst_conn_ports *ports,
    open_cfw_em9305_mst_conn_entry entry,
    open_cfw_em9305_mst_conn_invocation *invocation)
{
    if (ports == 0 || invocation == 0 || entry < OPEN_CFW_EM9305_MST_CONN_ENTRY_31DFD0 ||
        entry >= OPEN_CFW_EM9305_MST_CONN_ENTRY_COUNT) {
        return OPEN_CFW_EM9305_MST_CONN_INVALID;
    }
    if (ports->provider == 0) return OPEN_CFW_EM9305_MST_CONN_UNSUPPORTED;
    return ports->provider(ports->context, entry, invocation) == 0
               ? OPEN_CFW_EM9305_MST_CONN_OK : OPEN_CFW_EM9305_MST_CONN_FAILED;
}
