#include "openr1/r1_power_lease.h"

#include <stddef.h>

static bool client_valid(r1_power_client client) {
    return (unsigned int)client < R1_POWER_LEASE_CLIENT_COUNT;
}

static uint8_t client_mask(r1_power_client client) {
    return (uint8_t)(UINT8_C(1) << (unsigned int)client);
}

void r1_power_lease_initialize(r1_power_lease *lease) {
    if (lease != NULL) {
        lease->provider = NULL;
        lease->provider_context = NULL;
        lease->active_client_mask = 0u;
    }
}

r1_error r1_power_lease_bind(r1_power_lease *lease,
                             const r1_power_provider_ops *provider,
                             void *provider_context) {
    if (lease == NULL || provider == NULL ||
        provider->set_shared_power_enabled == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (lease->active_client_mask != 0u) {
        return R1_ERROR_STATE;
    }
    lease->provider = provider;
    lease->provider_context = provider_context;
    return R1_OK;
}

r1_error r1_power_lease_acquire(r1_power_lease *lease,
                                r1_power_client client) {
    if (lease == NULL || !client_valid(client)) {
        return R1_ERROR_ARGUMENT;
    }
    if (!r1_power_lease_provider_available(lease)) {
        return R1_ERROR_UNSUPPORTED;
    }
    const uint8_t bit = client_mask(client);
    if ((lease->active_client_mask & bit) != 0u) {
        return R1_OK;
    }
    if (lease->active_client_mask == 0u &&
        !lease->provider->set_shared_power_enabled(
            lease->provider_context, true)) {
        return R1_ERROR_STATE;
    }
    lease->active_client_mask = (uint8_t)(lease->active_client_mask | bit);
    return R1_OK;
}

r1_error r1_power_lease_release(r1_power_lease *lease,
                                r1_power_client client) {
    if (lease == NULL || !client_valid(client)) {
        return R1_ERROR_ARGUMENT;
    }
    const uint8_t bit = client_mask(client);
    if ((lease->active_client_mask & bit) == 0u) {
        return R1_OK;
    }
    if (!r1_power_lease_provider_available(lease)) {
        return R1_ERROR_UNSUPPORTED;
    }
    const uint8_t remaining =
        (uint8_t)(lease->active_client_mask & (uint8_t)~bit);
    if (remaining == 0u &&
        !lease->provider->set_shared_power_enabled(
            lease->provider_context, false)) {
        return R1_ERROR_STATE;
    }
    lease->active_client_mask = remaining;
    return R1_OK;
}

bool r1_power_lease_provider_available(const r1_power_lease *lease) {
    return lease != NULL && lease->provider != NULL &&
           lease->provider->set_shared_power_enabled != NULL;
}

bool r1_power_lease_is_active(const r1_power_lease *lease,
                              r1_power_client client) {
    return lease != NULL && client_valid(client) &&
           (lease->active_client_mask & client_mask(client)) != 0u;
}

uint8_t r1_power_lease_active_mask(const r1_power_lease *lease) {
    return lease == NULL
        ? 0u
        : (uint8_t)(lease->active_client_mask & R1_POWER_LEASE_VALID_MASK);
}
