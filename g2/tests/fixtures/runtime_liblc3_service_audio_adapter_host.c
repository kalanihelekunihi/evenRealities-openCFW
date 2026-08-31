/*
 * SPDX-License-Identifier: MIT
 *
 * Deterministic fake-provider host fixture for the service_audio LC3 adapter.
 */
#include "../../components/shared/liblc3/runtime_liblc3_service_audio_adapter.h"

#include <limits.h>
#include <stddef.h>
#include <stdint.h>

#define FIXTURE_MAX_CALLS 8U
#define FIXTURE_ENCODER_BYTES 1200U

struct fixture_call {
    uintptr_t pcm;
    size_t pcm_bytes;
    uintptr_t output;
    size_t output_size;
    uint32_t stride;
};

static struct fixture_call fixture_calls[FIXTURE_MAX_CALLS];
static uint32_t fixture_call_count;
static uint32_t fixture_fail_call;
static uint32_t fixture_encoder_bytes = FIXTURE_ENCODER_BYTES;
static int fixture_setup_status;
static uintptr_t fixture_setup_storage;
static size_t fixture_setup_storage_size;
static uint32_t fixture_setup_call_count;

static uint32_t fixture_sample_bytes(uint32_t format)
{
    static const uint8_t widths[4] = { 2U, 4U, 3U, 4U };

    return format < 4U ? widths[format] : 0U;
}

static int fixture_supported_rate(uint32_t rate)
{
    return rate == 8000U || rate == 16000U || rate == 24000U ||
        rate == 32000U || rate == 48000U;
}

void fixture_service_audio_reset(void)
{
    size_t index;

    for (index = 0U; index < FIXTURE_MAX_CALLS; index += 1U) {
        fixture_calls[index].pcm = 0U;
        fixture_calls[index].pcm_bytes = 0U;
        fixture_calls[index].output = 0U;
        fixture_calls[index].output_size = 0U;
        fixture_calls[index].stride = 0U;
    }
    fixture_call_count = 0U;
    fixture_fail_call = 0U;
    fixture_encoder_bytes = FIXTURE_ENCODER_BYTES;
    fixture_setup_status = OPEN_CFW_LIBLC3_ENCODER_OK;
    fixture_setup_storage = 0U;
    fixture_setup_storage_size = 0U;
    fixture_setup_call_count = 0U;
}

void fixture_service_audio_fail_call(uint32_t call_number)
{
    fixture_fail_call = call_number;
}

void fixture_service_audio_set_encoder_bytes(uint32_t encoder_bytes)
{
    fixture_encoder_bytes = encoder_bytes;
}

void fixture_service_audio_set_setup_status(int status)
{
    fixture_setup_status = status;
}

uint32_t fixture_service_audio_call_count(void)
{
    return fixture_call_count;
}

uintptr_t fixture_service_audio_setup_storage(void)
{
    return fixture_setup_storage;
}

size_t fixture_service_audio_setup_storage_size(void)
{
    return fixture_setup_storage_size;
}

uint32_t fixture_service_audio_setup_call_count(void)
{
    return fixture_setup_call_count;
}

uintptr_t fixture_service_audio_call_pcm(uint32_t index)
{
    return index < FIXTURE_MAX_CALLS ? fixture_calls[index].pcm : 0U;
}

size_t fixture_service_audio_call_pcm_bytes(uint32_t index)
{
    return index < FIXTURE_MAX_CALLS ? fixture_calls[index].pcm_bytes : 0U;
}

uintptr_t fixture_service_audio_call_output(uint32_t index)
{
    return index < FIXTURE_MAX_CALLS ? fixture_calls[index].output : 0U;
}

size_t fixture_service_audio_call_output_size(uint32_t index)
{
    return index < FIXTURE_MAX_CALLS ? fixture_calls[index].output_size : 0U;
}

uint32_t fixture_service_audio_call_stride(uint32_t index)
{
    return index < FIXTURE_MAX_CALLS ? fixture_calls[index].stride : 0U;
}

size_t fixture_service_audio_state_size(void)
{
    return sizeof(struct open_cfw_liblc3_service_audio_state);
}

size_t fixture_service_audio_state_alignment(void)
{
    return _Alignof(struct open_cfw_liblc3_service_audio_state);
}

size_t fixture_service_audio_config_word_offset(void)
{
    return offsetof(struct open_cfw_liblc3_service_audio_state, config_word);
}

size_t fixture_service_audio_owner_offset(void)
{
    return offsetof(struct open_cfw_liblc3_service_audio_state, owner_token);
}

size_t fixture_service_audio_storage_offset(void)
{
    return offsetof(struct open_cfw_liblc3_service_audio_state, storage);
}

int open_cfw_liblc3_encoder_provider_plan(
    const struct open_cfw_liblc3_encoder_provider_config *config,
    struct open_cfw_liblc3_encoder_provider_plan *plan)
{
    uint64_t samples;
    uint64_t frame_bytes;
    uint64_t scalar_span;
    uint64_t pcm_frame_bytes;
    uint32_t sample_bytes;

    if (config == NULL || plan == NULL ||
        (config->frame_us != 2500U && config->frame_us != 5000U &&
         config->frame_us != 7500U && config->frame_us != 10000U) ||
        !fixture_supported_rate(config->sample_rate_hz) ||
        (config->pcm_sample_rate_hz != 0U &&
         config->pcm_sample_rate_hz != config->sample_rate_hz) ||
        config->bitrate_bps == 0U || config->bitrate_bps > (uint32_t)INT_MAX ||
        config->pcm_stride == 0U || config->pcm_stride > (uint32_t)INT_MAX) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }
    sample_bytes = fixture_sample_bytes(config->pcm_format);
    if (sample_bytes == 0U) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }
    samples = (uint64_t)config->frame_us * config->sample_rate_hz /
        UINT64_C(1000000);
    frame_bytes = (uint64_t)config->frame_us * config->bitrate_bps /
        UINT64_C(8000000);
    scalar_span = (samples - 1U) * config->pcm_stride + 1U;
    pcm_frame_bytes = scalar_span * sample_bytes;
    if (samples == 0U || samples > UINT32_MAX || frame_bytes == 0U ||
        frame_bytes > UINT32_MAX || pcm_frame_bytes > UINT32_MAX) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }
    plan->encoded_samples_per_frame = (uint32_t)samples;
    plan->pcm_samples_per_frame = (uint32_t)samples;
    plan->frame_bytes = (uint32_t)frame_bytes;
    plan->encoder_bytes = fixture_encoder_bytes;
    plan->pcm_frame_bytes = (uint32_t)pcm_frame_bytes;
    plan->pcm_sample_bytes = sample_bytes;
    plan->storage_alignment = 8U;
    return OPEN_CFW_LIBLC3_ENCODER_OK;
}

int open_cfw_liblc3_encoder_provider_setup(
    struct open_cfw_liblc3_encoder_provider *provider,
    const struct open_cfw_liblc3_encoder_provider_config *config,
    void *storage,
    size_t storage_size)
{
    struct open_cfw_liblc3_encoder_provider_plan plan;
    int status;

    if (provider == NULL) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }
    fixture_setup_call_count += 1U;
    open_cfw_liblc3_encoder_provider_close(provider);
    if (fixture_setup_status != OPEN_CFW_LIBLC3_ENCODER_OK) {
        return fixture_setup_status;
    }
    status = open_cfw_liblc3_encoder_provider_plan(config, &plan);
    if (status != OPEN_CFW_LIBLC3_ENCODER_OK || storage == NULL ||
        storage_size < plan.encoder_bytes || ((uintptr_t)storage % 8U) != 0U) {
        return OPEN_CFW_LIBLC3_ENCODER_INVALID_ARGUMENT;
    }
    fixture_setup_storage = (uintptr_t)storage;
    fixture_setup_storage_size = storage_size;
    provider->initialized_seal = UINT32_C(0xC0DEC0DE);
    provider->encoder = storage;
    provider->storage_size = (uint32_t)storage_size;
    provider->config = *config;
    provider->config.pcm_sample_rate_hz = config->sample_rate_hz;
    provider->plan = plan;
    return OPEN_CFW_LIBLC3_ENCODER_OK;
}

int open_cfw_liblc3_encoder_provider_encode(
    struct open_cfw_liblc3_encoder_provider *provider,
    const void *pcm,
    size_t pcm_bytes,
    void *output,
    size_t output_size)
{
    uint32_t index = fixture_call_count;
    size_t byte_index;

    if (provider == NULL || provider->initialized_seal == 0U ||
        provider->encoder == NULL || pcm == NULL || output == NULL) {
        return OPEN_CFW_LIBLC3_ENCODER_NOT_INITIALIZED;
    }
    if (index < FIXTURE_MAX_CALLS) {
        fixture_calls[index].pcm = (uintptr_t)pcm;
        fixture_calls[index].pcm_bytes = pcm_bytes;
        fixture_calls[index].output = (uintptr_t)output;
        fixture_calls[index].output_size = output_size;
        fixture_calls[index].stride = provider->config.pcm_stride;
    }
    fixture_call_count += 1U;
    if (fixture_fail_call != 0U && fixture_call_count == fixture_fail_call) {
        return OPEN_CFW_LIBLC3_ENCODER_CODEC_ERROR;
    }
    for (byte_index = 0U; byte_index < output_size; byte_index += 1U) {
        ((uint8_t *)output)[byte_index] =
            (uint8_t)(UINT32_C(0x30) + fixture_call_count + byte_index);
    }
    return OPEN_CFW_LIBLC3_ENCODER_OK;
}

void open_cfw_liblc3_encoder_provider_close(
    struct open_cfw_liblc3_encoder_provider *provider)
{
    if (provider != NULL) {
        provider->initialized_seal = 0U;
        provider->encoder = NULL;
        provider->storage_size = 0U;
    }
}

#include "../../components/shared/liblc3/runtime_liblc3_service_audio_adapter.c"
