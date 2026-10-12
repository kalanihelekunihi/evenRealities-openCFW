/* Authenticated generated nanopb descriptor graph rooted at native 0x7766dc.
 * Source: official s200 v2.2.6.10 OTA SHA-256 36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863.
 * Nanopb field generator semantics: PB_FIELDINFO_1/2; no stock byte blob.
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
_Static_assert(offsetof(struct pb_msgdesc_candidate,field_count)==16u,"ARM nanopb field count offset");
#define FIELD1(tag,type,offset,size,size_offset) \
    (((((uint32_t)(tag))<<2u)&0xffu)|(((uint32_t)(type))<<8u)| \
     ((((uint32_t)(offset))&0xffu)<<16u)|((((uint32_t)(size_offset))&15u)<<24u)| \
     ((((uint32_t)(size))&15u)<<28u))
#define FIELD2(tag,type,offset,size,size_offset,array_size) \
    (1u|((((uint32_t)(tag))<<2u)&0xffu)|(((uint32_t)(type))<<8u)| \
     ((((uint32_t)(array_size))&0xfffu)<<16u)|((((uint32_t)(size_offset))&15u)<<28u)), \
    (((uint32_t)(offset)&0xffffu)|((((uint32_t)(size))&0xfffu)<<16u)| \
     ((((uint32_t)(tag))&0x3c0u)<<22u))
const struct pb_msgdesc_candidate audio_ble_ring_connect_pb_descriptor;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_7766f4;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77670c;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_776724;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77673c;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_776754;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77676c;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_776784;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77679c;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_7767b4;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_7767cc;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_7767fc;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_776814;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77682c;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_776844;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77685c;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_776874;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77688c;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_7768a4;
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_7768bc;
/* Native 0x7766dc: 16 fields, largest tag 129. */
static const uint32_t ring_fields_7766dc[] = {
    FIELD2(1u,0x12u,0u,1u,0u,1u),
    FIELD2(2u,0x12u,2u,2u,0u,1u),
    FIELD2(3u,0x38u,8u,3u,4u,1u),
    FIELD2(4u,0x38u,8u,2u,4u,1u),
    FIELD2(5u,0x38u,8u,30u,4u,1u),
    FIELD2(6u,0x38u,8u,8u,4u,1u),
    FIELD2(7u,0x38u,8u,12u,4u,1u),
    FIELD2(8u,0x38u,8u,12u,4u,1u),
    FIELD2(9u,0x38u,8u,2u,4u,1u),
    FIELD2(10u,0x38u,8u,200u,4u,1u),
    FIELD2(11u,0x38u,8u,200u,4u,1u),
    FIELD2(12u,0x38u,8u,1u,4u,1u),
    FIELD2(13u,0x38u,8u,1u,4u,1u),
    FIELD2(14u,0x38u,8u,1u,4u,1u),
    FIELD2(128u,0x38u,8u,8u,4u,1u),
    FIELD2(129u,0x38u,8u,12u,4u,1u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_7766dc[] = {
    &audio_ble_ring_pb_desc_7767b4,
    &audio_ble_ring_pb_desc_776814,
    &audio_ble_ring_pb_desc_7767cc,
    &audio_ble_ring_pb_desc_7767fc,
    &audio_ble_ring_pb_desc_77682c,
    &audio_ble_ring_pb_desc_776844,
    &audio_ble_ring_pb_desc_7766f4,
    &audio_ble_ring_pb_desc_77670c,
    &audio_ble_ring_pb_desc_77670c,
    &audio_ble_ring_pb_desc_77685c,
    &audio_ble_ring_pb_desc_77688c,
    &audio_ble_ring_pb_desc_776874,
    &audio_ble_ring_pb_desc_7768a4,
    &audio_ble_ring_pb_desc_7768bc,
    0
};
const struct pb_msgdesc_candidate audio_ble_ring_connect_pb_descriptor = {
    ring_fields_7766dc,ring_submessages_7766dc,0,0,16u,0u,129u
};
/* Native 0x7766f4: 2 fields, largest tag 2. */
static const uint32_t ring_fields_7766f4[] = {
    FIELD1(1u,0x12u,0u,1u,0u),
    FIELD1(2u,0x12u,1u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_7766f4[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_7766f4 = {
    ring_fields_7766f4,ring_submessages_7766f4,0,0,2u,0u,2u
};
/* Native 0x77670c: 2 fields, largest tag 2. */
static const uint32_t ring_fields_77670c[] = {
    FIELD2(1u,0x28u,4u,24u,4u,8u),
    FIELD2(2u,0x12u,196u,1u,0u,1u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_77670c[] = {
    &audio_ble_ring_pb_desc_776724,
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77670c = {
    ring_fields_77670c,ring_submessages_77670c,0,0,2u,0u,2u
};
/* Native 0x776724: 9 fields, largest tag 9. */
static const uint32_t ring_fields_776724[] = {
    FIELD1(1u,0x12u,0u,1u,0u),
    FIELD2(2u,0x38u,4u,8u,2u,1u),
    FIELD1(3u,0x32u,4u,1u,2u),
    FIELD2(4u,0x38u,4u,8u,2u,1u),
    FIELD2(5u,0x38u,4u,8u,2u,1u),
    FIELD2(6u,0x38u,4u,12u,2u,1u),
    FIELD2(7u,0x38u,4u,20u,2u,1u),
    FIELD2(8u,0x38u,4u,20u,2u,1u),
    FIELD2(9u,0x38u,4u,10u,2u,1u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_776724[] = {
    &audio_ble_ring_pb_desc_77673c,
    &audio_ble_ring_pb_desc_776754,
    &audio_ble_ring_pb_desc_776754,
    &audio_ble_ring_pb_desc_776784,
    &audio_ble_ring_pb_desc_77676c,
    &audio_ble_ring_pb_desc_77676c,
    &audio_ble_ring_pb_desc_77679c,
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_776724 = {
    ring_fields_776724,ring_submessages_776724,0,0,9u,0u,9u
};
/* Native 0x77673c: 3 fields, largest tag 3. */
static const uint32_t ring_fields_77673c[] = {
    FIELD1(1u,0x12u,0u,4u,0u),
    FIELD1(2u,0x12u,4u,1u,0u),
    FIELD1(3u,0x12u,5u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_77673c[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77673c = {
    ring_fields_77673c,ring_submessages_77673c,0,0,3u,0u,3u
};
/* Native 0x776754: 2 fields, largest tag 2. */
static const uint32_t ring_fields_776754[] = {
    FIELD1(1u,0x12u,0u,4u,0u),
    FIELD1(2u,0x12u,4u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_776754[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_776754 = {
    ring_fields_776754,ring_submessages_776754,0,0,2u,0u,2u
};
/* Native 0x77676c: 2 fields, largest tag 2. */
static const uint32_t ring_fields_77676c[] = {
    FIELD2(1u,0x16u,0u,18u,0u,1u),
    FIELD1(2u,0x12u,18u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_77676c[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77676c = {
    ring_fields_77676c,ring_submessages_77676c,0,0,2u,0u,2u
};
/* Native 0x776784: 3 fields, largest tag 3. */
static const uint32_t ring_fields_776784[] = {
    FIELD1(1u,0x12u,0u,4u,0u),
    FIELD1(2u,0x12u,4u,4u,0u),
    FIELD1(3u,0x12u,8u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_776784[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_776784 = {
    ring_fields_776784,ring_submessages_776784,0,0,3u,0u,3u
};
/* Native 0x77679c: 2 fields, largest tag 2. */
static const uint32_t ring_fields_77679c[] = {
    FIELD2(1u,0x16u,0u,8u,0u,1u),
    FIELD1(2u,0x12u,8u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_77679c[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77679c = {
    ring_fields_77679c,ring_submessages_77679c,0,0,2u,0u,2u
};
/* Native 0x7767b4: 3 fields, largest tag 3. */
static const uint32_t ring_fields_7767b4[] = {
    FIELD1(1u,0x10u,0u,1u,0u),
    FIELD1(2u,0x12u,1u,1u,0u),
    FIELD1(3u,0x12u,2u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_7767b4[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_7767b4 = {
    ring_fields_7767b4,ring_submessages_7767b4,0,0,3u,0u,3u
};
/* Native 0x7767cc: 5 fields, largest tag 5. */
static const uint32_t ring_fields_7767cc[] = {
    FIELD1(1u,0x10u,0u,1u,0u),
    FIELD2(2u,0x16u,2u,8u,0u,1u),
    FIELD2(3u,0x16u,10u,18u,0u,1u),
    FIELD1(4u,0x12u,28u,1u,0u),
    FIELD1(5u,0x12u,29u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_7767cc[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_7767cc = {
    ring_fields_7767cc,ring_submessages_7767cc,0,0,5u,0u,5u
};
/* Native 0x7767fc: 5 fields, largest tag 5. */
static const uint32_t ring_fields_7767fc[] = {
    FIELD1(1u,0x12u,0u,2u,0u),
    FIELD1(2u,0x12u,2u,2u,0u),
    FIELD1(3u,0x12u,4u,1u,0u),
    FIELD1(4u,0x10u,5u,1u,0u),
    FIELD1(5u,0x12u,6u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_7767fc[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_7767fc = {
    ring_fields_7767fc,ring_submessages_7767fc,0,0,5u,0u,5u
};
/* Native 0x776814: 2 fields, largest tag 2. */
static const uint32_t ring_fields_776814[] = {
    FIELD1(1u,0x12u,0u,1u,0u),
    FIELD1(2u,0x12u,1u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_776814[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_776814 = {
    ring_fields_776814,ring_submessages_776814,0,0,2u,0u,2u
};
/* Native 0x77682c: 3 fields, largest tag 3. */
static const uint32_t ring_fields_77682c[] = {
    FIELD1(1u,0x12u,0u,1u,0u),
    FIELD2(2u,0x16u,2u,8u,0u,1u),
    FIELD1(3u,0x12u,10u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_77682c[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77682c = {
    ring_fields_77682c,ring_submessages_77682c,0,0,3u,0u,3u
};
/* Native 0x776844: 3 fields, largest tag 3. */
static const uint32_t ring_fields_776844[] = {
    FIELD1(1u,0x12u,0u,1u,0u),
    FIELD2(2u,0x16u,2u,8u,0u,1u),
    FIELD1(3u,0x12u,10u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_776844[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_776844 = {
    ring_fields_776844,ring_submessages_776844,0,0,3u,0u,3u
};
/* Native 0x77685c: 1 fields, largest tag 1. */
static const uint32_t ring_fields_77685c[] = {
    FIELD1(1u,0x12u,0u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_77685c[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77685c = {
    ring_fields_77685c,ring_submessages_77685c,0,0,1u,0u,1u
};
/* Native 0x776874: 1 fields, largest tag 1. */
static const uint32_t ring_fields_776874[] = {
    FIELD1(1u,0x12u,0u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_776874[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_776874 = {
    ring_fields_776874,ring_submessages_776874,0,0,1u,0u,1u
};
/* Native 0x77688c: 1 fields, largest tag 1. */
static const uint32_t ring_fields_77688c[] = {
    FIELD1(1u,0x12u,0u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_77688c[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_77688c = {
    ring_fields_77688c,ring_submessages_77688c,0,0,1u,0u,1u
};
/* Native 0x7768a4: 3 fields, largest tag 3. */
static const uint32_t ring_fields_7768a4[] = {
    FIELD1(1u,0x12u,0u,4u,0u),
    FIELD1(2u,0x11u,4u,1u,0u),
    FIELD1(3u,0x12u,5u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_7768a4[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_7768a4 = {
    ring_fields_7768a4,ring_submessages_7768a4,0,0,3u,0u,3u
};
/* Native 0x7768bc: 3 fields, largest tag 3. */
static const uint32_t ring_fields_7768bc[] = {
    FIELD1(1u,0x12u,0u,1u,0u),
    FIELD1(2u,0x12u,4u,4u,0u),
    FIELD1(3u,0x12u,8u,1u,0u),
    0u
};
static const struct pb_msgdesc_candidate *const ring_submessages_7768bc[] = {
    0
};
static const struct pb_msgdesc_candidate audio_ble_ring_pb_desc_7768bc = {
    ring_fields_7768bc,ring_submessages_7768bc,0,0,3u,0u,3u
};
