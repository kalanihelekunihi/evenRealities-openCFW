/* Generated from authenticated Main 0x775b24 nanopb descriptor graph.
 * Regenerate with extract_main_conversate_descriptor_775b24_20261016.py.
 */
#include <stddef.h>
#include <stdint.h>
struct pb_msgdesc_candidate {
    const uint32_t *field_info;
    const struct pb_msgdesc_candidate *const *submsg_info;
    const uint8_t *default_value;
    void *field_callback;
    uint16_t field_count, required_field_count, largest_tag;
};
_Static_assert(sizeof(struct pb_msgdesc_candidate) == 24u,
               "ARM nanopb descriptor ABI");
_Static_assert(offsetof(struct pb_msgdesc_candidate, field_count) == 16u,
               "ARM nanopb field count offset");

extern const struct pb_msgdesc_candidate audio_conversate_response_descriptor_775b24;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775b54;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775b6c;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775b84;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775b9c;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775bb4;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775bcc;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775be4;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775bfc;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775c14;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775c2c;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775c44;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775c5c;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775c74;
extern const struct pb_msgdesc_candidate audio_conversate_descriptor_775c8c;

const uint32_t audio_conversate_fields_775b24[26] = {
    0x00011205u, 0x00010000u, 0x00011209u, 0x00010001u,
    0x2001380du, 0x00940004u, 0x20013811u, 0x00010004u,
    0x20013815u, 0x0aa80004u, 0x20013819u, 0x00080004u,
    0x2001381du, 0x048c0004u, 0x20013821u, 0x04080004u,
    0x20013825u, 0x00020004u, 0x20013829u, 0x00010004u,
    0x2001382du, 0x00010004u, 0x20013831u, 0x000c0004u,
    0x20013835u, 0x0fa80004u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775b24[12] = {
    &audio_conversate_descriptor_775bfc,
    &audio_conversate_descriptor_775b9c,
    &audio_conversate_descriptor_775b84,
    &audio_conversate_descriptor_775bb4,
    &audio_conversate_descriptor_775c14,
    &audio_conversate_descriptor_775c2c,
    &audio_conversate_descriptor_775c44,
    &audio_conversate_descriptor_775c74,
    &audio_conversate_descriptor_775c8c,
    &audio_conversate_descriptor_775c5c,
    &audio_conversate_descriptor_775be4,
    0
};
const struct pb_msgdesc_candidate audio_conversate_response_descriptor_775b24 = {
    audio_conversate_fields_775b24, audio_conversate_submessages_775b24, 0, 0,
    13u, 0u, 13u
};

const uint32_t audio_conversate_fields_775b54[5] = {
    0x10001204u, 0x10011208u, 0x1002120cu, 0x10031210u,
    0x10041214u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775b54[1] = {
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775b54 = {
    audio_conversate_fields_775b54, audio_conversate_submessages_775b54, 0, 0,
    5u, 0u, 5u
};

const uint32_t audio_conversate_fields_775b6c[3] = {
    0x40001204u, 0x00011609u, 0x00820004u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775b6c[1] = {
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775b6c = {
    audio_conversate_fields_775b6c, audio_conversate_submessages_775b6c, 0, 0,
    2u, 0u, 2u
};

const uint32_t audio_conversate_fields_775b84[4] = {
    0x40142805u, 0x00880004u, 0x00011209u, 0x00040aa4u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775b84[2] = {
    &audio_conversate_descriptor_775b6c,
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775b84 = {
    audio_conversate_fields_775b84, audio_conversate_submessages_775b84, 0, 0,
    2u, 0u, 2u
};

const uint32_t audio_conversate_fields_775b9c[1] = {
    0x00000000u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775b9c[1] = {
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775b9c = {
    audio_conversate_fields_775b9c, audio_conversate_submessages_775b9c, 0, 0,
    0u, 0u, 0u
};

const uint32_t audio_conversate_fields_775bb4[2] = {
    0x10001204u, 0x40041208u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775bb4[1] = {
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775bb4 = {
    audio_conversate_fields_775bb4, audio_conversate_submessages_775bb4, 0, 0,
    2u, 0u, 2u
};

const uint32_t audio_conversate_fields_775bcc[3] = {
    0x00011605u, 0x00820000u, 0x40841208u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775bcc[1] = {
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775bcc = {
    audio_conversate_fields_775bcc, audio_conversate_submessages_775bcc, 0, 0,
    2u, 0u, 2u
};

const uint32_t audio_conversate_fields_775be4[4] = {
    0x00011205u, 0x00040000u, 0x00011609u, 0x0fa20004u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775be4[1] = {
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775be4 = {
    audio_conversate_fields_775be4, audio_conversate_submessages_775be4, 0, 0,
    2u, 0u, 2u
};

const uint32_t audio_conversate_fields_775bfc[6] = {
    0x10001204u, 0x10011809u, 0x00050002u, 0x1001180du,
    0x00880008u, 0x10901210u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775bfc[3] = {
    &audio_conversate_descriptor_775b54,
    &audio_conversate_descriptor_775bcc,
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775bfc = {
    audio_conversate_fields_775bfc, audio_conversate_submessages_775bfc, 0, 0,
    4u, 0u, 4u
};

const uint32_t audio_conversate_fields_775c14[8] = {
    0x00011205u, 0x00010000u, 0x00011609u, 0x00820002u,
    0x0001160du, 0x04020084u, 0x00011211u, 0x00040488u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775c14[1] = {
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775c14 = {
    audio_conversate_fields_775c14, audio_conversate_submessages_775c14, 0, 0,
    4u, 0u, 4u
};

const uint32_t audio_conversate_fields_775c2c[4] = {
    0x00011605u, 0x04020000u, 0x00011209u, 0x00040404u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775c2c[1] = {
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775c2c = {
    audio_conversate_fields_775c2c, audio_conversate_submessages_775c2c, 0, 0,
    2u, 0u, 2u
};

const uint32_t audio_conversate_fields_775c44[2] = {
    0x10001204u, 0x10011208u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775c44[1] = {
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775c44 = {
    audio_conversate_fields_775c44, audio_conversate_submessages_775c44, 0, 0,
    2u, 0u, 2u
};

const uint32_t audio_conversate_fields_775c5c[4] = {
    0x40001204u, 0x10041208u, 0x1005120cu, 0x40081210u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775c5c[1] = {
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775c5c = {
    audio_conversate_fields_775c5c, audio_conversate_submessages_775c5c, 0, 0,
    4u, 0u, 4u
};

const uint32_t audio_conversate_fields_775c74[1] = {
    0x10001204u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775c74[1] = {
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775c74 = {
    audio_conversate_fields_775c74, audio_conversate_submessages_775c74, 0, 0,
    1u, 0u, 1u
};

const uint32_t audio_conversate_fields_775c8c[1] = {
    0x00000000u,
};
const struct pb_msgdesc_candidate *const audio_conversate_submessages_775c8c[1] = {
    0
};
const struct pb_msgdesc_candidate audio_conversate_descriptor_775c8c = {
    audio_conversate_fields_775c8c, audio_conversate_submessages_775c8c, 0, 0,
    0u, 0u, 0u
};
