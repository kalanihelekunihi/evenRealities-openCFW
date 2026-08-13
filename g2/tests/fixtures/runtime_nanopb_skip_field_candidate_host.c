#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "runtime_nanopb_skip_field_candidate.h"

struct open_cfw_nanopb_skip_field_result {
    uint32_t status;
    uint32_t provider;
    uint32_t count;
    uint32_t error_kind;
};

static bool provider_status;
static uint32_t selected_provider;
static uint32_t selected_count;
static const char existing_error[] = "existing error";

bool open_cfw_nanopb_skip_varint(
    struct open_cfw_nanopb_istream *stream
)
{
    (void)stream;
    selected_provider = 1U;
    return provider_status;
}

bool open_cfw_nanopb_skip_string(
    struct open_cfw_nanopb_istream *stream
)
{
    (void)stream;
    selected_provider = 2U;
    return provider_status;
}

bool open_cfw_nanopb_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    (void)stream;
    selected_provider = buffer == NULL ? 3U : 99U;
    selected_count = (uint32_t)count;
    return provider_status;
}

void open_cfw_test_nanopb_skip_field_candidate(
    uint8_t wire_type,
    bool succeed,
    bool preset_error,
    struct open_cfw_nanopb_skip_field_result *result
)
{
    struct open_cfw_nanopb_istream stream = {0};

    provider_status = succeed;
    selected_provider = 0U;
    selected_count = 0U;
    if (preset_error) {
        stream.errmsg = existing_error;
    }

    result->status = open_cfw_nanopb_skip_field_candidate(
        &stream,
        wire_type
    );
    result->provider = selected_provider;
    result->count = selected_count;
    if (stream.errmsg == NULL) {
        result->error_kind = 0U;
    } else if (stream.errmsg == existing_error) {
        result->error_kind = 1U;
    } else {
        result->error_kind = 2U;
    }
}
