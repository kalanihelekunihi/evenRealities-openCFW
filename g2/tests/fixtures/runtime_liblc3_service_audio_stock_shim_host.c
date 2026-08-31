/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "runtime_liblc3_service_audio_adapter_host.c"

static uint8_t fixture_stock_backing[4U * 2628U + 8U];

static struct open_cfw_liblc3_service_audio_state *fixture_stock_context(
    uint32_t index)
{
    uintptr_t raw = (uintptr_t)fixture_stock_backing;
    uintptr_t base = raw + ((4U - (raw & 7U)) & 7U);

    if (index >= 4U) {
        return NULL;
    }
    return (struct open_cfw_liblc3_service_audio_state *)(void *)(
        base + index * 2628U);
}

static int fixture_stock_context_index(const void *context)
{
    uint32_t index;

    for (index = 0U; index < 4U; index += 1U) {
        if (context == fixture_stock_context(index)) {
            return (int)index;
        }
    }
    return -1;
}

#define OPEN_CFW_LIBLC3_SERVICE_AUDIO_STOCK_CONTEXT_INDEX(context) \
    fixture_stock_context_index(context)
#include "../../components/shared/liblc3/runtime_liblc3_service_audio_stock_shim.c"

void fixture_stock_reset(void)
{
    memset(fixture_stock_backing, 0, sizeof(fixture_stock_backing));
    fixture_service_audio_reset();
}

uintptr_t fixture_stock_context_address(uint32_t index)
{
    return (uintptr_t)fixture_stock_context(index);
}

void fixture_stock_configure(
    uint32_t index,
    const struct open_cfw_liblc3_service_audio_config *config)
{
    struct open_cfw_liblc3_service_audio_state *state =
        fixture_stock_context(index);

    if (state != NULL && config != NULL) {
        memcpy(state, config, sizeof(*config));
        state->bitrate_bps = 0U;
    }
}

void fixture_stock_copy_header(uint32_t index, void *output)
{
    struct open_cfw_liblc3_service_audio_state *state =
        fixture_stock_context(index);

    if (state != NULL && output != NULL) {
        memcpy(output, state, 28U);
    }
}
