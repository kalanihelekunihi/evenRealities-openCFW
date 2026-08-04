/*
 * Test-only access to nanopb's file-static EOF-aware decoder. The pristine
 * implementation is included once; this fixture does not paste or alter it.
 */

#include <stdbool.h>
#include <stdint.h>

#include "third_party/nanopb/pb_decode.c"

bool open_cfw_test_nanopb_decode_varint32_eof_oracle(
    pb_istream_t *stream,
    uint32_t *destination,
    bool *eof
)
{
    return pb_decode_varint32_eof(stream, destination, eof);
}

int open_cfw_test_nanopb_decode_varint32_oracle_abi(void)
{
    pb_istream_t stream = {0};
    uint32_t destination = UINT32_C(0xA5A55A5A);
    bool eof = false;
    bool (*oracle_abi)(pb_istream_t *, uint32_t *, bool *) =
        open_cfw_test_nanopb_decode_varint32_eof_oracle;

    if (oracle_abi(&stream, &destination, &eof)) {
        return __LINE__;
    }
    if (!eof || destination != UINT32_C(0xA5A55A5A)) {
        return __LINE__;
    }
    if (stream.bytes_left != 0U || stream.errmsg == NULL) {
        return __LINE__;
    }
    return 0;
}
