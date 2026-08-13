#ifndef OPENR1_R1_POWER_LEASE_H
#define OPENR1_R1_POWER_LEASE_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

/*
 * R1 product ownership policy for the shared battery/optical/touch rail.
 *
 * The electrical transition remains in a YHM2710 provider.  This module does
 * not contain a YHM register address, register value, or wire transaction.
 */
#define R1_POWER_LEASE_CLIENT_COUNT 3u
#define R1_POWER_LEASE_VALID_MASK UINT8_C(0x07)

typedef enum {
    R1_POWER_CLIENT_BATTERY_SAMPLING = 0,
    R1_POWER_CLIENT_OPTICAL_PPG = 1,
    R1_POWER_CLIENT_TOUCH = 2
} r1_power_client;

typedef struct {
    bool (*set_shared_power_enabled)(void *context, bool enabled);
} r1_power_provider_ops;

typedef struct {
    const r1_power_provider_ops *provider;
    void *provider_context;
    uint8_t active_client_mask;
} r1_power_lease;

void r1_power_lease_initialize(r1_power_lease *lease);
r1_error r1_power_lease_bind(r1_power_lease *lease,
                             const r1_power_provider_ops *provider,
                             void *provider_context);
r1_error r1_power_lease_acquire(r1_power_lease *lease,
                                r1_power_client client);
r1_error r1_power_lease_release(r1_power_lease *lease,
                                r1_power_client client);
bool r1_power_lease_provider_available(const r1_power_lease *lease);
bool r1_power_lease_is_active(const r1_power_lease *lease,
                              r1_power_client client);
uint8_t r1_power_lease_active_mask(const r1_power_lease *lease);

#endif
