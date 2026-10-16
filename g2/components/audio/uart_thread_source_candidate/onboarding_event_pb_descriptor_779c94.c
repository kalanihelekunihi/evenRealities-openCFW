/* Stock nanopb descriptor graph rooted at Apollo ROM 0x779c94. */
#include <stddef.h>
#include <stdint.h>

struct onboarding_pb_msgdesc {
    const uint32_t *field_info;
    const struct onboarding_pb_msgdesc *const *submsg_info;
    const uint8_t *default_value;
    void *field_callback;
    uint16_t field_count, required_field_count, largest_tag;
};
_Static_assert(sizeof(struct onboarding_pb_msgdesc) == 24u, "ARM nanopb descriptor ABI");
_Static_assert(offsetof(struct onboarding_pb_msgdesc, field_count) == 16u,
               "ARM nanopb descriptor counts offset");

static const struct onboarding_pb_msgdesc node_779cac;
static const struct onboarding_pb_msgdesc node_779cc4;
static const struct onboarding_pb_msgdesc node_779cdc;
static const uint32_t fields_7572c0[] = {
    0x10001204u, 0x10011208u, 0x2001380du, 0x00020004u,
    0x20013811u, 0x00010004u, 0x20013815u, 0x000c0004u, 0u
};
static const struct onboarding_pb_msgdesc *const sub_787b70[] = {
    &node_779cac, &node_779cc4, &node_779cdc, 0
};
const struct onboarding_pb_msgdesc audio_onboarding_event_descriptor_779c94 = {
    fields_7572c0, sub_787b70, 0, 0, 5u, 0u, 5u
};
static const uint32_t fields_78b63c[] = {0x10001204u, 0x10011208u, 0u};
static const uint32_t fields_78de3c[] = {0x10001204u, 0u};
static const uint32_t fields_787b80[] = {
    0x10001204u, 0x40041208u, 0x1008120cu, 0u
};
static const struct onboarding_pb_msgdesc *const empty_78f324[] = {0};
static const struct onboarding_pb_msgdesc *const empty_78f328[] = {0};
static const struct onboarding_pb_msgdesc *const empty_78f32c[] = {0};
static const struct onboarding_pb_msgdesc node_779cac = {
    fields_78b63c, empty_78f324, 0, 0, 2u, 0u, 2u
};
static const struct onboarding_pb_msgdesc node_779cc4 = {
    fields_78de3c, empty_78f328, 0, 0, 1u, 0u, 1u
};
static const struct onboarding_pb_msgdesc node_779cdc = {
    fields_787b80, empty_78f32c, 0, 0, 3u, 0u, 3u
};
