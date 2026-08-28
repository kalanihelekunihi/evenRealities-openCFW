/* SPDX-License-Identifier: MIT */
/*
 * Clean-room typed boundary for the authenticated slave-connection cluster.
 * The carrier is OpenCFW-owned and does not claim the stock ARC ABI.  Every
 * entry remains unsupported unless a separately reviewed provider is bound.
 */

#include "runtime_controller_slave_connection_boundary.h"

const open_cfw_em9305_slv_conn_evidence
open_cfw_em9305_slv_conn_evidence_map[OPEN_CFW_EM9305_SLV_CONN_ENTRY_COUNT] = {
    {0x00329888U, 0x00329FD6U, "lctrSlvConnEndOp",
     "99a73c81f0b0b16df5d9f77ebacd741c4fc16eb90858b229e2ebe90d884e61cb",
     "vendor-modified; exact source and redistribution authority unavailable"},
    {0x00329FD8U, 0x00329FFEU, "lctrSlvConnExecute",
     "137340641ee0e455564bfc29f1e7a107ddecbc8fe258da6a095695e74aee4076",
     "opcode-exact only; relocation-masked byte identity not proven"},
    {0x0032A000U, 0x0032A216U, "lctrSlvConnExecuteSm",
     "8a85df82679c8a74fab531a537fc27c7a68f68e25a605a2afbfa32f6cbc0f15e",
     "vendor-modified; exact source and redistribution authority unavailable"},
    {0x0032A218U, 0x0032A22EU, "lctrSlvConnResetHandler",
     "0f3641bda66dabfedd5cc888e4b833e4230ef1c543c249ec46c99e0b842c106a",
     "opcode-exact only; relocation-masked byte identity not proven"},
    {0x0032A230U, 0x0032A47CU, "lctrSlvConnRxCompletion",
     "5976a1985cf0db85b8e66e60d6360326d360ce1f3435aec73e80658c431d0f4c",
     "vendor-modified; exact source and redistribution authority unavailable"},
    {0x0032A47CU, 0x0032A4BEU, "lctrSlvConnTxCompletion",
     "346fbe7c747edabb178b903b452604c14efc36f4458859feeeb365b84addab8c",
     "vendor-divergent; exact source and redistribution authority unavailable"},
};

int32_t open_cfw_em9305_slv_conn_boundary(
    const open_cfw_em9305_slv_conn_ports *ports,
    open_cfw_em9305_slv_conn_entry entry,
    open_cfw_em9305_slv_conn_invocation *invocation)
{
    if (ports == 0 || invocation == 0 || entry < OPEN_CFW_EM9305_SLV_CONN_END_OP ||
        entry >= OPEN_CFW_EM9305_SLV_CONN_ENTRY_COUNT) {
        return OPEN_CFW_EM9305_SLV_CONN_INVALID_ARGUMENT;
    }
    if (ports->provider == 0) {
        return OPEN_CFW_EM9305_SLV_CONN_UNSUPPORTED;
    }
    return ports->provider(ports->context, entry, invocation) == 0
               ? OPEN_CFW_EM9305_SLV_CONN_OK
               : OPEN_CFW_EM9305_SLV_CONN_PROVIDER_FAILED;
}
