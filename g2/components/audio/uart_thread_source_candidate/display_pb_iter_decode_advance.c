/* Native nanopb iterator field decoder 0x4d916e and advance 0x4d930a.
 * The descriptor and field records are source-defined; no stock data is embedded.
 */
#include <stddef.h>
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
_Static_assert(offsetof(struct pb_field_iter_candidate,type)==22u,"native type offset");
_Static_assert(sizeof(struct pb_msgdesc_candidate)==24u,"native descriptor size");

uint32_t audio_pb_iter_decode_field_4d916e(struct pb_field_iter_candidate *iter)
{
    const struct pb_msgdesc_candidate *desc=iter->descriptor;
    const uint32_t *words=desc->field_info+iter->field_info_index;
    uint32_t w0,w1,data_offset;
    int32_t size_offset;
    if (iter->index>=desc->field_count) return 0u;
    w0=words[0];
    iter->type=(uint8_t)(w0>>8);
    iter->tag=(uint16_t)((w0>>2)&63u);
    switch (w0&3u) {
    case 0u:
        iter->array_size=1u;
        size_offset=(int32_t)((w0>>24)&15u);
        data_offset=(w0>>16)&255u;
        iter->data_size=(uint16_t)(w0>>28);
        break;
    case 1u:
        w1=words[1];
        iter->array_size=(uint16_t)((w0>>16)&4095u);
        iter->tag=(uint16_t)(iter->tag|((w1>>28)<<6));
        size_offset=(int32_t)(w0>>28);
        data_offset=w1&65535u;
        iter->data_size=(uint16_t)((w1>>16)&4095u);
        break;
    case 2u:
        w1=words[1];
        iter->array_size=(uint16_t)(w0>>16);
        iter->tag=(uint16_t)(iter->tag|((w1>>8)<<6));
        size_offset=(int8_t)w1;
        data_offset=words[2];
        iter->data_size=(uint16_t)words[3];
        break;
    default:
        w1=words[1];
        iter->array_size=(uint16_t)words[4];
        iter->tag=(uint16_t)(iter->tag|((w1>>8)<<6));
        size_offset=(int8_t)w1;
        data_offset=words[2];
        iter->data_size=(uint16_t)words[3];
        break;
    }
    if (iter->message==NULL) {
        iter->field=NULL;
        iter->size=NULL;
        /* Native leaves data unchanged on this path. */
    } else {
        iter->field=(uint8_t *)iter->message+data_offset;
        if (size_offset==0) {
            if ((iter->type&0x30u)==0x20u &&
                ((iter->type&0xc0u)==0u || (iter->type&0xc0u)==0x80u))
                iter->size=&iter->array_size;
            else iter->size=NULL;
        } else iter->size=(uint8_t *)iter->field-(int8_t)size_offset;
        if ((iter->type&0xc0u)==0x80u && iter->field!=NULL)
            iter->data=*(void **)iter->field;
        else iter->data=iter->field;
    }
    if ((iter->type&15u)==8u || (iter->type&15u)==9u)
        iter->submessage_descriptor=desc->submsg_info[iter->submessage_index];
    else iter->submessage_descriptor=NULL;
    return 1u;
}

void audio_pb_iter_advance_4d930a(struct pb_field_iter_candidate *iter)
{
    uint32_t word;
    uint32_t type;
    iter->index=(uint16_t)(iter->index+1u);
    if (iter->index>=iter->descriptor->field_count) {
        iter->index=0u;
        iter->field_info_index=0u;
        iter->required_field_index=0u;
        iter->submessage_index=0u;
        return;
    }
    word=iter->descriptor->field_info[iter->field_info_index];
    type=(word>>8)&255u;
    iter->field_info_index=(uint16_t)(iter->field_info_index+(1u<<(word&3u)));
    iter->required_field_index=(uint16_t)(iter->required_field_index+((type&0x30u)==0u));
    iter->submessage_index=(uint16_t)(iter->submessage_index+((type&15u)==8u || (type&15u)==9u));
}
