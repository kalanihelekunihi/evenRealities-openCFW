#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "runtime_nanopb_dispatch_extension.h"

static unsigned int static_calls;
static unsigned int pointer_calls;
static unsigned int callback_calls;
static unsigned int iterator_calls;
static unsigned int dynamic_calls;
static bool helper_result;
static bool iterator_result;
static bool dynamic_result;
static bool consume_dynamic;
static struct open_cfw_nanopb_field_iter iterator_value;

bool open_cfw_nanopb_decode_static_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
)
{
    (void)stream;
    (void)wire_type;
    (void)field;
    ++static_calls;
    return helper_result;
}

bool open_cfw_nanopb_decode_pointer_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
)
{
    (void)stream;
    (void)wire_type;
    (void)field;
    ++pointer_calls;
    return helper_result;
}

bool open_cfw_nanopb_decode_callback_field(
    struct open_cfw_nanopb_istream *stream,
    unsigned int wire_type,
    struct open_cfw_nanopb_field_iter *field
)
{
    (void)stream;
    (void)wire_type;
    (void)field;
    ++callback_calls;
    return helper_result;
}

bool open_cfw_nanopb_field_iter_begin_extension(
    struct open_cfw_nanopb_field_iter *iter,
    struct open_cfw_nanopb_extension *extension
)
{
    (void)extension;
    ++iterator_calls;
    *iter = iterator_value;
    return iterator_result;
}

static bool dynamic_decode(
    struct open_cfw_nanopb_istream *stream,
    struct open_cfw_nanopb_extension *extension,
    uint32_t tag,
    uint8_t wire_type
)
{
    (void)extension;
    (void)tag;
    (void)wire_type;
    ++dynamic_calls;
    if (consume_dynamic) {
        --stream->bytes_left;
    }
    return dynamic_result;
}

static void reset_state(void)
{
    static_calls = 0U;
    pointer_calls = 0U;
    callback_calls = 0U;
    iterator_calls = 0U;
    dynamic_calls = 0U;
    helper_result = true;
    iterator_result = true;
    dynamic_result = true;
    consume_dynamic = false;
    memset(&iterator_value, 0, sizeof(iterator_value));
}

static bool test_field_dispatch(void)
{
    struct open_cfw_nanopb_istream stream = {NULL, NULL, 7U, NULL};
    struct open_cfw_nanopb_field_iter field;
    memset(&field, 0, sizeof(field));
    reset_state();
    field.type = 0x00U;
    if (!open_cfw_nanopb_decode_field(&stream, 2U, &field)
        || static_calls != 1U) {
        return false;
    }
    field.type = 0x80U;
    if (!open_cfw_nanopb_decode_field(&stream, 2U, &field)
        || pointer_calls != 1U) {
        return false;
    }
    field.type = 0x40U;
    if (!open_cfw_nanopb_decode_field(&stream, 2U, &field)
        || callback_calls != 1U) {
        return false;
    }
    field.type = 0xC0U;
    if (open_cfw_nanopb_decode_field(&stream, 2U, &field)
        || strcmp(stream.errmsg, "invalid field type") != 0) {
        return false;
    }
    stream.errmsg = "sticky";
    return !open_cfw_nanopb_decode_field(&stream, 2U, &field)
        && strcmp(stream.errmsg, "sticky") == 0;
}

static bool test_default_extension(void)
{
    struct open_cfw_nanopb_istream stream = {NULL, NULL, 7U, NULL};
    struct open_cfw_nanopb_extension extension;
    struct open_cfw_nanopb_msgdesc descriptor;
    memset(&extension, 0, sizeof(extension));
    memset(&descriptor, 0, sizeof(descriptor));
    reset_state();
    iterator_result = false;
    if (open_cfw_nanopb_default_extension_decoder(
            &stream, &extension, 9U, 2U)
        || strcmp(stream.errmsg, "invalid extension") != 0) {
        return false;
    }
    reset_state();
    iterator_value.tag = 8U;
    if (!open_cfw_nanopb_default_extension_decoder(
            &stream, &extension, 9U, 2U)
        || extension.found || static_calls != 0U) {
        return false;
    }
    iterator_value.tag = 9U;
    iterator_value.descriptor = &descriptor;
    iterator_value.type = 0x00U;
    return open_cfw_nanopb_default_extension_decoder(
            &stream, &extension, 9U, 2U)
        && extension.found && static_calls == 1U;
}

static bool test_extension_chain(void)
{
    struct open_cfw_nanopb_istream stream = {NULL, NULL, 7U, NULL};
    struct open_cfw_nanopb_extension_type dynamic_type = {
        dynamic_decode, NULL, NULL
    };
    struct open_cfw_nanopb_extension first;
    struct open_cfw_nanopb_extension second;
    memset(&first, 0, sizeof(first));
    memset(&second, 0, sizeof(second));
    reset_state();
    first.type = &dynamic_type;
    first.next = &second;
    second.type = &dynamic_type;
    if (!open_cfw_nanopb_decode_extension(&stream, 9U, 2U, &first)
        || dynamic_calls != 2U) {
        return false;
    }
    reset_state();
    consume_dynamic = true;
    if (!open_cfw_nanopb_decode_extension(&stream, 9U, 2U, &first)
        || dynamic_calls != 1U || stream.bytes_left != 6U) {
        return false;
    }
    reset_state();
    dynamic_result = false;
    return !open_cfw_nanopb_decode_extension(&stream, 9U, 2U, &first)
        && dynamic_calls == 1U;
}

int main(void)
{
    return test_field_dispatch()
        && test_default_extension()
        && test_extension_chain() ? 0 : 1;
}
