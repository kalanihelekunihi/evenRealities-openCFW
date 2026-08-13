#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "runtime_nanopb_field_decoder_cluster.h"

enum {
    CALL_NONE,
    CALL_BOOL,
    CALL_VARINT,
    CALL_FIXED32,
    CALL_FIXED64,
    CALL_BYTES,
    CALL_STRING,
    CALL_SUBMESSAGE
};

static unsigned int called;
static unsigned int callback_calls;
static unsigned int skip_calls;
static unsigned int defaults_calls;
static unsigned int iterator_calls;
static unsigned int callback_mode;
static uint32_t decoded_size;
static uint8_t read_source[32];
static struct open_cfw_nanopb_istream stream;
static struct open_cfw_nanopb_field_iter field;
static struct open_cfw_nanopb_msgdesc descriptor;
static struct open_cfw_nanopb_msgdesc submessage_descriptor;
static uint8_t storage[32];
static uint16_t field_size;

static bool consume_one(struct open_cfw_nanopb_istream *value, unsigned int id)
{
    called = id;
    if (value->bytes_left != 0U) {
        --value->bytes_left;
    }
    return true;
}

bool open_cfw_nanopb_dec_bool(
    struct open_cfw_nanopb_istream *value,
    const struct open_cfw_nanopb_field_iter *unused
)
{
    (void)unused;
    return consume_one(value, CALL_BOOL);
}

bool open_cfw_nanopb_dec_varint(
    struct open_cfw_nanopb_istream *value,
    const struct open_cfw_nanopb_field_iter *unused
)
{
    (void)unused;
    return consume_one(value, CALL_VARINT);
}

bool open_cfw_nanopb_decode_fixed32(
    struct open_cfw_nanopb_istream *value,
    void *unused
)
{
    (void)unused;
    return consume_one(value, CALL_FIXED32);
}

bool open_cfw_nanopb_decode_fixed64(
    struct open_cfw_nanopb_istream *value,
    void *unused
)
{
    (void)unused;
    return consume_one(value, CALL_FIXED64);
}

bool open_cfw_nanopb_dec_bytes(
    struct open_cfw_nanopb_istream *value,
    const struct open_cfw_nanopb_field_iter *unused
)
{
    (void)unused;
    return consume_one(value, CALL_BYTES);
}

bool open_cfw_nanopb_dec_string(
    struct open_cfw_nanopb_istream *value,
    const struct open_cfw_nanopb_field_iter *unused
)
{
    (void)unused;
    return consume_one(value, CALL_STRING);
}

bool open_cfw_nanopb_dec_submessage(
    struct open_cfw_nanopb_istream *value,
    const struct open_cfw_nanopb_field_iter *unused
)
{
    (void)unused;
    return consume_one(value, CALL_SUBMESSAGE);
}

bool open_cfw_nanopb_make_string_substream(
    struct open_cfw_nanopb_istream *parent,
    struct open_cfw_nanopb_istream *substream
)
{
    *substream = *parent;
    parent->bytes_left = 0U;
    return true;
}

bool open_cfw_nanopb_close_string_substream(
    struct open_cfw_nanopb_istream *parent,
    struct open_cfw_nanopb_istream *substream
)
{
    substream->bytes_left = 0U;
    parent->state = substream->state;
    if (parent->errmsg == NULL) {
        parent->errmsg = substream->errmsg;
    }
    return true;
}

bool open_cfw_nanopb_field_iter_begin(
    struct open_cfw_nanopb_field_iter *iter,
    const struct open_cfw_nanopb_msgdesc *fields,
    void *destination
)
{
    ++iterator_calls;
    memset(iter, 0, sizeof(*iter));
    iter->descriptor = fields;
    iter->message = destination;
    return true;
}

bool open_cfw_nanopb_message_set_to_defaults(
    struct open_cfw_nanopb_field_iter *unused
)
{
    (void)unused;
    ++defaults_calls;
    return callback_mode != 5U;
}

bool open_cfw_nanopb_skip_field(
    struct open_cfw_nanopb_istream *value,
    uint8_t wire_type
)
{
    (void)wire_type;
    ++skip_calls;
    value->bytes_left = 0U;
    return true;
}

bool open_cfw_nanopb_read_raw_value(
    struct open_cfw_nanopb_istream *value,
    uint8_t wire_type,
    uint8_t *buffer,
    size_t *size
)
{
    (void)wire_type;
    if (*size == 0U) {
        return false;
    }
    buffer[0] = 0x2AU;
    *size = 1U;
    if (value->bytes_left != 0U) {
        --value->bytes_left;
    }
    return true;
}

struct open_cfw_nanopb_istream open_cfw_nanopb_istream_from_buffer(
    const uint8_t *buffer,
    size_t message_length
)
{
    struct open_cfw_nanopb_istream result = {
        NULL, (void *)buffer, message_length, NULL
    };
    return result;
}

bool open_cfw_nanopb_decode_varint32(
    struct open_cfw_nanopb_istream *value,
    uint32_t *destination
)
{
    (void)value;
    *destination = decoded_size;
    return true;
}

bool open_cfw_nanopb_read(
    struct open_cfw_nanopb_istream *value,
    uint8_t *destination,
    size_t count
)
{
    if (value->bytes_left < count) {
        return false;
    }
    if (destination != NULL) {
        memcpy(destination, read_source, count);
    }
    value->bytes_left -= count;
    return true;
}

static bool dynamic_callback(
    struct open_cfw_nanopb_istream *value,
    void *ostream,
    const struct open_cfw_nanopb_field_iter *unused
)
{
    (void)ostream;
    (void)unused;
    ++callback_calls;
    if (callback_mode == 2U) {
        value->errmsg = "callback detail";
        return false;
    }
    if (callback_mode == 3U) {
        return false;
    }
    if (callback_mode != 4U && value->bytes_left != 0U) {
        --value->bytes_left;
    }
    return true;
}

static bool (*generic_dynamic_callback(void))(void)
{
    union {
        bool (*generic)(void);
        bool (*callback)(
            struct open_cfw_nanopb_istream *,
            void *,
            const struct open_cfw_nanopb_field_iter *
        );
    } conversion;
    conversion.callback = dynamic_callback;
    return conversion.generic;
}

void open_cfw_test_reset(void)
{
    unsigned int index;
    memset(&stream, 0, sizeof(stream));
    memset(&field, 0, sizeof(field));
    memset(&descriptor, 0, sizeof(descriptor));
    memset(&submessage_descriptor, 0, sizeof(submessage_descriptor));
    memset(storage, 0xA5, sizeof(storage));
    for (index = 0U; index < sizeof(read_source); ++index) {
        read_source[index] = (uint8_t)(index + 1U);
    }
    field.descriptor = &descriptor;
    field.field = storage;
    field.data = storage;
    field.size = &field_size;
    field.data_size = 1U;
    field.array_size = 4U;
    field.tag = 7U;
    field_size = 0U;
    called = CALL_NONE;
    callback_calls = 0U;
    skip_calls = 0U;
    defaults_calls = 0U;
    iterator_calls = 0U;
    callback_mode = 0U;
    decoded_size = 0U;
}

bool open_cfw_test_basic(unsigned int logical_type, unsigned int wire_type)
{
    field.type = (uint8_t)logical_type;
    stream.bytes_left = 16U;
    return open_cfw_nanopb_decode_basic_field(&stream, wire_type, &field);
}

bool open_cfw_test_static_optional(void)
{
    bool present = false;
    field.type = 0x10U;
    field.size = &present;
    stream.bytes_left = 1U;
    if (!open_cfw_nanopb_decode_static_field(&stream, 0U, &field)) {
        return false;
    }
    return present;
}

bool open_cfw_test_static_packed(unsigned int entries, unsigned int capacity)
{
    field.type = 0x20U;
    field.array_size = (uint16_t)capacity;
    field.data_size = 1U;
    field_size = 0U;
    stream.bytes_left = entries;
    return open_cfw_nanopb_decode_static_field(&stream, 2U, &field);
}

bool open_cfw_test_static_repeated(unsigned int initial, unsigned int capacity)
{
    field.type = 0x20U;
    field.array_size = (uint16_t)capacity;
    field.data_size = 1U;
    field_size = (uint16_t)initial;
    stream.bytes_left = 1U;
    return open_cfw_nanopb_decode_static_field(&stream, 0U, &field);
}

bool open_cfw_test_static_oneof(unsigned int mode)
{
    static const uint8_t default_value[] = {0U};
    static const struct open_cfw_nanopb_msgdesc *submessages[] = {NULL};
    callback_mode = mode;
    submessage_descriptor.default_value = default_value;
    submessage_descriptor.submessage_info = submessages;
    field.type = 0x38U;
    field.data_size = 4U;
    field.submessage_descriptor = &submessage_descriptor;
    field_size = 1U;
    stream.bytes_left = 1U;
    return open_cfw_nanopb_decode_static_field(&stream, 2U, &field);
}

bool open_cfw_test_pointer(void)
{
    return open_cfw_nanopb_decode_pointer_field(&stream, 0U, &field);
}

bool open_cfw_test_callback(unsigned int mode, unsigned int wire_type)
{
    callback_mode = mode;
    stream.bytes_left = wire_type == 2U ? 3U : 1U;
    descriptor.field_callback = mode == 0U
        ? NULL : generic_dynamic_callback();
    return open_cfw_nanopb_decode_callback_field(
        &stream, wire_type, &field);
}

bool open_cfw_test_fixed_length(unsigned int size, unsigned int data_size)
{
    decoded_size = size;
    field.data_size = (uint16_t)data_size;
    stream.bytes_left = sizeof(read_source);
    return open_cfw_nanopb_dec_fixed_length_bytes(&stream, &field);
}

unsigned int open_cfw_test_called(void) { return called; }
unsigned int open_cfw_test_callback_calls(void) { return callback_calls; }
unsigned int open_cfw_test_skip_calls(void) { return skip_calls; }
unsigned int open_cfw_test_defaults_calls(void) { return defaults_calls; }
unsigned int open_cfw_test_iterator_calls(void) { return iterator_calls; }
unsigned int open_cfw_test_field_size(void) { return field_size; }
unsigned int open_cfw_test_stream_left(void) { return (unsigned int)stream.bytes_left; }
const char *open_cfw_test_error(void) { return stream.errmsg; }
const uint8_t *open_cfw_test_storage(void) { return storage; }
