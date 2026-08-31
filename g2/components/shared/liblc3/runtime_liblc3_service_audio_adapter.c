/*
 * SPDX-License-Identifier: MIT
 *
 * Stock-slot-sized service-audio geometry, ownership, and lifetime boundary
 * for the admitted Google liblc3 v1.1.3-compatible encoder provider.
 */
#include "runtime_liblc3_service_audio_adapter.h"

#include <limits.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_LIBLC3_SERVICE_AUDIO_CLOSED_SEAL UINT32_C(0x5341334C)
#define OPEN_CFW_LIBLC3_SERVICE_AUDIO_SEAL_BASIS UINT32_C(0xA3D10C5E)
#define OPEN_CFW_LIBLC3_SERVICE_AUDIO_BUSY_BIT UINT32_C(0x80000000)
#define OPEN_CFW_LIBLC3_SERVICE_AUDIO_SEAL_MASK UINT32_C(0x7FFFFFFF)
#define OPEN_CFW_LIBLC3_SERVICE_AUDIO_CONFIG_TAG UINT32_C(0x4C330000)
#define OPEN_CFW_LIBLC3_SERVICE_AUDIO_CONFIG_MASK UINT32_C(0xFFFFFF80)
#define OPEN_CFW_LIBLC3_ENCODER_SEAL_BASIS UINT32_C(0x4C433345)

_Static_assert(sizeof(struct open_cfw_liblc3_service_audio_config) == 24U,
    "service_audio LC3 configuration ABI changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_config,
    pcm_format) == 0U, "service_audio PCM format offset changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_config,
    frame_us) == 4U, "service_audio frame duration offset changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_config,
    sample_rate_hz) == 8U, "service_audio sample-rate offset changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_config,
    channels) == 12U, "service_audio channel-count offset changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_config,
    channel_offset) == 16U, "service_audio channel-offset changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_config,
    bitrate_bps) == 20U, "service_audio bitrate offset changed");
_Static_assert(sizeof(struct open_cfw_liblc3_service_audio_plan) == 20U,
    "service_audio LC3 plan ABI changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_state,
    state_seal) == 0U, "service_audio state seal offset changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_state,
    owner_token) == 4U, "service_audio state owner offset changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_state,
    generation) == 8U, "service_audio state generation offset changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_state,
    config_word) == 12U, "service_audio state config word offset changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_state,
    channels) == 16U, "service_audio state channels offset changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_state,
    channel_offset) == 20U, "service_audio state channel offset changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_state,
    bitrate_bps) == 24U, "service_audio state bitrate offset changed");
_Static_assert(offsetof(struct open_cfw_liblc3_service_audio_state,
    storage) == 28U, "service_audio state storage offset changed");
_Static_assert(sizeof(struct open_cfw_liblc3_service_audio_state) == 2628U,
    "service_audio state no longer fits one authenticated stock slot");
_Static_assert(_Alignof(struct open_cfw_liblc3_service_audio_state) == 4U,
    "service_audio stock-slot state alignment changed");

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(struct open_cfw_liblc3_encoder_provider) == 64U,
    "provider ABI changed");
#endif

static uint32_t open_cfw_liblc3_service_audio_seal_word(
    uint32_t seal, uint32_t value)
{
    return (seal ^ value) * UINT32_C(16777619);
}

static bool open_cfw_liblc3_service_audio_ranges_overlap(
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

static bool open_cfw_liblc3_service_audio_address_valid(
    const struct open_cfw_liblc3_service_audio_state *state)
{
    return state != NULL &&
        ((uintptr_t)state % _Alignof(
            struct open_cfw_liblc3_service_audio_state)) == 0U;
}

static uint8_t *open_cfw_liblc3_service_audio_encoder_storage(
    struct open_cfw_liblc3_service_audio_state *state,
    uint32_t *storage_size)
{
    uintptr_t raw = (uintptr_t)state->storage;
    uintptr_t aligned = (raw + 7U) & ~(uintptr_t)7U;
    uint32_t prefix = (uint32_t)(aligned - raw);

    *storage_size = OPEN_CFW_LIBLC3_SERVICE_AUDIO_STORAGE_BYTES - prefix;
    return (uint8_t *)aligned;
}

static bool open_cfw_liblc3_service_audio_frame_code(
    uint32_t frame_us, uint32_t *code)
{
    switch (frame_us) {
    case 2500U: *code = 0U; return true;
    case 5000U: *code = 1U; return true;
    case 7500U: *code = 2U; return true;
    case 10000U: *code = 3U; return true;
    default: return false;
    }
}

static bool open_cfw_liblc3_service_audio_rate_code(
    uint32_t sample_rate_hz, uint32_t *code)
{
    switch (sample_rate_hz) {
    case 8000U: *code = 0U; return true;
    case 16000U: *code = 1U; return true;
    case 24000U: *code = 2U; return true;
    case 32000U: *code = 3U; return true;
    case 48000U: *code = 4U; return true;
    default: return false;
    }
}

static bool open_cfw_liblc3_service_audio_pack_config(
    const struct open_cfw_liblc3_service_audio_config *config,
    uint32_t *word)
{
    uint32_t frame;
    uint32_t rate;

    if (config->pcm_format > 3U ||
        !open_cfw_liblc3_service_audio_frame_code(config->frame_us, &frame) ||
        !open_cfw_liblc3_service_audio_rate_code(
            config->sample_rate_hz, &rate)) {
        return false;
    }
    *word = OPEN_CFW_LIBLC3_SERVICE_AUDIO_CONFIG_TAG |
        config->pcm_format | (frame << 2) | (rate << 4);
    return true;
}

static bool open_cfw_liblc3_service_audio_unpack_config(
    const struct open_cfw_liblc3_service_audio_state *state,
    struct open_cfw_liblc3_service_audio_config *config)
{
    static const uint16_t frame_us[4] = { 2500U, 5000U, 7500U, 10000U };
    static const uint16_t sample_rate_hz[5] = {
        8000U, 16000U, 24000U, 32000U, 48000U
    };
    uint32_t rate = (state->config_word >> 4) & 7U;

    if ((state->config_word & OPEN_CFW_LIBLC3_SERVICE_AUDIO_CONFIG_MASK) !=
            OPEN_CFW_LIBLC3_SERVICE_AUDIO_CONFIG_TAG || rate >= 5U) {
        return false;
    }
    config->pcm_format = state->config_word & 3U;
    config->frame_us = frame_us[(state->config_word >> 2) & 3U];
    config->sample_rate_hz = sample_rate_hz[rate];
    config->channels = state->channels;
    config->channel_offset = state->channel_offset;
    config->bitrate_bps = state->bitrate_bps;
    return config->channels != 0U &&
        config->channels <= (uint32_t)INT_MAX &&
        config->channel_offset < config->channels;
}

/* Mirrors the maintained provider's private seal for a transient view. */
static uint32_t open_cfw_liblc3_service_audio_provider_seal(
    const struct open_cfw_liblc3_encoder_provider *provider)
{
    uintptr_t encoder = (uintptr_t)provider->encoder;
    uint32_t seal = OPEN_CFW_LIBLC3_ENCODER_SEAL_BASIS;

    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, (uint32_t)encoder);
#if UINTPTR_MAX > UINT32_MAX
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, (uint32_t)(encoder >> 32));
#endif
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->storage_size);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->config.frame_us);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->config.sample_rate_hz);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->config.pcm_sample_rate_hz);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->config.bitrate_bps);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->config.pcm_format);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->config.pcm_stride);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.encoded_samples_per_frame);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.pcm_samples_per_frame);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.frame_bytes);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.encoder_bytes);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.pcm_frame_bytes);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.pcm_sample_bytes);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.storage_alignment);
    return seal == 0U ? UINT32_MAX : seal;
}

static bool open_cfw_liblc3_service_audio_provider_view(
    struct open_cfw_liblc3_service_audio_state *state,
    struct open_cfw_liblc3_encoder_provider *provider,
    struct open_cfw_liblc3_service_audio_config *service_config)
{
    struct open_cfw_liblc3_encoder_provider_config provider_config;
    struct open_cfw_liblc3_encoder_provider_plan provider_plan;
    uint32_t storage_size;
    uint8_t *storage;

    if (!open_cfw_liblc3_service_audio_address_valid(state) ||
        !open_cfw_liblc3_service_audio_unpack_config(state, service_config)) {
        return false;
    }
    provider_config.frame_us = service_config->frame_us;
    provider_config.sample_rate_hz = service_config->sample_rate_hz;
    provider_config.pcm_sample_rate_hz = 0U;
    provider_config.bitrate_bps = service_config->bitrate_bps;
    provider_config.pcm_format = service_config->pcm_format;
    provider_config.pcm_stride = service_config->channels;
    if (open_cfw_liblc3_encoder_provider_plan(
            &provider_config, &provider_plan) != OPEN_CFW_LIBLC3_ENCODER_OK ||
        provider_plan.frame_bytes < 20U ||
        provider_plan.encoder_bytes >
            OPEN_CFW_LIBLC3_SERVICE_AUDIO_STORAGE_BYTES ||
        provider_plan.storage_alignment != 8U) {
        return false;
    }
    storage = open_cfw_liblc3_service_audio_encoder_storage(
        state, &storage_size);
    if (provider_plan.encoder_bytes > storage_size) {
        return false;
    }
    provider->initialized_seal = 0U;
    provider->encoder = (lc3_encoder_t)(void *)storage;
    provider->storage_size = storage_size;
    provider->config = provider_config;
    provider->config.pcm_sample_rate_hz = provider_config.sample_rate_hz;
    provider->plan = provider_plan;
    provider->initialized_seal =
        open_cfw_liblc3_service_audio_provider_seal(provider);
    return true;
}

static uint32_t open_cfw_liblc3_service_audio_open_seal(
    const struct open_cfw_liblc3_service_audio_state *state,
    const struct open_cfw_liblc3_encoder_provider *provider)
{
    uintptr_t encoder = (uintptr_t)provider->encoder;
    uint32_t seal = OPEN_CFW_LIBLC3_SERVICE_AUDIO_SEAL_BASIS;

    seal = open_cfw_liblc3_service_audio_seal_word(seal, state->owner_token);
    seal = open_cfw_liblc3_service_audio_seal_word(seal, state->generation);
    seal = open_cfw_liblc3_service_audio_seal_word(seal, state->config_word);
    seal = open_cfw_liblc3_service_audio_seal_word(seal, state->channels);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, state->channel_offset);
    seal = open_cfw_liblc3_service_audio_seal_word(seal, state->bitrate_bps);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->initialized_seal);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, (uint32_t)encoder);
#if UINTPTR_MAX > UINT32_MAX
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, (uint32_t)(encoder >> 32));
#endif
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->storage_size);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.encoded_samples_per_frame);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.pcm_samples_per_frame);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.frame_bytes);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.encoder_bytes);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.pcm_frame_bytes);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.pcm_sample_bytes);
    seal = open_cfw_liblc3_service_audio_seal_word(
        seal, provider->plan.storage_alignment);
    seal &= OPEN_CFW_LIBLC3_SERVICE_AUDIO_SEAL_MASK;
    if (seal == 0U || seal == OPEN_CFW_LIBLC3_SERVICE_AUDIO_CLOSED_SEAL) {
        seal = UINT32_C(0x2D6E4A17);
    }
    return seal;
}

static bool open_cfw_liblc3_service_audio_is_closed(
    const struct open_cfw_liblc3_service_audio_state *state)
{
    return state->state_seal == OPEN_CFW_LIBLC3_SERVICE_AUDIO_CLOSED_SEAL &&
        state->owner_token == 0U && state->generation != 0U &&
        state->config_word == 0U && state->channels == 0U &&
        state->channel_offset == 0U && state->bitrate_bps == 0U;
}

static bool open_cfw_liblc3_service_audio_is_open(
    struct open_cfw_liblc3_service_audio_state *state,
    struct open_cfw_liblc3_encoder_provider *provider,
    struct open_cfw_liblc3_service_audio_config *config)
{
    return state->owner_token != 0U && state->generation != 0U &&
        open_cfw_liblc3_service_audio_provider_view(state, provider, config) &&
        (state->state_seal & OPEN_CFW_LIBLC3_SERVICE_AUDIO_SEAL_MASK) ==
            open_cfw_liblc3_service_audio_open_seal(state, provider);
}

static bool open_cfw_liblc3_service_audio_is_pristine(
    const struct open_cfw_liblc3_service_audio_state *state)
{
    const uint8_t *bytes = (const uint8_t *)state;
    size_t index;

    for (index = 0U;
         index < offsetof(struct open_cfw_liblc3_service_audio_state, storage);
         index += 1U) {
        if (bytes[index] != 0U) {
            return false;
        }
    }
    return true;
}

static void open_cfw_liblc3_service_audio_advance_generation(
    struct open_cfw_liblc3_service_audio_state *state)
{
    state->generation += 1U;
    if (state->generation == 0U) {
        state->generation = 1U;
    }
}

static void open_cfw_liblc3_service_audio_invalidate(
    struct open_cfw_liblc3_service_audio_state *state)
{
    state->state_seal = OPEN_CFW_LIBLC3_SERVICE_AUDIO_CLOSED_SEAL;
    state->owner_token = 0U;
    state->config_word = 0U;
    state->channels = 0U;
    state->channel_offset = 0U;
    state->bitrate_bps = 0U;
    open_cfw_liblc3_service_audio_advance_generation(state);
}

int open_cfw_liblc3_service_audio_state_init(
    struct open_cfw_liblc3_service_audio_state *state)
{
    struct open_cfw_liblc3_encoder_provider provider;
    struct open_cfw_liblc3_service_audio_config config;

    if (!open_cfw_liblc3_service_audio_address_valid(state)) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_INVALID_ARGUMENT;
    }
    if (open_cfw_liblc3_service_audio_is_closed(state)) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK;
    }
    if (open_cfw_liblc3_service_audio_is_open(state, &provider, &config)) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_ALREADY_OPEN;
    }
    if (!open_cfw_liblc3_service_audio_is_pristine(state)) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_STATE_CORRUPT;
    }
    state->generation = 1U;
    state->state_seal = OPEN_CFW_LIBLC3_SERVICE_AUDIO_CLOSED_SEAL;
    state->owner_token = 0U;
    state->config_word = 0U;
    state->channels = 0U;
    state->channel_offset = 0U;
    state->bitrate_bps = 0U;
    return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK;
}

int open_cfw_liblc3_service_audio_open(
    struct open_cfw_liblc3_service_audio_state *state,
    uint32_t owner_token,
    const struct open_cfw_liblc3_service_audio_config *config,
    struct open_cfw_liblc3_service_audio_plan *plan)
{
    struct open_cfw_liblc3_encoder_provider_config provider_config;
    struct open_cfw_liblc3_encoder_provider_plan provider_plan;
    struct open_cfw_liblc3_encoder_provider provider;
    struct open_cfw_liblc3_service_audio_config stored_config;
    uint64_t interleaved_bytes;
    uint32_t config_word;
    uint32_t storage_size;
    uint8_t *storage;
    int status;

    if (!open_cfw_liblc3_service_audio_address_valid(state) ||
        config == NULL || owner_token == 0U) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_INVALID_ARGUMENT;
    }
    if (open_cfw_liblc3_service_audio_ranges_overlap(
            config, sizeof(*config), state, sizeof(*state)) ||
        (plan != NULL && open_cfw_liblc3_service_audio_ranges_overlap(
            plan, sizeof(*plan), state, sizeof(*state)))) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OVERLAP;
    }
    if (!open_cfw_liblc3_service_audio_is_closed(state)) {
        if (open_cfw_liblc3_service_audio_is_open(
                state, &provider, &stored_config)) {
            return state->owner_token == owner_token ?
                OPEN_CFW_LIBLC3_SERVICE_AUDIO_ALREADY_OPEN :
                OPEN_CFW_LIBLC3_SERVICE_AUDIO_WRONG_OWNER;
        }
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_STATE_CORRUPT;
    }
    if (config->channels == 0U || config->channels > (uint32_t)INT_MAX ||
        config->channel_offset >= config->channels ||
        !open_cfw_liblc3_service_audio_pack_config(config, &config_word)) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_UNSUPPORTED;
    }

    provider_config.frame_us = config->frame_us;
    provider_config.sample_rate_hz = config->sample_rate_hz;
    provider_config.pcm_sample_rate_hz = 0U;
    provider_config.bitrate_bps = config->bitrate_bps;
    provider_config.pcm_format = config->pcm_format;
    provider_config.pcm_stride = config->channels;
    status = open_cfw_liblc3_encoder_provider_plan(
        &provider_config, &provider_plan);
    storage = open_cfw_liblc3_service_audio_encoder_storage(
        state, &storage_size);
    if (status != OPEN_CFW_LIBLC3_ENCODER_OK ||
        provider_plan.frame_bytes < 20U ||
        provider_plan.encoder_bytes > storage_size ||
        provider_plan.storage_alignment != 8U) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_UNSUPPORTED;
    }
    interleaved_bytes = (uint64_t)provider_plan.pcm_samples_per_frame *
        config->channels * provider_plan.pcm_sample_bytes;
    if (interleaved_bytes == 0U || interleaved_bytes > UINT32_MAX) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OVERFLOW;
    }

    status = open_cfw_liblc3_encoder_provider_setup(
        &provider, &provider_config, storage, storage_size);
    if (status != OPEN_CFW_LIBLC3_ENCODER_OK) {
        open_cfw_liblc3_encoder_provider_close(&provider);
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_PROVIDER_ERROR;
    }
    state->owner_token = owner_token;
    open_cfw_liblc3_service_audio_advance_generation(state);
    state->config_word = config_word;
    state->channels = config->channels;
    state->channel_offset = config->channel_offset;
    state->bitrate_bps = config->bitrate_bps;
    if (!open_cfw_liblc3_service_audio_provider_view(
            state, &provider, &stored_config)) {
        open_cfw_liblc3_service_audio_invalidate(state);
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_PROVIDER_ERROR;
    }
    state->state_seal =
        open_cfw_liblc3_service_audio_open_seal(state, &provider);

    if (plan != NULL) {
        plan->pcm_samples_per_frame = provider_plan.pcm_samples_per_frame;
        plan->frame_bytes = provider_plan.frame_bytes;
        plan->pcm_sample_bytes = provider_plan.pcm_sample_bytes;
        plan->interleaved_input_frame_bytes = (uint32_t)interleaved_bytes;
        plan->encoder_storage_bytes = provider_plan.encoder_bytes;
    }
    return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK;
}

int open_cfw_liblc3_service_audio_query_plan(
    struct open_cfw_liblc3_service_audio_state *state,
    uint32_t owner_token,
    struct open_cfw_liblc3_service_audio_plan *plan)
{
    struct open_cfw_liblc3_service_audio_config config;

    return open_cfw_liblc3_service_audio_snapshot(
        state, owner_token, &config, plan);
}

int open_cfw_liblc3_service_audio_snapshot(
    struct open_cfw_liblc3_service_audio_state *state,
    uint32_t owner_token,
    struct open_cfw_liblc3_service_audio_config *config,
    struct open_cfw_liblc3_service_audio_plan *plan)
{
    struct open_cfw_liblc3_encoder_provider provider;
    uint64_t interleaved_bytes;

    if (!open_cfw_liblc3_service_audio_address_valid(state) ||
        owner_token == 0U || config == NULL || plan == NULL) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_INVALID_ARGUMENT;
    }
    if (open_cfw_liblc3_service_audio_ranges_overlap(
            config, sizeof(*config), state, sizeof(*state)) ||
        open_cfw_liblc3_service_audio_ranges_overlap(
            plan, sizeof(*plan), state, sizeof(*state)) ||
        open_cfw_liblc3_service_audio_ranges_overlap(
            config, sizeof(*config), plan, sizeof(*plan))) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OVERLAP;
    }
    if (!open_cfw_liblc3_service_audio_is_open(state, &provider, config)) {
        return open_cfw_liblc3_service_audio_is_closed(state) ?
            OPEN_CFW_LIBLC3_SERVICE_AUDIO_NOT_OPEN :
            OPEN_CFW_LIBLC3_SERVICE_AUDIO_STATE_CORRUPT;
    }
    if (state->owner_token != owner_token) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_WRONG_OWNER;
    }
    if ((state->state_seal & OPEN_CFW_LIBLC3_SERVICE_AUDIO_BUSY_BIT) != 0U) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_BUSY;
    }
    interleaved_bytes =
        (uint64_t)provider.plan.pcm_samples_per_frame *
        config->channels * provider.plan.pcm_sample_bytes;
    if (interleaved_bytes == 0U || interleaved_bytes > UINT32_MAX) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OVERFLOW;
    }
    plan->pcm_samples_per_frame = provider.plan.pcm_samples_per_frame;
    plan->frame_bytes = provider.plan.frame_bytes;
    plan->pcm_sample_bytes = provider.plan.pcm_sample_bytes;
    plan->interleaved_input_frame_bytes = (uint32_t)interleaved_bytes;
    plan->encoder_storage_bytes = provider.plan.encoder_bytes;
    return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK;
}

int open_cfw_liblc3_service_audio_encode(
    struct open_cfw_liblc3_service_audio_state *state,
    uint32_t owner_token,
    const void *pcm,
    size_t pcm_bytes,
    void *output,
    size_t output_capacity,
    size_t *output_bytes)
{
    struct open_cfw_liblc3_encoder_provider provider;
    struct open_cfw_liblc3_service_audio_config config;
    const uint8_t *input_cursor;
    uint8_t *output_cursor;
    uint64_t frame_input_bytes;
    uint64_t output_required;
    size_t channel_offset_bytes;
    size_t frame_count;
    size_t frame_index;
    int status;

    if (!open_cfw_liblc3_service_audio_address_valid(state) ||
        owner_token == 0U || pcm == NULL || output == NULL ||
        output_bytes == NULL) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_INVALID_ARGUMENT;
    }
    if (open_cfw_liblc3_service_audio_ranges_overlap(
            output_bytes, sizeof(*output_bytes), state, sizeof(*state)) ||
        open_cfw_liblc3_service_audio_ranges_overlap(
            output_bytes, sizeof(*output_bytes), pcm, pcm_bytes) ||
        open_cfw_liblc3_service_audio_ranges_overlap(
            output_bytes, sizeof(*output_bytes), output, output_capacity)) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OVERLAP;
    }
    *output_bytes = 0U;
    if (!open_cfw_liblc3_service_audio_is_open(state, &provider, &config)) {
        return open_cfw_liblc3_service_audio_is_closed(state) ?
            OPEN_CFW_LIBLC3_SERVICE_AUDIO_NOT_OPEN :
            OPEN_CFW_LIBLC3_SERVICE_AUDIO_STATE_CORRUPT;
    }
    if (state->owner_token != owner_token) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_WRONG_OWNER;
    }
    if ((state->state_seal & OPEN_CFW_LIBLC3_SERVICE_AUDIO_BUSY_BIT) != 0U) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_BUSY;
    }

    frame_input_bytes =
        (uint64_t)provider.plan.pcm_samples_per_frame *
        config.channels * provider.plan.pcm_sample_bytes;
    if (frame_input_bytes == 0U || frame_input_bytes > SIZE_MAX) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OVERFLOW;
    }
    if (pcm_bytes % (size_t)frame_input_bytes != 0U) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_INPUT_GEOMETRY;
    }
    frame_count = pcm_bytes / (size_t)frame_input_bytes;
    output_required = (uint64_t)frame_count * provider.plan.frame_bytes;
    if (output_required > SIZE_MAX) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OVERFLOW;
    }
    if (output_capacity < (size_t)output_required) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OUTPUT_TOO_SMALL;
    }
    if (open_cfw_liblc3_service_audio_ranges_overlap(
            pcm, pcm_bytes, state, sizeof(*state)) ||
        open_cfw_liblc3_service_audio_ranges_overlap(
            output, (size_t)output_required, state, sizeof(*state)) ||
        open_cfw_liblc3_service_audio_ranges_overlap(
            pcm, pcm_bytes, output, (size_t)output_required)) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OVERLAP;
    }

    channel_offset_bytes =
        (size_t)config.channel_offset * provider.plan.pcm_sample_bytes;
    input_cursor = (const uint8_t *)pcm;
    output_cursor = (uint8_t *)output;
    state->state_seal |= OPEN_CFW_LIBLC3_SERVICE_AUDIO_BUSY_BIT;
    for (frame_index = 0U; frame_index < frame_count; frame_index += 1U) {
        status = open_cfw_liblc3_encoder_provider_encode(
            &provider,
            input_cursor + channel_offset_bytes,
            (size_t)frame_input_bytes - channel_offset_bytes,
            output_cursor,
            provider.plan.frame_bytes);
        if (status != OPEN_CFW_LIBLC3_ENCODER_OK) {
            *output_bytes = frame_index * provider.plan.frame_bytes;
            open_cfw_liblc3_service_audio_invalidate(state);
            return OPEN_CFW_LIBLC3_SERVICE_AUDIO_PROVIDER_ERROR;
        }
        input_cursor += (size_t)frame_input_bytes;
        output_cursor += provider.plan.frame_bytes;
    }
    state->state_seal &= OPEN_CFW_LIBLC3_SERVICE_AUDIO_SEAL_MASK;
    *output_bytes = (size_t)output_required;
    return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK;
}

int open_cfw_liblc3_service_audio_close(
    struct open_cfw_liblc3_service_audio_state *state,
    uint32_t owner_token)
{
    struct open_cfw_liblc3_encoder_provider provider;
    struct open_cfw_liblc3_service_audio_config config;

    if (!open_cfw_liblc3_service_audio_address_valid(state) ||
        owner_token == 0U) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_INVALID_ARGUMENT;
    }
    if (!open_cfw_liblc3_service_audio_is_open(state, &provider, &config)) {
        return open_cfw_liblc3_service_audio_is_closed(state) ?
            OPEN_CFW_LIBLC3_SERVICE_AUDIO_NOT_OPEN :
            OPEN_CFW_LIBLC3_SERVICE_AUDIO_STATE_CORRUPT;
    }
    if (state->owner_token != owner_token) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_WRONG_OWNER;
    }
    if ((state->state_seal & OPEN_CFW_LIBLC3_SERVICE_AUDIO_BUSY_BIT) != 0U) {
        return OPEN_CFW_LIBLC3_SERVICE_AUDIO_BUSY;
    }
    open_cfw_liblc3_encoder_provider_close(&provider);
    open_cfw_liblc3_service_audio_invalidate(state);
    return OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK;
}
