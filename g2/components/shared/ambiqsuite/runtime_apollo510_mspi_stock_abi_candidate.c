/*
 * SPDX-License-Identifier: BSD-3-Clause
 * Copyright (c) 2026 OpenCFW Contributors
 *
 * G2 stock-request adapter for the unmodified AmbiqSuite 5.1.0 Apollo510
 * MSPI HAL.  Ambiq's translation unit and license remain vendored under
 * third_party/ambiqsuite-apollo510; no Ambiq implementation is copied here.
 */

#include "runtime_apollo510_mspi_stock_abi_candidate.h"

/* Public ABI of am_hal_mspi_control; its enum is a 32-bit Arm C integer. */
extern uint32_t am_hal_mspi_control(
    void *handle,
    uint32_t request,
    void *configuration
);

struct open_cfw_g2_mspi_request_pair {
    uint8_t stock;
    uint8_t upstream;
};

/*
 * Stock 10/11 are removed SDR250 disable/enable controls.  Public 5.1.0
 * inserted no replacement.  Stock swaps DEVICE_CONFIG and CLOCK_CONFIG,
 * while public 5.1.0 appends SCRAMBLE_CONFIG and SET_DATA_LATENCY after the
 * last request present in stock.
 */
static const struct open_cfw_g2_mspi_request_pair g_request_translation[] = {
    {  0u,  0u }, {  1u,  1u }, {  2u,  2u }, {  3u,  3u },
    {  4u,  4u }, {  5u,  5u }, {  6u,  6u }, {  7u,  7u },
    {  8u,  8u }, {  9u,  9u },
    { 12u, 10u }, { 13u, 11u }, { 14u, 12u }, { 15u, 13u },
    { 16u, 14u }, { 17u, 15u }, { 18u, 16u }, { 19u, 17u },
    { 20u, 18u }, { 21u, 19u }, { 22u, 20u }, { 23u, 21u },
    { 24u, 22u }, { 25u, 24u }, { 26u, 23u }, { 27u, 25u },
    { 28u, 26u }, { 29u, 27u }, { 30u, 28u }, { 31u, 29u },
    { 32u, 30u }, { 33u, 31u }, { 34u, 32u }, { 35u, 33u },
    { 36u, 34u }, { 37u, 35u }, { 38u, 36u }, { 39u, 37u },
};

uint32_t
open_cfw_g2_mspi_request_translate(
    uint32_t stock_request,
    uint32_t *upstream_request
)
{
    uint32_t index;
    uint32_t request = stock_request & 0xffu;

    if (upstream_request == 0) {
        return 0u;
    }
    *upstream_request = OPEN_CFW_G2_MSPI_REQUEST_UNSUPPORTED;
    for (index = 0u;
         index < sizeof(g_request_translation) / sizeof(g_request_translation[0]);
         ++index) {
        if ((uint32_t)g_request_translation[index].stock == request) {
            *upstream_request = (uint32_t)g_request_translation[index].upstream;
            return 1u;
        }
    }
    return 0u;
}

uint32_t
open_cfw_g2_mspi_control_dispatch(
    void *handle,
    uint32_t stock_request,
    void *configuration,
    open_cfw_g2_mspi_control_provider_t provider
)
{
    uint32_t upstream_request;

    if (provider == 0 ||
        open_cfw_g2_mspi_request_translate(
            stock_request,
            &upstream_request
        ) == 0u) {
        return OPEN_CFW_G2_MSPI_STATUS_INVALID_ARG;
    }
    return provider(handle, upstream_request, configuration);
}

uint32_t
open_cfw_g2_mspi_control_stock_abi_candidate(
    void *handle,
    uint32_t stock_request,
    void *configuration
)
{
    return open_cfw_g2_mspi_control_dispatch(
        handle,
        stock_request,
        configuration,
        am_hal_mspi_control
    );
}
