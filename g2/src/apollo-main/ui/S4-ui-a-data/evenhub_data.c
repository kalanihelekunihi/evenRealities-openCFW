/* EvenHub UI storage (S4-ui-a storage-definition pass, G2 2.2.6.10).
 *
 * Stock owners app\gui\evenhub (loading page, main page, ui page, data parser).
 * .data values come from the decoded scatter init streams (records 0x75d3f4
 * for 0x20000000.. and 0x75d404 for 0x20080000..); every other RAM cell is
 * zero-initialised (.bss 0x20004558.. / 0x2013be70..). ROM bytes are copied
 * from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0). Absolute
 * placement is a linker obligation; compiling this file does not establish
 * byte identity. */
#include <stdint.h>

struct pb_msgdesc_candidate {
    const uint32_t *field_info;
    const struct pb_msgdesc_candidate *const *submsg_info;
    const uint8_t *default_value;
    void *field_callback;
    uint16_t field_count, required_field_count, largest_tag;
};
_Static_assert(sizeof(struct pb_msgdesc_candidate) == 24u, "ARM nanopb 0.4 pb_msgdesc_t");
/* ROM 0x77754c: EvenHub nanopb message graph (30 descriptors; field words,
 * submessage tables and counts copied from ROM; no defaults/callbacks).
 * extern view const uint8_t[]. */
static const struct pb_msgdesc_candidate pb_desc_7773b4;
static const struct pb_msgdesc_candidate pb_desc_77730c;
static const struct pb_msgdesc_candidate pb_desc_7772f4;
static const struct pb_msgdesc_candidate pb_desc_777354;
static const struct pb_msgdesc_candidate pb_desc_77739c;
static const struct pb_msgdesc_candidate pb_desc_7773cc;
static const struct pb_msgdesc_candidate pb_desc_77736c;
static const struct pb_msgdesc_candidate pb_desc_777384;
static const struct pb_msgdesc_candidate pb_desc_7773e4;
static const struct pb_msgdesc_candidate pb_desc_7773fc;
static const struct pb_msgdesc_candidate pb_desc_777324;
static const struct pb_msgdesc_candidate pb_desc_77733c;
static const struct pb_msgdesc_candidate pb_desc_777414;
static const struct pb_msgdesc_candidate pb_desc_77742c;
static const struct pb_msgdesc_candidate pb_desc_7772dc;
static const struct pb_msgdesc_candidate pb_desc_777264;
static const struct pb_msgdesc_candidate pb_desc_77727c;
static const struct pb_msgdesc_candidate pb_desc_7772c4;
static const struct pb_msgdesc_candidate pb_desc_777294;
static const struct pb_msgdesc_candidate pb_desc_777474;
static const struct pb_msgdesc_candidate pb_desc_77748c;
static const struct pb_msgdesc_candidate pb_desc_77745c;
static const struct pb_msgdesc_candidate pb_desc_7774a4;
static const struct pb_msgdesc_candidate pb_desc_7774bc;
static const struct pb_msgdesc_candidate pb_desc_7774d4;
static const struct pb_msgdesc_candidate pb_desc_7774ec;
static const struct pb_msgdesc_candidate pb_desc_777504;
static const struct pb_msgdesc_candidate pb_desc_77751c;
static const struct pb_msgdesc_candidate pb_desc_777534;
static const uint32_t pb_fields_6c8740[] = { /* ROM 0x6c8740 */
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000001u,
    0x0001120au, 0x00000000u, 0x00000001u, 0x00000001u,
    0x0001380eu, 0x00000002u, 0x00000004u, 0x00003754u,
    0x00013812u, 0x00000002u, 0x00000004u, 0x00000001u,
    0x00013816u, 0x00000002u, 0x00000004u, 0x0000102cu,
    0x0001381au, 0x00000002u, 0x00000004u, 0x0000002cu,
    0x0001381eu, 0x00000002u, 0x00000004u, 0x00003750u,
    0x00013822u, 0x00000002u, 0x00000004u, 0x00000001u,
    0x00013826u, 0x00000002u, 0x00000004u, 0x000007ecu,
    0x0001382au, 0x00000002u, 0x00000004u, 0x00000001u,
    0x0001382eu, 0x00000002u, 0x00000004u, 0x00000004u,
    0x00013832u, 0x00000002u, 0x00000004u, 0x00000001u,
    0x00013836u, 0x00000002u, 0x00000004u, 0x00000060u,
    0x0001383au, 0x00000002u, 0x00000004u, 0x00000004u,
    0x0001383eu, 0x00000002u, 0x00000004u, 0x00000008u,
    0x00013842u, 0x00000002u, 0x00000004u, 0x0000001cu,
    0x00013846u, 0x00000002u, 0x00000004u, 0x00000008u,
    0x0001384au, 0x00000002u, 0x00000004u, 0x00000004u,
    0x0001384eu, 0x00000002u, 0x00000004u, 0x00000004u,
    0x00013852u, 0x00000002u, 0x00000004u, 0x00000004u,
    0x00013856u, 0x00000002u, 0x00000004u, 0x000000ccu,
    0x0001385au, 0x00000002u, 0x00000004u, 0x00000008u,
    0x0001385eu, 0x00000002u, 0x00000004u, 0x00000004u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_6e30f0[] = { /* ROM 0x6e30f0 */
    &pb_desc_7773b4, &pb_desc_7773cc, &pb_desc_77736c, &pb_desc_777384, &pb_desc_7773e4, &pb_desc_7773fc, &pb_desc_777324, &pb_desc_77733c, &pb_desc_777414, &pb_desc_77742c, &pb_desc_7772dc, &pb_desc_777474, &pb_desc_77748c, &pb_desc_77745c, &pb_desc_7774a4, &pb_desc_7774bc, &pb_desc_7774d4, &pb_desc_7774ec, &pb_desc_777504, &pb_desc_77751c, &pb_desc_777534, 0
};
const struct pb_msgdesc_candidate g2_evenhub_pb_msg_fields_77754c = { /* ROM 0x77754c */
    pb_fields_6c8740, pb_submsgs_6e30f0, 0, 0, 23u, 0u, 23u
};
static const uint32_t pb_fields_6e7978[] = { /* ROM 0x6e7978 */
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000004u,
    0x0004280au, 0x00000004u, 0x00000008u, 0x00000554u,
    0x0008280eu, 0x00000004u, 0x0000155cu, 0x00000428u,
    0x00042812u, 0x00000004u, 0x000036a0u, 0x0000002cu,
    0x00011216u, 0x00000000u, 0x00003750u, 0x00000004u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_785e30[] = { /* ROM 0x785e30 */
    &pb_desc_77730c, &pb_desc_777354, &pb_desc_77739c, 0
};
static const struct pb_msgdesc_candidate pb_desc_7773b4 = { /* ROM 0x7773b4 */
    pb_fields_6e7978, pb_submsgs_785e30, 0, 0, 5u, 0u, 5u
};
static const uint32_t pb_fields_6a8a74[] = { /* ROM 0x6a8a74 */
    0x00011205u, 0x00040000u,
    0x00011209u, 0x00040004u,
    0x0001120du, 0x00040008u,
    0x00011211u, 0x0004000cu,
    0x00011215u, 0x00040010u,
    0x00011219u, 0x00040014u,
    0x0001121du, 0x00040018u,
    0x00011221u, 0x0004001cu,
    0x00011225u, 0x00040020u,
    0x00011729u, 0x00100024u,
    0x4001182du, 0x05100038u,
    0x00011231u, 0x00040548u,
    0x40011235u, 0x00040550u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78d544[] = { /* ROM 0x78d544 */
    &pb_desc_7772f4, 0
};
static const struct pb_msgdesc_candidate pb_desc_77730c = { /* ROM 0x77730c */
    pb_fields_6a8a74, pb_submsgs_78d544, 0, 0, 13u, 0u, 13u
};
static const uint32_t pb_fields_7544e8[] = { /* ROM 0x7544e8 */
    0x00011205u, 0x00040000u,
    0x00011209u, 0x00040004u,
    0x0001120du, 0x00040008u,
    0x20142711u, 0x0040000eu,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f050[] = { /* ROM 0x78f050 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_7772f4 = { /* ROM 0x7772f4 */
    pb_fields_7544e8, pb_submsgs_78f050, 0, 0, 4u, 0u, 4u
};
static const uint32_t pb_fields_6a8d84[] = { /* ROM 0x6a8d84 */
    0x00011205u, 0x00040000u,
    0x00011209u, 0x00040004u,
    0x0001120du, 0x00040008u,
    0x00011211u, 0x0004000cu,
    0x00011215u, 0x00040010u,
    0x00011219u, 0x00040014u,
    0x0001121du, 0x00040018u,
    0x00011221u, 0x0004001cu,
    0x00011225u, 0x00040020u,
    0x00011729u, 0x00100024u,
    0x0001122du, 0x00040034u,
    0x00011731u, 0x03e80038u,
    0x40011235u, 0x00040424u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f05c[] = { /* ROM 0x78f05c */
    0
};
static const struct pb_msgdesc_candidate pb_desc_777354 = { /* ROM 0x777354 */
    pb_fields_6a8d84, pb_submsgs_78f05c, 0, 0, 13u, 0u, 13u
};
static const uint32_t pb_fields_75450c[] = { /* ROM 0x75450c */
    0x40001204u,
    0x40041208u,
    0x4008120cu,
    0x400c1210u,
    0x40101214u,
    0x00011719u, 0x00100014u,
    0x4428121cu,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f068[] = { /* ROM 0x78f068 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_77739c = { /* ROM 0x77739c */
    pb_fields_75450c, pb_submsgs_78f068, 0, 0, 7u, 0u, 7u
};
static const uint32_t pb_fields_78d554[] = { /* ROM 0x78d554 */
    0x10001204u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f06c[] = { /* ROM 0x78f06c */
    0
};
static const struct pb_msgdesc_candidate pb_desc_7773cc = { /* ROM 0x7773cc */
    pb_fields_78d554, pb_submsgs_78f06c, 0, 0, 1u, 0u, 1u
};
static const uint32_t pb_fields_6d4e38[] = { /* ROM 0x6d4e38 */
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000004u,
    0x0001170au, 0x00000000u, 0x00000004u, 0x00000010u,
    0x0001120eu, 0x00000000u, 0x00000014u, 0x00000004u,
    0x00011212u, 0x00000000u, 0x00000018u, 0x00000004u,
    0x00011216u, 0x00000000u, 0x0000001cu, 0x00000004u,
    0x0001121au, 0x00000000u, 0x00000020u, 0x00000004u,
    0x0001121eu, 0x00000000u, 0x00000024u, 0x00000004u,
    0x00011622u, 0x00000000u, 0x00000028u, 0x00001002u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f060[] = { /* ROM 0x78f060 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_77736c = { /* ROM 0x77736c */
    pb_fields_6d4e38, pb_submsgs_78f060, 0, 0, 8u, 0u, 8u
};
static const uint32_t pb_fields_749eac[] = { /* ROM 0x749eac */
    0x40001204u,
    0x00011709u, 0x00100004u,
    0x4014120cu,
    0x40181210u,
    0x401c1214u,
    0x40201218u,
    0x4024121cu,
    0x10281220u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f064[] = { /* ROM 0x78f064 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_777384 = { /* ROM 0x777384 */
    pb_fields_749eac, pb_submsgs_78f064, 0, 0, 8u, 0u, 8u
};
static const uint32_t pb_fields_702724[] = { /* ROM 0x702724 */
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000004u,
    0x0004280au, 0x00000004u, 0x00000008u, 0x00000554u,
    0x0008280eu, 0x00000004u, 0x0000155cu, 0x00000428u,
    0x00042812u, 0x00000004u, 0x000036a0u, 0x0000002cu,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_785e40[] = { /* ROM 0x785e40 */
    &pb_desc_77730c, &pb_desc_777354, &pb_desc_77739c, 0
};
static const struct pb_msgdesc_candidate pb_desc_7773e4 = { /* ROM 0x7773e4 */
    pb_fields_702724, pb_submsgs_785e40, 0, 0, 4u, 0u, 4u
};
static const uint32_t pb_fields_78d55c[] = { /* ROM 0x78d55c */
    0x10001204u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f070[] = { /* ROM 0x78f070 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_7773fc = { /* ROM 0x7773fc */
    pb_fields_78d55c, pb_submsgs_78f070, 0, 0, 1u, 0u, 1u
};
static const uint32_t pb_fields_73ec0c[] = { /* ROM 0x73ec0c */
    0x00011205u, 0x00040000u,
    0x00011709u, 0x00100004u,
    0x0001120du, 0x00040014u,
    0x00011211u, 0x00040018u,
    0x00011715u, 0x07d0001cu,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f054[] = { /* ROM 0x78f054 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_777324 = { /* ROM 0x777324 */
    pb_fields_73ec0c, pb_submsgs_78f054, 0, 0, 5u, 0u, 5u
};
static const uint32_t pb_fields_78d54c[] = { /* ROM 0x78d54c */
    0x10001204u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f058[] = { /* ROM 0x78f058 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_77733c = { /* ROM 0x77733c */
    pb_fields_78d54c, pb_submsgs_78f058, 0, 0, 1u, 0u, 1u
};
static const uint32_t pb_fields_78d564[] = { /* ROM 0x78d564 */
    0x40001204u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f074[] = { /* ROM 0x78f074 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_777414 = { /* ROM 0x777414 */
    pb_fields_78d564, pb_submsgs_78f074, 0, 0, 1u, 0u, 1u
};
static const uint32_t pb_fields_78d56c[] = { /* ROM 0x78d56c */
    0x10001204u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f078[] = { /* ROM 0x78f078 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_77742c = { /* ROM 0x77742c */
    pb_fields_78d56c, pb_submsgs_78f078, 0, 0, 1u, 0u, 1u
};
static const uint32_t pb_fields_76b714[] = { /* ROM 0x76b714 */
    0x40013805u, 0x005c0004u,
    0x40013809u, 0x00180004u,
    0x4001380du, 0x00140004u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_785e20[] = { /* ROM 0x785e20 */
    &pb_desc_777264, &pb_desc_77727c, &pb_desc_7772c4, 0
};
static const struct pb_msgdesc_candidate pb_desc_7772dc = { /* ROM 0x7772dc */
    pb_fields_76b714, pb_submsgs_785e20, 0, 0, 3u, 0u, 3u
};
static const uint32_t pb_fields_75fe90[] = { /* ROM 0x75fe90 */
    0x40001204u,
    0x00011709u, 0x00100004u,
    0x0001170du, 0x00400014u,
    0x40541210u,
    0x10581214u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f044[] = { /* ROM 0x78f044 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_777264 = { /* ROM 0x777264 */
    pb_fields_75fe90, pb_submsgs_78f044, 0, 0, 5u, 0u, 5u
};
static const uint32_t pb_fields_77f388[] = { /* ROM 0x77f388 */
    0x40001204u,
    0x00011709u, 0x00100004u,
    0x1014120cu,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f048[] = { /* ROM 0x78f048 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_77727c = { /* ROM 0x77727c */
    pb_fields_77f388, pb_submsgs_78f048, 0, 0, 3u, 0u, 3u
};
static const uint32_t pb_fields_7772ac[] = { /* ROM 0x7772ac */
    0x10001204u,
    0x10011208u,
    0x2001180du, 0x000c0004u,
    0x40101210u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78d53c[] = { /* ROM 0x78d53c */
    &pb_desc_777294, 0
};
static const struct pb_msgdesc_candidate pb_desc_7772c4 = { /* ROM 0x7772c4 */
    pb_fields_7772ac, pb_submsgs_78d53c, 0, 0, 4u, 0u, 4u
};
static const uint32_t pb_fields_785e10[] = { /* ROM 0x785e10 */
    0x40001404u,
    0x40041408u,
    0x4008140cu,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f04c[] = { /* ROM 0x78f04c */
    0
};
static const struct pb_msgdesc_candidate pb_desc_777294 = { /* ROM 0x777294 */
    pb_fields_785e10, pb_submsgs_78f04c, 0, 0, 3u, 0u, 3u
};
static const uint32_t pb_fields_78d574[] = { /* ROM 0x78d574 */
    0x40001204u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f080[] = { /* ROM 0x78f080 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_777474 = { /* ROM 0x777474 */
    pb_fields_78d574, pb_submsgs_78f080, 0, 0, 1u, 0u, 1u
};
static const uint32_t pb_fields_78aa00[] = { /* ROM 0x78aa00 */
    0x40001204u,
    0x10041208u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f084[] = { /* ROM 0x78f084 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_77748c = { /* ROM 0x77748c */
    pb_fields_78aa00, pb_submsgs_78f084, 0, 0, 2u, 0u, 2u
};
static const uint32_t pb_fields_777444[] = { /* ROM 0x777444 */
    0x40001204u,
    0x00011709u, 0x00100004u,
    0x4014120cu,
    0x40181210u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f07c[] = { /* ROM 0x78f07c */
    0
};
static const struct pb_msgdesc_candidate pb_desc_77745c = { /* ROM 0x77745c */
    pb_fields_777444, pb_submsgs_78f07c, 0, 0, 4u, 0u, 4u
};
static const uint32_t pb_fields_78aa0c[] = { /* ROM 0x78aa0c */
    0x10001204u,
    0x40041208u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f088[] = { /* ROM 0x78f088 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_7774a4 = { /* ROM 0x7774a4 */
    pb_fields_78aa0c, pb_submsgs_78f088, 0, 0, 2u, 0u, 2u
};
static const uint32_t pb_fields_78d57c[] = { /* ROM 0x78d57c */
    0x40001204u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f08c[] = { /* ROM 0x78f08c */
    0
};
static const struct pb_msgdesc_candidate pb_desc_7774bc = { /* ROM 0x7774bc */
    pb_fields_78d57c, pb_submsgs_78f08c, 0, 0, 1u, 0u, 1u
};
static const uint32_t pb_fields_78d584[] = { /* ROM 0x78d584 */
    0x40001204u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f090[] = { /* ROM 0x78f090 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_7774d4 = { /* ROM 0x7774d4 */
    pb_fields_78d584, pb_submsgs_78f090, 0, 0, 1u, 0u, 1u
};
static const uint32_t pb_fields_78d58c[] = { /* ROM 0x78d58c */
    0x40001204u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f094[] = { /* ROM 0x78f094 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_7774ec = { /* ROM 0x7774ec */
    pb_fields_78d58c, pb_submsgs_78f094, 0, 0, 1u, 0u, 1u
};
static const uint32_t pb_fields_785e50[] = { /* ROM 0x785e50 */
    0x40001204u,
    0x00011709u, 0x00c80004u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f098[] = { /* ROM 0x78f098 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_777504 = { /* ROM 0x777504 */
    pb_fields_785e50, pb_submsgs_78f098, 0, 0, 2u, 0u, 2u
};
static const uint32_t pb_fields_78aa18[] = { /* ROM 0x78aa18 */
    0x40001204u,
    0x40041208u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f09c[] = { /* ROM 0x78f09c */
    0
};
static const struct pb_msgdesc_candidate pb_desc_77751c = { /* ROM 0x77751c */
    pb_fields_78aa18, pb_submsgs_78f09c, 0, 0, 2u, 0u, 2u
};
static const uint32_t pb_fields_78d594[] = { /* ROM 0x78d594 */
    0x40001204u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f0a0[] = { /* ROM 0x78f0a0 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_777534 = { /* ROM 0x777534 */
    pb_fields_78d594, pb_submsgs_78f0a0, 0, 0, 1u, 0u, 1u
};

const uint32_t g2_evenhub_start_record_init[2] = {0u, 1u}; /* ROM 0x78d5a4; extern view: const evenhub_start_record_t g2_evenhub_start_record_init; */

const uint32_t g2_evenhub_exit_record_init[2] = {0u, 2u}; /* ROM 0x78d5e4; extern view: const evenhub_exit_record_t g2_evenhub_exit_record_init; */

void *g2_evenhub_data_mutex_2007458c; /* RAM 0x2007458c */

void *g2_evenhub_loading_root_obj; /* RAM 0x20074590 */

int32_t g2_evenhub_loading_timeout_cnt; /* RAM 0x20074594 */

uint32_t g2_evenhub_loading_dimmed; /* RAM 0x20074598 */

uint32_t g2_evenhub_loading_foreground; /* RAM 0x2007459c */

void *g2_evenhub_loading_label; /* RAM 0x200745a0 */

uint32_t g2_evenhub_loading_startup_widget_id; /* RAM 0x200745a4 */

void *g2_evenhub_manager; /* RAM 0x200745a8 */

uint32_t g2_evenhub_heartbeat_ticks; /* RAM 0x200745ac */

uint32_t g2_evenhub_timeout_page_ticks; /* RAM 0x200745b0 */

uint32_t g2_evenhub_audio_acquired; /* RAM 0x200745b4 */

uint32_t g2_evenhub_shutdown_state; /* RAM 0x200745b8 */

uint32_t g2_evenhub_imu_enabled; /* RAM 0x200745bc */

uint32_t g2_evenhub_dimmed; /* RAM 0x200745c0 */

uint32_t g2_evenhub_exit_pending; /* RAM 0x200745c4 */

uint32_t g2_evenhub_start_tick; /* RAM 0x200745c8 */

uint32_t g2_evenhub_startup_widget_id; /* RAM 0x200745cc */

uint8_t g2_evenhub_foreground; /* RAM 0x20074fc3 */

uint8_t g2_evenhub_timeout_page; /* RAM 0x20074fc4 */

__attribute__((aligned(4))) uint8_t g2_evenhub_tx_buffer_203362c4[0x38ec]; /* RAM 0x203362c4; extern view: uint8_t g2_evenhub_tx_buffer_203362c4[EVENHUB_TX_BUFFER_SIZE]; */

__attribute__((aligned(4))) uint8_t g2_evenhub_parser_msg[0x3758]; /* RAM 0x2033d3f0; extern view: evenhub_parser_msg_t g2_evenhub_parser_msg; */

__attribute__((aligned(4))) uint8_t g2_evenhub_tx_msg_20340b48[0x3758]; /* RAM 0x20340b48; extern view: g2_evenhub_tx_msg_t g2_evenhub_tx_msg_20340b48; */

__attribute__((aligned(4))) uint8_t g2_evenhub_rx_msg[0x3758]; /* RAM 0x203442a0; extern view: evenhub_msg_t g2_evenhub_rx_msg; */
