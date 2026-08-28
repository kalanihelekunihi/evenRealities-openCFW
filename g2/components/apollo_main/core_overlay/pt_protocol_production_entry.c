/* SPDX-License-Identifier: MIT */
#include "pt_protocol_production_entry.h"

#include "pt_protocol_board_backend.h"


enum {
    OPEN_CFW_PT_PRODUCTION_OTA_STORAGE_BYTES = 6000U,
    OPEN_CFW_PT_PRODUCTION_STATE_MAGIC = 0x50544346U
};

struct open_cfw_pt_production_state {
    struct open_cfw_pt_platform_adapter platform_adapter;
    struct open_cfw_pt_firmware_service firmware_service;
    struct open_cfw_pt_board_backend board;
    struct open_cfw_pt_platform_backend backend;
    uint32_t magic;
    uint8_t installed;
};

_Static_assert(sizeof(struct open_cfw_pt_production_state) <
    OPEN_CFW_PT_PRODUCTION_OTA_STORAGE_BYTES,
    "PT production state must leave OTA transfer staging space");

/*
 * The authenticated Apollo image reserves [0x20059EF8, +6000) for PT OTA
 * transfer data.  The production implementation places persistent control
 * state at the high end and stages transfer bytes in the disjoint low end.
 * A flush copies the low-end staging span to the same low-end OTA ABI buffer,
 * so it cannot overwrite control state.  Host builds retain ordinary storage
 * to keep semantic tests independent of target addresses.
 */
static struct open_cfw_pt_production_state *production_state(void)
{
#if defined(__arm__) || defined(__thumb__)
    return (struct open_cfw_pt_production_state *)(uintptr_t)(
        0x20059EF8U + OPEN_CFW_PT_PRODUCTION_OTA_STORAGE_BYTES -
        sizeof(struct open_cfw_pt_production_state));
#else
    static struct open_cfw_pt_production_state host_state;
    return &host_state;
#endif
}

static int production_install_with_storage(
    const struct open_cfw_pt_platform_backend *backend,
    uint8_t *transfer_staging, size_t transfer_staging_capacity);


int open_cfw_pt_protocol_production_bootstrap(void)
{
    struct open_cfw_pt_production_state *state = production_state();
    int result;
    state->installed = 0U;
    state->magic = 0U;
    result = open_cfw_pt_board_backend_initialize_production(
        &state->board, &state->backend);
    if (result != OPEN_CFW_PT_OK) {
        return result;
    }
    return production_install_with_storage(
        &state->backend, state->board.calls->ota_async_data,
        OPEN_CFW_PT_PRODUCTION_OTA_STORAGE_BYTES - sizeof(*state));
}


int open_cfw_pt_protocol_production_install(
    const struct open_cfw_pt_platform_backend *backend)
{
    return production_install_with_storage(backend, NULL, 0U);
}


static int production_install_with_storage(
    const struct open_cfw_pt_platform_backend *backend,
    uint8_t *transfer_staging, size_t transfer_staging_capacity)
{
    struct open_cfw_pt_production_state *state = production_state();
    int result;
    state->installed = 0U;
    result = open_cfw_pt_platform_adapter_initialize(
        &state->platform_adapter, backend);
    if (result != OPEN_CFW_PT_OK) {
        return result;
    }
    result = open_cfw_pt_firmware_service_initialize(
        &state->firmware_service, &state->platform_adapter.all,
        transfer_staging, transfer_staging_capacity);
    if (result == OPEN_CFW_PT_OK) {
        state->magic = OPEN_CFW_PT_PRODUCTION_STATE_MAGIC;
        state->installed = 1U;
    }
    return result;
}


int open_cfw_pt_protocol_production_entry(
    uint8_t *request, uint8_t request_length,
    uint8_t *response, uint8_t *response_length)
{
    struct open_cfw_pt_production_state *state = production_state();
#if defined(__arm__) || defined(__thumb__)
    if (state->magic != OPEN_CFW_PT_PRODUCTION_STATE_MAGIC ||
        state->installed == 0U) {
        int result = open_cfw_pt_protocol_production_bootstrap();
        if (result != OPEN_CFW_PT_OK) return result;
        state = production_state();
    }
#endif
    if (state->installed == 0U) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    return open_cfw_pt_firmware_service_dispatch(
        &state->firmware_service, request, request_length, response, 256U,
        response_length);
}


int open_cfw_pt_protocol_production_postprocess(
    const uint8_t *request, uint8_t request_length,
    const uint8_t *response, uint8_t response_length)
{
    struct open_cfw_pt_production_state *state = production_state();
    if (state->installed == 0U ||
        state->platform_adapter.backend.perform == NULL) {
        return OPEN_CFW_PT_HANDLER_FAILED;
    }
    return state->platform_adapter.backend.perform(
        OPEN_CFW_PT_OP_POST_RESPONSE,
        (uintptr_t)request, (uintptr_t)request_length,
        (uintptr_t)response, (uintptr_t)response_length, 0U,
        state->platform_adapter.backend.context);
}


#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_PT_LEGACY_SECTION(name) \
    __attribute__((used, noinline, section(name)))
#else
#define OPEN_CFW_PT_LEGACY_SECTION(name) __attribute__((used, noinline))
#endif


OPEN_CFW_PT_LEGACY_SECTION(".pt_legacy_entry")
int open_cfw_pt_protocol_legacy_entry(
    uint8_t *request, uint8_t request_length,
    uint8_t *response, uint8_t *response_length)
{
    return open_cfw_pt_protocol_production_entry(
        request, request_length, response, response_length);
}


OPEN_CFW_PT_LEGACY_SECTION(".pt_legacy_postprocess")
int open_cfw_pt_protocol_legacy_postprocess(
    const uint8_t *request, uint8_t request_length,
    const uint8_t *response, uint8_t response_length)
{
    return open_cfw_pt_protocol_production_postprocess(
        request, request_length, response, response_length);
}


#undef OPEN_CFW_PT_LEGACY_SECTION


void open_cfw_pt_protocol_production_reset(void)
{
    production_state()->installed = 0U;
}
