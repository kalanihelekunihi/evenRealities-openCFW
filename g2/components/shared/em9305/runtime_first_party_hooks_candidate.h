/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 OpenCFW Contributors
 *
 * Clean-room, fail-closed source model for the seven authenticated first-party
 * EM9305 application spans.  This is an OpenCFW adapter API, not a claim about
 * the unpublished stock C prototypes.
 */

#ifndef OPEN_CFW_RUNTIME_EM9305_FIRST_PARTY_HOOKS_CANDIDATE_H
#define OPEN_CFW_RUNTIME_EM9305_FIRST_PARTY_HOOKS_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define OPEN_CFW_EM9305_FIRST_PARTY_SPAN_COUNT 7u
#define OPEN_CFW_EM9305_FIRST_PARTY_TOTAL_BYTES 1224u

enum open_cfw_em9305_first_party_span_id {
    OPEN_CFW_EM9305_SPAN_STARTUP_HOOK_TARGET = 0,
    OPEN_CFW_EM9305_SPAN_MYAPP_MODULE = 1,
    OPEN_CFW_EM9305_SPAN_VENDOR_RESUME_EXTENSION = 2,
    OPEN_CFW_EM9305_SPAN_VENDOR_STARTUP_EXTENSION = 3,
    OPEN_CFW_EM9305_SPAN_QF_RESUME_INTERNAL = 4,
    OPEN_CFW_EM9305_SPAN_QF_STARTUP_INTERNAL = 5,
    OPEN_CFW_EM9305_SPAN_QK_IDLE_INTERNAL = 6
};

enum open_cfw_em9305_candidate_status {
    OPEN_CFW_EM9305_CANDIDATE_OK = 0,
    OPEN_CFW_EM9305_CANDIDATE_INVALID_ARGUMENT = 1,
    OPEN_CFW_EM9305_CANDIDATE_UNRESOLVED_PROVIDER = 2,
    OPEN_CFW_EM9305_CANDIDATE_PROVIDER_FAILED = 3
};

enum open_cfw_em9305_span_model {
    OPEN_CFW_EM9305_MODEL_PROVIDER_REQUIRED = 0,
    OPEN_CFW_EM9305_MODEL_EXACT_TAIL_BRANCH = 1,
    OPEN_CFW_EM9305_MODEL_EXACT_ORDERED_CALL_SHELL = 2
};

/*
 * Conservative OpenCFW-owned carrier for unknown stock entry arguments.
 * The four words mirror the maximum ordinary ARC r0-r3 argument window; a
 * word's presence here does not assert that the stock body consumes it.
 */
struct open_cfw_em9305_opaque_invocation {
    uintptr_t words[4];
};

struct open_cfw_em9305_span_evidence {
    enum open_cfw_em9305_first_party_span_id id;
    uintptr_t stock_start;
    uintptr_t stock_end_exclusive;
    size_t stock_bytes;
    const char *stock_sha256;
    const char *family;
    enum open_cfw_em9305_span_model model;
};

typedef enum open_cfw_em9305_candidate_status
(*open_cfw_em9305_opaque_span_provider_t)(
    void *context,
    const struct open_cfw_em9305_opaque_invocation *invocation
);

typedef enum open_cfw_em9305_candidate_status
(*open_cfw_em9305_idle_step_provider_t)(void *context);

typedef enum open_cfw_em9305_candidate_status
(*open_cfw_em9305_idle_final_provider_t)(void *context, uint32_t argument);

struct open_cfw_em9305_first_party_providers {
    void *context;
    open_cfw_em9305_opaque_span_provider_t startup_hook_target;
    open_cfw_em9305_opaque_span_provider_t myapp_module;
    open_cfw_em9305_opaque_span_provider_t vendor_resume_extension;
    open_cfw_em9305_opaque_span_provider_t vendor_startup_extension;
    open_cfw_em9305_opaque_span_provider_t qf_resume_target;
    open_cfw_em9305_idle_step_provider_t idle_step_0x00333d7c;
    open_cfw_em9305_idle_step_provider_t idle_step_0x003100ec;
    open_cfw_em9305_idle_final_provider_t idle_final_0x00310728;
};

const struct open_cfw_em9305_span_evidence *
open_cfw_em9305_first_party_span_evidence(
    enum open_cfw_em9305_first_party_span_id id
);

enum open_cfw_em9305_candidate_status
open_cfw_em9305_startup_hook_target_candidate(
    const struct open_cfw_em9305_first_party_providers *providers,
    const struct open_cfw_em9305_opaque_invocation *invocation
);

enum open_cfw_em9305_candidate_status open_cfw_em9305_myapp_module_candidate(
    const struct open_cfw_em9305_first_party_providers *providers,
    const struct open_cfw_em9305_opaque_invocation *invocation
);

enum open_cfw_em9305_candidate_status
open_cfw_em9305_vendor_resume_extension_candidate(
    const struct open_cfw_em9305_first_party_providers *providers,
    const struct open_cfw_em9305_opaque_invocation *invocation
);

enum open_cfw_em9305_candidate_status
open_cfw_em9305_vendor_startup_extension_candidate(
    const struct open_cfw_em9305_first_party_providers *providers,
    const struct open_cfw_em9305_opaque_invocation *invocation
);

enum open_cfw_em9305_candidate_status
open_cfw_em9305_qf_resume_internal_hook_candidate(
    const struct open_cfw_em9305_first_party_providers *providers,
    const struct open_cfw_em9305_opaque_invocation *invocation
);

enum open_cfw_em9305_candidate_status
open_cfw_em9305_qf_startup_internal_hook_candidate(
    const struct open_cfw_em9305_first_party_providers *providers,
    const struct open_cfw_em9305_opaque_invocation *invocation
);

enum open_cfw_em9305_candidate_status
open_cfw_em9305_qk_idle_internal_hook_candidate(
    const struct open_cfw_em9305_first_party_providers *providers
);

#ifdef __cplusplus
}
#endif

#endif
