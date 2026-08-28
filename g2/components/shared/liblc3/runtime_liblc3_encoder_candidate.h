/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-excluded, bounded G2 adapter for the authenticated Google
 * liblc3 v1.1.3 encoder source snapshot.
 */

#ifndef OPEN_CFW_RUNTIME_LIBLC3_ENCODER_CANDIDATE_H
#define OPEN_CFW_RUNTIME_LIBLC3_ENCODER_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

#include <lc3.h>

enum open_cfw_liblc3_status {
    OPEN_CFW_LIBLC3_OK = 0,
    OPEN_CFW_LIBLC3_INVALID_ARGUMENT = -1,
    OPEN_CFW_LIBLC3_STORAGE_TOO_SMALL = -2,
    OPEN_CFW_LIBLC3_PCM_TOO_SHORT = -3,
    OPEN_CFW_LIBLC3_OUTPUT_TOO_SMALL = -4,
    OPEN_CFW_LIBLC3_CODEC_ERROR = -5
};

/*
 * Fixed-width boundary corresponding to one mono LC3 encoder.  Interleaved
 * PCM is represented by pcm_stride; the adapter never owns the PCM or output
 * buffers.  A zero pcm_sample_rate_hz selects sample_rate_hz, as in liblc3.
 */
struct open_cfw_liblc3_encoder_config {
    uint32_t frame_us;
    uint32_t sample_rate_hz;
    uint32_t pcm_sample_rate_hz;
    uint32_t bitrate_bps;
    uint32_t pcm_format;
    uint32_t pcm_stride;
};

struct open_cfw_liblc3_encoder_plan {
    uint32_t encoded_samples_per_frame;
    uint32_t pcm_samples_per_frame;
    uint32_t frame_bytes;
    uint32_t encoder_bytes;
};

struct open_cfw_liblc3_encoder_candidate {
    lc3_encoder_t encoder;
    struct open_cfw_liblc3_encoder_config config;
    struct open_cfw_liblc3_encoder_plan plan;
};

/* Validate and derive all memory and frame geometry without mutating storage. */
int open_cfw_liblc3_encoder_plan(
    const struct open_cfw_liblc3_encoder_config *config,
    struct open_cfw_liblc3_encoder_plan *plan
);

/*
 * Initialize caller-owned encoder storage.  storage must be pointer-aligned
 * and at least plan.encoder_bytes bytes.  No allocation is performed.
 */
int open_cfw_liblc3_encoder_setup(
    struct open_cfw_liblc3_encoder_candidate *candidate,
    const struct open_cfw_liblc3_encoder_config *config,
    void *storage,
    size_t storage_size
);

/*
 * Encode exactly one frame after proving both buffer bounds.  pcm_scalar_count
 * is the number of addressable scalar PCM elements, including stride gaps.
 */
int open_cfw_liblc3_encoder_encode(
    struct open_cfw_liblc3_encoder_candidate *candidate,
    const void *pcm,
    size_t pcm_scalar_count,
    void *output,
    size_t output_size
);

#endif
