/* Host-only differential harness for the production nanopb varint leaf. */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "components/shared/nanopb/runtime_nanopb_decode_varint.h"

struct open_cfw_test_nanopb_production_input {
    const uint8_t *bytes;
    size_t size;
    size_t offset;
    uint32_t calls;
    uint32_t fail_call;
};

struct open_cfw_test_nanopb_production_result {
    uint64_t value;
    uint64_t bytes_left;
    uint64_t consumed;
    uint32_t status;
    uint32_t calls;
    uint32_t error;
};

static const char open_cfw_test_nanopb_production_preexisting[] = "preexisting";

static bool open_cfw_test_nanopb_production_callback(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    struct open_cfw_test_nanopb_production_input *input =
        (struct open_cfw_test_nanopb_production_input *)stream->state;

    input->calls++;
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

static uint32_t open_cfw_test_nanopb_production_error(const char *error)
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
    if (strcmp(error, open_cfw_test_nanopb_production_preexisting) == 0) {
        return 4U;
    }
    return 0xFFFFU;
}

void open_cfw_test_nanopb_run_production(
    const uint8_t *bytes,
    size_t size,
    size_t bytes_left,
    uint32_t fail_call,
    uint32_t preexisting_error,
    uint64_t initial_value,
    struct open_cfw_test_nanopb_production_result *output
)
{
    struct open_cfw_test_nanopb_production_input input = {
        bytes, size, 0U, 0U, fail_call
    };
    struct open_cfw_nanopb_istream stream = {
        open_cfw_test_nanopb_production_callback,
        &input,
        bytes_left,
        preexisting_error ?
            open_cfw_test_nanopb_production_preexisting : (const char *)0
    };
    uint64_t value = initial_value;
    bool status = open_cfw_nanopb_decode_varint(&stream, &value);

    output->value = value;
    output->bytes_left = stream.bytes_left;
    output->consumed = input.offset;
    output->status = status ? 1U : 0U;
    output->calls = input.calls;
    output->error = open_cfw_test_nanopb_production_error(stream.errmsg);
}
