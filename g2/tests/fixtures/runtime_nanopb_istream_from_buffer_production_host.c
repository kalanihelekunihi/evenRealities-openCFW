/* Host differential oracle for the production nanopb constructor. */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "components/shared/nanopb/runtime_nanopb_istream_from_buffer.h"
#include "third_party/nanopb/pb_decode.h"

#define CHECK(value) do { if (!(value)) { return __LINE__; } } while (0)

static size_t open_cfw_test_callback_calls;

bool open_cfw_nanopb_stock_buffer_read_identity(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
)
{
    const uint8_t *source = (const uint8_t *)stream->state;
    open_cfw_test_callback_calls++;
    stream->state = (void *)(source + count);
    if (buffer != NULL) {
        memcpy(buffer, source, count);
    }
    return true;
}

int open_cfw_test_nanopb_istream_from_buffer_production(void)
{
    static const uint8_t source[] = {0x10U, 0x22U, 0x34U, 0x48U, 0x5AU};
    uint8_t production_output[3] = {0U, 0U, 0U};
    uint8_t upstream_output[3] = {0U, 0U, 0U};
    struct open_cfw_nanopb_istream production =
        open_cfw_nanopb_istream_from_buffer(
            source,
            sizeof(source)
        );
    pb_istream_t upstream = pb_istream_from_buffer(source, sizeof(source));

    CHECK(production.callback == open_cfw_nanopb_stock_buffer_read_identity);
    CHECK(production.state == source);
    CHECK(production.bytes_left == sizeof(source));
    CHECK(production.errmsg == NULL);
    CHECK(upstream.callback != NULL);
    CHECK(upstream.state == source);
    CHECK(upstream.bytes_left == sizeof(source));
    CHECK(upstream.errmsg == NULL);

    open_cfw_test_callback_calls = 0U;
    CHECK(production.callback(&production, production_output, 3U));
    CHECK(open_cfw_test_callback_calls == 1U);
    CHECK(production.state == source + 3U);
    CHECK(production.bytes_left == sizeof(source));
    CHECK(production.errmsg == NULL);
    CHECK(memcmp(production_output, source, 3U) == 0);

    CHECK(upstream.callback(&upstream, upstream_output, 3U));
    CHECK(upstream.state == source + 3U);
    CHECK(upstream.bytes_left == sizeof(source));
    CHECK(upstream.errmsg == NULL);
    CHECK(memcmp(upstream_output, production_output, 3U) == 0);

    production = open_cfw_nanopb_istream_from_buffer(NULL, 0U);
    CHECK(production.callback == open_cfw_nanopb_stock_buffer_read_identity);
    CHECK(production.state == NULL);
    CHECK(production.bytes_left == 0U);
    CHECK(production.errmsg == NULL);

    return 0;
}
