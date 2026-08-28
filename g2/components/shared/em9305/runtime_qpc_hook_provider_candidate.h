/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_EM9305_QPC_HOOK_PROVIDER_CANDIDATE_H
#define OPEN_CFW_EM9305_QPC_HOOK_PROVIDER_CANDIDATE_H

#include <stdint.h>

enum {
    OPEN_CFW_EM9305_HOOK_PROVIDER_OK = 0,
    OPEN_CFW_EM9305_HOOK_PROVIDER_MISSING = 1,
    OPEN_CFW_EM9305_HOOK_PROVIDER_FAILED = 2,
};

enum {
    OPEN_CFW_EM9305_HOOK_MODEL_NAMED_ARCHIVE_PROVIDER = 1,
    OPEN_CFW_EM9305_HOOK_MODEL_TYPED_UNRESOLVED_PROVIDER = 2,
    OPEN_CFW_EM9305_HOOK_MODEL_EXACT_NOOP_TARGET = 3,
};

typedef int32_t (*open_cfw_em9305_hook_call_fn)(void *context);
typedef int32_t (*open_cfw_em9305_hook_call_u32_fn)(void *context,
                                                    uint32_t argument);

typedef struct open_cfw_em9305_qpc_hook_ports {
    void *context;
    open_cfw_em9305_hook_call_fn pal_uart_resume;
    open_cfw_em9305_hook_call_fn wsf_os_run_idle_tasks;
    open_cfw_em9305_hook_call_u32_fn volt_mon_do_measurement;
} open_cfw_em9305_qpc_hook_ports;

typedef struct open_cfw_em9305_qpc_hook_evidence {
    uint32_t stock_start;
    uint32_t stock_end;
    uint32_t model;
    const char *stock_sha256;
    const char *provider_name;
    const char *provider_license_status;
} open_cfw_em9305_qpc_hook_evidence;

extern const open_cfw_em9305_qpc_hook_evidence
    open_cfw_em9305_qpc_hook_provider_evidence[4];

int32_t open_cfw_em9305_qf_resume_named_boundary(
    const open_cfw_em9305_qpc_hook_ports *ports);
int32_t open_cfw_em9305_qk_idle_named_boundary(
    const open_cfw_em9305_qpc_hook_ports *ports);

#endif
