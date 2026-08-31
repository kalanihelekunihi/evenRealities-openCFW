/*
 * SPDX-License-Identifier: MIT
 *
 * Minimal stock-ABI transition shim for the four authenticated G2 Apollo
 * service_audio LC3 contexts.  This is source-owned routing material; it does
 * not by itself authorize stock call patches or flash placement.
 */
#include "runtime_liblc3_service_audio_stock_shim.h"

#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "runtime_liblc3_service_audio_adapter.h"

#define OPEN_CFW_LIBLC3_STOCK_FAILURE INT32_C(-1)
#define OPEN_CFW_LIBLC3_STOCK_OWNER_BASIS UINT32_C(0x4C430000)

_Static_assert(sizeof(struct open_cfw_liblc3_service_audio_config) == 24U,
    "stock LC3 configuration geometry changed");
_Static_assert(sizeof(struct open_cfw_liblc3_service_audio_state) == 2628U,
    "stock LC3 context slot geometry changed");
_Static_assert(OPEN_CFW_LIBLC3_STOCK_CONTEXT_1 -
    OPEN_CFW_LIBLC3_STOCK_CONTEXT_0 == 2628U,
    "stock LC3 context 0/1 spacing changed");
_Static_assert(OPEN_CFW_LIBLC3_STOCK_CONTEXT_2 -
    OPEN_CFW_LIBLC3_STOCK_CONTEXT_1 == 2628U,
    "stock LC3 context 1/2 spacing changed");
_Static_assert(OPEN_CFW_LIBLC3_STOCK_CONTEXT_3 -
    OPEN_CFW_LIBLC3_STOCK_CONTEXT_2 == 2628U,
    "stock LC3 context 2/3 spacing changed");
_Static_assert(OPEN_CFW_LIBLC3_STOCK_CONTEXT_END -
    OPEN_CFW_LIBLC3_STOCK_CONTEXT_3 == 2628U,
    "stock LC3 context 3/end spacing changed");

static bool open_cfw_liblc3_stock_ranges_overlap(
    const void *first, size_t first_size,
    const void *second, size_t second_size)
{
    uintptr_t first_start = (uintptr_t)first;
    uintptr_t second_start = (uintptr_t)second;

    if (first_size == 0U || second_size == 0U) {
        return false;
    }
    if (first_size > UINTPTR_MAX - first_start ||
        second_size > UINTPTR_MAX - second_start) {
        return true;
    }
    return first_start < second_start + second_size &&
        second_start < first_start + first_size;
}

static int open_cfw_liblc3_stock_context_index(const void *context)
{
#ifdef OPEN_CFW_LIBLC3_SERVICE_AUDIO_STOCK_CONTEXT_INDEX
    return OPEN_CFW_LIBLC3_SERVICE_AUDIO_STOCK_CONTEXT_INDEX(context);
#else
    static const uintptr_t contexts[4] = {
        OPEN_CFW_LIBLC3_STOCK_CONTEXT_0,
        OPEN_CFW_LIBLC3_STOCK_CONTEXT_1,
        OPEN_CFW_LIBLC3_STOCK_CONTEXT_2,
        OPEN_CFW_LIBLC3_STOCK_CONTEXT_3,
    };
    uintptr_t address = (uintptr_t)context;
    size_t index;

    for (index = 0U; index < 4U; index += 1U) {
        if (address == contexts[index]) {
            return (int)index;
        }
    }
    return -1;
#endif
}

static uint32_t open_cfw_liblc3_stock_owner(int index)
{
    return OPEN_CFW_LIBLC3_STOCK_OWNER_BASIS | (uint32_t)(index + 1);
}

static bool open_cfw_liblc3_stock_frame_valid(uint32_t frame_us)
{
    return frame_us == 2500U || frame_us == 5000U ||
        frame_us == 7500U || frame_us == 10000U;
}

static bool open_cfw_liblc3_stock_rate_valid(uint32_t sample_rate_hz)
{
    return sample_rate_hz == 8000U || sample_rate_hz == 16000U ||
        sample_rate_hz == 24000U || sample_rate_hz == 32000U ||
        sample_rate_hz == 48000U;
}

static bool open_cfw_liblc3_stock_header_valid(
    const struct open_cfw_liblc3_service_audio_config *config,
    const struct open_cfw_liblc3_service_audio_state *state)
{
    /* Stock +24 is the cached encoder pointer; zero proves pre-transition. */
    return state->bitrate_bps == 0U && config->pcm_format <= 3U &&
        open_cfw_liblc3_stock_frame_valid(config->frame_us) &&
        open_cfw_liblc3_stock_rate_valid(config->sample_rate_hz) &&
        config->channels != 0U && config->channels <= (uint32_t)INT_MAX &&
        config->channel_offset < config->channels &&
        config->bitrate_bps != 0U;
}

static void open_cfw_liblc3_stock_restore_header(
    struct open_cfw_liblc3_service_audio_state *state,
    const struct open_cfw_liblc3_service_audio_config *config)
{
    memcpy(state, config, sizeof(*config));
    state->bitrate_bps = 0U;
}

static int open_cfw_liblc3_stock_transition(
    struct open_cfw_liblc3_service_audio_state *state,
    uint32_t owner,
    struct open_cfw_liblc3_service_audio_plan *plan)
{
    struct open_cfw_liblc3_service_audio_config stock_config;
    int status;

    memcpy(&stock_config, state, sizeof(stock_config));
    if (!open_cfw_liblc3_stock_header_valid(&stock_config, state)) {
        return OPEN_CFW_LIBLC3_STOCK_FAILURE;
    }
    state->state_seal = 0U;
    state->owner_token = 0U;
    state->generation = 0U;
    state->config_word = 0U;
    state->channels = 0U;
    state->channel_offset = 0U;
    state->bitrate_bps = 0U;
    status = open_cfw_liblc3_service_audio_state_init(state);
    if (status == OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK) {
        status = open_cfw_liblc3_service_audio_open(
            state, owner, &stock_config, plan);
    }
    if (status != OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK) {
        open_cfw_liblc3_stock_restore_header(state, &stock_config);
        return OPEN_CFW_LIBLC3_STOCK_FAILURE;
    }
    return 0;
}

static int open_cfw_liblc3_stock_ensure_open(
    void *stock_context,
    struct open_cfw_liblc3_service_audio_plan *plan)
{
    struct open_cfw_liblc3_service_audio_state *state =
        (struct open_cfw_liblc3_service_audio_state *)stock_context;
    int index = open_cfw_liblc3_stock_context_index(stock_context);
    uint32_t owner;
    int status;

    if (index < 0) {
        return OPEN_CFW_LIBLC3_STOCK_FAILURE;
    }
    owner = open_cfw_liblc3_stock_owner(index);
    status = open_cfw_liblc3_service_audio_query_plan(state, owner, plan);
    if (status == OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK) {
        return 0;
    }
    return open_cfw_liblc3_stock_transition(state, owner, plan);
}

static int open_cfw_liblc3_stock_force_setup(
    void *stock_context,
    struct open_cfw_liblc3_service_audio_plan *plan)
{
    struct open_cfw_liblc3_service_audio_state *state =
        (struct open_cfw_liblc3_service_audio_state *)stock_context;
    struct open_cfw_liblc3_service_audio_config config;
    int index = open_cfw_liblc3_stock_context_index(stock_context);
    uint32_t owner;
    int status;

    if (index < 0) {
        return OPEN_CFW_LIBLC3_STOCK_FAILURE;
    }
    owner = open_cfw_liblc3_stock_owner(index);
    status = open_cfw_liblc3_service_audio_snapshot(
        state, owner, &config, plan);
    if (status != OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK) {
        return open_cfw_liblc3_stock_transition(state, owner, plan);
    }
    status = open_cfw_liblc3_service_audio_close(state, owner);
    if (status == OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK) {
        status = open_cfw_liblc3_service_audio_open(
            state, owner, &config, plan);
    }
    if (status != OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK) {
        open_cfw_liblc3_stock_restore_header(state, &config);
        return OPEN_CFW_LIBLC3_STOCK_FAILURE;
    }
    return 0;
}

void open_cfw_liblc3_service_audio_stock_setup(void *stock_context)
{
    struct open_cfw_liblc3_service_audio_plan plan;

    if (stock_context != NULL) {
        (void)open_cfw_liblc3_stock_force_setup(stock_context, &plan);
    }
}

int32_t open_cfw_liblc3_service_audio_stock_encode(
    const void *pcm,
    uint32_t pcm_bytes,
    void *output,
    int32_t *output_bytes,
    void *stock_context)
{
    struct open_cfw_liblc3_service_audio_state *state =
        (struct open_cfw_liblc3_service_audio_state *)stock_context;
    struct open_cfw_liblc3_service_audio_plan plan;
    uint64_t frame_count;
    uint64_t required;
    size_t produced = 0U;
    uint32_t owner;
    int index;
    int status;

    if (pcm == NULL || output == NULL || output_bytes == NULL ||
        stock_context == NULL) {
        return OPEN_CFW_LIBLC3_STOCK_FAILURE;
    }
    index = open_cfw_liblc3_stock_context_index(stock_context);
    if (index < 0 || open_cfw_liblc3_stock_ensure_open(
            stock_context, &plan) != 0 ||
        plan.interleaved_input_frame_bytes == 0U ||
        pcm_bytes % plan.interleaved_input_frame_bytes != 0U) {
        return OPEN_CFW_LIBLC3_STOCK_FAILURE;
    }
    frame_count = pcm_bytes / plan.interleaved_input_frame_bytes;
    required = frame_count * plan.frame_bytes;
    if (required > (uint64_t)INT32_MAX ||
        open_cfw_liblc3_stock_ranges_overlap(
            output_bytes, sizeof(*output_bytes), state, sizeof(*state)) ||
        open_cfw_liblc3_stock_ranges_overlap(
            output_bytes, sizeof(*output_bytes), pcm, pcm_bytes) ||
        open_cfw_liblc3_stock_ranges_overlap(
            output_bytes, sizeof(*output_bytes), output, (size_t)required)) {
        return OPEN_CFW_LIBLC3_STOCK_FAILURE;
    }
    owner = open_cfw_liblc3_stock_owner(index);
    status = open_cfw_liblc3_service_audio_encode(
        state, owner, pcm, pcm_bytes, output, (size_t)required, &produced);
    if (status == OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK ||
        status == OPEN_CFW_LIBLC3_SERVICE_AUDIO_PROVIDER_ERROR) {
        if (produced > (size_t)INT32_MAX) {
            return OPEN_CFW_LIBLC3_STOCK_FAILURE;
        }
        *output_bytes = (int32_t)produced;
    }
    return status == OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK ?
        0 : OPEN_CFW_LIBLC3_STOCK_FAILURE;
}
