/* Product nanopb message descriptors (S3 storage-definition pass,
 * 2.2.6.10).
 *
 * Generated from the stock image ota_s200_firmware_ota.bin (VA = file offset
 * + 0x437fe0) by walking each root pb_msgdesc_t (nanopb 0.4.9 layout:
 * field_info, submsg_info, default_value, field_callback, field_count,
 * required_field_count, largest_tag; 24 bytes). Field-info word counts follow
 * pb_common.c load_descriptor_values (word0 bits 1:0 select 1/2/4/8 words);
 * submessage arrays hold one entry per SUBMESSAGE / SUBMSG_W_CB field plus
 * the generator's NULL terminator. Every descriptor in these graphs has no
 * default values and no field callback. These are protoc-nanopb outputs of
 * the product .proto files, not nanopb library code.
 *
 * Roots: 0x776664 dashboard extension, 0x77610c dashboard data package,
 * 0x777a14 health, 0x77979c module configure, 0x77c304 teleprompt,
 * 0x77ce5c translate. Nested descriptors are named by stock address. */
#include "pb.h"

/* ROM 0x78d2ec */
static const uint32_t field_info_78d2ec[1] = {
    0x40001204u,
};
/* ROM 0x7765a4 */
static const uint32_t field_info_7765a4[5] = {
    0x40001204u, 0x00011709u, 0x00100004u, 0x0001170du,
    0x00200014u,
};
/* ROM 0x78d2f4 */
static const uint32_t field_info_78d2f4[1] = {
    0x40001204u,
};
/* ROM 0x78d2fc */
static const uint32_t field_info_78d2fc[1] = {
    0x40001204u,
};
/* ROM 0x78d304 */
static const uint32_t field_info_78d304[1] = {
    0x40001204u,
};
/* ROM 0x6da610 */
static const uint32_t field_info_6da610[24] = {
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000004u,
    0x0001120au, 0x00000000u, 0x00000004u, 0x00000004u,
    0x0001120eu, 0x00000000u, 0x00000008u, 0x00000004u,
    0x00011212u, 0x00000000u, 0x0000000cu, 0x00000004u,
    0x00011216u, 0x00000000u, 0x00000010u, 0x00000004u,
    0x0001161au, 0x00000000u, 0x00000014u, 0x00001002u,
};
/* ROM 0x76aa9c */
static const uint32_t field_info_76aa9c[6] = {
    0x40001204u, 0x40041208u, 0x4008120cu, 0x400c1210u,
    0x40101214u, 0x40141218u,
};
/* ROM 0x78d30c */
static const uint32_t field_info_78d30c[1] = {
    0x40001204u,
};
/* ROM 0x6d2bc8 */
static const uint32_t field_info_6d2bc8[40] = {
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000001u,
    0x0001120au, 0x00000000u, 0x00000004u, 0x00000004u,
    0x0001380eu, 0x00000004u, 0x0000000cu, 0x00000004u,
    0x00013812u, 0x00000004u, 0x0000000cu, 0x00000034u,
    0x00013816u, 0x00000004u, 0x0000000cu, 0x00000004u,
    0x0001381au, 0x00000004u, 0x0000000cu, 0x00000004u,
    0x0001381eu, 0x00000004u, 0x0000000cu, 0x00000004u,
    0x00013822u, 0x00000004u, 0x0000000cu, 0x00001018u,
    0x00013826u, 0x00000004u, 0x0000000cu, 0x00000018u,
    0x0001382au, 0x00000004u, 0x0000000cu, 0x00000004u,
};
/* ROM 0x78a730 */
static const uint32_t field_info_78a730[2] = {
    0x40001204u, 0x10041208u,
};
/* ROM 0x748cb4 */
static const uint32_t field_info_748cb4[9] = {
    0x40001204u, 0x40041208u, 0x200a220du, 0x0001000au,
    0x40141210u, 0x200a2215u, 0x0001001au, 0x40241218u,
    0x4028121cu,
};
/* ROM 0x7283e0 */
static const uint32_t field_info_7283e0[12] = {
    0x40001404u, 0x10041208u, 0x1005120cu, 0x80081210u,
    0x00011715u, 0x00200010u, 0x40301218u, 0x0001171du,
    0x00200034u, 0x40541120u, 0x00011725u, 0x00200058u,
};
/* ROM 0x78a6dc */
static const uint32_t field_info_78a6dc[2] = {
    0x80011805u, 0x00780008u,
};
/* ROM 0x73d714 */
static const uint32_t field_info_73d714[10] = {
    0x00011205u, 0x00040000u, 0x00011709u, 0x00800004u,
    0x0001120du, 0x00080088u, 0x00011711u, 0x00800090u,
    0x00011715u, 0x0bb80110u,
};
/* ROM 0x7531a4 */
static const uint32_t field_info_7531a4[8] = {
    0x00011205u, 0x00040000u, 0x00011209u, 0x00040004u,
    0x8001180du, 0x0cc80010u, 0x00011211u, 0x00040cd8u,
};
/* ROM 0x6d4ba4 */
static const uint32_t field_info_6d4ba4[32] = {
    0x00011705u, 0x00400000u, 0x00011709u, 0x00400040u,
    0x0001150du, 0x00080080u, 0x00011411u, 0x00040088u,
    0x00011415u, 0x0004008cu, 0x00011719u, 0x00800090u,
    0x0001141du, 0x00040110u, 0x00011421u, 0x00040114u,
    0x00011425u, 0x00040118u, 0x00011229u, 0x00080120u,
    0x0001152du, 0x00080128u, 0x00011431u, 0x00040130u,
    0x00011235u, 0x00040134u, 0x00011239u, 0x00040138u,
    0x0001143du, 0x0004013cu, 0x40b92441u, 0x00040144u,
};
/* ROM 0x76a968 */
static const uint32_t field_info_76a968[6] = {
    0x00011205u, 0x00040000u, 0x00011209u, 0x00040004u,
    0x8001180du, 0x04280010u,
};
/* ROM 0x73d740 */
static const uint32_t field_info_73d740[10] = {
    0x00011205u, 0x00040000u, 0x00011709u, 0x00b00004u,
    0x0001170du, 0x011b00b4u, 0x00011711u, 0x004001cfu,
    0x00011215u, 0x00040210u,
};
/* ROM 0x7531c8 */
static const uint32_t field_info_7531c8[8] = {
    0x00011205u, 0x00040000u, 0x00011209u, 0x00040004u,
    0x4001180du, 0x0214000cu, 0x00011211u, 0x00040220u,
};
/* ROM 0x76a984 */
static const uint32_t field_info_76a984[6] = {
    0x80013805u, 0x0ce00008u, 0x80013809u, 0x04380008u,
    0x8001380du, 0x02240008u,
};
/* ROM 0x77eb90 */
static const uint32_t field_info_77eb90[4] = {
    0x80013805u, 0x00800008u, 0x80013809u, 0x0ce80008u,
};
/* ROM 0x78d294 */
static const uint32_t field_info_78d294[1] = {
    0x40001204u,
};
/* ROM 0x7531ec */
static const uint32_t field_info_7531ec[8] = {
    0x00011205u, 0x00040000u, 0x40013809u, 0x002c0008u,
    0x4001380du, 0x0cf00008u, 0x40013811u, 0x00040008u,
};
/* ROM 0x78a748 */
static const uint32_t field_info_78a748[2] = {
    0x40001204u, 0x10041208u,
};
/* ROM 0x78d26c */
static const uint32_t field_info_78d26c[1] = {
    0x40001204u,
};
/* ROM 0x78a6d0 */
static const uint32_t field_info_78a6d0[2] = {
    0x40001404u, 0x40041408u,
};
/* ROM 0x77eb68 */
static const uint32_t field_info_77eb68[4] = {
    0x40011805u, 0x00040004u, 0x40011809u, 0x0008000cu,
};
/* ROM 0x78a6f4 */
static const uint32_t field_info_78a6f4[2] = {
    0x40001204u, 0x40041208u,
};
/* ROM 0x78a700 */
static const uint32_t field_info_78a700[2] = {
    0x40001204u, 0x80081208u,
};
/* ROM 0x77eb7c */
static const uint32_t field_info_77eb7c[4] = {
    0x80013805u, 0x00080008u, 0x80013809u, 0x00100008u,
};
/* ROM 0x78a718 */
static const uint32_t field_info_78a718[2] = {
    0x00011705u, 0x00400000u,
};
/* ROM 0x78a724 */
static const uint32_t field_info_78a724[2] = {
    0x40001204u, 0x40041208u,
};
/* ROM 0x76a9a0 */
static const uint32_t field_info_76a9a0[6] = {
    0x80013805u, 0x00180008u, 0x80013809u, 0x00400008u,
    0x8001380du, 0x00080008u,
};
/* ROM 0x78a754 */
static const uint32_t field_info_78a754[2] = {
    0x40001204u, 0x10041208u,
};
/* ROM 0x78d29c */
static const uint32_t field_info_78d29c[1] = {
    0x40001204u,
};
/* ROM 0x78d2a4 */
static const uint32_t field_info_78d2a4[1] = {
    0x40001204u,
};
/* ROM 0x78d2ac */
static const uint32_t field_info_78d2ac[1] = {
    0x40001204u,
};
/* ROM 0x76a9bc */
static const uint32_t field_info_76a9bc[6] = {
    0x40001204u, 0x400a2209u, 0x00040008u, 0x4030120cu,
    0x40341210u, 0x10381014u,
};
/* ROM 0x78d2b4 */
static const uint32_t field_info_78d2b4[1] = {
    0x40001204u,
};
/* ROM 0x71d650 */
static const uint32_t field_info_71d650[13] = {
    0x10001204u, 0x20013809u, 0x00080004u, 0x2001380du,
    0x00040004u, 0x20013811u, 0x00040004u, 0x20013815u,
    0x00040004u, 0x20013819u, 0x003c0004u, 0x2001381du,
    0x00040004u,
};
/* ROM 0x753210 */
static const uint32_t field_info_753210[8] = {
    0x40001204u, 0x10041008u, 0x2001380du, 0x00140008u,
    0x20013811u, 0x00480008u, 0x20013815u, 0x00400008u,
};
/* ROM 0x78d23c */
static const uint32_t field_info_78d23c[1] = {
    0x40001204u,
};
/* ROM 0x78d244 */
static const uint32_t field_info_78d244[1] = {
    0x40001204u,
};
/* ROM 0x78d24c */
static const uint32_t field_info_78d24c[1] = {
    0x40001204u,
};
/* ROM 0x7858b0 */
static const uint32_t field_info_7858b0[3] = {
    0x40001204u, 0x400a2209u, 0x00040008u,
};
/* ROM 0x6d3a18 */
static const uint32_t field_info_6d3a18[36] = {
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000004u,
    0x0001120au, 0x00000000u, 0x00000004u, 0x00000004u,
    0x0001120eu, 0x00000000u, 0x00000008u, 0x00000004u,
    0x00011212u, 0x00000000u, 0x0000000cu, 0x00000004u,
    0x00011216u, 0x00000000u, 0x00000010u, 0x00000004u,
    0x0001171au, 0x00000000u, 0x00000014u, 0x00000080u,
    0x0001121eu, 0x00000000u, 0x00000098u, 0x00000008u,
    0x00011722u, 0x00000000u, 0x000000a0u, 0x00000080u,
    0x00011726u, 0x00000000u, 0x00000120u, 0x00001b8au,
};
/* ROM 0x77607c */
static const uint32_t field_info_77607c[5] = {
    0x40001204u, 0x40041208u, 0x4008120cu, 0x400c1210u,
    0x40101214u,
};
/* ROM 0x78d254 */
static const uint32_t field_info_78d254[1] = {
    0x40001204u,
};
/* ROM 0x78a6c4 */
static const uint32_t field_info_78a6c4[2] = {
    0x10001204u, 0x40041208u,
};
/* ROM 0x78d25c */
static const uint32_t field_info_78d25c[1] = {
    0x40001204u,
};
/* ROM 0x78d264 */
static const uint32_t field_info_78d264[1] = {
    0x40001204u,
};
/* ROM 0x6cc61c */
static const uint32_t field_info_6cc61c[64] = {
    0x00011206u, 0x00000000u, 0x00000000u, 0x00000001u,
    0x0001120au, 0x00000000u, 0x00000004u, 0x00000004u,
    0x0001380eu, 0x00000008u, 0x00000010u, 0x00000008u,
    0x00013812u, 0x00000008u, 0x00000010u, 0x00000cf8u,
    0x00013816u, 0x00000008u, 0x00000010u, 0x00000008u,
    0x0001381au, 0x00000008u, 0x00000010u, 0x00000050u,
    0x0001381eu, 0x00000008u, 0x00000010u, 0x00000004u,
    0x00013822u, 0x00000008u, 0x00000010u, 0x00000004u,
    0x00013826u, 0x00000008u, 0x00000010u, 0x00000004u,
    0x0001382au, 0x00000008u, 0x00000010u, 0x00000030u,
    0x0001382eu, 0x00000008u, 0x00000010u, 0x00001cb0u,
    0x00013832u, 0x00000008u, 0x00000010u, 0x00000014u,
    0x00013836u, 0x00000008u, 0x00000010u, 0x00000004u,
    0x0001383au, 0x00000008u, 0x00000010u, 0x00000008u,
    0x0001383eu, 0x00000008u, 0x00000010u, 0x00000004u,
    0x00013842u, 0x00000008u, 0x00000010u, 0x00000004u,
};
/* ROM 0x760330 */
static const uint32_t field_info_760330[7] = {
    0x10001204u, 0x40041208u, 0x4008140cu, 0x400c1410u,
    0x40101214u, 0x10141218u, 0x1015121cu,
};
/* ROM 0x77f770 */
static const uint32_t field_info_77f770[4] = {
    0x10001204u, 0x20082809u, 0x00180004u, 0x10c4120cu,
};
/* ROM 0x76bd18 */
static const uint32_t field_info_76bd18[6] = {
    0x00011205u, 0x00010000u, 0x00011609u, 0x01020002u,
    0x0001120du, 0x00010104u,
};
/* ROM 0x77f784 */
static const uint32_t field_info_77f784[4] = {
    0x20032805u, 0x01060002u, 0x00011209u, 0x00010314u,
};
/* ROM 0x729ee4 */
static const uint32_t field_info_729ee4[12] = {
    0x00011205u, 0x00010000u, 0x00011209u, 0x00010001u,
    0x2001380du, 0x00180004u, 0x20013811u, 0x00c80004u,
    0x20013815u, 0x01060004u, 0x20013819u, 0x03160004u,
};
/* ROM 0x78dd1c */
static const uint32_t field_info_78dd1c[1] = {
    0x40001204u,
};
/* ROM 0x78dd24 */
static const uint32_t field_info_78dd24[1] = {
    0x40001204u,
};
/* ROM 0x76e168 */
static const uint32_t field_info_76e168[6] = {
    0x10001204u, 0x10011208u, 0x2001380du, 0x00040004u,
    0x20013811u, 0x00040004u,
};
/* ROM 0x7390d4 */
static const uint32_t field_info_7390d4[11] = {
    0x10001204u, 0x40041208u, 0x4008120cu, 0x400c1210u,
    0x40101214u, 0x40141218u, 0x4018121cu, 0x401c1220u,
    0x40201224u, 0x40241228u, 0x1028122cu,
};
/* ROM 0x7896f0 */
static const uint32_t field_info_7896f0[3] = {
    0x10001204u, 0x30011809u, 0x002c0004u,
};
/* ROM 0x783dd4 */
static const uint32_t field_info_783dd4[4] = {
    0x00011605u, 0x00420000u, 0x00011609u, 0x00820042u,
};
/* ROM 0x78c4dc */
static const uint32_t field_info_78c4dc[2] = {
    0x20142805u, 0x00c40002u,
};
/* ROM 0x772a08 */
static const uint32_t field_info_772a08[6] = {
    0x00011205u, 0x00040000u, 0x00011209u, 0x00040004u,
    0x0001160du, 0x04020008u,
};
/* ROM 0x789700 */
static const uint32_t field_info_789700[3] = {
    0x40001204u, 0x40041208u, 0x4008120cu,
};
/* ROM 0x78c4e8 */
static const uint32_t field_info_78c4e8[2] = {
    0x10001204u, 0x10011208u,
};
/* ROM 0x78f434 */
static const uint32_t field_info_78f434[0] = {
};
/* ROM 0x78c4f4 */
static const uint32_t field_info_78c4f4[2] = {
    0x00011605u, 0x00420000u,
};
/* ROM 0x78ead4 */
static const uint32_t field_info_78ead4[1] = {
    0x40001204u,
};
/* ROM 0x789710 */
static const uint32_t field_info_789710[3] = {
    0x40001204u, 0x40041208u, 0x4008120cu,
};
/* ROM 0x78eadc */
static const uint32_t field_info_78eadc[1] = {
    0x10001204u,
};
/* ROM 0x783de8 */
static const uint32_t field_info_783de8[4] = {
    0x40001204u, 0x40041208u, 0x4008120cu, 0x400c1210u,
};
/* ROM 0x6d7ee8 */
static const uint32_t field_info_6d7ee8[26] = {
    0x00011205u, 0x00010000u, 0x00011209u, 0x00010001u,
    0x2001380du, 0x00300004u, 0x20013811u, 0x0f520004u,
    0x20013815u, 0x040c0004u, 0x20013819u, 0x000c0004u,
    0x2001381du, 0x00020004u, 0x20013821u, 0x00010004u,
    0x20013825u, 0x00420004u, 0x20013829u, 0x00040004u,
    0x2001382du, 0x000c0004u, 0x20013831u, 0x00010004u,
    0x20013835u, 0x00100004u,
};
/* ROM 0x77cebc */
static const uint32_t field_info_77cebc[5] = {
    0x10001204u, 0x00011609u, 0x000a0002u, 0x400c120cu,
    0x10101210u,
};
/* ROM 0x745a0c */
static const uint32_t field_info_745a0c[10] = {
    0x00011605u, 0x04020000u, 0x00011609u, 0x04020402u,
    0x0001120du, 0x00010804u, 0x00011211u, 0x00040808u,
    0x00011615u, 0x0042080cu,
};
/* ROM 0x78c788 */
static const uint32_t field_info_78c788[2] = {
    0x10001204u, 0x10011208u,
};
/* ROM 0x78ec4c */
static const uint32_t field_info_78ec4c[1] = {
    0x40001204u,
};
/* ROM 0x78ec54 */
static const uint32_t field_info_78ec54[1] = {
    0x10001204u,
};
/* ROM 0x78f4ec */
static const uint32_t field_info_78f4ec[0] = {
};
/* ROM 0x7076d4 */
static const uint32_t field_info_7076d4[16] = {
    0x00011205u, 0x00010000u, 0x00011209u, 0x00010001u,
    0x2001380du, 0x00140004u, 0x20013811u, 0x08500004u,
    0x20013815u, 0x00020004u, 0x20013819u, 0x00040004u,
    0x2001381du, 0x00010004u, 0x20013821u, 0x00010004u,
};
static const pb_msgdesc_t g2_pb_msgdesc_77658c;
static const pb_msgdesc_t g2_pb_msgdesc_7765bc;
static const pb_msgdesc_t g2_pb_msgdesc_7765d4;
static const pb_msgdesc_t g2_pb_msgdesc_7765ec;
static const pb_msgdesc_t g2_pb_msgdesc_776604;
static const pb_msgdesc_t g2_pb_msgdesc_77661c;
static const pb_msgdesc_t g2_pb_msgdesc_776634;
static const pb_msgdesc_t g2_pb_msgdesc_77664c;
static const pb_msgdesc_t g2_pb_msgdesc_7762ec;
static const pb_msgdesc_t g2_pb_msgdesc_77631c;
static const pb_msgdesc_t g2_pb_msgdesc_776124;
static const pb_msgdesc_t g2_pb_msgdesc_77616c;
static const pb_msgdesc_t g2_pb_msgdesc_7761b4;
static const pb_msgdesc_t g2_pb_msgdesc_77619c;
static const pb_msgdesc_t g2_pb_msgdesc_77622c;
static const pb_msgdesc_t g2_pb_msgdesc_776214;
static const pb_msgdesc_t g2_pb_msgdesc_776274;
static const pb_msgdesc_t g2_pb_msgdesc_77625c;
static const pb_msgdesc_t g2_pb_msgdesc_7762a4;
static const pb_msgdesc_t g2_pb_msgdesc_776334;
static const pb_msgdesc_t g2_pb_msgdesc_7762d4;
static const pb_msgdesc_t g2_pb_msgdesc_776304;
static const pb_msgdesc_t g2_pb_msgdesc_77634c;
static const pb_msgdesc_t g2_pb_msgdesc_77613c;
static const pb_msgdesc_t g2_pb_msgdesc_776154;
static const pb_msgdesc_t g2_pb_msgdesc_776184;
static const pb_msgdesc_t g2_pb_msgdesc_7761cc;
static const pb_msgdesc_t g2_pb_msgdesc_7761e4;
static const pb_msgdesc_t g2_pb_msgdesc_7761fc;
static const pb_msgdesc_t g2_pb_msgdesc_776244;
static const pb_msgdesc_t g2_pb_msgdesc_77628c;
static const pb_msgdesc_t g2_pb_msgdesc_7762bc;
static const pb_msgdesc_t g2_pb_msgdesc_77637c;
static const pb_msgdesc_t g2_pb_msgdesc_776394;
static const pb_msgdesc_t g2_pb_msgdesc_7763ac;
static const pb_msgdesc_t g2_pb_msgdesc_7763c4;
static const pb_msgdesc_t g2_pb_msgdesc_7763dc;
static const pb_msgdesc_t g2_pb_msgdesc_7763f4;
static const pb_msgdesc_t g2_pb_msgdesc_77640c;
static const pb_msgdesc_t g2_pb_msgdesc_776364;
static const pb_msgdesc_t g2_pb_msgdesc_776004;
static const pb_msgdesc_t g2_pb_msgdesc_77601c;
static const pb_msgdesc_t g2_pb_msgdesc_776034;
static const pb_msgdesc_t g2_pb_msgdesc_77604c;
static const pb_msgdesc_t g2_pb_msgdesc_776064;
static const pb_msgdesc_t g2_pb_msgdesc_776094;
static const pb_msgdesc_t g2_pb_msgdesc_7760ac;
static const pb_msgdesc_t g2_pb_msgdesc_7760c4;
static const pb_msgdesc_t g2_pb_msgdesc_7760dc;
static const pb_msgdesc_t g2_pb_msgdesc_7760f4;
static const pb_msgdesc_t g2_pb_msgdesc_777a2c;
static const pb_msgdesc_t g2_pb_msgdesc_777a44;
static const pb_msgdesc_t g2_pb_msgdesc_777a5c;
static const pb_msgdesc_t g2_pb_msgdesc_777a74;
static const pb_msgdesc_t g2_pb_msgdesc_77976c;
static const pb_msgdesc_t g2_pb_msgdesc_779784;
static const pb_msgdesc_t g2_pb_msgdesc_77c334;
static const pb_msgdesc_t g2_pb_msgdesc_77c34c;
static const pb_msgdesc_t g2_pb_msgdesc_77c31c;
static const pb_msgdesc_t g2_pb_msgdesc_77c364;
static const pb_msgdesc_t g2_pb_msgdesc_77c37c;
static const pb_msgdesc_t g2_pb_msgdesc_77c394;
static const pb_msgdesc_t g2_pb_msgdesc_77c3ac;
static const pb_msgdesc_t g2_pb_msgdesc_77c3c4;
static const pb_msgdesc_t g2_pb_msgdesc_77c3dc;
static const pb_msgdesc_t g2_pb_msgdesc_77c3f4;
static const pb_msgdesc_t g2_pb_msgdesc_77c424;
static const pb_msgdesc_t g2_pb_msgdesc_77c40c;
static const pb_msgdesc_t g2_pb_msgdesc_77c43c;
static const pb_msgdesc_t g2_pb_msgdesc_77ced4;
static const pb_msgdesc_t g2_pb_msgdesc_77ceec;
static const pb_msgdesc_t g2_pb_msgdesc_77ce74;
static const pb_msgdesc_t g2_pb_msgdesc_77ce8c;
static const pb_msgdesc_t g2_pb_msgdesc_77cea4;
static const pb_msgdesc_t g2_pb_msgdesc_77cf04;

/* ROM 0x78ef88 */
static const pb_msgdesc_t *const submsg_info_78ef88[1] = {NULL};
/* ROM 0x78ef8c */
static const pb_msgdesc_t *const submsg_info_78ef8c[1] = {NULL};
/* ROM 0x78ef90 */
static const pb_msgdesc_t *const submsg_info_78ef90[1] = {NULL};
/* ROM 0x78ef94 */
static const pb_msgdesc_t *const submsg_info_78ef94[1] = {NULL};
/* ROM 0x78ef98 */
static const pb_msgdesc_t *const submsg_info_78ef98[1] = {NULL};
/* ROM 0x78ef9c */
static const pb_msgdesc_t *const submsg_info_78ef9c[1] = {NULL};
/* ROM 0x78efa0 */
static const pb_msgdesc_t *const submsg_info_78efa0[1] = {NULL};
/* ROM 0x78efa4 */
static const pb_msgdesc_t *const submsg_info_78efa4[1] = {NULL};
/* ROM 0x753450 */
static const pb_msgdesc_t *const submsg_info_753450[9] = {&g2_pb_msgdesc_77658c, &g2_pb_msgdesc_7765bc, &g2_pb_msgdesc_7765d4, &g2_pb_msgdesc_7765ec, &g2_pb_msgdesc_776604, &g2_pb_msgdesc_77661c, &g2_pb_msgdesc_776634, &g2_pb_msgdesc_77664c, NULL};
/* ROM 0x78ef54 */
static const pb_msgdesc_t *const submsg_info_78ef54[1] = {NULL};
/* ROM 0x78ef58 */
static const pb_msgdesc_t *const submsg_info_78ef58[1] = {NULL};
/* ROM 0x78ef28 */
static const pb_msgdesc_t *const submsg_info_78ef28[1] = {NULL};
/* ROM 0x78d274 */
static const pb_msgdesc_t *const submsg_info_78d274[2] = {&g2_pb_msgdesc_776124, NULL};
/* ROM 0x78ef34 */
static const pb_msgdesc_t *const submsg_info_78ef34[1] = {NULL};
/* ROM 0x78d27c */
static const pb_msgdesc_t *const submsg_info_78d27c[2] = {&g2_pb_msgdesc_7761b4, NULL};
/* ROM 0x78ef40 */
static const pb_msgdesc_t *const submsg_info_78ef40[1] = {NULL};
/* ROM 0x78d284 */
static const pb_msgdesc_t *const submsg_info_78d284[2] = {&g2_pb_msgdesc_77622c, NULL};
/* ROM 0x78ef48 */
static const pb_msgdesc_t *const submsg_info_78ef48[1] = {NULL};
/* ROM 0x78d28c */
static const pb_msgdesc_t *const submsg_info_78d28c[2] = {&g2_pb_msgdesc_776274, NULL};
/* ROM 0x7858c0 */
static const pb_msgdesc_t *const submsg_info_7858c0[4] = {&g2_pb_msgdesc_77619c, &g2_pb_msgdesc_776214, &g2_pb_msgdesc_77625c, NULL};
/* ROM 0x78a73c */
static const pb_msgdesc_t *const submsg_info_78a73c[3] = {&g2_pb_msgdesc_77616c, &g2_pb_msgdesc_7762a4, NULL};
/* ROM 0x78ef50 */
static const pb_msgdesc_t *const submsg_info_78ef50[1] = {NULL};
/* ROM 0x7858e0 */
static const pb_msgdesc_t *const submsg_info_7858e0[4] = {&g2_pb_msgdesc_77631c, &g2_pb_msgdesc_776334, &g2_pb_msgdesc_7762d4, NULL};
/* ROM 0x78ef5c */
static const pb_msgdesc_t *const submsg_info_78ef5c[1] = {NULL};
/* ROM 0x78ef2c */
static const pb_msgdesc_t *const submsg_info_78ef2c[1] = {NULL};
/* ROM 0x78ef30 */
static const pb_msgdesc_t *const submsg_info_78ef30[1] = {NULL};
/* ROM 0x78a6e8 */
static const pb_msgdesc_t *const submsg_info_78a6e8[3] = {&g2_pb_msgdesc_77613c, &g2_pb_msgdesc_776154, NULL};
/* ROM 0x78ef38 */
static const pb_msgdesc_t *const submsg_info_78ef38[1] = {NULL};
/* ROM 0x78ef3c */
static const pb_msgdesc_t *const submsg_info_78ef3c[1] = {NULL};
/* ROM 0x78a70c */
static const pb_msgdesc_t *const submsg_info_78a70c[3] = {&g2_pb_msgdesc_7761cc, &g2_pb_msgdesc_7761e4, NULL};
/* ROM 0x78ef44 */
static const pb_msgdesc_t *const submsg_info_78ef44[1] = {NULL};
/* ROM 0x78ef4c */
static const pb_msgdesc_t *const submsg_info_78ef4c[1] = {NULL};
/* ROM 0x7858d0 */
static const pb_msgdesc_t *const submsg_info_7858d0[4] = {&g2_pb_msgdesc_7761fc, &g2_pb_msgdesc_776244, &g2_pb_msgdesc_77628c, NULL};
/* ROM 0x78ef60 */
static const pb_msgdesc_t *const submsg_info_78ef60[1] = {NULL};
/* ROM 0x78ef64 */
static const pb_msgdesc_t *const submsg_info_78ef64[1] = {NULL};
/* ROM 0x78ef68 */
static const pb_msgdesc_t *const submsg_info_78ef68[1] = {NULL};
/* ROM 0x78ef6c */
static const pb_msgdesc_t *const submsg_info_78ef6c[1] = {NULL};
/* ROM 0x78ef70 */
static const pb_msgdesc_t *const submsg_info_78ef70[1] = {NULL};
/* ROM 0x78ef74 */
static const pb_msgdesc_t *const submsg_info_78ef74[1] = {NULL};
/* ROM 0x76a9d8 */
static const pb_msgdesc_t *const submsg_info_76a9d8[7] = {&g2_pb_msgdesc_77637c, &g2_pb_msgdesc_776394, &g2_pb_msgdesc_7763ac, &g2_pb_msgdesc_7763c4, &g2_pb_msgdesc_7763dc, &g2_pb_msgdesc_7763f4, NULL};
/* ROM 0x7858f0 */
static const pb_msgdesc_t *const submsg_info_7858f0[4] = {&g2_pb_msgdesc_776184, &g2_pb_msgdesc_7762bc, &g2_pb_msgdesc_77640c, NULL};
/* ROM 0x78ef00 */
static const pb_msgdesc_t *const submsg_info_78ef00[1] = {NULL};
/* ROM 0x78ef04 */
static const pb_msgdesc_t *const submsg_info_78ef04[1] = {NULL};
/* ROM 0x78ef08 */
static const pb_msgdesc_t *const submsg_info_78ef08[1] = {NULL};
/* ROM 0x78ef0c */
static const pb_msgdesc_t *const submsg_info_78ef0c[1] = {NULL};
/* ROM 0x78ef10 */
static const pb_msgdesc_t *const submsg_info_78ef10[1] = {NULL};
/* ROM 0x78ef14 */
static const pb_msgdesc_t *const submsg_info_78ef14[1] = {NULL};
/* ROM 0x78ef18 */
static const pb_msgdesc_t *const submsg_info_78ef18[1] = {NULL};
/* ROM 0x78ef1c */
static const pb_msgdesc_t *const submsg_info_78ef1c[1] = {NULL};
/* ROM 0x78ef20 */
static const pb_msgdesc_t *const submsg_info_78ef20[1] = {NULL};
/* ROM 0x78ef24 */
static const pb_msgdesc_t *const submsg_info_78ef24[1] = {NULL};
/* ROM 0x713c0c */
static const pb_msgdesc_t *const submsg_info_713c0c[15] = {&g2_pb_msgdesc_7762ec, &g2_pb_msgdesc_776304, &g2_pb_msgdesc_77634c, &g2_pb_msgdesc_776364, &g2_pb_msgdesc_776004, &g2_pb_msgdesc_77601c, &g2_pb_msgdesc_776034, &g2_pb_msgdesc_77604c, &g2_pb_msgdesc_776064, &g2_pb_msgdesc_776094, &g2_pb_msgdesc_7760ac, &g2_pb_msgdesc_7760c4, &g2_pb_msgdesc_7760dc, &g2_pb_msgdesc_7760f4, NULL};
/* ROM 0x78f110 */
static const pb_msgdesc_t *const submsg_info_78f110[1] = {NULL};
/* ROM 0x78d70c */
static const pb_msgdesc_t *const submsg_info_78d70c[2] = {&g2_pb_msgdesc_777a2c, NULL};
/* ROM 0x78f114 */
static const pb_msgdesc_t *const submsg_info_78f114[1] = {NULL};
/* ROM 0x78d714 */
static const pb_msgdesc_t *const submsg_info_78d714[2] = {&g2_pb_msgdesc_777a5c, NULL};
/* ROM 0x77f75c */
static const pb_msgdesc_t *const submsg_info_77f75c[5] = {&g2_pb_msgdesc_777a2c, &g2_pb_msgdesc_777a44, &g2_pb_msgdesc_777a5c, &g2_pb_msgdesc_777a74, NULL};
/* ROM 0x78f2cc */
static const pb_msgdesc_t *const submsg_info_78f2cc[1] = {NULL};
/* ROM 0x78f2d0 */
static const pb_msgdesc_t *const submsg_info_78f2d0[1] = {NULL};
/* ROM 0x78b5c4 */
static const pb_msgdesc_t *const submsg_info_78b5c4[3] = {&g2_pb_msgdesc_77976c, &g2_pb_msgdesc_779784, NULL};
/* ROM 0x78f424 */
static const pb_msgdesc_t *const submsg_info_78f424[1] = {NULL};
/* ROM 0x78eac4 */
static const pb_msgdesc_t *const submsg_info_78eac4[2] = {&g2_pb_msgdesc_77c334, NULL};
/* ROM 0x78f420 */
static const pb_msgdesc_t *const submsg_info_78f420[1] = {NULL};
/* ROM 0x78eacc */
static const pb_msgdesc_t *const submsg_info_78eacc[2] = {&g2_pb_msgdesc_77c31c, NULL};
/* ROM 0x78f428 */
static const pb_msgdesc_t *const submsg_info_78f428[1] = {NULL};
/* ROM 0x78f42c */
static const pb_msgdesc_t *const submsg_info_78f42c[1] = {NULL};
/* ROM 0x78f430 */
static const pb_msgdesc_t *const submsg_info_78f430[1] = {NULL};
/* ROM 0x78f438 */
static const pb_msgdesc_t *const submsg_info_78f438[1] = {NULL};
/* ROM 0x78f43c */
static const pb_msgdesc_t *const submsg_info_78f43c[1] = {NULL};
/* ROM 0x78f440 */
static const pb_msgdesc_t *const submsg_info_78f440[1] = {NULL};
/* ROM 0x78f448 */
static const pb_msgdesc_t *const submsg_info_78f448[1] = {NULL};
/* ROM 0x78f444 */
static const pb_msgdesc_t *const submsg_info_78f444[1] = {NULL};
/* ROM 0x78f44c */
static const pb_msgdesc_t *const submsg_info_78f44c[1] = {NULL};
/* ROM 0x7390a4 */
static const pb_msgdesc_t *const submsg_info_7390a4[12] = {&g2_pb_msgdesc_77c34c, &g2_pb_msgdesc_77c364, &g2_pb_msgdesc_77c37c, &g2_pb_msgdesc_77c394, &g2_pb_msgdesc_77c3ac, &g2_pb_msgdesc_77c3c4, &g2_pb_msgdesc_77c3dc, &g2_pb_msgdesc_77c3f4, &g2_pb_msgdesc_77c424, &g2_pb_msgdesc_77c40c, &g2_pb_msgdesc_77c43c, NULL};
/* ROM 0x78f4e4 */
static const pb_msgdesc_t *const submsg_info_78f4e4[1] = {NULL};
/* ROM 0x78f4e8 */
static const pb_msgdesc_t *const submsg_info_78f4e8[1] = {NULL};
/* ROM 0x78f4d8 */
static const pb_msgdesc_t *const submsg_info_78f4d8[1] = {NULL};
/* ROM 0x78f4dc */
static const pb_msgdesc_t *const submsg_info_78f4dc[1] = {NULL};
/* ROM 0x78f4e0 */
static const pb_msgdesc_t *const submsg_info_78f4e0[1] = {NULL};
/* ROM 0x78f4f0 */
static const pb_msgdesc_t *const submsg_info_78f4f0[1] = {NULL};
/* ROM 0x773ae0 */
static const pb_msgdesc_t *const submsg_info_773ae0[7] = {&g2_pb_msgdesc_77ced4, &g2_pb_msgdesc_77ceec, &g2_pb_msgdesc_77ce74, &g2_pb_msgdesc_77ce8c, &g2_pb_msgdesc_77cea4, &g2_pb_msgdesc_77cf04, NULL};
/* ROM 0x77658c */
static const pb_msgdesc_t g2_pb_msgdesc_77658c = {
    field_info_78d2ec, submsg_info_78ef88, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x7765bc */
static const pb_msgdesc_t g2_pb_msgdesc_7765bc = {
    field_info_7765a4, submsg_info_78ef8c, NULL, NULL, 3u, 0u, 3u};
/* ROM 0x7765d4 */
static const pb_msgdesc_t g2_pb_msgdesc_7765d4 = {
    field_info_78d2f4, submsg_info_78ef90, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x7765ec */
static const pb_msgdesc_t g2_pb_msgdesc_7765ec = {
    field_info_78d2fc, submsg_info_78ef94, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x776604 */
static const pb_msgdesc_t g2_pb_msgdesc_776604 = {
    field_info_78d304, submsg_info_78ef98, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77661c */
static const pb_msgdesc_t g2_pb_msgdesc_77661c = {
    field_info_6da610, submsg_info_78ef9c, NULL, NULL, 6u, 0u, 6u};
/* ROM 0x776634 */
static const pb_msgdesc_t g2_pb_msgdesc_776634 = {
    field_info_76aa9c, submsg_info_78efa0, NULL, NULL, 6u, 0u, 6u};
/* ROM 0x77664c */
static const pb_msgdesc_t g2_pb_msgdesc_77664c = {
    field_info_78d30c, submsg_info_78efa4, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x776664, dashboard extension (a-39-dashboard-ext/dashboard_ext_pb_file.c) */
const pb_msgdesc_t g2_dash_ext_pb_fields = {
    field_info_6d2bc8, submsg_info_753450, NULL, NULL, 10u, 0u, 10u};
/* ROM 0x7762ec */
static const pb_msgdesc_t g2_pb_msgdesc_7762ec = {
    field_info_78a730, submsg_info_78ef54, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x77631c */
static const pb_msgdesc_t g2_pb_msgdesc_77631c = {
    field_info_748cb4, submsg_info_78ef58, NULL, NULL, 7u, 0u, 7u};
/* ROM 0x776124 */
static const pb_msgdesc_t g2_pb_msgdesc_776124 = {
    field_info_7283e0, submsg_info_78ef28, NULL, NULL, 9u, 0u, 9u};
/* ROM 0x77616c */
static const pb_msgdesc_t g2_pb_msgdesc_77616c = {
    field_info_78a6dc, submsg_info_78d274, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x7761b4 */
static const pb_msgdesc_t g2_pb_msgdesc_7761b4 = {
    field_info_73d714, submsg_info_78ef34, NULL, NULL, 5u, 0u, 5u};
/* ROM 0x77619c */
static const pb_msgdesc_t g2_pb_msgdesc_77619c = {
    field_info_7531a4, submsg_info_78d27c, NULL, NULL, 4u, 0u, 4u};
/* ROM 0x77622c */
static const pb_msgdesc_t g2_pb_msgdesc_77622c = {
    field_info_6d4ba4, submsg_info_78ef40, NULL, NULL, 16u, 0u, 16u};
/* ROM 0x776214 */
static const pb_msgdesc_t g2_pb_msgdesc_776214 = {
    field_info_76a968, submsg_info_78d284, NULL, NULL, 3u, 0u, 3u};
/* ROM 0x776274 */
static const pb_msgdesc_t g2_pb_msgdesc_776274 = {
    field_info_73d740, submsg_info_78ef48, NULL, NULL, 5u, 0u, 5u};
/* ROM 0x77625c */
static const pb_msgdesc_t g2_pb_msgdesc_77625c = {
    field_info_7531c8, submsg_info_78d28c, NULL, NULL, 4u, 0u, 4u};
/* ROM 0x7762a4 */
static const pb_msgdesc_t g2_pb_msgdesc_7762a4 = {
    field_info_76a984, submsg_info_7858c0, NULL, NULL, 3u, 0u, 3u};
/* ROM 0x776334 */
static const pb_msgdesc_t g2_pb_msgdesc_776334 = {
    field_info_77eb90, submsg_info_78a73c, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x7762d4 */
static const pb_msgdesc_t g2_pb_msgdesc_7762d4 = {
    field_info_78d294, submsg_info_78ef50, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x776304 */
static const pb_msgdesc_t g2_pb_msgdesc_776304 = {
    field_info_7531ec, submsg_info_7858e0, NULL, NULL, 4u, 0u, 4u};
/* ROM 0x77634c */
static const pb_msgdesc_t g2_pb_msgdesc_77634c = {
    field_info_78a748, submsg_info_78ef5c, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x77613c */
static const pb_msgdesc_t g2_pb_msgdesc_77613c = {
    field_info_78d26c, submsg_info_78ef2c, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x776154 */
static const pb_msgdesc_t g2_pb_msgdesc_776154 = {
    field_info_78a6d0, submsg_info_78ef30, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x776184 */
static const pb_msgdesc_t g2_pb_msgdesc_776184 = {
    field_info_77eb68, submsg_info_78a6e8, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x7761cc */
static const pb_msgdesc_t g2_pb_msgdesc_7761cc = {
    field_info_78a6f4, submsg_info_78ef38, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x7761e4 */
static const pb_msgdesc_t g2_pb_msgdesc_7761e4 = {
    field_info_78a700, submsg_info_78ef3c, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x7761fc */
static const pb_msgdesc_t g2_pb_msgdesc_7761fc = {
    field_info_77eb7c, submsg_info_78a70c, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x776244 */
static const pb_msgdesc_t g2_pb_msgdesc_776244 = {
    field_info_78a718, submsg_info_78ef44, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77628c */
static const pb_msgdesc_t g2_pb_msgdesc_77628c = {
    field_info_78a724, submsg_info_78ef4c, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x7762bc */
static const pb_msgdesc_t g2_pb_msgdesc_7762bc = {
    field_info_76a9a0, submsg_info_7858d0, NULL, NULL, 3u, 0u, 3u};
/* ROM 0x77637c */
static const pb_msgdesc_t g2_pb_msgdesc_77637c = {
    field_info_78a754, submsg_info_78ef60, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x776394 */
static const pb_msgdesc_t g2_pb_msgdesc_776394 = {
    field_info_78d29c, submsg_info_78ef64, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x7763ac */
static const pb_msgdesc_t g2_pb_msgdesc_7763ac = {
    field_info_78d2a4, submsg_info_78ef68, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x7763c4 */
static const pb_msgdesc_t g2_pb_msgdesc_7763c4 = {
    field_info_78d2ac, submsg_info_78ef6c, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x7763dc */
static const pb_msgdesc_t g2_pb_msgdesc_7763dc = {
    field_info_76a9bc, submsg_info_78ef70, NULL, NULL, 5u, 0u, 5u};
/* ROM 0x7763f4 */
static const pb_msgdesc_t g2_pb_msgdesc_7763f4 = {
    field_info_78d2b4, submsg_info_78ef74, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77640c */
static const pb_msgdesc_t g2_pb_msgdesc_77640c = {
    field_info_71d650, submsg_info_76a9d8, NULL, NULL, 7u, 0u, 7u};
/* ROM 0x776364 */
static const pb_msgdesc_t g2_pb_msgdesc_776364 = {
    field_info_753210, submsg_info_7858f0, NULL, NULL, 5u, 0u, 5u};
/* ROM 0x776004 */
static const pb_msgdesc_t g2_pb_msgdesc_776004 = {
    field_info_78d23c, submsg_info_78ef00, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77601c */
static const pb_msgdesc_t g2_pb_msgdesc_77601c = {
    field_info_78d244, submsg_info_78ef04, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x776034 */
static const pb_msgdesc_t g2_pb_msgdesc_776034 = {
    field_info_78d24c, submsg_info_78ef08, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77604c */
static const pb_msgdesc_t g2_pb_msgdesc_77604c = {
    field_info_7858b0, submsg_info_78ef0c, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x776064 */
static const pb_msgdesc_t g2_pb_msgdesc_776064 = {
    field_info_6d3a18, submsg_info_78ef10, NULL, NULL, 9u, 0u, 9u};
/* ROM 0x776094 */
static const pb_msgdesc_t g2_pb_msgdesc_776094 = {
    field_info_77607c, submsg_info_78ef14, NULL, NULL, 5u, 0u, 5u};
/* ROM 0x7760ac */
static const pb_msgdesc_t g2_pb_msgdesc_7760ac = {
    field_info_78d254, submsg_info_78ef18, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x7760c4 */
static const pb_msgdesc_t g2_pb_msgdesc_7760c4 = {
    field_info_78a6c4, submsg_info_78ef1c, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x7760dc */
static const pb_msgdesc_t g2_pb_msgdesc_7760dc = {
    field_info_78d25c, submsg_info_78ef20, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x7760f4 */
static const pb_msgdesc_t g2_pb_msgdesc_7760f4 = {
    field_info_78d264, submsg_info_78ef24, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77610c, dashboard data package (a-38-dashboard-data-process) */
const pb_msgdesc_t g2_dashboard_package_fields = {
    field_info_6cc61c, submsg_info_713c0c, NULL, NULL, 16u, 0u, 16u};
/* ROM 0x777a2c */
static const pb_msgdesc_t g2_pb_msgdesc_777a2c = {
    field_info_760330, submsg_info_78f110, NULL, NULL, 7u, 0u, 7u};
/* ROM 0x777a44 */
static const pb_msgdesc_t g2_pb_msgdesc_777a44 = {
    field_info_77f770, submsg_info_78d70c, NULL, NULL, 3u, 0u, 3u};
/* ROM 0x777a5c */
static const pb_msgdesc_t g2_pb_msgdesc_777a5c = {
    field_info_76bd18, submsg_info_78f114, NULL, NULL, 3u, 0u, 3u};
/* ROM 0x777a74 */
static const pb_msgdesc_t g2_pb_msgdesc_777a74 = {
    field_info_77f784, submsg_info_78d714, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x777a14, health service (pb_service_health.c) */
const pb_msgdesc_t g2_health_pb_descriptor = {
    field_info_729ee4, submsg_info_77f75c, NULL, NULL, 6u, 0u, 6u};
/* ROM 0x77976c */
static const pb_msgdesc_t g2_pb_msgdesc_77976c = {
    field_info_78dd1c, submsg_info_78f2cc, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x779784 */
static const pb_msgdesc_t g2_pb_msgdesc_779784 = {
    field_info_78dd24, submsg_info_78f2d0, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77979c, module configure (p-03-general-configure) */
const pb_msgdesc_t g2_module_configure_pb_fields = {
    field_info_76e168, submsg_info_78b5c4, NULL, NULL, 4u, 0u, 4u};
/* ROM 0x77c334 */
static const pb_msgdesc_t g2_pb_msgdesc_77c334 = {
    field_info_7390d4, submsg_info_78f424, NULL, NULL, 11u, 0u, 11u};
/* ROM 0x77c34c */
static const pb_msgdesc_t g2_pb_msgdesc_77c34c = {
    field_info_7896f0, submsg_info_78eac4, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x77c31c */
static const pb_msgdesc_t g2_pb_msgdesc_77c31c = {
    field_info_783dd4, submsg_info_78f420, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x77c364 */
static const pb_msgdesc_t g2_pb_msgdesc_77c364 = {
    field_info_78c4dc, submsg_info_78eacc, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77c37c */
static const pb_msgdesc_t g2_pb_msgdesc_77c37c = {
    field_info_772a08, submsg_info_78f428, NULL, NULL, 3u, 0u, 3u};
/* ROM 0x77c394 */
static const pb_msgdesc_t g2_pb_msgdesc_77c394 = {
    field_info_789700, submsg_info_78f42c, NULL, NULL, 3u, 0u, 3u};
/* ROM 0x77c3ac */
static const pb_msgdesc_t g2_pb_msgdesc_77c3ac = {
    field_info_78c4e8, submsg_info_78f430, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x77c3c4 */
static const pb_msgdesc_t g2_pb_msgdesc_77c3c4 = {
    field_info_78f434, submsg_info_78f438, NULL, NULL, 0u, 0u, 0u};
/* ROM 0x77c3dc */
static const pb_msgdesc_t g2_pb_msgdesc_77c3dc = {
    field_info_78c4f4, submsg_info_78f43c, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77c3f4 */
static const pb_msgdesc_t g2_pb_msgdesc_77c3f4 = {
    field_info_78ead4, submsg_info_78f440, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77c424 */
static const pb_msgdesc_t g2_pb_msgdesc_77c424 = {
    field_info_789710, submsg_info_78f448, NULL, NULL, 3u, 0u, 3u};
/* ROM 0x77c40c */
static const pb_msgdesc_t g2_pb_msgdesc_77c40c = {
    field_info_78eadc, submsg_info_78f444, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77c43c */
static const pb_msgdesc_t g2_pb_msgdesc_77c43c = {
    field_info_783de8, submsg_info_78f44c, NULL, NULL, 4u, 0u, 4u};
/* ROM 0x77c304, teleprompt service (pb_service_teleprompt.c) */
const pb_msgdesc_t g2_teleprompt_pb_msgdesc_77c304 = {
    field_info_6d7ee8, submsg_info_7390a4, NULL, NULL, 13u, 0u, 13u};
/* ROM 0x77ced4 */
static const pb_msgdesc_t g2_pb_msgdesc_77ced4 = {
    field_info_77cebc, submsg_info_78f4e4, NULL, NULL, 4u, 0u, 4u};
/* ROM 0x77ceec */
static const pb_msgdesc_t g2_pb_msgdesc_77ceec = {
    field_info_745a0c, submsg_info_78f4e8, NULL, NULL, 5u, 0u, 5u};
/* ROM 0x77ce74 */
static const pb_msgdesc_t g2_pb_msgdesc_77ce74 = {
    field_info_78c788, submsg_info_78f4d8, NULL, NULL, 2u, 0u, 2u};
/* ROM 0x77ce8c */
static const pb_msgdesc_t g2_pb_msgdesc_77ce8c = {
    field_info_78ec4c, submsg_info_78f4dc, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77cea4 */
static const pb_msgdesc_t g2_pb_msgdesc_77cea4 = {
    field_info_78ec54, submsg_info_78f4e0, NULL, NULL, 1u, 0u, 1u};
/* ROM 0x77cf04 */
static const pb_msgdesc_t g2_pb_msgdesc_77cf04 = {
    field_info_78f4ec, submsg_info_78f4f0, NULL, NULL, 0u, 0u, 0u};
/* ROM 0x77ce5c, translate service (pb_service_translate.c) */
const pb_msgdesc_t g2_translate_pb_msgdesc = {
    field_info_7076d4, submsg_info_773ae0, NULL, NULL, 8u, 0u, 8u};
