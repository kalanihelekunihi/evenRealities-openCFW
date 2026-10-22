/* RingDataRelay nanopb graph rooted at native ROM 0x77b104.
 * Field words and graph pointers come from the official s200 2.2.6.10 image.
 * Absolute ROM placement remains a linker obligation. */
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
_Static_assert(sizeof(struct pb_msgdesc_candidate)==24u,"ARM nanopb descriptor ABI");
_Static_assert(offsetof(struct pb_msgdesc_candidate,field_count)==16u,"ARM field count offset");
#define FIELD1(tag,type,offset,size,size_offset) \
    (((((uint32_t)(tag))<<2u)&0xffu)|(((uint32_t)(type))<<8u)| \
     ((((uint32_t)(offset))&0xffu)<<16u)|((((uint32_t)(size_offset))&15u)<<24u)| \
     ((((uint32_t)(size))&15u)<<28u))
#define FIELD2(tag,type,offset,size,size_offset,array_size) \
    (1u|((((uint32_t)(tag))<<2u)&0xffu)|(((uint32_t)(type))<<8u)| \
     ((((uint32_t)(array_size))&0xfffu)<<16u)|((((uint32_t)(size_offset))&15u)<<28u)), \
    (((uint32_t)(offset)&0xffffu)|((((uint32_t)(size))&0xfffu)<<16u)| \
     ((((uint32_t)(tag))&0x3c0u)<<22u))
static const struct pb_msgdesc_candidate ring_pb_desc_77b134;
static const struct pb_msgdesc_candidate ring_pb_desc_77b14c;
static const uint32_t field_info_7709e0[] = {
    FIELD1(1u,0x12u,0u,1u,0u), FIELD1(2u,0x12u,1u,1u,0u),
    FIELD2(3u,0x38u,4u,20u,2u,1u), FIELD2(4u,0x38u,4u,60u,2u,1u), 0u
};
static const struct pb_msgdesc_candidate *const submsg_info_78bd80[] = {
    &ring_pb_desc_77b134, &ring_pb_desc_77b14c, 0
};
const struct pb_msgdesc_candidate audio_ring_pb_descriptor = {
    field_info_7709e0,submsg_info_78bd80,0,0,4u,0u,4u
};
static const uint32_t field_info_77b11c[] = {
    FIELD2(1u,0x16u,0u,8u,0u,1u), FIELD1(2u,0x12u,8u,1u,0u),
    FIELD1(3u,0x12u,12u,4u,0u), FIELD1(4u,0x12u,16u,1u,0u), 0u
};
static const struct pb_msgdesc_candidate *const submsg_info_78f3b0[] = {0};
static const struct pb_msgdesc_candidate ring_pb_desc_77b134 = {
    field_info_77b11c,submsg_info_78f3b0,0,0,4u,0u,4u
};
static const uint32_t field_info_6fc80c[] = {
    FIELD1(1u,0x12u,0u,1u,0u), FIELD1(2u,0x12u,1u,1u,0u),
    FIELD1(3u,0x12u,2u,1u,0u), FIELD1(4u,0x12u,4u,4u,0u),
    FIELD1(5u,0x12u,8u,1u,0u), FIELD1(6u,0x12u,12u,4u,0u),
    FIELD1(7u,0x12u,16u,2u,0u), FIELD1(8u,0x12u,20u,4u,0u),
    FIELD1(9u,0x12u,24u,2u,0u), FIELD1(10u,0x12u,28u,4u,0u),
    FIELD1(11u,0x12u,32u,2u,0u), FIELD1(12u,0x12u,36u,4u,0u),
    FIELD1(13u,0x12u,40u,2u,0u), FIELD1(14u,0x12u,44u,4u,0u),
    FIELD1(15u,0x12u,48u,4u,0u), FIELD1(16u,0x12u,52u,4u,0u),
    FIELD1(17u,0x12u,56u,1u,0u), 0u
};
static const struct pb_msgdesc_candidate *const submsg_info_78f3b4[] = {0};
static const struct pb_msgdesc_candidate ring_pb_desc_77b14c = {
    field_info_6fc80c,submsg_info_78f3b4,0,0,17u,0u,17u
};
