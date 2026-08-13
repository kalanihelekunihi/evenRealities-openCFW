/* Host-only differential harness for the production nanopb varint32 pair. */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "components/shared/nanopb/runtime_nanopb_decode_varint32.h"
#include "pb_decode.h"

struct open_cfw_test_nanopb_input {
    const uint8_t *bytes;
    size_t size;
    size_t offset;
    uint32_t calls;
    uint32_t fail_call;
    uint32_t mutate_call;
    size_t mutated_budget;
};

struct open_cfw_test_nanopb_varint32_result {
    uint32_t value;
    uint64_t bytes_left;
    uint64_t callback_offset;
    uint64_t consumed;
    uint32_t status;
    uint32_t calls;
    uint32_t error;
    uint32_t eof;
};

static const char open_cfw_test_nanopb_preexisting[] = "preexisting";

static bool open_cfw_test_nanopb_read(
    struct open_cfw_test_nanopb_input *input,
    size_t *bytes_left,
    uint8_t *buffer,
    size_t count
)
{
    input->calls++;
    if (input->calls == input->mutate_call) {
        *bytes_left = input->mutated_budget;
    }
    if (
        input->calls == input->fail_call ||
        count > input->size - input->offset
    ) {
        return false;
    }
    memcpy(buffer, input->bytes + input->offset, count);
    input->offset += count;
    return true;
}

static bool open_cfw_test_nanopb_production_callback(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    return open_cfw_test_nanopb_read(
        (struct open_cfw_test_nanopb_input *)stream->state,
        &stream->bytes_left,
        buffer,
        count
    );
}

static bool open_cfw_test_nanopb_upstream_callback(
    pb_istream_t *stream,
    pb_byte_t *buffer,
    size_t count
)
{
    return open_cfw_test_nanopb_read(
        (struct open_cfw_test_nanopb_input *)stream->state,
        &stream->bytes_left,
        buffer,
        count
    );
}

static uint32_t open_cfw_test_nanopb_error(const char *error)
{
    if (error == (const char *)0) {
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
    if (strcmp(error, open_cfw_test_nanopb_preexisting) == 0) {
        return 4U;
    }
    return UINT32_C(0xFFFF);
}

bool open_cfw_nanopb_readbyte(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *byte
)
{
    if (stream->bytes_left == 0U) {
        if (stream->errmsg == (const char *)0) {
            stream->errmsg = "end-of-stream";
        }
        return false;
    }

    if (!stream->callback(stream, byte, 1U)) {
        if (stream->errmsg == (const char *)0) {
            stream->errmsg = "io error";
        }
        return false;
    }

    stream->bytes_left--;
    return true;
}

static void open_cfw_test_nanopb_store_result(
    uint32_t value,
    bool status,
    bool eof,
    const struct open_cfw_test_nanopb_input *input,
    size_t bytes_left,
    const char *errmsg,
    struct open_cfw_test_nanopb_varint32_result *output
)
{
    output->value = value;
    output->bytes_left = bytes_left;
    output->callback_offset = input->offset;
    output->consumed = input->offset;
    output->status = status ? 1U : 0U;
    output->calls = input->calls;
    output->error = open_cfw_test_nanopb_error(errmsg);
    output->eof = eof ? 1U : 0U;
}

void open_cfw_test_nanopb_run_production_varint32(
    const uint8_t *bytes,
    size_t size,
    size_t bytes_left,
    uint32_t fail_call,
    uint32_t mutate_call,
    size_t mutated_budget,
    uint32_t preexisting_error,
    uint32_t public_wrapper,
    uint32_t initial_eof,
    uint32_t initial_value,
    struct open_cfw_test_nanopb_varint32_result *output
)
{
    struct open_cfw_test_nanopb_input input = {
        bytes, size, 0U, 0U, fail_call, mutate_call, mutated_budget
    };
    struct open_cfw_nanopb_istream stream = {
        open_cfw_test_nanopb_production_callback,
        &input,
        bytes_left,
        preexisting_error ? open_cfw_test_nanopb_preexisting : (const char *)0
    };
    uint32_t value = initial_value;
    bool eof = initial_eof != 0U;
    bool status;

    if (public_wrapper != 0U) {
        status = open_cfw_nanopb_decode_varint32(&stream, &value);
    } else {
        status = open_cfw_nanopb_decode_varint32_eof(
            &stream, &value, &eof
        );
    }
    open_cfw_test_nanopb_store_result(
        value, status, eof, &input, stream.bytes_left, stream.errmsg, output
    );
}

extern bool open_cfw_test_nanopb_decode_varint32_eof_oracle(
    pb_istream_t *stream,
    uint32_t *destination,
    bool *eof
);

void open_cfw_test_nanopb_run_upstream_varint32(
    const uint8_t *bytes,
    size_t size,
    size_t bytes_left,
    uint32_t fail_call,
    uint32_t mutate_call,
    size_t mutated_budget,
    uint32_t preexisting_error,
    uint32_t public_wrapper,
    uint32_t initial_eof,
    uint32_t initial_value,
    struct open_cfw_test_nanopb_varint32_result *output
)
{
    struct open_cfw_test_nanopb_input input = {
        bytes, size, 0U, 0U, fail_call, mutate_call, mutated_budget
    };
    pb_istream_t stream = {
        open_cfw_test_nanopb_upstream_callback,
        &input,
        bytes_left,
        preexisting_error ? open_cfw_test_nanopb_preexisting : (const char *)0
    };
    uint32_t value = initial_value;
    bool eof = initial_eof != 0U;
    bool status;

    if (public_wrapper != 0U) {
        status = pb_decode_varint32(&stream, &value);
    } else {
        status = open_cfw_test_nanopb_decode_varint32_eof_oracle(
            &stream, &value, &eof
        );
    }
    open_cfw_test_nanopb_store_result(
        value, status, eof, &input, stream.bytes_left, stream.errmsg, output
    );
}

int main(void)
{
    static const uint8_t input[] = {UINT8_C(0x96), UINT8_C(0x01)};
    struct open_cfw_test_nanopb_varint32_result output;

    open_cfw_test_nanopb_run_production_varint32(
        input, sizeof(input), sizeof(input), 0U, 0U, 0U, 0U, 1U, 0U,
        UINT32_C(0xA5A55A5A), &output
    );
    return !(
        output.status == 1U && output.value == UINT32_C(150) &&
        output.calls == 2U && output.consumed == 2U &&
        output.bytes_left == 0U && output.error == 0U
    );
}
