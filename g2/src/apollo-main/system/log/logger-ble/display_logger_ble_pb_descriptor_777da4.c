/* Native nanopb descriptor graph rooted at official Main ROM 0x777da4. */
/* field_info_<addr> / submsg_info_<addr> arrays are named by their own stock
 * ROM address (checked against the stock image); desc_<addr> by the descriptor. */
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
_Static_assert(offsetof(struct pb_msgdesc_candidate, field_count) == 16u,
               "ARM nanopb count offset");

static const struct pb_msgdesc_candidate desc_777d5c;
static const struct pb_msgdesc_candidate desc_777d74;
static const struct pb_msgdesc_candidate desc_777d8c;
static const uint32_t field_info_715afc[] = {
    0x00011205u, 0x00010000u, 0x00011209u, 0x00010001u,
    0x2001320du, 0x00040004u, 0x20013811u, 0x00040004u,
    0x20013715u, 0x00800004u, 0x20013819u, 0x05020004u,
    0x2001381du, 0x00200004u, 0u
};
static const struct pb_msgdesc_candidate *const submsg_info_786210[] = {
    &desc_777d8c, &desc_777d5c, &desc_777d74, 0
};
const struct pb_msgdesc_candidate audio_uart_ble_log_pb_descriptor_777da4 = {
    field_info_715afc, submsg_info_786210, 0, 0, 7u, 0u, 7u
};

static const uint32_t field_info_78abe0[] = { 0x20282705u, 0x00200002u, 0u };
static const uint32_t field_info_78abec[] = { 0x00011705u, 0x00200000u, 0u };
static const uint32_t field_info_78d80c[] = { 0x40001204u, 0u };
/* Stock keeps one NULL-terminated submessage array per descriptor
 * (ROM 0x78f124 / 0x78f128 / 0x78f12c), not a shared one. */
static const struct pb_msgdesc_candidate *const submsg_info_78f124[] = { 0 };
static const struct pb_msgdesc_candidate *const submsg_info_78f128[] = { 0 };
static const struct pb_msgdesc_candidate *const submsg_info_78f12c[] = { 0 };
static const struct pb_msgdesc_candidate desc_777d5c = {
    field_info_78abe0, submsg_info_78f124, 0, 0, 1u, 0u, 1u
};
static const struct pb_msgdesc_candidate desc_777d74 = {
    field_info_78abec, submsg_info_78f128, 0, 0, 1u, 0u, 1u
};
static const struct pb_msgdesc_candidate desc_777d8c = {
    field_info_78d80c, submsg_info_78f12c, 0, 0, 1u, 0u, 1u
};
