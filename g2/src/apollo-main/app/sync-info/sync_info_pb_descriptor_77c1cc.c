/* Authenticated two-node SyncInfo nanopb descriptor graph from stock Main.
 * Root 0x77c1cc, child 0x77c1b4; field tables and edges are checked by
 * audit_main_sync_info_pb_descriptor_77c1cc_20261016.py. */
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
               "ARM nanopb field-count offset");

const uint32_t audio_sync_info_root_fields_783c94[5] = {
    0x10001204u, 0x10011208u, 0x2001180du, 0x00080004u, 0u
};
const uint32_t audio_sync_info_child_fields_78c4c4[3] = {
    0x40001204u, 0x40041208u, 0u
};
const struct pb_msgdesc_candidate audio_sync_info_child_descriptor_77c1b4;
const struct pb_msgdesc_candidate *const audio_sync_info_root_submsgs_78e9c4[2] = {
    &audio_sync_info_child_descriptor_77c1b4, 0
};
const struct pb_msgdesc_candidate *const audio_sync_info_child_submsgs_78f404[1] = {0};

const struct pb_msgdesc_candidate audio_sync_info_child_descriptor_77c1b4 = {
    audio_sync_info_child_fields_78c4c4,
    audio_sync_info_child_submsgs_78f404, 0, 0, 2u, 0u, 2u
};
const struct pb_msgdesc_candidate audio_sync_info_pb_descriptor_77c1cc = {
    audio_sync_info_root_fields_783c94,
    audio_sync_info_root_submsgs_78e9c4, 0, 0, 3u, 0u, 3u
};
