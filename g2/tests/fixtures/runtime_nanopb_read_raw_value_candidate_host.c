#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "runtime_nanopb_read_raw_value_candidate.h"

struct open_cfw_nanopb_raw_result {
    uint32_t status;
    uint32_t size;
    uint32_t read_calls;
    uint32_t total_requested;
    uint32_t error_kind;
    uint8_t buffer[16];
};

static const uint8_t *provider_source;
static size_t provider_size;
static size_t provider_offset;
static uint32_t provider_calls;
static uint32_t provider_requested;
static uint32_t provider_fail_call;
static const char existing_error[] = "existing error";

bool open_cfw_nanopb_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    (void)stream;
    provider_calls += 1U;
    provider_requested += (uint32_t)count;
    if (provider_fail_call != 0U && provider_calls == provider_fail_call) {
        return false;
    }
    if (count > provider_size - provider_offset) {
        return false;
    }
    memcpy(buffer, provider_source + provider_offset, count);
    provider_offset += count;
    return true;
}

void open_cfw_test_nanopb_read_raw_value_candidate(
    uint8_t wire_type,
    size_t maximum_size,
    const uint8_t *source,
    size_t source_size,
    uint32_t fail_call,
    bool preset_error,
    struct open_cfw_nanopb_raw_result *result
)
{
    struct open_cfw_nanopb_istream stream = {0};
    size_t size = maximum_size;

    memset(result, 0, sizeof(*result));
    provider_source = source;
    provider_size = source_size;
    provider_offset = 0U;
    provider_calls = 0U;
    provider_requested = 0U;
    provider_fail_call = fail_call;
    if (preset_error) {
        stream.errmsg = existing_error;
    }

    result->status = open_cfw_nanopb_read_raw_value_candidate(
        &stream,
        wire_type,
        result->buffer,
        &size
    );
    result->size = (uint32_t)size;
    result->read_calls = provider_calls;
    result->total_requested = provider_requested;
    if (stream.errmsg == NULL) {
        result->error_kind = 0U;
    } else if (stream.errmsg == existing_error) {
        result->error_kind = 1U;
    } else if (strcmp(stream.errmsg, "varint overflow") == 0) {
        result->error_kind = 2U;
    } else if (strcmp(stream.errmsg, "invalid wire_type") == 0) {
        result->error_kind = 3U;
    } else {
        result->error_kind = 4U;
    }
}
