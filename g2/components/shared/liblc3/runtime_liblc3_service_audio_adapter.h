/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded service_audio-facing lifetime adapter for the admitted LC3 encoder.
 */
#ifndef OPEN_CFW_RUNTIME_LIBLC3_SERVICE_AUDIO_ADAPTER_H
#define OPEN_CFW_RUNTIME_LIBLC3_SERVICE_AUDIO_ADAPTER_H

#include <stddef.h>
#include <stdint.h>

#include "runtime_liblc3_encoder_provider.h"

#define OPEN_CFW_LIBLC3_SERVICE_AUDIO_STORAGE_BYTES UINT32_C(2600)

enum open_cfw_liblc3_service_audio_status {
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_OK = 0,
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_INVALID_ARGUMENT = -1,
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_STATE_CORRUPT = -2,
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_NOT_OPEN = -3,
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_WRONG_OWNER = -4,
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_ALREADY_OPEN = -5,
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_BUSY = -6,
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_UNSUPPORTED = -7,
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_INPUT_GEOMETRY = -8,
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_OUTPUT_TOO_SMALL = -9,
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_PROVIDER_ERROR = -10,
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_OVERFLOW = -11,
    OPEN_CFW_LIBLC3_SERVICE_AUDIO_OVERLAP = -12
};

/* Exact fixed-width counterpart of the recovered 24-byte stock header. */
struct open_cfw_liblc3_service_audio_config {
    uint32_t pcm_format;
    uint32_t frame_us;
    uint32_t sample_rate_hz;
    uint32_t channels;
    uint32_t channel_offset;
    uint32_t bitrate_bps;
};

struct open_cfw_liblc3_service_audio_plan {
    uint32_t pcm_samples_per_frame;
    uint32_t frame_bytes;
    uint32_t pcm_sample_bytes;
    uint32_t interleaved_input_frame_bytes;
    uint32_t encoder_storage_bytes;
};

/*
 * One explicitly owned encoder lifetime sized to the authenticated stock
 * context slot.  The seven-word control header losslessly codes every
 * provider-admitted configuration; channels, channel offset, and bitrate keep
 * their full 32-bit values.  The storage address, not the state type, requires
 * eight-byte alignment.  Authenticated stock slots alternate between zero and
 * four modulo eight; the implementation aligns the encoder within the byte
 * storage at offset 28 and consumes at most a four-byte prefix.
 *
 * A nonzero owner token must match for encode and close operations.  The
 * boundary is single-executor; a seal bit records a visible busy state and
 * fails closed.  Before first initialization, every control byte must be zero.
 * Encoder storage itself need not be cleared and is retained across closed
 * lifetimes.
 */
struct open_cfw_liblc3_service_audio_state {
    uint32_t state_seal;
    uint32_t owner_token;
    uint32_t generation;
    uint32_t config_word;
    uint32_t channels;
    uint32_t channel_offset;
    uint32_t bitrate_bps;
    uint8_t storage[OPEN_CFW_LIBLC3_SERVICE_AUDIO_STORAGE_BYTES];
};

int open_cfw_liblc3_service_audio_state_init(
    struct open_cfw_liblc3_service_audio_state *state);

int open_cfw_liblc3_service_audio_open(
    struct open_cfw_liblc3_service_audio_state *state,
    uint32_t owner_token,
    const struct open_cfw_liblc3_service_audio_config *config,
    struct open_cfw_liblc3_service_audio_plan *plan);

/* Re-derive the authenticated plan without reinitializing encoder storage. */
int open_cfw_liblc3_service_audio_query_plan(
    struct open_cfw_liblc3_service_audio_state *state,
    uint32_t owner_token,
    struct open_cfw_liblc3_service_audio_plan *plan);

/* Snapshot the sealed configuration and plan without touching codec state. */
int open_cfw_liblc3_service_audio_snapshot(
    struct open_cfw_liblc3_service_audio_state *state,
    uint32_t owner_token,
    struct open_cfw_liblc3_service_audio_config *config,
    struct open_cfw_liblc3_service_audio_plan *plan);

/* Encode zero or more complete interleaved frames from one selected channel. */
int open_cfw_liblc3_service_audio_encode(
    struct open_cfw_liblc3_service_audio_state *state,
    uint32_t owner_token,
    const void *pcm,
    size_t pcm_bytes,
    void *output,
    size_t output_capacity,
    size_t *output_bytes);

/* Close only the matching lifetime; encoder storage is deliberately retained. */
int open_cfw_liblc3_service_audio_close(
    struct open_cfw_liblc3_service_audio_state *state,
    uint32_t owner_token);

#endif
