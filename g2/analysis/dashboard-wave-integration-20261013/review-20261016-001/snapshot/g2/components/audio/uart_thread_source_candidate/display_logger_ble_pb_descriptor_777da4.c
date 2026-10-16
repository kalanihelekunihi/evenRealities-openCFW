/* Native nanopb descriptor graph rooted at official Main ROM 0x777da4. */
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
static const uint32_t fields_777da4[] = {
    0x00011205u, 0x00010000u, 0x00011209u, 0x00010001u,
    0x2001320du, 0x00040004u, 0x20013811u, 0x00040004u,
    0x20013715u, 0x00800004u, 0x20013819u, 0x05020004u,
    0x2001381du, 0x00200004u, 0u
};
static const struct pb_msgdesc_candidate *const sub_777da4[] = {
    &desc_777d8c, &desc_777d5c, &desc_777d74, 0
};
const struct pb_msgdesc_candidate audio_uart_ble_log_pb_descriptor_777da4 = {
    fields_777da4, sub_777da4, 0, 0, 7u, 0u, 7u
};

static const uint32_t fields_777d5c[] = { 0x20282705u, 0x00200002u, 0u };
static const uint32_t fields_777d74[] = { 0x00011705u, 0x00200000u, 0u };
static const uint32_t fields_777d8c[] = { 0x40001204u, 0u };
static const struct pb_msgdesc_candidate *const empty_submsg[] = { 0 };
static const struct pb_msgdesc_candidate desc_777d5c = {
    fields_777d5c, empty_submsg, 0, 0, 1u, 0u, 1u
};
static const struct pb_msgdesc_candidate desc_777d74 = {
    fields_777d74, empty_submsg, 0, 0, 1u, 0u, 1u
};
static const struct pb_msgdesc_candidate desc_777d8c = {
    fields_777d8c, empty_submsg, 0, 0, 1u, 0u, 1u
};
