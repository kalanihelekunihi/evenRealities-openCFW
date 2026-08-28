/* SPDX-License-Identifier: MIT */
/* Typed clean-room seam only; this file contains no Packetcraft/EM body. */

#include "runtime_controller_pawr_boundary.h"

const open_cfw_em9305_pawr_evidence
open_cfw_em9305_pawr_evidence_map[OPEN_CFW_EM9305_PAWR_ENTRY_COUNT] = {
    {0x00321C30U, 0x00321E14U, "lctrMstPerScanRxPerAdvPktPostHandler",
     "8f74070caffcaede5e606614ee3c7f0ef7c755a287c4e5ad4c1d14828c4dbcca",
     "vendor-divergent; exact source and redistribution authority unavailable"},
    {0x00321E14U, 0x00322178U, "lctrMstPerScanTransferOpCommit",
     "df4784fcbc7a3624f7bf6c04ff22d99159ebc7d6f601bbe94054debe77659978",
     "vendor-modified; exact source and redistribution authority unavailable"},
    {0x00322178U, 0x00322182U, "lctrMstPerScanWithRspAbortOp",
     "fe9b95826f8876fb0b5cc3c35e4211c60fcf5631108e95e77e9d2e4e0d8b6066",
     "opcode-exact only; relocation-masked byte identity not proven"},
    {0x00322184U, 0x0032233CU, "lctrMstPerScanWithRspCommitOp",
     "e70986eda9470d4ac535ea3a919c486e4fb7e24bf6c4b826a700a7071ff93453",
     "vendor-modified; exact source and redistribution authority unavailable"},
};

int32_t open_cfw_em9305_pawr_boundary(
    const open_cfw_em9305_pawr_ports *ports,
    open_cfw_em9305_pawr_entry entry,
    open_cfw_em9305_pawr_invocation *invocation)
{
    if (ports == 0 || invocation == 0 || entry < OPEN_CFW_EM9305_PAWR_RX_POST_HANDLER ||
        entry >= OPEN_CFW_EM9305_PAWR_ENTRY_COUNT) {
        return OPEN_CFW_EM9305_PAWR_INVALID_ARGUMENT;
    }
    if (ports->provider == 0) {
        return OPEN_CFW_EM9305_PAWR_UNSUPPORTED;
    }
    return ports->provider(ports->context, entry, invocation) == 0
               ? OPEN_CFW_EM9305_PAWR_OK
               : OPEN_CFW_EM9305_PAWR_PROVIDER_FAILED;
}
