/* SPDX-License-Identifier: MIT */
/*
 * Clean-room, fail-closed adapter for two authenticated EM9305 QP/C hooks.
 * Callback return values belong to this adapter contract, not to the stock ARC
 * ABI. Exact provider source and redistribution authority remain separate gates.
 */

#include "runtime_qpc_hook_provider_candidate.h"

const open_cfw_em9305_qpc_hook_evidence
open_cfw_em9305_qpc_hook_provider_evidence[4] = {
    {0x00311150U, 0x00311154U,
     OPEN_CFW_EM9305_HOOK_MODEL_NAMED_ARCHIVE_PROVIDER,
     "7766b559c480d3129860a74a673038b9db4a622de9bb71c7957ee5e1837047de",
     "PalUartResume", "exact SDK archive; redistribution authority unresolved"},
    {0x00311620U, 0x00311634U,
     OPEN_CFW_EM9305_HOOK_MODEL_NAMED_ARCHIVE_PROVIDER,
     "fbb0316db14f6fc107f338a4cbf5852049003c2def1230d9f5e117e7a0a2abe4",
     "wsfOsRunIdleTasks", "exact SDK archive; redistribution authority unresolved"},
    {0x003100ECU, 0x003100F0U,
     OPEN_CFW_EM9305_HOOK_MODEL_NAMED_ARCHIVE_PROVIDER,
     "f64115f823d5675ed59321d1edd7c76faddd893e7ed7914dec00cb156a6a8a04",
     "VoltMon_DoMeasurement", "exact SDK archive; redistribution authority unresolved"},
    {0x00310728U, 0x0031072EU,
     OPEN_CFW_EM9305_HOOK_MODEL_EXACT_NOOP_TARGET,
     "e9d2f8dea13fd219fc4d874e188bad89a6a1185db4704f7067ed7a5a7797564c",
     "no-op target 0x003101E8", "authenticated stock semantics; no copied source"},
};

static int32_t call_checked(open_cfw_em9305_hook_call_fn function,
                            void *context)
{
    if (function == 0) {
        return OPEN_CFW_EM9305_HOOK_PROVIDER_MISSING;
    }
    return function(context) == 0 ? OPEN_CFW_EM9305_HOOK_PROVIDER_OK
                                  : OPEN_CFW_EM9305_HOOK_PROVIDER_FAILED;
}

int32_t open_cfw_em9305_qf_resume_named_boundary(
    const open_cfw_em9305_qpc_hook_ports *ports)
{
    if (ports == 0) {
        return OPEN_CFW_EM9305_HOOK_PROVIDER_MISSING;
    }
    return call_checked(ports->pal_uart_resume, ports->context);
}

int32_t open_cfw_em9305_qk_idle_named_boundary(
    const open_cfw_em9305_qpc_hook_ports *ports)
{
    if (ports == 0 || ports->wsf_os_run_idle_tasks == 0 ||
        ports->volt_mon_do_measurement == 0) {
        return OPEN_CFW_EM9305_HOOK_PROVIDER_MISSING;
    }
    if (ports->wsf_os_run_idle_tasks(ports->context) != 0 ||
        ports->volt_mon_do_measurement(ports->context, 0U) != 0) {
        return OPEN_CFW_EM9305_HOOK_PROVIDER_FAILED;
    }
    /* The final authenticated call chain terminates in a four-byte no-op. */
    return OPEN_CFW_EM9305_HOOK_PROVIDER_OK;
}
