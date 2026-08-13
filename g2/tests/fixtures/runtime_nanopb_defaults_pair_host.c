#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "runtime_nanopb_defaults_pair.h"

static unsigned int begin_calls;
static unsigned int begin_extension_calls;
static unsigned int next_calls;
static unsigned int decode_tag_calls;
static unsigned int decode_field_calls;
static struct open_cfw_nanopb_field_iter *nested_iter;
static uint32_t encoded_tag;
static bool fail_decode_field;

static void reset_stubs(void)
{
    begin_calls = 0U;
    begin_extension_calls = 0U;
    next_calls = 0U;
    decode_tag_calls = 0U;
    decode_field_calls = 0U;
    nested_iter = NULL;
    encoded_tag = 0U;
    fail_decode_field = false;
}

bool open_cfw_nanopb_field_iter_begin(
    struct open_cfw_nanopb_field_iter *iter,
    const struct open_cfw_nanopb_msgdesc *descriptor,
    void *message
)
{
    (void)descriptor;
    (void)message;
    ++begin_calls;
    if (nested_iter == NULL) {
        return false;
    }
    *iter = *nested_iter;
    return true;
}

bool open_cfw_nanopb_field_iter_begin_extension(
    struct open_cfw_nanopb_field_iter *iter,
    struct open_cfw_nanopb_extension *extension
)
{
    (void)extension;
    ++begin_extension_calls;
    if (nested_iter == NULL) {
        return false;
    }
    *iter = *nested_iter;
    return true;
}

bool open_cfw_nanopb_field_iter_next(
    struct open_cfw_nanopb_field_iter *iter
)
{
    (void)iter;
    ++next_calls;
    return false;
}

struct open_cfw_nanopb_istream open_cfw_nanopb_istream_from_buffer(
    const uint8_t *buffer,
    size_t message_length
)
{
    struct open_cfw_nanopb_istream stream = {
        NULL, (void *)buffer, message_length, NULL
    };
    return stream;
}

bool open_cfw_nanopb_decode_tag(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *wire_type,
    uint32_t *tag,
    bool *eof
)
{
    (void)stream;
    *eof = false;
    *wire_type = 0U;
    ++decode_tag_calls;
    if (decode_tag_calls == 1U) {
        *tag = encoded_tag;
    } else {
        *tag = 0U;
    }
    return true;
}

bool open_cfw_nanopb_decode_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *iter
)
{
    (void)stream;
    (void)wire_type;
    ++decode_field_calls;
    if (fail_decode_field) {
        return false;
    }
    *(uint8_t *)iter->data = 0x5AU;
    return true;
}

static int test_static_optional(void)
{
    uint8_t data[4] = {1U, 2U, 3U, 4U};
    bool present = true;
    struct open_cfw_nanopb_field_iter iter = {0};
    iter.type = 0x10U | 0x02U;
    iter.data = data;
    iter.data_size = sizeof(data);
    iter.size = &present;
    return open_cfw_nanopb_field_set_to_default(&iter)
        && !present
        && memcmp(data, "\0\0\0\0", sizeof(data)) == 0;
}

static int test_static_repeated(void)
{
    uint8_t data[3] = {1U, 2U, 3U};
    uint16_t count = 3U;
    struct open_cfw_nanopb_field_iter iter = {0};
    iter.type = 0x20U | 0x02U;
    iter.data = data;
    iter.data_size = sizeof(data);
    iter.size = &count;
    return open_cfw_nanopb_field_set_to_default(&iter)
        && count == 0U
        && data[0] == 1U && data[1] == 2U && data[2] == 3U;
}

static int test_pointer_repeated(void)
{
    uint8_t value = 7U;
    void *pointer = &value;
    uint16_t count = 9U;
    struct open_cfw_nanopb_field_iter iter = {0};
    iter.type = 0x80U | 0x20U | 0x02U;
    iter.field = &pointer;
    iter.size = &count;
    return open_cfw_nanopb_field_set_to_default(&iter)
        && pointer == NULL && count == 0U;
}

static int test_callback_preserved(void)
{
    uintptr_t callback_state = 0x1234U;
    struct open_cfw_nanopb_field_iter iter = {0};
    iter.type = 0x40U | 0x07U;
    iter.data = &callback_state;
    iter.data_size = sizeof(callback_state);
    return open_cfw_nanopb_field_set_to_default(&iter)
        && callback_state == 0x1234U;
}

static int test_submessage_recursion(void)
{
    static const struct open_cfw_nanopb_msgdesc *submessages[1] = {NULL};
    struct open_cfw_nanopb_msgdesc descriptor = {
        NULL, submessages, NULL, (bool (*)(void))(uintptr_t)1U, 1U, 0U, 1U
    };
    uint8_t nested_data = 0xA5U;
    struct open_cfw_nanopb_field_iter nested = {0};
    struct open_cfw_nanopb_field_iter outer = {0};
    nested.descriptor = &descriptor;
    nested.type = 0x02U;
    nested.data = &nested_data;
    nested.data_size = 1U;
    outer.type = 0x08U;
    outer.data = &nested_data;
    outer.data_size = 1U;
    outer.submessage_descriptor = &descriptor;
    nested_iter = &nested;
    return open_cfw_nanopb_field_set_to_default(&outer)
        && begin_calls == 1U && next_calls == 1U && nested_data == 0U;
}

static int test_extension_recursion(void)
{
    static const struct open_cfw_nanopb_msgdesc *submessages[1] = {NULL};
    struct open_cfw_nanopb_msgdesc descriptor = {
        NULL, submessages, NULL, NULL, 1U, 0U, 1U
    };
    uint8_t nested_data = 0x3CU;
    struct open_cfw_nanopb_field_iter nested = {0};
    struct open_cfw_nanopb_extension extension = {0};
    struct open_cfw_nanopb_extension *extension_pointer = &extension;
    struct open_cfw_nanopb_field_iter outer = {0};
    nested.descriptor = &descriptor;
    nested.type = 0x02U;
    nested.data = &nested_data;
    nested.data_size = 1U;
    extension.found = true;
    outer.type = 0x0AU;
    outer.data = &extension_pointer;
    nested_iter = &nested;
    return open_cfw_nanopb_field_set_to_default(&outer)
        && begin_extension_calls == 1U && next_calls == 1U
        && !extension.found && nested_data == 0U;
}

static int test_message_without_encoded_default(void)
{
    static const struct open_cfw_nanopb_msgdesc *submessages[1] = {NULL};
    struct open_cfw_nanopb_msgdesc descriptor = {
        NULL, submessages, NULL, NULL, 1U, 0U, 1U
    };
    uint8_t data = 0x77U;
    struct open_cfw_nanopb_field_iter iter = {0};
    iter.descriptor = &descriptor;
    iter.type = 0x02U;
    iter.data = &data;
    iter.data_size = 1U;
    return open_cfw_nanopb_message_set_to_defaults(&iter)
        && data == 0U && decode_tag_calls == 0U
        && decode_field_calls == 0U && next_calls == 1U;
}

static int test_message_with_encoded_default(void)
{
    static const uint8_t default_bytes[1] = {0U};
    static const struct open_cfw_nanopb_msgdesc *submessages[1] = {NULL};
    struct open_cfw_nanopb_msgdesc descriptor = {
        NULL, submessages, default_bytes, NULL, 1U, 0U, 7U
    };
    uint8_t data = 0x77U;
    bool present = true;
    struct open_cfw_nanopb_field_iter iter = {0};
    iter.descriptor = &descriptor;
    iter.tag = 7U;
    iter.type = 0x10U | 0x02U;
    iter.data = &data;
    iter.data_size = 1U;
    iter.size = &present;
    encoded_tag = 7U;
    return open_cfw_nanopb_message_set_to_defaults(&iter)
        && data == 0x5AU && !present && decode_tag_calls == 2U
        && decode_field_calls == 1U && next_calls == 1U;
}

static int test_decode_failure(void)
{
    static const uint8_t default_bytes[1] = {0U};
    static const struct open_cfw_nanopb_msgdesc *submessages[1] = {NULL};
    struct open_cfw_nanopb_msgdesc descriptor = {
        NULL, submessages, default_bytes, NULL, 1U, 0U, 3U
    };
    uint8_t data = 1U;
    struct open_cfw_nanopb_field_iter iter = {0};
    iter.descriptor = &descriptor;
    iter.tag = 3U;
    iter.type = 0x02U;
    iter.data = &data;
    iter.data_size = 1U;
    encoded_tag = 3U;
    fail_decode_field = true;
    return !open_cfw_nanopb_message_set_to_defaults(&iter)
        && decode_field_calls == 1U && next_calls == 0U;
}

int main(void)
{
    int ok = 1;
    reset_stubs(); ok &= test_static_optional();
    reset_stubs(); ok &= test_static_repeated();
    reset_stubs(); ok &= test_pointer_repeated();
    reset_stubs(); ok &= test_callback_preserved();
    reset_stubs(); ok &= test_submessage_recursion();
    reset_stubs(); ok &= test_extension_recursion();
    reset_stubs(); ok &= test_message_without_encoded_default();
    reset_stubs(); ok &= test_message_with_encoded_default();
    reset_stubs(); ok &= test_decode_failure();
    return ok ? 0 : 1;
}
