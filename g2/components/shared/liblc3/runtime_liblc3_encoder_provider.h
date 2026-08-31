/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded source-provider contract for the Google liblc3 encoder.
 */
#ifndef OPEN_CFW_RUNTIME_LIBLC3_ENCODER_PROVIDER_H
#define OPEN_CFW_RUNTIME_LIBLC3_ENCODER_PROVIDER_H

#include <stddef.h>
#include <stdint.h>

#include <lc3.h>

enum open_cfw_liblc3_encoder_provider_status {
    OPEN_CFW_LIBLC3_ENCODER_OK = 0,
    OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT = -1,
    OPEN_CFW_LIBLC3_ENCODER_STORAGE_TOO_SMALL = -2,
    OPEN_CFW_LIBLC3_ENCODER_PCM_TOO_SHORT = -3,
    OPEN_CFW_LIBLC3_ENCODER_OUTPUT_TOO_SMALL = -4,
    OPEN_CFW_LIBLC3_ENCODER_MISALIGNED = -5,
    OPEN_CFW_LIBLC3_ENCODER_OVERLAP = -6,
    OPEN_CFW_LIBLC3_ENCODER_CODEC_ERROR = -7,
    OPEN_CFW_LIBLC3_ENCODER_NOT_INITIALIZED = -8
};

/*
 * One mono encoder.  pcm_stride is measured in complete PCM samples, not
 * bytes.  A zero pcm_sample_rate_hz selects sample_rate_hz.
 */
struct open_cfw_liblc3_encoder_provider_config {
    uint32_t frame_us;
    uint32_t sample_rate_hz;
    uint32_t pcm_sample_rate_hz;
    uint32_t bitrate_bps;
    uint32_t pcm_format;
    uint32_t pcm_stride;
};

/* All sizes are exact requirements for the normalized configuration. */
struct open_cfw_liblc3_encoder_provider_plan {
    uint32_t encoded_samples_per_frame;
    uint32_t pcm_samples_per_frame;
    uint32_t frame_bytes;
    uint32_t encoder_bytes;
    uint32_t pcm_frame_bytes;
    uint32_t pcm_sample_bytes;
    uint32_t storage_alignment;
};

/*
 * The fields are public only to keep allocation deterministic.  Callers must
 * treat them as opaque; every operation verifies the initialization seal and
 * re-derives the stored plan before entering upstream code.
 */
struct open_cfw_liblc3_encoder_provider {
    uint32_t initialized_seal;
    lc3_encoder_t encoder;
    uint32_t storage_size;
    struct open_cfw_liblc3_encoder_provider_config config;
    struct open_cfw_liblc3_encoder_provider_plan plan;
};

int open_cfw_liblc3_encoder_provider_plan(
    const struct open_cfw_liblc3_encoder_provider_config *config,
    struct open_cfw_liblc3_encoder_provider_plan *plan);

int open_cfw_liblc3_encoder_provider_setup(
    struct open_cfw_liblc3_encoder_provider *provider,
    const struct open_cfw_liblc3_encoder_provider_config *config,
    void *storage,
    size_t storage_size);

/*
 * Encode one frame.  PCM and output capacities are byte counts, including
 * all interleaving gaps.  Neither range may alias the provider or its encoder
 * storage.
 */
int open_cfw_liblc3_encoder_provider_encode(
    struct open_cfw_liblc3_encoder_provider *provider,
    const void *pcm,
    size_t pcm_bytes,
    void *output,
    size_t output_size);

/* Invalidate the provider.  Caller-owned encoder storage is not erased. */
void open_cfw_liblc3_encoder_provider_close(
    struct open_cfw_liblc3_encoder_provider *provider);

#endif
