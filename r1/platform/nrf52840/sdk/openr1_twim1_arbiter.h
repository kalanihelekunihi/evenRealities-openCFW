#ifndef OPENR1_TWIM1_ARBITER_H
#define OPENR1_TWIM1_ARBITER_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "nrfx_twim.h"
#include "sdk_errors.h"

/*
 * Ownership arbiter for the single nRF52840 TWIM1 hardware peripheral.
 *
 * This module is R1-owned adaptation glue, not a recovery of stock behavior:
 * the stock firmware ran both logical buses (i2c_1 motion and i2c_5 NFC/YHM)
 * on GPIO-driven software-TWI engines that remain implementation-blocked.
 * OpenR1 substitutes the hardware TWIM1 for both clients, so this arbiter owns
 * every nrfx_twim init/uninit/transfer for instance 1 and serializes the two
 * OpenR1 clients:
 *
 * - OPENR1_TWIM1_CLIENT_MOTION: worn context, pins P0.11/P0.14;
 * - OPENR1_TWIM1_CLIENT_NFC: dock/charging context, pins P1.11/P1.14.
 *
 * The recovered product contexts are mutually exclusive, and the dock context
 * wins: NFC acquisition while motion owns the bus performs a documented
 * handoff (the motion configuration is uninitialized and the NFC configuration
 * is initialized). Motion never preempts NFC; a contested motion acquisition
 * fails honestly with NRFX_ERROR_BUSY. A preempted client's transfers fail
 * with NRFX_ERROR_BUSY until it re-acquires the bus after the owner releases
 * it. Concurrent use can therefore never silently corrupt a transfer.
 *
 * The arbiter exposes no raw register or bus-pin operation; clients keep
 * their own pin/frequency/priority configuration and only pass it to
 * openr1_twim1_acquire.
 */

typedef enum {
    OPENR1_TWIM1_CLIENT_NONE = 0,
    OPENR1_TWIM1_CLIENT_MOTION,
    OPENR1_TWIM1_CLIENT_NFC,
} openr1_twim1_client;

ret_code_t openr1_twim1_arbiter_initialize(void);
nrfx_err_t openr1_twim1_acquire(
    openr1_twim1_client client, const nrfx_twim_config_t *configuration);
nrfx_err_t openr1_twim1_release(openr1_twim1_client client);
nrfx_err_t openr1_twim1_tx(openr1_twim1_client client, uint8_t address,
                           const uint8_t *data, size_t length, bool no_stop);
nrfx_err_t openr1_twim1_rx(openr1_twim1_client client, uint8_t address,
                           uint8_t *data, size_t length);

#endif
