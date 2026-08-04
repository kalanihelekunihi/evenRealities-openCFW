/* Host-only differential harness for the private nanopb read production pair. */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "components/shared/nanopb/runtime_nanopb_private_read_pair.h"
#include "pb_decode.h"

#define CHECK(condition) do { if (!(condition)) return __LINE__; } while (0)

const char open_cfw_nanopb_end_of_stream_error[] = "end-of-stream";
const char open_cfw_nanopb_io_error[] = "io error";

static size_t open_cfw_test_memcpy_calls;

void __aeabi_memcpy(
    void *destination,
    const void *source,
    size_t count
)
{
    open_cfw_test_memcpy_calls++;
    (void)memcpy(destination, source, count);
}

struct open_cfw_test_read_context {
    const uint8_t *source;
    size_t size;
    size_t offset;
    size_t calls;
    bool fail;
    bool zero_budget_after_success;
};

struct open_cfw_test_read_result {
    size_t bytes_left;
    size_t consumed;
    size_t calls;
    uint64_t value;
    const char *errmsg;
    bool status;
};

static const char open_cfw_test_preexisting_error[] = "preexisting";

static bool open_cfw_test_production_callback(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    struct open_cfw_test_read_context *context =
        (struct open_cfw_test_read_context *)stream->state;

    context->calls++;
    if (context->fail || count > context->size - context->offset) {
        return false;
    }

    (void)memcpy(buffer, context->source + context->offset, count);
    context->offset += count;
    if (context->zero_budget_after_success) {
        stream->bytes_left = 0U;
    }
    return true;
}

static bool open_cfw_test_upstream_callback(
    pb_istream_t *stream,
    pb_byte_t *buffer,
    size_t count
)
{
    struct open_cfw_test_read_context *context =
        (struct open_cfw_test_read_context *)stream->state;

    context->calls++;
    if (context->fail || count > context->size - context->offset) {
        return false;
    }

    (void)memcpy(buffer, context->source + context->offset, count);
    context->offset += count;
    if (context->zero_budget_after_success) {
        stream->bytes_left = 0U;
    }
    return true;
}

static struct open_cfw_test_read_result open_cfw_test_run_production(
    const uint8_t *source,
    size_t size,
    size_t bytes_left,
    bool fail,
    bool zero_budget_after_success,
    bool preexisting_error
)
{
    struct open_cfw_test_read_context context = {
        source, size, 0U, 0U, fail, zero_budget_after_success
    };
    struct open_cfw_nanopb_istream stream = {
        open_cfw_test_production_callback,
        &context,
        bytes_left,
        preexisting_error ? open_cfw_test_preexisting_error : NULL
    };
    uint8_t value = 0xA5U;
    bool status = open_cfw_nanopb_readbyte(&stream, &value);
    struct open_cfw_test_read_result result = {
        stream.bytes_left,
        context.offset,
        context.calls,
        value,
        stream.errmsg,
        status
    };
    return result;
}

static struct open_cfw_test_read_result open_cfw_test_run_upstream(
    const uint8_t *source,
    size_t size,
    size_t bytes_left,
    bool fail,
    bool zero_budget_after_success,
    bool preexisting_error
)
{
    struct open_cfw_test_read_context context = {
        source, size, 0U, 0U, fail, zero_budget_after_success
    };
    pb_istream_t stream = {
        open_cfw_test_upstream_callback,
        &context,
        bytes_left,
        preexisting_error ? open_cfw_test_preexisting_error : NULL
    };
    uint64_t value = 0xA5U;
    bool status = pb_decode_varint(&stream, &value);
    struct open_cfw_test_read_result result = {
        stream.bytes_left,
        context.offset,
        context.calls,
        value,
        stream.errmsg,
        status
    };
    return result;
}

static bool open_cfw_test_same_result(
    const struct open_cfw_test_read_result *production,
    const struct open_cfw_test_read_result *upstream
)
{
    bool same_error = false;

    if (production->errmsg == NULL || upstream->errmsg == NULL) {
        same_error = production->errmsg == upstream->errmsg;
    } else {
        same_error = strcmp(production->errmsg, upstream->errmsg) == 0;
    }

    return production->bytes_left == upstream->bytes_left &&
        production->consumed == upstream->consumed &&
        production->calls == upstream->calls &&
        production->value == upstream->value &&
        production->status == upstream->status &&
        same_error;
}

static int open_cfw_test_buf_read_production(void)
{
    static const uint8_t source[] = {1U, 2U, 3U, 4U, 5U, 6U};
    uint8_t production_output[3] = {0U};
    uint8_t upstream_output[3] = {0U};
    struct open_cfw_nanopb_istream production = {
        open_cfw_nanopb_buf_read,
        (void *)source,
        99U,
        open_cfw_test_preexisting_error
    };
    pb_istream_t upstream = pb_istream_from_buffer(source, 99U);

    upstream.errmsg = open_cfw_test_preexisting_error;
    open_cfw_test_memcpy_calls = 0U;
    CHECK(open_cfw_nanopb_buf_read(
        &production, production_output, sizeof(production_output)
    ));
    CHECK(upstream.callback(
        &upstream, upstream_output, sizeof(upstream_output)
    ));
    CHECK(memcmp(production_output, upstream_output, sizeof(production_output)) == 0);
    CHECK(production.state == source + 3U);
    CHECK(upstream.state == source + 3U);
    CHECK(production.bytes_left == upstream.bytes_left);
    CHECK(production.errmsg == open_cfw_test_preexisting_error);
    CHECK(upstream.errmsg == open_cfw_test_preexisting_error);
    CHECK(open_cfw_test_memcpy_calls == 1U);

    CHECK(open_cfw_nanopb_buf_read(&production, NULL, 2U));
    CHECK(upstream.callback(&upstream, NULL, 2U));
    CHECK(production.state == source + 5U);
    CHECK(upstream.state == source + 5U);
    CHECK(production.bytes_left == 99U);
    CHECK(upstream.bytes_left == 99U);
    CHECK(open_cfw_test_memcpy_calls == 1U);
    return 0;
}

static int open_cfw_test_readbyte_production(void)
{
    static const uint8_t source[] = {0x2AU};
    size_t index;
    static const bool cases[][4] = {
        {false, false, false, false},
        {true,  false, false, false},
        {false, true,  false, false},
        {false, false, true,  false},
        {true,  false, true,  false},
        {false, false, false, true},
        {false, false, true,  true}
    };

    for (index = 0U; index < sizeof(cases) / sizeof(cases[0]); index++) {
        bool fail = cases[index][0];
        bool zero_after = cases[index][1];
        bool preexisting = cases[index][2];
        size_t bytes_left = cases[index][3] ? 0U : 1U;
        struct open_cfw_test_read_result production =
            open_cfw_test_run_production(
                source, sizeof(source), bytes_left, fail, zero_after, preexisting
            );
        struct open_cfw_test_read_result upstream =
            open_cfw_test_run_upstream(
                source, sizeof(source), bytes_left, fail, zero_after, preexisting
            );

        CHECK(open_cfw_test_same_result(&production, &upstream));
    }
    return 0;
}

static int open_cfw_test_atomic_buffer_path(void)
{
    static const uint8_t source[] = {0x7FU};
    uint8_t production_value = 0U;
    uint64_t upstream_value = 0U;
    struct open_cfw_nanopb_istream production = {
        open_cfw_nanopb_buf_read,
        (void *)source,
        sizeof(source),
        NULL
    };
    pb_istream_t upstream = pb_istream_from_buffer(source, sizeof(source));

    open_cfw_test_memcpy_calls = 0U;
    CHECK(open_cfw_nanopb_readbyte(
        &production, &production_value
    ));
    CHECK(pb_decode_varint(&upstream, &upstream_value));
    CHECK(production_value == upstream_value);
    CHECK(production.state == upstream.state);
    CHECK(production.bytes_left == upstream.bytes_left);
    CHECK(production.errmsg == NULL && upstream.errmsg == NULL);
    CHECK(open_cfw_test_memcpy_calls == 1U);
    return 0;
}

int open_cfw_test_nanopb_private_read_pair(void)
{
    int result;

    result = open_cfw_test_buf_read_production();
    if (result != 0) return result;
    result = open_cfw_test_readbyte_production();
    if (result != 0) return result;
    result = open_cfw_test_atomic_buffer_path();
    if (result != 0) return result;
    return 0;
}
