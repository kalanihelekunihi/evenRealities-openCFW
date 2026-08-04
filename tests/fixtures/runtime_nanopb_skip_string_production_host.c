/* Candidate oracle and production integration fixture for nanopb skip-string. */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define CHECK(value) do { if (!(value)) { return __LINE__; } } while (0)

#if defined(OPENCFW_SKIP_STRING_CANDIDATE_ORACLE)

#include "components/shared/nanopb/runtime_nanopb_skip_string.h"
#include "third_party/nanopb/pb_decode.h"

static bool test_decode_result;
static uint32_t test_decode_length;
static size_t test_decode_calls;
static struct open_cfw_nanopb_istream *test_decode_stream;
static bool test_read_result;
static size_t test_read_calls;
static struct open_cfw_nanopb_istream *test_read_stream;
static uint8_t *test_read_buffer;
static size_t test_read_count;

bool open_cfw_nanopb_decode_varint32(
    struct open_cfw_nanopb_istream *stream,
    uint32_t *destination
)
{
    test_decode_calls++;
    test_decode_stream = stream;
    if (!test_decode_result) {
        return false;
    }
    *destination = test_decode_length;
    return true;
}

bool open_cfw_nanopb_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    test_read_calls++;
    test_read_stream = stream;
    test_read_buffer = buffer;
    test_read_count = count;
    return test_read_result;
}

static void reset_seams(void)
{
    test_decode_result = true;
    test_decode_length = 0U;
    test_decode_calls = 0U;
    test_decode_stream = NULL;
    test_read_result = true;
    test_read_calls = 0U;
    test_read_stream = NULL;
    test_read_buffer = (uint8_t *)(uintptr_t)1U;
    test_read_count = 0U;
}

static int check_candidate_case(
    uint32_t length,
    bool decode_result,
    bool read_result
)
{
    struct open_cfw_nanopb_istream stream = {0};
    bool result;

    reset_seams();
    test_decode_length = length;
    test_decode_result = decode_result;
    test_read_result = read_result;
    result = open_cfw_nanopb_skip_string(&stream);

    CHECK(result == (decode_result && read_result));
    CHECK(test_decode_calls == 1U);
    CHECK(test_decode_stream == &stream);
    CHECK(test_read_calls == (decode_result ? 1U : 0U));
    if (decode_result) {
        CHECK(test_read_stream == &stream);
        CHECK(test_read_buffer == NULL);
        CHECK(test_read_count == (size_t)length);
    }
    return 0;
}

static int check_upstream_case(
    const uint8_t *encoded,
    size_t encoded_size,
    size_t expected_remaining,
    bool expected_result
)
{
    pb_istream_t stream = pb_istream_from_buffer(encoded, encoded_size);
    bool result = pb_skip_field(&stream, PB_WT_STRING);

    CHECK(result == expected_result);
    CHECK(stream.bytes_left == expected_remaining);
    return 0;
}

int open_cfw_test_nanopb_skip_string_candidate(void)
{
    static const uint8_t empty[] = {0x00U};
    static const uint8_t three[] = {0x03U, 0x11U, 0x22U, 0x33U};
    static const uint8_t one_twenty_eight[130] = {0x80U, 0x01U};
    static const uint8_t truncated_length[] = {0x80U};
    static const uint8_t truncated_payload[] = {0x03U, 0x11U, 0x22U};
    int line;

    line = check_candidate_case(0U, true, true);
    CHECK(line == 0);
    line = check_candidate_case(3U, true, true);
    CHECK(line == 0);
    line = check_candidate_case(0xFFFFFFFFU, true, false);
    CHECK(line == 0);
    line = check_candidate_case(17U, false, true);
    CHECK(line == 0);

    line = check_upstream_case(empty, sizeof(empty), 0U, true);
    CHECK(line == 0);
    line = check_upstream_case(three, sizeof(three), 0U, true);
    CHECK(line == 0);
    line = check_upstream_case(
        one_twenty_eight,
        sizeof(one_twenty_eight),
        0U,
        true
    );
    CHECK(line == 0);
    line = check_upstream_case(
        truncated_length,
        sizeof(truncated_length),
        0U,
        false
    );
    CHECK(line == 0);
    line = check_upstream_case(
        truncated_payload,
        sizeof(truncated_payload),
        2U,
        false
    );
    CHECK(line == 0);

    return 0;
}

#elif defined(OPENCFW_SKIP_STRING_PRODUCTION_SEAM_PROBE)

#include "components/shared/nanopb/runtime_nanopb_skip_string.h"

static bool test_decode_result;
static uint32_t test_decode_length;
static size_t test_decode_calls;
static size_t test_read_calls;
static uint8_t *test_read_buffer;
static size_t test_read_count;
static bool test_read_result;

bool open_cfw_nanopb_decode_varint32(
    struct open_cfw_nanopb_istream *stream,
    uint32_t *destination
)
{
    (void)stream;
    test_decode_calls++;
    if (!test_decode_result) {
        return false;
    }
    *destination = test_decode_length;
    return true;
}

bool open_cfw_nanopb_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    (void)stream;
    test_read_calls++;
    test_read_buffer = buffer;
    test_read_count = count;
    return test_read_result;
}

static void reset_production_seams(void)
{
    test_decode_result = true;
    test_decode_length = 0U;
    test_decode_calls = 0U;
    test_read_calls = 0U;
    test_read_buffer = (uint8_t *)(uintptr_t)1U;
    test_read_count = 0U;
    test_read_result = true;
}

int open_cfw_test_nanopb_skip_string_production_seams(void)
{
    struct open_cfw_nanopb_istream stream = {0};

    reset_production_seams();
    test_decode_result = false;
    CHECK(!open_cfw_nanopb_skip_string(&stream));
    CHECK(test_decode_calls == 1U);
    CHECK(test_read_calls == 0U);

    reset_production_seams();
    CHECK(open_cfw_nanopb_skip_string(&stream));
    CHECK(test_decode_calls == 1U);
    CHECK(test_read_calls == 1U);
    CHECK(test_read_buffer == NULL);
    CHECK(test_read_count == 0U);

    reset_production_seams();
    test_decode_length = UINT32_MAX;
    test_read_result = false;
    CHECK(!open_cfw_nanopb_skip_string(&stream));
    CHECK(test_decode_calls == 1U);
    CHECK(test_read_calls == 1U);
    CHECK(test_read_buffer == NULL);
    CHECK(test_read_count == (size_t)UINT32_MAX);

    return 0;
}

#else

#include "components/shared/nanopb/runtime_nanopb_skip_string.h"
#include "third_party/nanopb/pb_decode.h"

#define OPEN_CFW_TEST_MAX_CALLS 16U

const char open_cfw_nanopb_end_of_stream_error[] = "end-of-stream";
const char open_cfw_nanopb_io_error[] = "io error";

struct open_cfw_test_skip_string_input {
    const uint8_t *bytes;
    size_t size;
    size_t offset;
    uint32_t calls;
    uint32_t fail_call;
    uint32_t mutate_call;
    size_t mutated_budget;
    uint32_t null_calls;
    size_t counts[OPEN_CFW_TEST_MAX_CALLS];
};

struct open_cfw_test_skip_string_result {
    uint64_t bytes_left;
    uint64_t consumed;
    uint64_t callback_offset;
    uint64_t counts[OPEN_CFW_TEST_MAX_CALLS];
    uint32_t status;
    uint32_t calls;
    uint32_t error;
    uint32_t state_unchanged;
    uint32_t null_calls;
};

static const char open_cfw_test_skip_string_preexisting[] = "preexisting";

static bool open_cfw_test_skip_string_read(
    struct open_cfw_test_skip_string_input *input,
    size_t *bytes_left,
    uint8_t *buffer,
    size_t count
)
{
    uint32_t index = input->calls++;

    if (index < OPEN_CFW_TEST_MAX_CALLS) {
        input->counts[index] = count;
    }
    if (buffer == NULL) {
        input->null_calls++;
    }
    if (input->calls == input->mutate_call) {
        *bytes_left = input->mutated_budget;
    }
    if (
        input->calls == input->fail_call ||
        input->offset > input->size ||
        count > input->size - input->offset
    ) {
        return false;
    }
    if (buffer == NULL) {
        return false;
    }
    (void)memcpy(buffer, input->bytes + input->offset, count);
    input->offset += count;
    return true;
}

static bool open_cfw_test_skip_string_production_callback(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    return open_cfw_test_skip_string_read(
        (struct open_cfw_test_skip_string_input *)stream->state,
        &stream->bytes_left,
        buffer,
        count
    );
}

static bool open_cfw_test_skip_string_upstream_callback(
    pb_istream_t *stream,
    pb_byte_t *buffer,
    size_t count
)
{
    return open_cfw_test_skip_string_read(
        (struct open_cfw_test_skip_string_input *)stream->state,
        &stream->bytes_left,
        buffer,
        count
    );
}

bool open_cfw_nanopb_stock_buffer_read_identity(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    const uint8_t *source = (const uint8_t *)stream->state;

    if (buffer != NULL) {
        (void)memcpy(buffer, source, count);
    }
    stream->state = (void *)(source + count);
    return true;
}

static uint32_t open_cfw_test_skip_string_error(const char *error)
{
    if (error == NULL) {
        return 0U;
    }
    if (strcmp(error, "end-of-stream") == 0) {
        return 1U;
    }
    if (strcmp(error, "io error") == 0) {
        return 2U;
    }
    if (strcmp(error, "varint overflow") == 0) {
        return 3U;
    }
    if (strcmp(error, open_cfw_test_skip_string_preexisting) == 0) {
        return 4U;
    }
    return UINT32_MAX;
}

static void open_cfw_test_skip_string_store(
    bool status,
    const struct open_cfw_test_skip_string_input *input,
    size_t bytes_left,
    const char *errmsg,
    const void *initial_state,
    const void *final_state,
    struct open_cfw_test_skip_string_result *output
)
{
    size_t index;

    output->bytes_left = bytes_left;
    output->consumed = input->offset;
    output->callback_offset = input->offset;
    for (index = 0U; index < OPEN_CFW_TEST_MAX_CALLS; index++) {
        output->counts[index] = input->counts[index];
    }
    output->status = status ? 1U : 0U;
    output->calls = input->calls;
    output->error = open_cfw_test_skip_string_error(errmsg);
    output->state_unchanged = initial_state == final_state ? 1U : 0U;
    output->null_calls = input->null_calls;
}

void open_cfw_test_nanopb_skip_string_run_production(
    const uint8_t *bytes,
    size_t size,
    size_t bytes_left,
    uint32_t fail_call,
    uint32_t mutate_call,
    size_t mutated_budget,
    uint32_t preexisting_error,
    struct open_cfw_test_skip_string_result *output
)
{
    struct open_cfw_test_skip_string_input input = {
        bytes, size, 0U, 0U, fail_call, mutate_call, mutated_budget,
        0U, {0U}
    };
    struct open_cfw_nanopb_istream stream = {
        open_cfw_test_skip_string_production_callback,
        &input,
        bytes_left,
        preexisting_error ? open_cfw_test_skip_string_preexisting : NULL
    };
    const void *initial_state = stream.state;
    bool status = open_cfw_nanopb_skip_string(&stream);

    open_cfw_test_skip_string_store(
        status, &input, stream.bytes_left, stream.errmsg,
        initial_state, stream.state, output
    );
}

void open_cfw_test_nanopb_skip_string_run_upstream(
    const uint8_t *bytes,
    size_t size,
    size_t bytes_left,
    uint32_t fail_call,
    uint32_t mutate_call,
    size_t mutated_budget,
    uint32_t preexisting_error,
    struct open_cfw_test_skip_string_result *output
)
{
    struct open_cfw_test_skip_string_input input = {
        bytes, size, 0U, 0U, fail_call, mutate_call, mutated_budget,
        0U, {0U}
    };
    pb_istream_t stream = {
        open_cfw_test_skip_string_upstream_callback,
        &input,
        bytes_left,
        preexisting_error ? open_cfw_test_skip_string_preexisting : NULL
    };
    const void *initial_state = stream.state;
    bool status = pb_skip_field(&stream, PB_WT_STRING);

    open_cfw_test_skip_string_store(
        status, &input, stream.bytes_left, stream.errmsg,
        initial_state, stream.state, output
    );
}

int open_cfw_test_nanopb_skip_string_canonical_buffer(void)
{
    static const uint8_t bytes[] = {0x03U, 0x11U, 0x22U, 0x33U};
    struct open_cfw_nanopb_istream production = {
        open_cfw_nanopb_stock_buffer_read_identity,
        (void *)bytes,
        sizeof(bytes),
        NULL
    };
    pb_istream_t upstream = pb_istream_from_buffer(bytes, sizeof(bytes));

    CHECK(open_cfw_nanopb_skip_string(&production));
    CHECK(pb_skip_field(&upstream, PB_WT_STRING));
    CHECK(production.bytes_left == upstream.bytes_left);
    CHECK(production.bytes_left == 0U);
    CHECK(production.state == bytes + sizeof(bytes));
    CHECK(upstream.state == bytes + sizeof(bytes));
    CHECK(production.errmsg == NULL);
    CHECK(upstream.errmsg == NULL);
    return 0;
}

#endif
