/* Native nanopb field and extension lookup, 0x4d93f8 and 0x4d946e.
 * The 40-byte iterator layout is shared with display_pb_iter_decode_advance.c.
 */
#include <stdint.h>

struct pb_msgdesc_candidate {
    const uint32_t *field_info;
    const struct pb_msgdesc_candidate *const *submsg_info;
    const uint8_t *default_value;
    void *field_callback;
    uint16_t field_count,required_field_count,largest_tag;
};
struct pb_field_iter_candidate {
    const struct pb_msgdesc_candidate *descriptor;
    void *message;
    uint16_t index,field_info_index,required_field_index,submessage_index;
    uint16_t tag,data_size,array_size;
    uint8_t type;
    void *field,*data,*size;
    const struct pb_msgdesc_candidate *submessage_descriptor;
};
_Static_assert(sizeof(struct pb_field_iter_candidate)==40u,"native iterator size");
extern void audio_pb_iter_advance_4d930a(struct pb_field_iter_candidate *);
extern uint32_t audio_pb_iter_decode_field_4d916e(struct pb_field_iter_candidate *);

uint32_t audio_pb_iter_find_tag_4d93f8(struct pb_field_iter_candidate *iter,uint32_t tag)
{
    uint16_t start;
    if (iter->tag==tag) return 1u;
    if (iter->descriptor->largest_tag<tag) return 0u;
    start=iter->index;
    if (tag<iter->tag) iter->index=iter->descriptor->field_count;
    do {
        audio_pb_iter_advance_4d930a(iter);
        if (((iter->descriptor->field_info[iter->field_info_index]>>2)&63u)==(tag&63u)) {
            audio_pb_iter_decode_field_4d916e(iter);
            if (iter->tag==tag && (iter->type&15u)!=10u) return 1u;
        }
    } while (iter->index!=start);
    audio_pb_iter_decode_field_4d916e(iter);
    return 0u;
}

uint32_t audio_pb_iter_find_extension_4d946e(struct pb_field_iter_candidate *iter)
{
    uint16_t start;
    if ((iter->type&15u)==10u) return 1u;
    start=iter->index;
    do {
        audio_pb_iter_advance_4d930a(iter);
        if (((iter->descriptor->field_info[iter->field_info_index]>>8)&15u)==10u)
            return audio_pb_iter_decode_field_4d916e(iter);
    } while (iter->index!=start);
    audio_pb_iter_decode_field_4d916e(iter);
    return 0u;
}
