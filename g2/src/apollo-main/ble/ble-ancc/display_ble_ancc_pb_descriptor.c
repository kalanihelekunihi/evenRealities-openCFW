/* Source-owned nanopb descriptor graph rooted at native 0x7799f4.
 * Field records are expressed by generator semantics, not a stock data blob.
 * Absolute ROM placement remains a separate image/linker obligation. */
#include <stddef.h>
#include <stdint.h>
struct pb_msgdesc_candidate {
    const uint32_t *field_info;
    const struct pb_msgdesc_candidate *const *submsg_info;
    const uint8_t *default_value;
    uint8_t (*field_callback)(void *,void *,const void *);
    uint16_t field_count,required_field_count,largest_tag;
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
static const struct pb_msgdesc_candidate desc_779a24,desc_779a54,desc_779a6c,desc_779a84,desc_779a9c;
static const uint32_t fields_7799f4[]={
    FIELD1(1u,0x12u,0u,1u,0u),FIELD1(2u,0x12u,1u,1u,0u),
    FIELD2(3u,0x38u,4u,5u,2u,1u),FIELD2(4u,0x38u,4u,70u,2u,1u),
    FIELD2(5u,0x38u,4u,2u,2u,1u),FIELD2(6u,0x38u,4u,2u,2u,1u),
    FIELD2(7u,0x38u,4u,8u,2u,1u),0u
};
static const struct pb_msgdesc_candidate *const sub_7799f4[]={
    &desc_779a24,&desc_779a54,&desc_779a6c,&desc_779a84,&desc_779a9c,0
};
const struct pb_msgdesc_candidate audio_ble_ancc_not_whitelisted_pb_descriptor={
    fields_7799f4,sub_7799f4,0,0,7u,0u,7u
};
static const uint32_t fields_779a24[]={
    FIELD1(1u,0x12u,0u,1u,0u),FIELD1(2u,0x12u,1u,1u,0u),
    FIELD1(3u,0x12u,2u,1u,0u),FIELD1(4u,0x12u,3u,1u,0u),
    FIELD1(5u,0x12u,4u,1u,0u),0u
};
static const struct pb_msgdesc_candidate *const sub_779a24[]={0};
static const struct pb_msgdesc_candidate desc_779a24={fields_779a24,sub_779a24,0,0,5u,0u,5u};
static const uint32_t fields_779a54[]={
    FIELD2(1u,0x16u,0u,34u,0u,1u),FIELD2(2u,0x16u,34u,34u,0u,1u),
    FIELD1(3u,0x12u,68u,1u,0u),0u
};
static const struct pb_msgdesc_candidate *const sub_779a54[]={0};
static const struct pb_msgdesc_candidate desc_779a54={fields_779a54,sub_779a54,0,0,3u,0u,3u};
static const uint32_t fields_779a6c[]={
    FIELD1(1u,0x12u,0u,1u,0u),FIELD1(2u,0x12u,1u,1u,0u),0u
};
static const struct pb_msgdesc_candidate *const sub_779a6c[]={0};
static const struct pb_msgdesc_candidate desc_779a6c={fields_779a6c,sub_779a6c,0,0,2u,0u,2u};
static const uint32_t fields_779a84[]={
    FIELD1(1u,0x12u,0u,1u,0u),FIELD1(2u,0x12u,1u,1u,0u),0u
};
static const struct pb_msgdesc_candidate *const sub_779a84[]={0};
static const struct pb_msgdesc_candidate desc_779a84={fields_779a84,sub_779a84,0,0,2u,0u,2u};
static const uint32_t fields_779a9c[]={
    FIELD1(1u,0x12u,0u,4u,0u),FIELD1(2u,0x12u,4u,1u,0u),
    FIELD1(3u,0x12u,5u,1u,0u),0u
};
static const struct pb_msgdesc_candidate *const sub_779a9c[]={0};
static const struct pb_msgdesc_candidate desc_779a9c={fields_779a9c,sub_779a9c,0,0,3u,0u,3u};
