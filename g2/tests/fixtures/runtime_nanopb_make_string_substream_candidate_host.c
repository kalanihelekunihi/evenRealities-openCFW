#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "runtime_nanopb_make_string_substream_candidate.h"

struct open_cfw_nanopb_substream_result {
    uint32_t status;
    uint32_t decode_calls;
    uint64_t parent_bytes_left;
    uint64_t substream_bytes_left;
    uint32_t parent_callback_kind;
    uint32_t substream_callback_kind;
    uint32_t parent_state_kind;
    uint32_t substream_state_kind;
    uint32_t parent_error_kind;
    uint32_t substream_error_kind;
};

static uint32_t provider_size;
static bool provider_status;
static bool provider_mutates_stream;
static size_t provider_bytes_left;
static uint32_t provider_calls;

static const char existing_error[] = "existing error";
static const char substream_sentinel_error[] = "substream sentinel";
static uint32_t state_before;
static uint32_t state_after;
static uint32_t state_substream;

static bool callback_before(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    (void)stream;
    (void)buffer;
    (void)count;
    return true;
}

static bool callback_after(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    (void)stream;
    (void)buffer;
    (void)count;
    return true;
}

static bool callback_substream(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    (void)stream;
    (void)buffer;
    (void)count;
    return true;
}

bool open_cfw_nanopb_decode_varint32(
    struct open_cfw_nanopb_istream *stream,
    uint32_t *destination
)
{
    provider_calls += 1U;
    *destination = provider_size;
    if (provider_mutates_stream) {
        stream->callback = callback_after;
        stream->state = &state_after;
        stream->bytes_left = provider_bytes_left;
    }
    return provider_status;
}

static uint32_t callback_kind(open_cfw_nanopb_read_callback callback)
{
    if (callback == callback_before) {
        return 1U;
    }
    if (callback == callback_after) {
        return 2U;
    }
    if (callback == callback_substream) {
        return 3U;
    }
    return 4U;
}

static uint32_t state_kind(const void *state)
{
    if (state == &state_before) {
        return 1U;
    }
    if (state == &state_after) {
        return 2U;
    }
    if (state == &state_substream) {
        return 3U;
    }
    return 4U;
}

static uint32_t error_kind(const char *error)
{
    if (error == NULL) {
        return 0U;
    }
    if (error == existing_error) {
        return 1U;
    }
    if (error == substream_sentinel_error) {
        return 2U;
    }
    return 3U;
}

void open_cfw_test_nanopb_make_string_substream_candidate(
    uint32_t decoded_size,
    bool decode_status,
    bool mutate_stream,
    uint64_t parent_bytes_left,
    bool preset_parent_error,
    bool alias_streams,
    struct open_cfw_nanopb_substream_result *result
)
{
    struct open_cfw_nanopb_istream parent = {
        callback_before,
        &state_before,
        (size_t)parent_bytes_left,
        preset_parent_error ? existing_error : NULL
    };
    struct open_cfw_nanopb_istream substream = {
        callback_substream,
        &state_substream,
        (size_t)0xA5A5U,
        substream_sentinel_error
    };
    struct open_cfw_nanopb_istream *substream_pointer =
        alias_streams ? &parent : &substream;

    provider_size = decoded_size;
    provider_status = decode_status;
    provider_mutates_stream = mutate_stream;
    provider_bytes_left = (size_t)parent_bytes_left;
    provider_calls = 0U;

    result->status = open_cfw_nanopb_make_string_substream_candidate(
        &parent,
        substream_pointer
    );
    result->decode_calls = provider_calls;
    result->parent_bytes_left = (uint64_t)parent.bytes_left;
    result->substream_bytes_left = (uint64_t)substream_pointer->bytes_left;
    result->parent_callback_kind = callback_kind(parent.callback);
    result->substream_callback_kind = callback_kind(substream_pointer->callback);
    result->parent_state_kind = state_kind(parent.state);
    result->substream_state_kind = state_kind(substream_pointer->state);
    result->parent_error_kind = error_kind(parent.errmsg);
    result->substream_error_kind = error_kind(substream_pointer->errmsg);
}
