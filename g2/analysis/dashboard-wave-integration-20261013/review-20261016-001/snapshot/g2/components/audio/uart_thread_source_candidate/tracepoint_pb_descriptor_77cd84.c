/* Stock Apollo tracepoint nanopb descriptor graph rooted at ROM 0x77cd84. */
#include <stddef.h>
#include <stdint.h>
struct tracepoint_pb_msgdesc {
    const uint32_t *field_info;
    const struct tracepoint_pb_msgdesc *const *submsg_info;
    const uint8_t *default_value;
    void *field_callback;
    uint16_t field_count, required_field_count, largest_tag;
};
_Static_assert(sizeof(struct tracepoint_pb_msgdesc) == 24u,
               "ARM nanopb message descriptor ABI");
_Static_assert(offsetof(struct tracepoint_pb_msgdesc, field_count) == 16u,
               "ARM nanopb descriptor counts offset");

static const struct tracepoint_pb_msgdesc desc_77cd3c;
static const struct tracepoint_pb_msgdesc desc_77cd54;
static const struct tracepoint_pb_msgdesc desc_77cd6c;
static const uint32_t fields_7457d0[] = {
    0x00011205u, 0x00010000u, 0x00011209u, 0x00010001u,
    0x2001380du, 0x02020004u, 0x20013811u, 0x00200004u,
    0x20013815u, 0x00010004u, 0u
};
static const struct tracepoint_pb_msgdesc *const sub_789c20[] = {
    &desc_77cd3c, &desc_77cd54, &desc_77cd6c, 0
};
const struct tracepoint_pb_msgdesc audio_tracepoint_message_descriptor = {
    fields_7457d0, sub_789c20, 0, 0, 5u, 0u, 5u
};

static const uint32_t fields_78c74c[] = {0x20102705u, 0x00200002u, 0u};
static const uint32_t fields_78c758[] = {0x00011705u, 0x00200000u, 0u};
static const uint32_t fields_78ec04[] = {0x10001204u, 0u};
static const struct tracepoint_pb_msgdesc *const empty_78f4cc[] = {0};
static const struct tracepoint_pb_msgdesc *const empty_78f4d0[] = {0};
static const struct tracepoint_pb_msgdesc *const empty_78f4d4[] = {0};
static const struct tracepoint_pb_msgdesc desc_77cd3c = {
    fields_78c74c, empty_78f4cc, 0, 0, 1u, 0u, 1u
};
static const struct tracepoint_pb_msgdesc desc_77cd54 = {
    fields_78c758, empty_78f4d0, 0, 0, 1u, 0u, 1u
};
static const struct tracepoint_pb_msgdesc desc_77cd6c = {
    fields_78ec04, empty_78f4d4, 0, 0, 1u, 0u, 1u
};
