/* Authenticated dashboard nanopb descriptor graph rooted at native 0x776574.
 * The call at 0x501ff8 loads its descriptor pointer from literal 0x502664.
 * Source: official s200 v2.2.6.10 OTA SHA-256 36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863.
 * Typed field initializers and relocations; final ROM placement is separate. */
/* Naming: *_field_info_<addr> / *_submsg_info_<addr> arrays carry their own
 * stock ROM address (byte-checked against the stock image); descriptors are
 * named by the descriptor address. */
#include <stdint.h>
struct pb_msgdesc_candidate {
 const uint32_t *field_info;
 const struct pb_msgdesc_candidate *const *submsg_info;
 const uint8_t *default_value;
 void *field_callback;
 uint16_t field_count,required_field_count,largest_tag;
};
_Static_assert(sizeof(struct pb_msgdesc_candidate)==24u,"ARM descriptor ABI");
#define FIELD1(tag,type,offset,size,size_offset) \
 (((((uint32_t)(tag))<<2u)&0xffu)|(((uint32_t)(type))<<8u)| \
 ((((uint32_t)(offset))&0xffu)<<16u)|((((uint32_t)(size_offset))&15u)<<24u)| \
 ((((uint32_t)(size))&15u)<<28u))
#define FIELD2(tag,type,offset,size,size_offset,array_size) \
 (1u|((((uint32_t)(tag))<<2u)&0xffu)|(((uint32_t)(type))<<8u)| \
 ((((uint32_t)(array_size))&0xfffu)<<16u)|((((uint32_t)(size_offset))&15u)<<28u)), \
 (((uint32_t)(offset)&0xffffu)|((((uint32_t)(size))&0xfffu)<<16u)| \
 ((((uint32_t)(tag))&0x3c0u)<<22u))
static const struct pb_msgdesc_candidate audio_uart_dashboard_pb_desc_7764e4;
static const struct pb_msgdesc_candidate audio_uart_dashboard_pb_desc_776514;
static const struct pb_msgdesc_candidate audio_uart_dashboard_pb_desc_77652c;
static const struct pb_msgdesc_candidate audio_uart_dashboard_pb_desc_776544;
static const struct pb_msgdesc_candidate audio_uart_dashboard_pb_desc_77655c;
const struct pb_msgdesc_candidate audio_uart_dashboard_pb_descriptor;
/* Native 0x7764e4: 3 fields, largest tag 3. */
static const uint32_t dashboard_field_info_785920[] = {
 FIELD1(1u,0x12u,0u,4u,0u),
 FIELD1(2u,0x12u,4u,1u,0u),
 FIELD1(3u,0x12u,5u,1u,0u),
 0u
};
static const struct pb_msgdesc_candidate *const dashboard_submsg_info_78ef78[] = {
 0
};
static const struct pb_msgdesc_candidate audio_uart_dashboard_pb_desc_7764e4 = {
 dashboard_field_info_785920,dashboard_submsg_info_78ef78,0,0,3u,0u,3u
};
/* Native 0x776514: 4 fields, largest tag 4. */
static const uint32_t dashboard_field_info_7764fc[] = {
 FIELD1(1u,0x12u,0u,4u,0u),
 FIELD1(2u,0x12u,4u,4u,0u),
 FIELD1(3u,0x12u,8u,4u,0u),
 FIELD2(4u,0x22u,14u,1u,2u,3u),
 0u
};
static const struct pb_msgdesc_candidate *const dashboard_submsg_info_78ef7c[] = {
 0
};
static const struct pb_msgdesc_candidate audio_uart_dashboard_pb_desc_776514 = {
 dashboard_field_info_7764fc,dashboard_submsg_info_78ef7c,0,0,4u,0u,4u
};
/* Native 0x77652c: 3 fields, largest tag 3. */
static const uint32_t dashboard_field_info_785930[] = {
 FIELD1(1u,0x12u,0u,4u,0u),
 FIELD1(2u,0x12u,4u,4u,0u),
 FIELD1(3u,0x12u,8u,4u,0u),
 0u
};
static const struct pb_msgdesc_candidate *const dashboard_submsg_info_78ef80[] = {
 0
};
static const struct pb_msgdesc_candidate audio_uart_dashboard_pb_desc_77652c = {
 dashboard_field_info_785930,dashboard_submsg_info_78ef80,0,0,3u,0u,3u
};
/* Native 0x776544: 4 fields, largest tag 4. */
static const uint32_t dashboard_field_info_76aa80[] = {
 FIELD1(1u,0x12u,0u,4u,0u),
 FIELD1(2u,0x12u,4u,4u,0u),
 FIELD2(3u,0x27u,10u,32u,2u,3u),
 FIELD2(4u,0x24u,108u,4u,2u,3u),
 0u
};
static const struct pb_msgdesc_candidate *const dashboard_submsg_info_78ef84[] = {
 0
};
static const struct pb_msgdesc_candidate audio_uart_dashboard_pb_desc_776544 = {
 dashboard_field_info_76aa80,dashboard_submsg_info_78ef84,0,0,4u,0u,4u
};
/* Native 0x77655c: 4 fields, largest tag 4. */
static const uint32_t dashboard_field_info_75342c[] = {
 FIELD2(1u,0x38u,4u,8u,4u,1u),
 FIELD2(2u,0x38u,4u,20u,4u,1u),
 FIELD2(3u,0x38u,4u,12u,4u,1u),
 FIELD2(4u,0x38u,4u,120u,4u,1u),
 0u
};
static const struct pb_msgdesc_candidate *const dashboard_submsg_info_77ec08[] = {
 &audio_uart_dashboard_pb_desc_7764e4,
 &audio_uart_dashboard_pb_desc_776514,
 &audio_uart_dashboard_pb_desc_77652c,
 &audio_uart_dashboard_pb_desc_776544,
 0
};
static const struct pb_msgdesc_candidate audio_uart_dashboard_pb_desc_77655c = {
 dashboard_field_info_75342c,dashboard_submsg_info_77ec08,0,0,4u,0u,4u
};
/* Native 0x776574: 6 fields, largest tag 7. */
static const uint32_t dashboard_field_info_73d9a8[] = {
 FIELD2(1u,0x17u,0u,16u,0u,1u),
 FIELD2(2u,0x17u,16u,32u,0u,1u),
 FIELD1(3u,0x12u,48u,1u,0u),
 FIELD1(4u,0x12u,52u,4u,0u),
 FIELD2(6u,0x22u,58u,1u,2u,5u),
 FIELD2(7u,0x18u,64u,124u,1u,1u),
 0u
};
static const struct pb_msgdesc_candidate *const dashboard_submsg_info_78d2e4[] = {
 &audio_uart_dashboard_pb_desc_77655c,
 0
};
const struct pb_msgdesc_candidate audio_uart_dashboard_pb_descriptor = {
 dashboard_field_info_73d9a8,dashboard_submsg_info_78d2e4,0,0,6u,0u,7u
};
const void *const audio_uart_dashboard_schema=&audio_uart_dashboard_pb_descriptor;
