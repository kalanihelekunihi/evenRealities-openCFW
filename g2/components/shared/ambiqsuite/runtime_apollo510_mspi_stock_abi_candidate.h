/*
 * SPDX-License-Identifier: BSD-3-Clause
 * Copyright (c) 2026 OpenCFW Contributors
 *
 * Compatibility declarations for the G2 pre-release Apollo510 MSPI request
 * ABI.  The provider remains the unmodified, BSD-3-Clause AmbiqSuite 5.1.0
 * am_hal_mspi.c translation unit.
 */

#ifndef OPEN_CFW_RUNTIME_APOLLO510_MSPI_STOCK_ABI_CANDIDATE_H
#define OPEN_CFW_RUNTIME_APOLLO510_MSPI_STOCK_ABI_CANDIDATE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define OPEN_CFW_G2_MSPI_STATUS_INVALID_ARG 6u
#define OPEN_CFW_G2_MSPI_STOCK_REQUEST_MAX 40u
#define OPEN_CFW_G2_MSPI_REQUEST_UNSUPPORTED UINT32_MAX

typedef uint32_t (*open_cfw_g2_mspi_control_provider_t)(
    void *handle,
    uint32_t request,
    void *configuration
);

/*
 * Translate the low-byte request ABI used by opaque G2 stock callers to the
 * public AmbiqSuite 5.1.0 ordinal.  Returns one when a public equivalent
 * exists.  Stock-only SDR250 disable/enable requests 10 and 11, the stock
 * sentinel 40, and all other invalid low-byte requests return zero.
 */
uint32_t open_cfw_g2_mspi_request_translate(
    uint32_t stock_request,
    uint32_t *upstream_request
);

/* Injectable form used by the candidate's software-only qualification. */
uint32_t open_cfw_g2_mspi_control_dispatch(
    void *handle,
    uint32_t stock_request,
    void *configuration,
    open_cfw_g2_mspi_control_provider_t provider
);

/* Production-shaped entry: dispatch to the authenticated upstream HAL. */
uint32_t open_cfw_g2_mspi_control_stock_abi_candidate(
    void *handle,
    uint32_t stock_request,
    void *configuration
);

#ifdef __cplusplus
}
#endif

#endif
