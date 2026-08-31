/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 OpenCFW Contributors
 *
 * Original OpenCFW source model.  It deliberately does not reproduce or
 * speculate about the unpublished application behavior in the stock spans.
 */

#include "runtime_first_party_hooks_candidate.h"

static const struct open_cfw_em9305_span_evidence
open_cfw_em9305_first_party_evidence[OPEN_CFW_EM9305_FIRST_PARTY_SPAN_COUNT] = {
    {
        OPEN_CFW_EM9305_SPAN_STARTUP_HOOK_TARGET,
        0x0030482cu, 0x003048aeu, 130u,
        "1aff5715814514aacc29daa8bee11dc4a20cd3ff573e312f4014b884a38d813f",
        "application_startup_hook",
        OPEN_CFW_EM9305_MODEL_PROVIDER_REQUIRED
    },
    {
        OPEN_CFW_EM9305_SPAN_MYAPP_MODULE,
        0x0030ea08u, 0x0030eb0au, 258u,
        "e7b37ea140c3ed01ba07ffb164e1d06a46189d8c2682d44e261a7f837f96d722",
        "application_module_myapp",
        OPEN_CFW_EM9305_MODEL_PROVIDER_REQUIRED
    },
    {
        OPEN_CFW_EM9305_SPAN_VENDOR_RESUME_EXTENSION,
        0x0030eb8cu, 0x0030ec9au, 270u,
        "ff00d26e1173283a929d94b70c2b9e179b6909a7e4cb4d48d17b973188171a4f",
        "application_hook",
        OPEN_CFW_EM9305_MODEL_PROVIDER_REQUIRED
    },
    {
        OPEN_CFW_EM9305_SPAN_VENDOR_STARTUP_EXTENSION,
        0x0030ecf8u, 0x0030ef12u, 538u,
        "8da28f1db4ff4d13912c78b8f6f4ddb7f36a9f93018233187d69cca3f3934d9f",
        "application_hook",
        OPEN_CFW_EM9305_MODEL_PROVIDER_REQUIRED
    },
    {
        OPEN_CFW_EM9305_SPAN_QF_RESUME_INTERNAL,
        0x00311150u, 0x00311154u, 4u,
        "7766b559c480d3129860a74a673038b9db4a622de9bb71c7957ee5e1837047de",
        "qpc_vendor_hook",
        OPEN_CFW_EM9305_MODEL_EXACT_TAIL_BRANCH
    },
    {
        OPEN_CFW_EM9305_SPAN_QF_STARTUP_INTERNAL,
        0x003111a4u, 0x003111a8u, 4u,
        "5c2ae05832a4449cd2bb20f41b843eb22dae95f3f95d0d30b0236e77ebcf5f1e",
        "qpc_vendor_hook",
        OPEN_CFW_EM9305_MODEL_EXACT_TAIL_BRANCH
    },
    {
        OPEN_CFW_EM9305_SPAN_QK_IDLE_INTERNAL,
        0x00311620u, 0x00311634u, 20u,
        "fbb0316db14f6fc107f338a4cbf5852049003c2def1230d9f5e117e7a0a2abe4",
        "application_hook",
        OPEN_CFW_EM9305_MODEL_EXACT_ORDERED_CALL_SHELL
    }
};

static const struct open_cfw_em9305_span_evidence *const
open_cfw_em9305_first_party_evidence_by_id[
    OPEN_CFW_EM9305_FIRST_PARTY_SPAN_COUNT
] = {
    &open_cfw_em9305_first_party_evidence[0],
    &open_cfw_em9305_first_party_evidence[1],
    &open_cfw_em9305_first_party_evidence[2],
    &open_cfw_em9305_first_party_evidence[3],
    &open_cfw_em9305_first_party_evidence[4],
    &open_cfw_em9305_first_party_evidence[5],
    &open_cfw_em9305_first_party_evidence[6]
};

static enum open_cfw_em9305_candidate_status open_cfw_em9305_call_opaque(
    const struct open_cfw_em9305_first_party_providers *providers,
    open_cfw_em9305_opaque_span_provider_t provider,
    const struct open_cfw_em9305_opaque_invocation *invocation
)
{
    enum open_cfw_em9305_candidate_status status;

    if (providers == 0 || invocation == 0) {
        return OPEN_CFW_EM9305_CANDIDATE_INVALID_ARGUMENT;
    }
    if (provider == 0) {
        return OPEN_CFW_EM9305_CANDIDATE_UNRESOLVED_PROVIDER;
    }
    status = provider(providers->context, invocation);
    return status == OPEN_CFW_EM9305_CANDIDATE_OK
        ? OPEN_CFW_EM9305_CANDIDATE_OK
        : OPEN_CFW_EM9305_CANDIDATE_PROVIDER_FAILED;
}

const struct open_cfw_em9305_span_evidence *
open_cfw_em9305_first_party_span_evidence(
    enum open_cfw_em9305_first_party_span_id id
)
{
    if ((unsigned int)id >= OPEN_CFW_EM9305_FIRST_PARTY_SPAN_COUNT) {
        return 0;
    }
    return open_cfw_em9305_first_party_evidence_by_id[(unsigned int)id];
}

enum open_cfw_em9305_candidate_status
open_cfw_em9305_startup_hook_target_candidate(
    const struct open_cfw_em9305_first_party_providers *providers,
    const struct open_cfw_em9305_opaque_invocation *invocation
)
{
    return open_cfw_em9305_call_opaque(
        providers,
        providers == 0 ? 0 : providers->startup_hook_target,
        invocation
    );
}

enum open_cfw_em9305_candidate_status open_cfw_em9305_myapp_module_candidate(
    const struct open_cfw_em9305_first_party_providers *providers,
    const struct open_cfw_em9305_opaque_invocation *invocation
)
{
    return open_cfw_em9305_call_opaque(
        providers,
        providers == 0 ? 0 : providers->myapp_module,
        invocation
    );
}

enum open_cfw_em9305_candidate_status
open_cfw_em9305_vendor_resume_extension_candidate(
    const struct open_cfw_em9305_first_party_providers *providers,
    const struct open_cfw_em9305_opaque_invocation *invocation
)
{
    return open_cfw_em9305_call_opaque(
        providers,
        providers == 0 ? 0 : providers->vendor_resume_extension,
        invocation
    );
}

enum open_cfw_em9305_candidate_status
open_cfw_em9305_vendor_startup_extension_candidate(
    const struct open_cfw_em9305_first_party_providers *providers,
    const struct open_cfw_em9305_opaque_invocation *invocation
)
{
    return open_cfw_em9305_call_opaque(
        providers,
        providers == 0 ? 0 : providers->vendor_startup_extension,
        invocation
    );
}

enum open_cfw_em9305_candidate_status
open_cfw_em9305_qf_resume_internal_hook_candidate(
    const struct open_cfw_em9305_first_party_providers *providers,
    const struct open_cfw_em9305_opaque_invocation *invocation
)
{
    return open_cfw_em9305_call_opaque(
        providers,
        providers == 0 ? 0 : providers->qf_resume_target,
        invocation
    );
}

enum open_cfw_em9305_candidate_status
open_cfw_em9305_qf_startup_internal_hook_candidate(
    const struct open_cfw_em9305_first_party_providers *providers,
    const struct open_cfw_em9305_opaque_invocation *invocation
)
{
    /* Stock is one tail branch to the modeled 0x0030482c target span. */
    return open_cfw_em9305_startup_hook_target_candidate(providers, invocation);
}

enum open_cfw_em9305_candidate_status
open_cfw_em9305_qk_idle_internal_hook_candidate(
    const struct open_cfw_em9305_first_party_providers *providers
)
{
    enum open_cfw_em9305_candidate_status status;

    if (providers == 0) {
        return OPEN_CFW_EM9305_CANDIDATE_INVALID_ARGUMENT;
    }
    /* Validate the whole shell before allowing its first side effect. */
    if (
        providers->idle_step_0x00333d7c == 0 ||
        providers->idle_step_0x003100ec == 0 ||
        providers->idle_final_0x00310728 == 0
    ) {
        return OPEN_CFW_EM9305_CANDIDATE_UNRESOLVED_PROVIDER;
    }
    status = providers->idle_step_0x00333d7c(providers->context);
    if (status != OPEN_CFW_EM9305_CANDIDATE_OK) {
        return OPEN_CFW_EM9305_CANDIDATE_PROVIDER_FAILED;
    }
    status = providers->idle_step_0x003100ec(providers->context);
    if (status != OPEN_CFW_EM9305_CANDIDATE_OK) {
        return OPEN_CFW_EM9305_CANDIDATE_PROVIDER_FAILED;
    }
    status = providers->idle_final_0x00310728(providers->context, 0u);
    return status == OPEN_CFW_EM9305_CANDIDATE_OK
        ? OPEN_CFW_EM9305_CANDIDATE_OK
        : OPEN_CFW_EM9305_CANDIDATE_PROVIDER_FAILED;
}
