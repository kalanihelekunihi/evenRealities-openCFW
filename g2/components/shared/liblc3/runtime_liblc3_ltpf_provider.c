/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded source-provider contract for Google liblc3 LTPF analysis.  The
 * pristine upstream ltpf.c is compiled separately under Apache-2.0.
 */
#include "runtime_liblc3_ltpf_provider.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "ltpf.h"

_Static_assert(sizeof(enum lc3_dt) == 1U,
    "G2 liblc3 LTPF requires -fshort-enums");
_Static_assert(sizeof(enum lc3_srate) == 1U,
    "G2 liblc3 LTPF requires -fshort-enums");
_Static_assert(sizeof(lc3_ltpf_analysis_t) == 0x488U,
    "liblc3 LTPF analysis state size changed");
_Static_assert(offsetof(lc3_ltpf_analysis_t, active) == 0x000U,
    "liblc3 LTPF active offset changed");
_Static_assert(offsetof(lc3_ltpf_analysis_t, pitch) == 0x004U,
    "liblc3 LTPF pitch offset changed");
_Static_assert(offsetof(lc3_ltpf_analysis_t, nc) == 0x008U,
    "liblc3 LTPF normalized-correlation offset changed");
_Static_assert(offsetof(lc3_ltpf_analysis_t, hp50) == 0x010U,
    "liblc3 LTPF high-pass state offset changed");
_Static_assert(offsetof(lc3_ltpf_analysis_t, x_12k8) == 0x020U,
    "liblc3 LTPF 12.8-kHz history offset changed");
_Static_assert(offsetof(lc3_ltpf_analysis_t, x_6k4) == 0x320U,
    "liblc3 LTPF 6.4-kHz history offset changed");
_Static_assert(offsetof(lc3_ltpf_analysis_t, tc) == 0x484U,
    "liblc3 LTPF pitch-lag offset changed");
_Static_assert(sizeof(lc3_ltpf_data_t) == 8U,
    "liblc3 LTPF result ABI changed");
_Static_assert(offsetof(lc3_ltpf_data_t, active) == 0U &&
    offsetof(lc3_ltpf_data_t, pitch_index) == 4U,
    "liblc3 LTPF result offsets changed");
_Static_assert(sizeof(struct open_cfw_liblc3_ltpf_config) == 4U,
    "OpenCFW LTPF config ABI changed");
_Static_assert(sizeof(struct open_cfw_liblc3_ltpf_plan) == 16U,
    "OpenCFW LTPF plan ABI changed");
_Static_assert(sizeof(struct open_cfw_liblc3_ltpf_result) == 8U,
    "OpenCFW LTPF result ABI changed");

static const uint32_t open_cfw_liblc3_duration_us[LC3_NUM_DT] = {
    2500U, 5000U, 7500U, 10000U
};

static const uint32_t open_cfw_liblc3_sample_rate_hz[LC3_NUM_SRATE] = {
    8000U, 16000U, 24000U, 32000U, 48000U, 48000U, 96000U
};

/* Exact `x -= w - 1` read-before-current contract in upstream ltpf.c. */
static const uint32_t open_cfw_liblc3_history_samples[LC3_NUM_SRATE] = {
    9U, 19U, 29U, 39U, 59U, 59U, 119U
};

int open_cfw_liblc3_ltpf_plan(
    const struct open_cfw_liblc3_ltpf_config *config,
    struct open_cfw_liblc3_ltpf_plan *plan)
{
    uint32_t duration_us;
    uint32_t sample_rate_hz;
    uint32_t frame_samples;
    uint32_t history_samples;

    if (config == NULL || plan == NULL || config->reserved[0] != 0U ||
        config->reserved[1] != 0U ||
        config->duration_index >= (uint8_t)LC3_NUM_DT ||
        config->sample_rate_index >= (uint8_t)LC3_NUM_SRATE) {
        return OPEN_CFW_LIBLC3_LTPF_INVALID_ARGUMENT;
    }

    duration_us = open_cfw_liblc3_duration_us[config->duration_index];
    sample_rate_hz =
        open_cfw_liblc3_sample_rate_hz[config->sample_rate_index];
    frame_samples = (sample_rate_hz / 400U) * (duration_us / 2500U);
    history_samples =
        open_cfw_liblc3_history_samples[config->sample_rate_index];

    plan->frame_samples = frame_samples;
    plan->history_samples = history_samples;
    plan->total_samples = frame_samples + history_samples;
    plan->current_offset_bytes = history_samples * sizeof(int16_t);
    return OPEN_CFW_LIBLC3_LTPF_OK;
}

void open_cfw_liblc3_ltpf_reset(
    struct open_cfw_liblc3_ltpf_state *state)
{
    if (state != NULL) {
        memset(&state->upstream, 0, sizeof(state->upstream));
    }
}

int open_cfw_liblc3_ltpf_analyse_bounded(
    struct open_cfw_liblc3_ltpf_state *state,
    const struct open_cfw_liblc3_ltpf_config *config,
    const struct open_cfw_liblc3_ltpf_plan *plan,
    const int16_t *samples,
    size_t sample_count,
    struct open_cfw_liblc3_ltpf_result *result)
{
    struct open_cfw_liblc3_ltpf_plan expected;
    lc3_ltpf_data_t data = { false, 0 };
    const int16_t *current;
    bool pitch_present;

    if (state == NULL || config == NULL || plan == NULL || samples == NULL ||
        result == NULL || open_cfw_liblc3_ltpf_plan(config, &expected) != 0 ||
        plan->frame_samples != expected.frame_samples ||
        plan->history_samples != expected.history_samples ||
        plan->total_samples != expected.total_samples ||
        plan->current_offset_bytes != expected.current_offset_bytes) {
        return OPEN_CFW_LIBLC3_LTPF_INVALID_ARGUMENT;
    }
    if (sample_count < (size_t)expected.total_samples) {
        return OPEN_CFW_LIBLC3_LTPF_INPUT_TOO_SHORT;
    }

    current = samples + expected.history_samples;
    if (((uintptr_t)current & 3U) != 0U) {
        return OPEN_CFW_LIBLC3_LTPF_INPUT_MISALIGNED;
    }

    pitch_present = lc3_ltpf_analyse(
        (enum lc3_dt)config->duration_index,
        (enum lc3_srate)config->sample_rate_index,
        &state->upstream,
        current,
        &data);
    result->pitch_present = pitch_present ? 1U : 0U;
    result->active = data.active ? 1U : 0U;
    result->reserved[0] = 0U;
    result->reserved[1] = 0U;
    result->pitch_index = data.pitch_index;
    return OPEN_CFW_LIBLC3_LTPF_OK;
}
