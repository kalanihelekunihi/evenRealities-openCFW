/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-capable bounded adapter for the authenticated Google liblc3
 * v1.1.3 compatibility snapshot.  The pristine upstream translation units
 * are compiled separately and remain unmodified.
 */
#include "runtime_liblc3_encoder_provider.h"

#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <lc3_private.h>

#define OPEN_CFW_LIBLC3_ENCODER_SEAL_BASIS UINT32_C(0x4C433345)

_Static_assert(sizeof(enum lc3_dt) == 1U,
    "G2 liblc3 encoder requires -fshort-enums");
_Static_assert(sizeof(enum lc3_srate) == 1U,
    "G2 liblc3 encoder requires -fshort-enums");
_Static_assert(offsetof(struct lc3_encoder, dt) == 0x000U,
    "G2 liblc3 encoder dt offset changed");
_Static_assert(offsetof(struct lc3_encoder, sr) == 0x001U,
    "G2 liblc3 encoder sample-rate offset changed");
_Static_assert(offsetof(struct lc3_encoder, sr_pcm) == 0x002U,
    "G2 liblc3 encoder PCM-rate offset changed");
_Static_assert(offsetof(struct lc3_encoder, attdet) == 0x004U,
    "G2 liblc3 encoder attack-detector offset changed");
_Static_assert(offsetof(struct lc3_encoder, ltpf) == 0x010U,
    "G2 liblc3 encoder LTPF offset changed");
_Static_assert(offsetof(struct lc3_encoder, spec) == 0x498U,
    "G2 liblc3 encoder spectrum-state offset changed");
_Static_assert(offsetof(struct lc3_encoder, xt_off) == 0x4A0U,
    "G2 liblc3 encoder temporal offset changed");
_Static_assert(offsetof(struct lc3_encoder, xs_off) == 0x4A4U,
    "G2 liblc3 encoder spectral offset changed");
_Static_assert(offsetof(struct lc3_encoder, xd_off) == 0x4A8U,
    "G2 liblc3 encoder MDCT offset changed");
_Static_assert(offsetof(struct lc3_encoder, x) == 0x4ACU,
    "G2 liblc3 encoder buffer offset changed");
_Static_assert(sizeof(struct lc3_encoder) == 0x4B0U,
    "G2 liblc3 encoder fixed state size changed");
_Static_assert(_Alignof(struct lc3_encoder) == 8U,
    "G2 liblc3 encoder alignment changed");
_Static_assert(sizeof(float) == 4U, "G2 liblc3 requires binary32 float");
_Static_assert(LC3_PCM_FORMAT_S16 == 0 && LC3_PCM_FORMAT_S24 == 1 &&
    LC3_PCM_FORMAT_S24_3LE == 2 && LC3_PCM_FORMAT_FLOAT == 3,
    "liblc3 PCM format ABI changed");
_Static_assert(sizeof(struct open_cfw_liblc3_encoder_provider_config) == 24U,
    "OpenCFW liblc3 encoder config ABI changed");
_Static_assert(sizeof(struct open_cfw_liblc3_encoder_provider_plan) == 28U,
    "OpenCFW liblc3 encoder plan ABI changed");

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_liblc3_encoder_provider) == 64U,
    "G2 liblc3 encoder provider ABI changed");
#endif

static void open_cfw_liblc3_encoder_provider_invalidate(
    struct open_cfw_liblc3_encoder_provider *provider)
{
    provider->initialized_seal = 0U;
    provider->encoder = NULL;
    provider->storage_size = 0U;
}

static bool open_cfw_liblc3_ranges_overlap(
    const void *first, size_t first_size,
    const void *second, size_t second_size)
{
    uintptr_t first_start = (uintptr_t)first;
    uintptr_t second_start = (uintptr_t)second;
    uintptr_t first_end;
    uintptr_t second_end;

    if (first_size == 0U || second_size == 0U) {
        return false;
    }
    if (first_size > UINTPTR_MAX - first_start ||
        second_size > UINTPTR_MAX - second_start) {
        return true;
    }
    first_end = first_start + first_size;
    second_end = second_start + second_size;
    return first_start < second_end && second_start < first_end;
}

static uint32_t open_cfw_liblc3_pcm_sample_bytes(uint32_t format)
{
    static const uint8_t widths[4] = { 2U, 4U, 3U, 4U };

    return format < 4U ? widths[format] : 0U;
}

static uint32_t open_cfw_liblc3_seal_word(uint32_t seal, uint32_t value)
{
    return (seal ^ value) * UINT32_C(16777619);
}

static bool open_cfw_liblc3_same_plan(
    const struct open_cfw_liblc3_encoder_provider_plan *first,
    const struct open_cfw_liblc3_encoder_provider_plan *second)
{
    return first->encoded_samples_per_frame ==
            second->encoded_samples_per_frame &&
        first->pcm_samples_per_frame == second->pcm_samples_per_frame &&
        first->frame_bytes == second->frame_bytes &&
        first->encoder_bytes == second->encoder_bytes &&
        first->pcm_frame_bytes == second->pcm_frame_bytes &&
        first->pcm_sample_bytes == second->pcm_sample_bytes &&
        first->storage_alignment == second->storage_alignment;
}

static uint32_t open_cfw_liblc3_encoder_provider_seal(
    const struct open_cfw_liblc3_encoder_provider *provider)
{
    uintptr_t encoder = (uintptr_t)provider->encoder;
    uint32_t seal = OPEN_CFW_LIBLC3_ENCODER_SEAL_BASIS;

    seal = open_cfw_liblc3_seal_word(seal, (uint32_t)encoder);
#if UINTPTR_MAX > UINT32_MAX
    seal = open_cfw_liblc3_seal_word(seal, (uint32_t)(encoder >> 32));
#endif
    seal = open_cfw_liblc3_seal_word(seal, provider->storage_size);
    seal = open_cfw_liblc3_seal_word(seal, provider->config.frame_us);
    seal = open_cfw_liblc3_seal_word(seal, provider->config.sample_rate_hz);
    seal = open_cfw_liblc3_seal_word(
        seal, provider->config.pcm_sample_rate_hz);
    seal = open_cfw_liblc3_seal_word(seal, provider->config.bitrate_bps);
    seal = open_cfw_liblc3_seal_word(seal, provider->config.pcm_format);
    seal = open_cfw_liblc3_seal_word(seal, provider->config.pcm_stride);
    seal = open_cfw_liblc3_seal_word(
        seal, provider->plan.encoded_samples_per_frame);
    seal = open_cfw_liblc3_seal_word(
        seal, provider->plan.pcm_samples_per_frame);
    seal = open_cfw_liblc3_seal_word(seal, provider->plan.frame_bytes);
    seal = open_cfw_liblc3_seal_word(seal, provider->plan.encoder_bytes);
    seal = open_cfw_liblc3_seal_word(seal, provider->plan.pcm_frame_bytes);
    seal = open_cfw_liblc3_seal_word(seal, provider->plan.pcm_sample_bytes);
    seal = open_cfw_liblc3_seal_word(seal, provider->plan.storage_alignment);
    return seal == 0U ? UINT32_MAX : seal;
}

int open_cfw_liblc3_encoder_provider_plan(
    const struct open_cfw_liblc3_encoder_provider_config *config,
    struct open_cfw_liblc3_encoder_provider_plan *plan)
{
    uint32_t pcm_sample_rate_hz;
    uint32_t sample_bytes;
    uint64_t scalar_span;
    uint64_t pcm_frame_bytes;
    int encoded_samples;
    int pcm_samples;
    int frame_bytes;
    unsigned encoder_bytes;

    if (config == NULL || plan == NULL || config->frame_us > (uint32_t)INT_MAX ||
        config->sample_rate_hz > (uint32_t)INT_MAX ||
        config->pcm_sample_rate_hz > (uint32_t)INT_MAX ||
        config->bitrate_bps > (uint32_t)INT_MAX ||
        config->pcm_stride == 0U || config->pcm_stride > (uint32_t)INT_MAX) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }
    sample_bytes = open_cfw_liblc3_pcm_sample_bytes(config->pcm_format);
    if (sample_bytes == 0U) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }

    pcm_sample_rate_hz = config->pcm_sample_rate_hz == 0U ?
        config->sample_rate_hz : config->pcm_sample_rate_hz;
    encoded_samples = lc3_frame_samples(
        (int)config->frame_us, (int)config->sample_rate_hz);
    pcm_samples = lc3_frame_samples(
        (int)config->frame_us, (int)pcm_sample_rate_hz);
    frame_bytes = lc3_hr_frame_bytes(false, (int)config->frame_us,
        (int)config->sample_rate_hz, (int)config->bitrate_bps);
    encoder_bytes = lc3_encoder_size(
        (int)config->frame_us, (int)pcm_sample_rate_hz);
    if (encoded_samples <= 0 || pcm_samples <= 0 || frame_bytes <= 0 ||
        encoder_bytes == 0U || pcm_sample_rate_hz < config->sample_rate_hz) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }

    scalar_span = (uint64_t)((uint32_t)pcm_samples - 1U) *
        config->pcm_stride + 1U;
    pcm_frame_bytes = scalar_span * sample_bytes;
    if (pcm_frame_bytes > UINT32_MAX) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }

    plan->encoded_samples_per_frame = (uint32_t)encoded_samples;
    plan->pcm_samples_per_frame = (uint32_t)pcm_samples;
    plan->frame_bytes = (uint32_t)frame_bytes;
    plan->encoder_bytes = (uint32_t)encoder_bytes;
    plan->pcm_frame_bytes = (uint32_t)pcm_frame_bytes;
    plan->pcm_sample_bytes = sample_bytes;
    plan->storage_alignment = (uint32_t)_Alignof(struct lc3_encoder);
    return OPEN_CFW_LIBLC3_ENCODER_OK;
}

int open_cfw_liblc3_encoder_provider_setup(
    struct open_cfw_liblc3_encoder_provider *provider,
    const struct open_cfw_liblc3_encoder_provider_config *config,
    void *storage,
    size_t storage_size)
{
    struct open_cfw_liblc3_encoder_provider_plan plan;
    uint32_t pcm_sample_rate_hz;
    lc3_encoder_t encoder;
    int status;

    if (provider == NULL) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }
    open_cfw_liblc3_encoder_provider_invalidate(provider);
    if (config == NULL || storage == NULL) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }
    status = open_cfw_liblc3_encoder_provider_plan(config, &plan);
    if (status != OPEN_CFW_LIBLC3_ENCODER_OK) {
        return status;
    }
    if (((uintptr_t)storage % plan.storage_alignment) != 0U) {
        return OPEN_CFW_LIBLC3_ENCODER_MISALIGNED;
    }
    if (storage_size < plan.encoder_bytes) {
        return OPEN_CFW_LIBLC3_ENCODER_STORAGE_TOO_SMALL;
    }
    if (storage_size > UINT32_MAX) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }
    if (open_cfw_liblc3_ranges_overlap(provider, sizeof(*provider), storage,
            plan.encoder_bytes)) {
        return OPEN_CFW_LIBLC3_ENCODER_OVERLAP;
    }

    pcm_sample_rate_hz = config->pcm_sample_rate_hz == 0U ?
        config->sample_rate_hz : config->pcm_sample_rate_hz;
    encoder = lc3_setup_encoder((int)config->frame_us,
        (int)config->sample_rate_hz, (int)pcm_sample_rate_hz, storage);
    if (encoder == NULL || encoder != storage) {
        return OPEN_CFW_LIBLC3_ENCODER_CODEC_ERROR;
    }

    provider->encoder = encoder;
    provider->storage_size = (uint32_t)storage_size;
    provider->config = *config;
    provider->config.pcm_sample_rate_hz = pcm_sample_rate_hz;
    provider->plan = plan;
    provider->initialized_seal =
        open_cfw_liblc3_encoder_provider_seal(provider);
    return OPEN_CFW_LIBLC3_ENCODER_OK;
}

int open_cfw_liblc3_encoder_provider_encode(
    struct open_cfw_liblc3_encoder_provider *provider,
    const void *pcm,
    size_t pcm_bytes,
    void *output,
    size_t output_size)
{
    struct open_cfw_liblc3_encoder_provider_config normalized;
    struct open_cfw_liblc3_encoder_provider_plan expected;
    uint32_t input_alignment;
    int status;

    if (provider == NULL || provider->initialized_seal == 0U ||
        provider->encoder == NULL) {
        return OPEN_CFW_LIBLC3_ENCODER_NOT_INITIALIZED;
    }
    if (pcm == NULL || output == NULL) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }
    normalized = provider->config;
    status = open_cfw_liblc3_encoder_provider_plan(&normalized, &expected);
    if (status != OPEN_CFW_LIBLC3_ENCODER_OK ||
        !open_cfw_liblc3_same_plan(&provider->plan, &expected) ||
        provider->storage_size < expected.encoder_bytes ||
        provider->initialized_seal !=
            open_cfw_liblc3_encoder_provider_seal(provider)) {
        return OPEN_CFW_LIBLC3_ENCODER_NOT_INITIALIZED;
    }
    if (pcm_bytes < expected.pcm_frame_bytes) {
        return OPEN_CFW_LIBLC3_ENCODER_PCM_TOO_SHORT;
    }
    if (output_size < expected.frame_bytes) {
        return OPEN_CFW_LIBLC3_ENCODER_OUTPUT_TOO_SMALL;
    }

    input_alignment = expected.pcm_sample_bytes == 3U ?
        1U : expected.pcm_sample_bytes;
    if (((uintptr_t)pcm % input_alignment) != 0U) {
        return OPEN_CFW_LIBLC3_ENCODER_MISALIGNED;
    }
    if (open_cfw_liblc3_ranges_overlap(pcm, expected.pcm_frame_bytes,
            provider, sizeof(*provider)) ||
        open_cfw_liblc3_ranges_overlap(output, expected.frame_bytes,
            provider, sizeof(*provider)) ||
        open_cfw_liblc3_ranges_overlap(pcm, expected.pcm_frame_bytes,
            provider->encoder, expected.encoder_bytes) ||
        open_cfw_liblc3_ranges_overlap(output, expected.frame_bytes,
            provider->encoder, expected.encoder_bytes)) {
        return OPEN_CFW_LIBLC3_ENCODER_OVERLAP;
    }

    status = lc3_encode(provider->encoder,
        (enum lc3_pcm_format)provider->config.pcm_format, pcm,
        (int)provider->config.pcm_stride, (int)expected.frame_bytes, output);
    return status == 0 ? OPEN_CFW_LIBLC3_ENCODER_OK :
        OPEN_CFW_LIBLC3_ENCODER_CODEC_ERROR;
}

void open_cfw_liblc3_encoder_provider_close(
    struct open_cfw_liblc3_encoder_provider *provider)
{
    if (provider != NULL) {
        open_cfw_liblc3_encoder_provider_invalidate(provider);
    }
}
