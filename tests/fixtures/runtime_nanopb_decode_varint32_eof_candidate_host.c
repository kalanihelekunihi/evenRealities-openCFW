/* Host differential oracle for the excluded nanopb varint32 EOF decoder. */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "components/shared/nanopb/runtime_nanopb_decode_varint32_eof_candidate.h"
#include "third_party/nanopb/pb_decode.h"

#define CHECK(value) do { if (!(value)) { return __LINE__; } } while (0)

struct candidate_input {
    const uint8_t *data;
    size_t position;
    bool force_failure;
    size_t calls;
};

static const char candidate_end_of_stream[] = "end-of-stream";
static const char candidate_io_error[] = "io error";

bool open_cfw_nanopb_readbyte(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *byte
)
{
    struct candidate_input *input = (struct candidate_input *)stream->state;
    input->calls++;

    if (stream->bytes_left == 0U) {
        if (stream->errmsg == NULL) {
            stream->errmsg = candidate_end_of_stream;
        }
        return false;
    }
    if (input->force_failure) {
        if (stream->errmsg == NULL) {
            stream->errmsg = candidate_io_error;
        }
        return false;
    }

    *byte = input->data[input->position++];
    stream->bytes_left--;
    return true;
}

static bool same_error(const char *left, const char *right)
{
    if (left == NULL || right == NULL) {
        return left == right;
    }
    return strcmp(left, right) == 0;
}

static int check_value_case(const uint8_t *encoded, size_t encoded_size)
{
    const uint32_t sentinel = 0xA5A55A5AU;
    pb_istream_t upstream_stream = pb_istream_from_buffer(encoded, encoded_size);
    uint32_t upstream_destination = sentinel;
    bool upstream_result = pb_decode_varint32(
        &upstream_stream,
        &upstream_destination
    );
    struct candidate_input input = {encoded, 0U, false, 0U};
    struct open_cfw_nanopb_istream candidate_stream = {
        NULL,
        &input,
        encoded_size,
        NULL
    };
    uint32_t candidate_destination = sentinel;
    bool candidate_result =
        open_cfw_nanopb_decode_varint32_eof_source_candidate(
            &candidate_stream,
            &candidate_destination,
            NULL
        );

    CHECK(candidate_result == upstream_result);
    CHECK(candidate_destination == upstream_destination);
    CHECK(candidate_stream.bytes_left == upstream_stream.bytes_left);
    CHECK(input.position == encoded_size - candidate_stream.bytes_left);
    CHECK(input.calls >= input.position);
    CHECK(same_error(candidate_stream.errmsg, upstream_stream.errmsg));
    return 0;
}

static bool upstream_forced_failure(
    pb_istream_t *stream,
    pb_byte_t *buffer,
    size_t count
)
{
    (void)stream;
    (void)buffer;
    (void)count;
    return false;
}

static int check_optional_eof_semantics(void)
{
    struct candidate_input input = {NULL, 0U, false, 0U};
    struct open_cfw_nanopb_istream candidate = {NULL, &input, 0U, NULL};
    uint32_t candidate_destination = 0xA5A55A5AU;
    bool candidate_eof = false;
    pb_istream_t upstream = pb_istream_from_buffer(NULL, 0U);
    pb_wire_type_t wire_type = PB_WT_VARINT;
    uint32_t tag = 123U;
    bool upstream_eof = false;

    CHECK(!open_cfw_nanopb_decode_varint32_eof_source_candidate(
        &candidate,
        &candidate_destination,
        &candidate_eof
    ));
    CHECK(!pb_decode_tag(&upstream, &wire_type, &tag, &upstream_eof));
    CHECK(candidate_eof);
    CHECK(upstream_eof);
    CHECK(candidate_destination == 0xA5A55A5AU);
    CHECK(same_error(candidate.errmsg, upstream.errmsg));

    {
        static const uint8_t truncated[] = {0x80U};
        struct candidate_input truncated_input = {
            truncated,
            0U,
            false,
            0U
        };
        struct open_cfw_nanopb_istream truncated_candidate = {
            NULL,
            &truncated_input,
            sizeof(truncated),
            NULL
        };
        bool truncated_eof = false;

        CHECK(!open_cfw_nanopb_decode_varint32_eof_source_candidate(
            &truncated_candidate,
            &candidate_destination,
            &truncated_eof
        ));
        CHECK(!truncated_eof);
    }

    {
        static const uint8_t valid[] = {0x01U};
        struct candidate_input valid_input = {valid, 0U, false, 0U};
        struct open_cfw_nanopb_istream valid_candidate = {
            NULL,
            &valid_input,
            sizeof(valid),
            NULL
        };
        bool untouched_eof = true;

        CHECK(open_cfw_nanopb_decode_varint32_eof_source_candidate(
            &valid_candidate,
            &candidate_destination,
            &untouched_eof
        ));
        CHECK(untouched_eof);
    }

    {
        static const uint8_t unread[] = {0x01U};
        struct candidate_input failed_input = {unread, 0U, true, 0U};
        struct open_cfw_nanopb_istream failed_candidate = {
            NULL,
            &failed_input,
            sizeof(unread),
            NULL
        };
        pb_istream_t failed_upstream = {
            upstream_forced_failure,
            NULL,
            sizeof(unread),
            NULL
        };
        bool failed_candidate_eof = true;
        bool failed_upstream_eof = true;

        CHECK(!open_cfw_nanopb_decode_varint32_eof_source_candidate(
            &failed_candidate,
            &candidate_destination,
            &failed_candidate_eof
        ));
        CHECK(!pb_decode_tag(
            &failed_upstream,
            &wire_type,
            &tag,
            &failed_upstream_eof
        ));
        CHECK(failed_candidate_eof);
        CHECK(!failed_upstream_eof);
        CHECK(failed_candidate.bytes_left == failed_upstream.bytes_left);
        CHECK(same_error(failed_candidate.errmsg, failed_upstream.errmsg));
    }

    return 0;
}

int open_cfw_test_nanopb_decode_varint32_eof_candidate(void)
{
    static const uint8_t zero[] = {0x00U};
    static const uint8_t one_byte_max[] = {0x7FU};
    static const uint8_t one_twenty_eight[] = {0x80U, 0x01U};
    static const uint8_t uint32_max[] = {
        0xFFU, 0xFFU, 0xFFU, 0xFFU, 0x0FU
    };
    static const uint8_t negative_extension[] = {
        0xFFU, 0xFFU, 0xFFU, 0xFFU, 0xFFU,
        0xFFU, 0xFFU, 0xFFU, 0xFFU, 0x01U
    };
    static const uint8_t truncated[] = {0x80U};
    static const uint8_t overflow_32[] = {
        0x80U, 0x80U, 0x80U, 0x80U, 0x10U
    };
    static const uint8_t overflow_64[] = {
        0x80U, 0x80U, 0x80U, 0x80U, 0x80U,
        0x80U, 0x80U, 0x80U, 0x80U, 0x80U, 0x00U
    };
    int line;

    line = check_value_case(zero, sizeof(zero));
    CHECK(line == 0);
    line = check_value_case(one_byte_max, sizeof(one_byte_max));
    CHECK(line == 0);
    line = check_value_case(one_twenty_eight, sizeof(one_twenty_eight));
    CHECK(line == 0);
    line = check_value_case(uint32_max, sizeof(uint32_max));
    CHECK(line == 0);
    line = check_value_case(negative_extension, sizeof(negative_extension));
    CHECK(line == 0);
    line = check_value_case(NULL, 0U);
    CHECK(line == 0);
    line = check_value_case(truncated, sizeof(truncated));
    CHECK(line == 0);
    line = check_value_case(overflow_32, sizeof(overflow_32));
    CHECK(line == 0);
    line = check_value_case(overflow_64, sizeof(overflow_64));
    CHECK(line == 0);
    line = check_optional_eof_semantics();
    CHECK(line == 0);

    return 0;
}
