/* Navigation nanopb message descriptors (S6-fonts-residual storage-definition
 * pass, G2 2.2.6.10).
 *
 * Generated from the stock image ota_s200_firmware_ota.bin (VA = file offset
 * + 0x437fe0) by walking the root pb_msgdesc_t at ROM 0x7798a4 (nanopb 0.4.9
 * layout: field_info, submsg_info, default_value, field_callback,
 * field_count, required_field_count, largest_tag; 24 bytes), following the
 * app/S3-app-data/pb_descriptors_data.c convention. Field-info word counts
 * follow pb_common.c load_descriptor_values (word0 bits 1:0 select 1/2/4/8
 * words); submessage arrays hold one entry per SUBMESSAGE / SUBMSG_W_CB field
 * plus the generator's NULL terminator. No descriptor in this graph has
 * default values or a field callback. These are protoc-nanopb outputs of the
 * product navigation .proto, not nanopb library code.
 *
 * Root: 0x7798a4 navigation message (ui/a-60-navigation-data send,
 * ui/a-61-navigation-data handler). Nested descriptors are named by stock
 * address. Absolute placement is a linker obligation. */
#include "pb.h"

/* ROM 0x781340 */
static const uint32_t field_info_781340[4] = {
    0x10001204u, 0x00011709u, 0x00400001u, 0x4044120cu,
};
/* ROM 0x756c24 */
static const uint32_t field_info_756c24[8] = {
    0x00011205u, 0x00040000u, 0x20142709u, 0x00400006u,
    0x2014220du, 0x00040508u, 0x00011211u, 0x00010558u,
};
/* ROM 0x6f469c */
static const uint32_t field_info_6f469c[18] = {
    0x00011205u, 0x00040000u, 0x00011709u, 0x00400004u,
    0x0001170du, 0x00400044u, 0x00011711u, 0x00400084u,
    0x00011715u, 0x004000c4u, 0x00011719u, 0x00400104u,
    0x0001171du, 0x00400144u, 0x00011221u, 0x00040184u,
    0x00011225u, 0x00010188u,
};
/* ROM 0x6d3aac */
static const uint32_t field_info_6d3aac[36] = {
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000004u,
    0x0001120au, 0x00000000u, 0x00000004u, 0x00000004u,
    0x0001160eu, 0x00000000u, 0x00000008u, 0x00002002u,
    0x00011212u, 0x00000000u, 0x0000200au, 0x00000001u,
    0x00011216u, 0x00000000u, 0x0000200cu, 0x00000004u,
    0x0001121au, 0x00000000u, 0x00002010u, 0x00000004u,
    0x0001121eu, 0x00000000u, 0x00002014u, 0x00000004u,
    0x00011222u, 0x00000000u, 0x00002018u, 0x00000004u,
    0x00011226u, 0x00000000u, 0x0000201cu, 0x00000004u,
};
/* ROM 0x6a0db4 */
static const uint32_t field_info_6a0db4[28] = {
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000004u,
    0x0001120au, 0x00000000u, 0x00000004u, 0x00000004u,
    0x0001120eu, 0x00000000u, 0x00000008u, 0x00000004u,
    0x00011212u, 0x00000000u, 0x0000000cu, 0x00000004u,
    0x00011216u, 0x00000000u, 0x00000010u, 0x00000004u,
    0x0001161au, 0x00000000u, 0x00000014u, 0x00001002u,
    0x0001121eu, 0x00000000u, 0x00001016u, 0x00000001u,
};
/* ROM 0x7797e4 */
static const uint32_t field_info_7797e4[5] = {
    0x00011705u, 0x00400000u, 0x10401208u, 0x4044120cu,
    0x40481210u,
};
/* ROM 0x78dd34 */
static const uint32_t field_info_78dd34[1] = {
    0x40001204u,
};
/* ROM 0x78dd3c */
static const uint32_t field_info_78dd3c[1] = {
    0x40001204u,
};
/* ROM 0x6d2d10 */
static const uint32_t field_info_6d2d10[40] = {
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000001u,
    0x0001120au, 0x00000000u, 0x00000001u, 0x00000001u,
    0x0001380eu, 0x00000002u, 0x00000004u, 0x00000048u,
    0x00013812u, 0x00000002u, 0x00000004u, 0x0000055cu,
    0x00013816u, 0x00000002u, 0x00000004u, 0x0000018cu,
    0x0001381au, 0x00000002u, 0x00000004u, 0x00002020u,
    0x0001381eu, 0x00000002u, 0x00000004u, 0x00001018u,
    0x00013822u, 0x00000002u, 0x00000004u, 0x0000004cu,
    0x00013826u, 0x00000002u, 0x00000004u, 0x00000004u,
    0x0001382au, 0x00000002u, 0x00000004u, 0x00000004u,
};
static const pb_msgdesc_t g2_pb_msgdesc_77985c;
static const pb_msgdesc_t g2_pb_msgdesc_7797cc;
static const pb_msgdesc_t g2_pb_msgdesc_779814;
static const pb_msgdesc_t g2_pb_msgdesc_77982c;
static const pb_msgdesc_t g2_pb_msgdesc_779844;
static const pb_msgdesc_t g2_pb_msgdesc_7797fc;
static const pb_msgdesc_t g2_pb_msgdesc_779874;
static const pb_msgdesc_t g2_pb_msgdesc_77988c;

/* ROM 0x78f2e8 */
static const pb_msgdesc_t *const submsg_info_78f2e8[1] = {NULL};
/* ROM 0x78f2d4 */
static const pb_msgdesc_t *const submsg_info_78f2d4[1] = {NULL};
/* ROM 0x78f2dc */
static const pb_msgdesc_t *const submsg_info_78f2dc[1] = {NULL};
/* ROM 0x78f2e0 */
static const pb_msgdesc_t *const submsg_info_78f2e0[1] = {NULL};
/* ROM 0x78f2e4 */
static const pb_msgdesc_t *const submsg_info_78f2e4[1] = {NULL};
/* ROM 0x78f2d8 */
static const pb_msgdesc_t *const submsg_info_78f2d8[1] = {NULL};
/* ROM 0x78f2ec */
static const pb_msgdesc_t *const submsg_info_78f2ec[1] = {NULL};
/* ROM 0x78f2f0 */
static const pb_msgdesc_t *const submsg_info_78f2f0[1] = {NULL};
/* ROM 0x756c48 */
static const pb_msgdesc_t *const submsg_info_756c48[9] = {&g2_pb_msgdesc_77985c, &g2_pb_msgdesc_7797cc, &g2_pb_msgdesc_779814, &g2_pb_msgdesc_77982c, &g2_pb_msgdesc_779844, &g2_pb_msgdesc_7797fc, &g2_pb_msgdesc_779874, &g2_pb_msgdesc_77988c, NULL};
/* ROM 0x77985c */
static const pb_msgdesc_t g2_pb_msgdesc_77985c = {
    field_info_781340, submsg_info_78f2e8, NULL, NULL, 3u, 0u, 3u};
/* ROM 0x7797cc */
static const pb_msgdesc_t g2_pb_msgdesc_7797cc = {
    field_info_756c24, submsg_info_78f2d4, NULL, NULL, 4u, 0u, 4u};
/* ROM 0x779814 */
static const pb_msgdesc_t g2_pb_msgdesc_779814 = {
    field_info_6f469c, submsg_info_78f2dc, NULL, NULL, 9u, 0u, 9u};
/* ROM 0x77982c */
static const pb_msgdesc_t g2_pb_msgdesc_77982c = {
    field_info_6d3aac, submsg_info_78f2e0, NULL, NULL, 9u, 0u, 9u};
/* ROM 0x779844 */
static const pb_msgdesc_t g2_pb_msgdesc_779844 = {
    field_info_6a0db4, submsg_info_78f2e4, NULL, NULL, 7u, 0u, 7u};
/* ROM 0x7797fc */
static const pb_msgdesc_t g2_pb_msgdesc_7797fc = {
    field_info_7797e4, submsg_info_78f2d8, NULL, NULL, 4u, 0u, 4u};
/* ROM 0x779874 */
static const pb_msgdesc_t g2_pb_msgdesc_779874 = {
    field_info_78dd34, submsg_info_78f2ec, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77988c */
static const pb_msgdesc_t g2_pb_msgdesc_77988c = {
    field_info_78dd3c, submsg_info_78f2f0, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x7798a4, navigation message (a-60/a-61 navigation data) */
const pb_msgdesc_t g2_nav_msg_fields_7798a4 = {
    field_info_6d2d10, submsg_info_756c48, NULL, NULL, 10u, 0u, 10u};
