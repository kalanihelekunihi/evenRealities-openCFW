/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_PT_PROTOCOL_PRODUCTION_ENTRY_H
#define OPEN_CFW_PT_PROTOCOL_PRODUCTION_ENTRY_H

#include <stdint.h>

#include "pt_protocol_platform_adapter.h"

/* Bind the authenticated Apollo board ABI and install the PT service. */
int open_cfw_pt_protocol_production_bootstrap(void);
int open_cfw_pt_protocol_production_install(
    const struct open_cfw_pt_platform_backend *backend);
/*
 * Stock-compatible four-argument entry.  The caller owns a response buffer of
 * OPEN_CFW_PT_MAX_FRAME_SIZE bytes; response_length is cleared by dispatch on
 * every installed-service failure path.
 */
int open_cfw_pt_protocol_production_entry(
    uint8_t *request, uint8_t request_length,
    uint8_t *response, uint8_t *response_length);
int open_cfw_pt_protocol_production_postprocess(
    const uint8_t *request, uint8_t request_length,
    const uint8_t *response, uint8_t response_length);
/* Fixed-address compatibility veneers used by stock and source UART ingress. */
int open_cfw_pt_protocol_legacy_entry(
    uint8_t *request, uint8_t request_length,
    uint8_t *response, uint8_t *response_length);
int open_cfw_pt_protocol_legacy_postprocess(
    const uint8_t *request, uint8_t request_length,
    const uint8_t *response, uint8_t response_length);
void open_cfw_pt_protocol_production_reset(void);

#endif
