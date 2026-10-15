/* QuickList nanopb descriptor graph rooted at native ROM 0x77b02c.
 * Field words and graph edges are from official Apollo s200 2.2.6.10. */
#include <stddef.h>
#include <stdint.h>

struct pb_msgdesc_candidate {
    const uint32_t *field_info;
    const struct pb_msgdesc_candidate *const *submsg_info;
    const uint8_t *default_value;
    void *field_callback;
    uint16_t field_count, required_field_count, largest_tag;
};
_Static_assert(sizeof(struct pb_msgdesc_candidate) == 24u, "ARM nanopb descriptor ABI");
_Static_assert(offsetof(struct pb_msgdesc_candidate, field_count) == 16u, "ARM field count offset");

static const struct pb_msgdesc_candidate quicklist_item_77b044;
static const struct pb_msgdesc_candidate quicklist_many_77b05c;
static const struct pb_msgdesc_candidate quicklist_event_77b074;

static const uint32_t quicklist_root_fields_6e98a4[] = {
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000001u,
    0x0001120au, 0x00000000u, 0x00000001u, 0x00000001u,
    0x0001380eu, 0x00000006u, 0x00000008u, 0x000000e8u,
    0x00013812u, 0x00000006u, 0x00000008u, 0x00001230u,
    0x00013816u, 0x00000006u, 0x00000008u, 0x0000000cu,
    0u
};
static const struct pb_msgdesc_candidate *const quicklist_root_submsgs_7885d0[] = {
    &quicklist_item_77b044, &quicklist_many_77b05c, &quicklist_event_77b074, 0
};
const struct pb_msgdesc_candidate audio_quicklist_pb_descriptor = {
    quicklist_root_fields_6e98a4, quicklist_root_submsgs_7885d0, 0, 0, 5u, 0u, 5u
};

static const uint32_t quicklist_item_fields_758e2c[] = {
    0x40001204u, 0x40041208u, 0x4008120cu, 0x80101110u,
    0x00011615u, 0x00cc0018u, 0x10e41218u, 0x10e5121cu, 0u
};
static const struct pb_msgdesc_candidate *const quicklist_item_submsgs_78f3a8[] = {0};
static const struct pb_msgdesc_candidate quicklist_item_77b044 = {
    quicklist_item_fields_758e2c, quicklist_item_submsgs_78f3a8, 0, 0, 7u, 0u, 7u
};

static const uint32_t quicklist_many_fields_704f84[] = {
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000001u,
    0x0001120au, 0x00000000u, 0x00000001u, 0x00000001u,
    0x0014280eu, 0x00000006u, 0x00000008u, 0x000000e8u,
    0x00011212u, 0x00000000u, 0x00001228u, 0x00000001u,
    0u
};
static const struct pb_msgdesc_candidate *const quicklist_many_submsgs_78e454[] = {
    &quicklist_item_77b044, 0
};
static const struct pb_msgdesc_candidate quicklist_many_77b05c = {
    quicklist_many_fields_704f84, quicklist_many_submsgs_78e454, 0, 0, 4u, 0u, 4u
};

static const uint32_t quicklist_event_fields_7885e0[] = {
    0x10001204u, 0x40041208u, 0x1008120cu, 0u
};
static const struct pb_msgdesc_candidate *const quicklist_event_submsgs_78f3ac[] = {0};
static const struct pb_msgdesc_candidate quicklist_event_77b074 = {
    quicklist_event_fields_7885e0, quicklist_event_submsgs_78f3ac, 0, 0, 3u, 0u, 3u
};
