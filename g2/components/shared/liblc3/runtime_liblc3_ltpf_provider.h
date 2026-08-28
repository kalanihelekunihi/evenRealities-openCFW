/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded source-provider contract for Google liblc3 LTPF analysis.
 */
#ifndef OPEN_CFW_RUNTIME_LIBLC3_LTPF_PROVIDER_H
#define OPEN_CFW_RUNTIME_LIBLC3_LTPF_PROVIDER_H

#include <stddef.h>
#include <stdint.h>

#include <lc3_private.h>

enum open_cfw_liblc3_ltpf_status {
    OPEN_CFW_LIBLC3_LTPF_OK = 0,
    OPEN_CFW_LIBLC3_LTPF_INVALID_ARGUMENT = -1,
    OPEN_CFW_LIBLC3_LTPF_INPUT_TOO_SHORT = -2,
    OPEN_CFW_LIBLC3_LTPF_INPUT_MISALIGNED = -3
};

struct open_cfw_liblc3_ltpf_config {
    uint8_t duration_index;
    uint8_t sample_rate_index;
    uint8_t reserved[2];
};

struct open_cfw_liblc3_ltpf_plan {
    uint32_t frame_samples;
    uint32_t history_samples;
    uint32_t total_samples;
    uint32_t current_offset_bytes;
};

struct open_cfw_liblc3_ltpf_state {
    lc3_ltpf_analysis_t upstream;
};

struct open_cfw_liblc3_ltpf_result {
    uint8_t pitch_present;
    uint8_t active;
    uint8_t reserved[2];
    int32_t pitch_index;
};

int open_cfw_liblc3_ltpf_plan(
    const struct open_cfw_liblc3_ltpf_config *config,
    struct open_cfw_liblc3_ltpf_plan *plan);

void open_cfw_liblc3_ltpf_reset(
    struct open_cfw_liblc3_ltpf_state *state);

int open_cfw_liblc3_ltpf_analyse_bounded(
    struct open_cfw_liblc3_ltpf_state *state,
    const struct open_cfw_liblc3_ltpf_config *config,
    const struct open_cfw_liblc3_ltpf_plan *plan,
    const int16_t *samples,
    size_t sample_count,
    struct open_cfw_liblc3_ltpf_result *result);

#endif
