/* Host seam and upstream oracle for the excluded nanopb varint32 wrapper. */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "components/shared/nanopb/runtime_nanopb_decode_varint32_candidate.h"
#include "third_party/nanopb/pb_decode.h"

#define CHECK(value) do { if (!(value)) { return __LINE__; } } while (0)

static bool test_seam_result;
static uint32_t test_seam_value;
static size_t test_seam_calls;
static struct open_cfw_nanopb_istream *test_seam_stream;
static uint32_t *test_seam_destination;
static bool *test_seam_eof;

bool open_cfw_nanopb_decode_varint32_eof_stock_candidate(
    struct open_cfw_nanopb_istream *stream,
    uint32_t *destination,
    bool *eof
)
{
    test_seam_calls++;
    test_seam_stream = stream;
    test_seam_destination = destination;
    test_seam_eof = eof;
    if (test_seam_result) {
        *destination = test_seam_value;
    }
    return test_seam_result;
}

static int check_case(const uint8_t *encoded, size_t encoded_size)
{
    const uint32_t sentinel = 0xA5A55A5AU;
    pb_istream_t upstream_stream = pb_istream_from_buffer(encoded, encoded_size);
    uint32_t upstream_destination = sentinel;
    bool upstream_result = pb_decode_varint32(
        &upstream_stream,
        &upstream_destination
    );
    struct open_cfw_nanopb_istream candidate_stream = {0};
    uint32_t candidate_destination = sentinel;
    bool candidate_result;

    test_seam_result = upstream_result;
    test_seam_value = upstream_destination;
    test_seam_calls = 0U;
    test_seam_stream = NULL;
    test_seam_destination = NULL;
    test_seam_eof = (bool *)(uintptr_t)1U;

    candidate_result = open_cfw_nanopb_decode_varint32_source_candidate(
        &candidate_stream,
        &candidate_destination
    );

    CHECK(candidate_result == upstream_result);
    CHECK(candidate_destination == upstream_destination);
    CHECK(test_seam_calls == 1U);
    CHECK(test_seam_stream == &candidate_stream);
    CHECK(test_seam_destination == &candidate_destination);
    CHECK(test_seam_eof == NULL);
    return 0;
}

int open_cfw_test_nanopb_decode_varint32_candidate(void)
{
    static const uint8_t zero[] = {0x00U};
    static const uint8_t one_byte_max[] = {0x7FU};
    static const uint8_t one_twenty_eight[] = {0x80U, 0x01U};
    static const uint8_t uint32_max[] = {
        0xFFU, 0xFFU, 0xFFU, 0xFFU, 0x0FU
    };
    static const uint8_t truncated[] = {0x80U};
    static const uint8_t overflow[] = {
        0x80U, 0x80U, 0x80U, 0x80U, 0x10U
    };
    int line;

    line = check_case(zero, sizeof(zero));
    CHECK(line == 0);
    line = check_case(one_byte_max, sizeof(one_byte_max));
    CHECK(line == 0);
    line = check_case(one_twenty_eight, sizeof(one_twenty_eight));
    CHECK(line == 0);
    line = check_case(uint32_max, sizeof(uint32_max));
    CHECK(line == 0);
    line = check_case(NULL, 0U);
    CHECK(line == 0);
    line = check_case(truncated, sizeof(truncated));
    CHECK(line == 0);
    line = check_case(overflow, sizeof(overflow));
    CHECK(line == 0);

    return 0;
}
